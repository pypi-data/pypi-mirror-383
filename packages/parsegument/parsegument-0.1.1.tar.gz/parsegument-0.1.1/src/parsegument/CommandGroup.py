
from .BaseGroup import BaseGroup
from .error import NodeDoesNotExist

class CommandGroup(BaseGroup):
    def __init__(self, name: str) -> None:
        super().__init__(name)
        self.children = {}

    def execute(self, nodes:list[str]):
        child = self.children.get(nodes[0])
        if not child:
            raise NodeDoesNotExist
        return child.execute(nodes[1:])
