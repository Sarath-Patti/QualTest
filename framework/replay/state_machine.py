"""Modem Finite State Machine for protocol signaling validation and state reconstruction."""

from framework.logger import get_logger
from framework.replay.models import ModemFSMState, ProtocolMessage

logger = get_logger("Replay.StateMachine")


class ModemFSM:
    """Reusable Finite State Machine for modem protocol state reconstruction."""

    TRANSITION_RULES: dict[tuple[ModemFSMState, ProtocolMessage], ModemFSMState] = {
        # IDLE -> RRC_CONNECTING
        (
            ModemFSMState.IDLE,
            ProtocolMessage.RRC_CONNECTION_REQUEST,
        ): ModemFSMState.RRC_CONNECTING,
        # RRC_CONNECTING -> CONNECTED
        (
            ModemFSMState.RRC_CONNECTING,
            ProtocolMessage.RRC_CONNECTION_SETUP,
        ): ModemFSMState.RRC_CONNECTING,
        (
            ModemFSMState.RRC_CONNECTING,
            ProtocolMessage.RRC_CONNECTION_SETUP_COMPLETE,
        ): ModemFSMState.CONNECTED,
        # CONNECTED -> REGISTERED
        (
            ModemFSMState.CONNECTED,
            ProtocolMessage.NAS_ATTACH_REQUEST,
        ): ModemFSMState.REGISTERED,
        (
            ModemFSMState.CONNECTED,
            ProtocolMessage.NAS_AUTH_REQUEST,
        ): ModemFSMState.CONNECTED,
        (
            ModemFSMState.CONNECTED,
            ProtocolMessage.NAS_AUTH_ACCEPT,
        ): ModemFSMState.CONNECTED,
        (
            ModemFSMState.CONNECTED,
            ProtocolMessage.NAS_ATTACH_ACCEPT,
        ): ModemFSMState.REGISTERED,
        (
            ModemFSMState.CONNECTED,
            ProtocolMessage.SERVICE_REQUEST,
        ): ModemFSMState.IN_SERVICE,
        # REGISTERED transitions
        (
            ModemFSMState.REGISTERED,
            ProtocolMessage.NAS_AUTH_REQUEST,
        ): ModemFSMState.REGISTERED,
        (
            ModemFSMState.REGISTERED,
            ProtocolMessage.NAS_AUTH_ACCEPT,
        ): ModemFSMState.REGISTERED,
        (
            ModemFSMState.REGISTERED,
            ProtocolMessage.NAS_ATTACH_ACCEPT,
        ): ModemFSMState.REGISTERED,
        (
            ModemFSMState.REGISTERED,
            ProtocolMessage.SERVICE_REQUEST,
        ): ModemFSMState.IN_SERVICE,
        (
            ModemFSMState.REGISTERED,
            ProtocolMessage.SERVICE_ACCEPT,
        ): ModemFSMState.IN_SERVICE,
        (
            ModemFSMState.REGISTERED,
            ProtocolMessage.HANDOVER_REQUEST,
        ): ModemFSMState.HANDOVER,
        (
            ModemFSMState.REGISTERED,
            ProtocolMessage.DETACH_REQUEST,
        ): ModemFSMState.DETACHED,
        # IN_SERVICE transitions
        (
            ModemFSMState.IN_SERVICE,
            ProtocolMessage.SERVICE_REQUEST,
        ): ModemFSMState.IN_SERVICE,
        (
            ModemFSMState.IN_SERVICE,
            ProtocolMessage.SERVICE_ACCEPT,
        ): ModemFSMState.IN_SERVICE,
        (
            ModemFSMState.IN_SERVICE,
            ProtocolMessage.HANDOVER_REQUEST,
        ): ModemFSMState.HANDOVER,
        (
            ModemFSMState.IN_SERVICE,
            ProtocolMessage.HANDOVER_COMPLETE,
        ): ModemFSMState.IN_SERVICE,
        (
            ModemFSMState.IN_SERVICE,
            ProtocolMessage.DETACH_REQUEST,
        ): ModemFSMState.DETACHED,
        # HANDOVER transitions
        (
            ModemFSMState.HANDOVER,
            ProtocolMessage.HANDOVER_COMPLETE,
        ): ModemFSMState.IN_SERVICE,
        (
            ModemFSMState.HANDOVER,
            ProtocolMessage.DETACH_REQUEST,
        ): ModemFSMState.DETACHED,
        # DETACHED transitions
        (ModemFSMState.DETACHED, ProtocolMessage.DETACH_ACCEPT): ModemFSMState.DETACHED,
        (
            ModemFSMState.DETACHED,
            ProtocolMessage.RRC_CONNECTION_REQUEST,
        ): ModemFSMState.RRC_CONNECTING,
        # ERROR state recovery
        (
            ModemFSMState.ERROR,
            ProtocolMessage.RRC_CONNECTION_REQUEST,
        ): ModemFSMState.RRC_CONNECTING,
        (ModemFSMState.ERROR, ProtocolMessage.DETACH_ACCEPT): ModemFSMState.DETACHED,
    }

    def __init__(self, initial_state: ModemFSMState = ModemFSMState.IDLE) -> None:
        """Initializes the ModemFSM.

        Args:
            initial_state: Starting modem state. Defaults to IDLE.
        """
        self._state = initial_state
        logger.debug("ModemFSM initialized with state: %s", self._state.value)

    @property
    def current_state(self) -> ModemFSMState:
        """Returns the current state of the state machine."""
        return self._state

    def reset(self, state: ModemFSMState = ModemFSMState.IDLE) -> None:
        """Resets the state machine to a specific state."""
        self._state = state
        logger.debug("ModemFSM reset to state: %s", self._state.value)

    def transition(
        self, message: ProtocolMessage
    ) -> tuple[ModemFSMState, ModemFSMState, bool]:
        """Evaluates state transition for an incoming protocol message.

        Args:
            message: Incoming ProtocolMessage instance.

        Returns:
            tuple[ModemFSMState, ModemFSMState, bool]: (previous_state, new_state, is_valid)
        """
        prev_state = self._state
        key = (prev_state, message)

        # Global Detach override
        if message in (ProtocolMessage.DETACH_REQUEST, ProtocolMessage.DETACH_ACCEPT):
            self._state = ModemFSMState.DETACHED
            logger.info(
                "FSM State Transition: %s -> %s via '%s'",
                prev_state.value,
                self._state.value,
                message.value,
            )
            return prev_state, self._state, True

        if key in self.TRANSITION_RULES:
            next_state = self.TRANSITION_RULES[key]
            self._state = next_state
            logger.info(
                "FSM State Transition: %s -> %s via '%s'",
                prev_state.value,
                self._state.value,
                message.value,
            )
            return prev_state, self._state, True

        # Invalid transition
        self._state = ModemFSMState.ERROR
        logger.warning(
            "Invalid FSM State Transition: '%s' is invalid in state %s. State set to ERROR.",
            message.value,
            prev_state.value,
        )
        return prev_state, self._state, False
