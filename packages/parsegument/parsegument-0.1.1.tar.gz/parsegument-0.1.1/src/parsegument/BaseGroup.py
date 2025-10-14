from __future__ import annotations
from typing import Union, Callable, TYPE_CHECKING
from inspect import signature
from .utils.convert_params import convert_param
from .Node import Node
from .Command import Command

if TYPE_CHECKING:
    from .CommandGroup import CommandGroup


class BaseGroup:
    def __init__(self, name:str):
        self.name = name
        self.children = {}

    def add_child(self, child: Union[Command, CommandGroup]):
        if child.name in [i.name for i in self.children]:
            return False
        self.children[child.name] = child
        return True

    def command(self, func: Callable):
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)

        params = signature(func).parameters
        func_name = func.__name__
        command_object = Command(name=func_name, executable=func)
        for key, param in params.items():
            converted = convert_param(param)
            command_object.add_node(converted)
        self.add_child(command_object)
        return wrapper