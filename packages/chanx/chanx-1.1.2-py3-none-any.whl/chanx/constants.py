"""
Chanx framework constants.

This module defines constants used throughout the Chanx framework, providing a
centralized location for string literals, error messages, and other constant values.
Using these named constants rather than string literals helps maintain consistency
and makes updates easier across the codebase.
"""

from typing import Literal, TypeAlias

MISSING_PYHUMPS_ERROR = (
    "Camelization is enabled but the 'pyhumps' package is not installed."
    " Please install it by running 'pip install pyhumps' or install the camel-case"
    " extra with 'pip install chanx[camel-case]'."
)

MESSAGE_ACTION_COMPLETE: Literal["complete"] = "complete"

EVENT_ACTION_COMPLETE: Literal["event_complete"] = "event_complete"

GROUP_ACTION_COMPLETE: Literal["group_complete"] = "group_complete"

COMPLETE_ACTIONS_TYPE: TypeAlias = Literal[
    "complete", "event_complete", "group_complete"
]
COMPLETE_ACTIONS = {
    MESSAGE_ACTION_COMPLETE,
    EVENT_ACTION_COMPLETE,
    GROUP_ACTION_COMPLETE,
}

CHANX_ACTIONS = COMPLETE_ACTIONS | {"error"}
