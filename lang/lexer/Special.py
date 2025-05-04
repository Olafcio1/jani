from enum import Enum, StrEnum
from typing import Final, Iterable

class Keywords(StrEnum):
    require = "require"
    """Requires the further statement to finish succesfully, and if it returns a non-void value, requires it to be truthfull."""

    mustfail = "mustfail"
    """Requires the further statement to fail."""

    background = "background"
    """Runs the further statement in a separate thread. If placed after the `mode` keyword, has a separate meaning; refer to `mode` documentation."""

    foreground = "foreground"
    """Refer to the `mode` keyword."""

    mode = "mode"
    """Changes the current calling mode to background/foreground, depending on which one is then specified."""

    repeatTimes = "rept"
    """Repeats the further block of code the given amount of times."""

    panic = "panic"
    """Exits the virus, deletes it and all traces of it from the victim's computer."""

    declare = "decl"
    """Declares a native function. Such functions require an implementation in the builder, so there are a lot of them in the standard library."""

    function = "fun"
    """Defines a function."""

    optional = "optional"
    """Indicates that the further parameter is optional."""

    bind = "bind"
    """Defines an implementation for the given native function."""

    const = "const"
    """Defines a constant. Constants must have a simple value, e.g. string or number, because they are inlined in the buld process."""

    var = "var"
    """Defines a variable."""

    text = "text"
    """Refers to the type."""

    integer = "integer"
    """Refers to the type."""

    float = "float"
    """Refers to the type."""

    null = "nul"
    """Refers to the type."""

    boolean = "boolean"
    """Refers to the type."""

    rgb = "rgb"
    """Refers to the type."""

    true = "true"
    """Refers to the boolean value TRUE."""

    false = "false"
    """Refers to the boolean value FALSE."""

    any = "any"
    """Refers to the type."""

    function_type = "function"
    """Refers to the type."""

    goto = "goto"
    """Teleports to the specified go-point."""

    return_ = "return"
    """Returns the further value from the function."""

    fallback = "fallback"
    """Modifier keyword for a function. Stops raising an error when the name already exists."""

    noRemap = "no_remap"
    """Modifier keyword for a function. Stops remapping the function, thus leaving its original name."""

    include = "include"
    """Imports the given JANI file into the global scope."""

    staticInclude = "static-include"
    """Imports the given JANI file into the global scope in the parser."""

    not_ = "not"
    """Converts the further to an inverted boolean."""

    and_ = "and"
    """Makes sure the current and next expression is truth-alike."""

    or_ = "or"
    """Makes sure either the current or next expression is truth-alike."""

    if_ = "if"
    """Executes a piece of code if the further expression is truth-alike."""

    while_ = "while"
    """Executes a piece of code while the further expression is truth-alike."""

class Operators(StrEnum):
    parenOpen = "("
    parenClose = ")"
    squareOpen = "["
    squareClose = "]"
    semicolon = ":"
    colon = ";"
    curlyOpen = "{"
    curlyClose = "}"
    angleOpen = "<"
    angleClose = ">"
    plus = "+"
    minus = "-"
    star = "*"
    slash = "/"
    dash = "^"
    xor = "|"
    xand = "&"
    at = "@"
    equals = '='

class Keychars(Enum):
    string = ('"',)
    no_escape_string = ("`",)
    escape = ("&",)
    interp = ("%",)

KEYWORDS: Final[dict[str, Keywords]] = Keywords._value2member_map_
OPERATORS: Final[dict[str, Operators]] = Operators._value2member_map_
KEYCHARS: Final[dict[str, Keychars]] = Keychars._value2member_map_
COMMENTS: Final[dict[str, str]] = {
    "#": "\n",
    "//": "\n",
    "/*": "*/",
    "---": "---"
}

def flat(iterable: Iterable, depth: int = 1) -> Iterable:
    for _ in range(depth):
        new = []
        for s in iterable:
            if hasattr(s, "__iter__"):
                new.extend(s)
            else:
                new.append(s)
        iterable = new

    return iterable

NONLITERAL: Final = [
    *OPERATORS,
    *flat(KEYCHARS),
    *COMMENTS,
    " ", "\n"
]
