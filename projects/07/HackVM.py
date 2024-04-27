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

# Map to Defined Label to Address
MapDefLabelToAddr = {"SP":0, "LCL":1, "ARG":2, "THIS":3, "THAT":4}