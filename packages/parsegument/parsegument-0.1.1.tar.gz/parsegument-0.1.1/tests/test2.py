import parsegument
from parsegument import CommandGroup

parser = parsegument.Parsegumenter(name="test")

@parser.command
def foo(bar:str):
    return bar

print(parser.execute("test foo 'testing'"))