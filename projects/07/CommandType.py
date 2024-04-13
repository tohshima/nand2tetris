from enum import IntEnum, auto

# Command type enumeration of Hack VM Translator
class CommandType(IntEnum):
    C_ARITHMETIC = auto()
    C_PUSH       = auto()
    C_POP        = auto()
    C_LABEL      = auto()
    C_GOTO       = auto()
    C_IF         = auto()
    C_FUNCTION   = auto()
    C_RETURN     = auto()
    C_CALL       = auto()

