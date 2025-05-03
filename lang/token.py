from typing import Any

class Token():
    kind: str

    def __init__(self, kind: str, properties: Any = {}):
        self.kind = kind
        for k in properties:
            setattr(self, k, properties[k])

    def __repr__(self):
        return "Token%r" % self.__dict__

    # def __str__(self):
    #     return self.kind

    def eq(self, **properties: Any) -> bool:
        for k in properties:
            if getattr(self, k, Undefined) != properties[k]:
                return False

        return True

Undefined = object()
