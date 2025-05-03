from typing import NotRequired, TypedDict

from ..token import Token
from ..parser.Arguments import Arguments
from ..parser.types.Type import Type

class Function(TypedDict):
    name: str
    body: NotRequired[list[Token]]
    args: Arguments
    ret: Type
    fallback: NotRequired[bool]
    defined: bool
    bound: bool
