from typing import Any, Iterable, ClassVar

from mhagenta.utils import ModuleTypes, Outbox, ConnType, Message, Goal, Observation, ActionStatus, Belief, State
from mhagenta.core.processes.mha_module import MHAModule, GlobalParams, ModuleBase


class LLOutbox(Outbox):
    """Internal communication outbox class for Low-level reasoner.

    Used to store and process outgoing messages to other modules.

    """
    def request_action(self, actuator_id: str, **kwargs) -> None:
        """Request an action from an actuator.

        Args:
            actuator_id (str): `module_id` of the actuator chosen to perform the action.
            **kwargs: additional keyword arguments to be included in the message.

        """
        self._add(actuator_id, ConnType.request, kwargs)

    def request_observation(self, perceptor_id: str, **kwargs) -> None:
        """Request an observation from a perceptor.

        Args:
            perceptor_id (str): `module_id` of the selected perceptor.
            **kwargs: additional keyword arguments to be included in the message.

        """
        self._add(perceptor_id, ConnType.request, kwargs)

    def send_beliefs(self, knowledge_id: str, observation: Observation, beliefs: Iterable[Belief], **kwargs) -> None:
        """Send belief update to a knowledge model module.

        Args:
            knowledge_id (str): `module_id` of the relevant knowledge model module.
            observation (Observation): Observation from which the beliefs were extracted.
            beliefs (Iterable[Belief]): a collection of beliefs to be sent.
            **kwargs: additional keyword arguments to be included in the message.

        """
        body = {'observation': observation, 'beliefs': beliefs}
        if kwargs:
            body.update(kwargs)
        self._add(knowledge_id, ConnType.send, body)

    def request_goals(self, goal_graph_id: str, **kwargs) -> None:
        """Request new or updated goals from a goal graph.

        Args:
            goal_graph_id (str): `module_id` of the relevant goal graph.
            **kwargs: additional keyword arguments to be included in the message.

        """
        self._add(goal_graph_id, ConnType.request, kwargs)

    def send_goal_update(self, goal_graph_id: str, goals: Iterable[Goal], **kwargs) -> None:
        """Update a goal graph on the goal statuses.

        Args:
            goal_graph_id (str): `module_id` of the relevant goal graph.
            goals (Iterable[Goal]): collection of goals to report.
            **kwargs: additional keyword arguments to be included in the message.

        """
        body = {'goals': goals}
        if kwargs:
            body.update(kwargs)
        self._add(goal_graph_id, ConnType.send, body)

    def request_model(self, learner_id: str, **kwargs) -> None:
        """Request the current model from a learner.

        Args:
            learner_id (str): `module_id` of a learner training the required model.
            **kwargs: additional keyword arguments to be included in the message.

        """
        self._add(learner_id, ConnType.request, kwargs)

    def send_learner_task(self, learner_id: str, task: Any, **kwargs) -> None:
        """Send a new or updated learning task to a learner.

        Args:
            learner_id (str): `module_id` of the relevant learner.
            task (Any): an object specifying the learning task.
            **kwargs: additional keyword arguments to be included in the message.

        """
        body = {'task': task}
        if kwargs:
            body.update(kwargs)
        self._add(learner_id, ConnType.send, body)


LLState = State[LLOutbox]


class LLReasonerBase(ModuleBase):
    """Base class for defining Low-level reasoner behavior (also inherits common methods from `ModuleBase`).

    To implement a custom behavior, override the empty base functions: `on_init`, `step`, `on_first`, `on_last`, and/or
    reactions to messages from other modules.

    """
    module_type: ClassVar[str] = ModuleTypes.LLREASONER

    def on_observation(self, state: LLState, sender: str, observation: Observation, **kwargs) -> LLState:
        """Override to define low-level reasoner's reaction to receiving an observation object.

        Args:
            state (LLState): Low-level reasoner's internal state enriched with relevant runtime information and
                functionality.
            sender (str): `module_id` of the Perceptor that sent the observation.
            observation (Observation): received observation object.
            **kwargs: additional keyword arguments included in the message.

        Returns:
            LLState: modified or unaltered internal state of the module.

        """
        return state

    def on_action_status(self, state: LLState, sender: str, action_status: ActionStatus, **kwargs) -> LLState:
        """Override to define low-level reasoner's reaction to receiving an action status object.

        Args:
            state (LLState): Low-level reasoner's internal state enriched with relevant runtime information and
                functionality.
            sender (str): `module_id` of the Actuator that sent the status report.
            action_status (ActionStatus): received action status object.
            **kwargs: additional keyword arguments included in the message.

        Returns:
            LLState: modified or unaltered internal state of the module.

        """
        return state

    def on_goal_update(self, state: LLState, sender: str, goals: list[Goal], **kwargs) -> LLState:
        """Override to define low-level reasoner's reaction to receiving a goals update.

        Args:
            state (LLState): Low-level reasoner's internal state enriched with relevant runtime information and
                functionality.
            sender (str): `module_id` of the Goal graph that sent the goal update.
            goals (list[Goal]): received list of updated goals.
            **kwargs: additional keyword arguments included in the message.

        Returns:
            LLState: modified or unaltered internal state of the module.

        """
        return state

    def on_model(self, state: LLState, sender: str, model: Any, **kwargs) -> LLState:
        """Override to define low-level reasoner's reaction to receiving a learned model.

        Args:
            state (LLState): Low-level reasoner's internal state enriched with relevant runtime information and
                functionality.
            sender (str): `module_id` of the learner that sent the model.
            model (Any): received learned model object.
            **kwargs: additional keyword arguments included in the message.

        Returns:
            LLState: modified or unaltered internal state of the module.

        """
        return state


class LLReasoner(MHAModule):
    def __init__(self,
                 global_params: GlobalParams,
                 base: LLReasonerBase
                 ) -> None:
        self._module_id = base.module_id
        self._base = base
        self._directory = global_params.directory

        out_id_channels = list()
        in_id_channels_callbacks = list()

        for perceptor in self._directory.internal.perception:
            out_id_channels.append(self.sender_reg_entry(perceptor.module_id, ConnType.request))
            in_id_channels_callbacks.append(self.recipient_reg_entry(perceptor.module_id, ConnType.send, self._receive_observation))

        for actuator in self._directory.internal.actuation:
            out_id_channels.append(self.sender_reg_entry(actuator.module_id, ConnType.request))
            in_id_channels_callbacks.append(self.recipient_reg_entry(actuator.module_id, ConnType.send, self._receive_action_status))

        for knowledge in self._directory.internal.knowledge:
            out_id_channels.append(self.sender_reg_entry(knowledge.module_id, ConnType.send))
        for goal_graph in self._directory.internal.goals:
            out_id_channels.append(self.sender_reg_entry(goal_graph.module_id, ConnType.request))
            out_id_channels.append(self.sender_reg_entry(goal_graph.module_id, ConnType.send))
            in_id_channels_callbacks.append(self.recipient_reg_entry(goal_graph.module_id, ConnType.send, self._receive_goals))

        for learner in self._directory.internal.learning:
            out_id_channels.append(self.sender_reg_entry(learner.module_id, ConnType.request))
            out_id_channels.append(self.sender_reg_entry(learner.module_id, ConnType.send))
            in_id_channels_callbacks.append(self.recipient_reg_entry(learner.module_id, ConnType.send, self._receive_learner_model))

        super().__init__(
            global_params=global_params,
            base=base,
            out_id_channels=out_id_channels,
            in_id_channel_callbacks=in_id_channels_callbacks,
            outbox_cls=LLOutbox
        )

    def _receive_observation(self, sender: str, channel: str, msg: Message) -> LLState:
        self.debug(f'Received observation {msg.id} from {sender}. Processing...')
        observation = msg.body.pop('observation')
        update = self._base.on_observation(state=self._state, sender=sender, observation=observation, **msg.body)
        self.log(5, f'Finished processing observation {msg.id}!')
        return update

    def _receive_action_status(self, sender: str, channel: str, msg: Message) -> LLState:
        self.debug(f'Received action status {msg.id} from {sender}. Processing...')
        action_status = msg.body.pop('action_status')
        update = self._base.on_action_status(state=self._state, sender=sender, action_status=action_status, **msg.body)
        self.log(5, f'Finished processing action status {msg.id}!')
        return update

    def _receive_goals(self, sender: str, channel: str, msg: Message) -> LLState:
        self.debug(f'Received goal update {msg.id} from {sender}. Processing...')
        goals = msg.body.pop('goals')
        update = self._base.on_goal_update(state=self._state, sender=sender, goals=goals, **msg.body)
        self.log(5, f'Finished processing goal update {msg.id}!')
        return update

    def _receive_learner_model(self, sender: str, channel: str, msg: Message) -> LLState:
        self.debug(f'Received learned model {msg.id} from {sender}. Processing...')
        model = msg.body.pop('model')
        update = self._base.on_model(state=self._state, sender=sender, model=model, **msg.body)
        self.log(5, f'Finished processing learned model {msg.id}!')
        return update
