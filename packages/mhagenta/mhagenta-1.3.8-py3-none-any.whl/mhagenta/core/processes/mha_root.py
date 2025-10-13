import asyncio
import logging
import subprocess
import sys
import time
from argparse import ArgumentError
from pathlib import Path
from typing import Any, Iterable, Literal

import dill

from mhagenta.utils import AgentCmd, StatusReport, Directory, ModuleTypes
from mhagenta.utils.common import DEFAULT_LOG_FORMAT
from mhagenta.core.connection import RootMessenger, Connector
from mhagenta.core.processes.process import MHAProcess
from mhagenta.core.processes.mha_module import GlobalParams, ModuleBase
from mhagenta.bases import *


def initialize_module(
        global_params: GlobalParams,
        base: ModuleBase,
        path: Path | str = '.',
        merge_output: bool = False
) -> subprocess.Popen:
    if isinstance(path, str):
        path = Path(path)
    path = path.resolve()
    if path.is_dir():
        path = path / base.module_id
    path.parent.mkdir(parents=True, exist_ok=True)

    kwargs = {
        'global_params': global_params.model_dump(),
        'base': dill.dumps(base, recurse=True)
    }

    params = {
        'class': base.module_type,
        'kwargs': kwargs
    }
    with open(path, 'wb') as f:
        dill.dump(params, f, recurse=True)

    return subprocess.Popen([
        f'{Path(sys.executable).resolve()}',
        f'{(Path(__file__).parent.parent / "module_launcher.py").resolve()}',
        f'\"{path.resolve()}\"'],
        stdout=subprocess.PIPE if merge_output else None,
        stderr=subprocess.STDOUT if merge_output else None
    )


class MHARoot(MHAProcess):
    class ModuleData:
        def __init__(self, base: ModuleBase):
            self.module_id = base.module_id
            self.process: subprocess.Popen | None = None
            self.base: ModuleBase = base
            self.ready: bool = False
            self.status: str = 'DECLARED'
            self.ts_status: float | None = None

    def __init__(self,
                 agent_id: str,
                 connector_cls: type[Connector],
                 directory: Directory,
                 modules: Iterable[ModuleBase] | None = None,
                 perceptors: Iterable[PerceptorBase] | PerceptorBase | None = None,
                 actuators: Iterable[ActuatorBase] | ActuatorBase | None = None,
                 ll_reasoners: Iterable[LLReasonerBase] | LLReasonerBase | None = None,
                 learners: Iterable[LearnerBase] | LearnerBase | None = None,
                 knowledge: Iterable[KnowledgeBase] | KnowledgeBase | None = None,
                 hl_reasoners: Iterable[HLReasonerBase] | HLReasonerBase | None = None,
                 goal_graphs: Iterable[GoalGraphBase] | GoalGraphBase | None = None,
                 memory: Iterable[MemoryBase] | MemoryBase | None = None,
                 connector_kwargs: dict[str, Any] | None = None,
                 step_frequency: float = 0.1,
                 status_frequency: float = 5.,
                 control_frequency: float = 0.05,
                 exec_start_time: float | None = None,
                 start_delay: float = 5.,
                 exec_duration: float = 60.,
                 save_dir: Path | str = './out/save',
                 save_format: Literal['json', 'dill'] = 'json',
                 resume: bool = False,
                 log_level: int = logging.INFO,
                 log_format: str = DEFAULT_LOG_FORMAT,
                 status_msg_format: str = '[status_upd]::{}'
                 ) -> None:
        agent_start_time = time.time()
        super().__init__(
            agent_id=agent_id,
            agent_start_time=agent_start_time,
            exec_start_time=None,
            init_timeout=60.,
            exec_duration=exec_duration,
            step_frequency=step_frequency,
            control_frequency=control_frequency,
            log_id='root',
            log_level=log_level,
            log_format=log_format
        )
        self._expected_start_time = exec_start_time

        if modules is None:
            modules: list[ModuleBase] = list()
        else:
            modules = list(modules)
        self._extend_modules_list(modules, perceptors)
        self._extend_modules_list(modules, actuators)
        self._extend_modules_list(modules, ll_reasoners)
        self._extend_modules_list(modules, learners)
        self._extend_modules_list(modules, knowledge)
        self._extend_modules_list(modules, hl_reasoners)
        self._extend_modules_list(modules, goal_graphs)
        self._extend_modules_list(modules, memory)

        self._directory = directory
        for module in modules:
            self._directory.internal._add_module(module.module_id, module.module_type, module.tags)

        if not modules:
            raise ValueError('No modules specified!')

        self._status_msg_format = status_msg_format
        self._modules: dict[str, MHARoot.ModuleData] = dict()

        self._start_delay = start_delay

        self._stop_sent = False

        if connector_kwargs is None:
            connector_kwargs = {}

        if not Path(save_dir).exists():
            Path(save_dir).mkdir(parents=True, exist_ok=True)

        self._global_params = GlobalParams(
            agent_id=agent_id,
            directory=self._directory,
            connector_cls=connector_cls,
            connector_kwargs=connector_kwargs,
            step_frequency=step_frequency,
            status_frequency=status_frequency,
            control_frequency=control_frequency,
            agent_start_time=agent_start_time,
            exec_duration=exec_duration,
            save_dir=str(save_dir.resolve()) if isinstance(save_dir, Path) else save_dir,
            save_format=save_format,
            resume=resume,
            log_level=log_level,
            log_format=log_format
        )

        self._messenger = RootMessenger(
            connector_cls=connector_cls,
            agent_id=agent_id,
            agent_time=self._time,
            status_callback=self.on_status,
            log_tags=self._log_tags,
            log_level=log_level,
            log_format=log_format,
            **connector_kwargs
        )

        self._add_modules(modules)

    async def on_init(self) -> None:
        self.debug('Initializing messenger...')
        await self._messenger.initialize()
        self.debug('Messenger initialized!')

    async def on_start(self) -> None:
        self._task_group.create_task(self._messenger.start())
        self._init_modules()
        self._queue.push(
            func=self.update_module_statuses,
            ts=self._time.agent,
            priority=True,
            periodic=True,
            frequency=self._global_params.status_frequency / 2.
        )
        self._queue.push(
            func=self._run,
            ts=self._time.agent,
            priority=True,
            periodic=True,
            frequency=self._control_frequency,
            stop_condition=lambda: self._stage == self.Stage.ready
        )

    def _run(self) -> None:
        if self._stage >= self.Stage.running:
            return

        if self._stage == self.Stage.ready:
            self._stage = self.Stage.running

    async def on_run(self) -> None:
        self._queue.push(
            func=self.synchronous_start,
            ts=self._time.agent,
            priority=True,
            periodic=True,
            frequency=self._control_frequency,
            stop_condition=lambda: all([module.ready for module in self._modules.values()]),
            # delay=self._start_delay
        )

    def cmd(self, cmd: AgentCmd) -> None:
        self._messenger.cmd(cmd=cmd)

    def on_status(self, status: StatusReport) -> None:
        if status.agent_id != self._agent_id or status.module_id not in self._modules:
            self.error(f'Wrongly received status for agent {status.agent_id}!')
            return

        self.debug(f'Received status: \"{status.module_id}:{status.status}\".')
        self._modules[status.module_id].status = status.status
        if status.status == status.READY:
            self._modules[status.module_id].ready = True
        elif status.status == status.FINISHED:
            self._modules[status.module_id].ready = False
        self._modules[status.module_id].ts_status = status.ts

    def _check_status_timeouts(self) -> None:
        for module in self._modules.values():
            if module.ts_status is None:
                continue
            if (self._time.agent - module.ts_status) >= 2 * self._global_params.status_frequency:
                module.status = f'{StatusReport.TIMEOUT}({module.ts_status})'

    def update_module_statuses(self) -> None:
        self.debug('Updating module statuses...')
        if self._stage == self.Stage.running:
            self._check_status_timeouts()

        self.log(level=logging.CRITICAL, message=self._status_msg_format.format(','.join([f'{module.base.module_id}:{module.status}' for module in self._modules.values()])))

    def _add_modules(self, bases: Iterable[ModuleBase] | ModuleBase | None) -> None:
        if bases is None:
            return
        if isinstance(bases, ModuleBase):
            self._modules[bases.module_id] = self.ModuleData(bases)
        else:
            for base in bases:
                self._modules[base.module_id] = self.ModuleData(base)

    def _init_modules(self) -> None:
        for module_id, module in self._modules.items():
            self.debug(f'Initializing module {module_id}...')
            module.process = initialize_module(
                global_params=self._global_params,
                base=module.base,
                path=Path(self._global_params.save_dir) / f'{module_id}.mha',
            )
            self.debug(f'Module {module_id} initialized!')

    def synchronous_start(self) -> None:
        if not all([module.ready for module in self._modules.values()]):
            return

        self._time.set_exec_start_ts(
            max(
                self._time.system,
                self._expected_start_time + self._start_delay
            ))
        self._stop_time = self._time.exec_start_ts - self._time.agent_start_ts + self._global_params.exec_duration
        self.info(f'Starting execution! Scheduling module execution start at {self._time.exec_start_ts} ({self._time.exec_start_ts - self._time.system} seconds from now)...')
        self.cmd(AgentCmd(
            agent_id=self._agent_id,
            cmd=AgentCmd.START,
            args={'start_ts': self._time.exec_start_ts}  # - self._time.agent_start_ts}
        ))

    def stop_exec(self, reason: str = 'AGENT TIMEOUT CMD') -> None:
        if self._stop_sent:
            return
        self.info(f'Sending {AgentCmd.STOP} command (reason {reason})')
        self.cmd(AgentCmd(
            agent_id=self._agent_id,
            cmd=AgentCmd.STOP,
            args={'reason': reason}
        ))
        self._stop_sent = True
        if self._stage < self.Stage.stopping:
            self.stop(reason=reason)

    async def on_stop(self) -> None:
        self.stop_exec()
        self.debug('Waiting for module execution to stop...')
        await self.wait_for_module_stop()
        self.debug('Waiting for module processes to terminate...')
        self.wait_for_module_process_term()
        self.debug('Waiting for messenger to stop...')
        await self._messenger.stop()

    async def wait_for_module_stop(self, timeout: float | None = None) -> bool:
        wait_start_ts = time.time()
        while any([module.ready for module in self._modules.values()]) and (timeout and (time.time() - wait_start_ts) < timeout):
            await asyncio.sleep(self._control_frequency)

        return not any([module.ready for module in self._modules.values()])

    def wait_for_module_process_term(self) -> None:
        for module in self._modules.values():
            if module.process.poll() is None:
                try:
                    module.process.wait(5.)
                except subprocess.TimeoutExpired:
                    if module.process.poll() is None:
                        module.process.kill()

    async def on_error(self, error: Exception) -> None:
        await super().on_error(error)
        self.error(self._format_exception(error))

    @staticmethod
    def _extend_modules_list(modules: list[ModuleBase], items: Iterable[ModuleBase] | ModuleBase | None) -> None:
        if items is None:
            return
        if isinstance(items, ModuleBase):
            modules.append(items)
        else:
            modules.extend(items)

    @property
    def agent_id(self) -> str:
        return self._agent_id

    @property
    def save_dir(self) -> str:
        return self._global_params.save_dir
