
from lark import Lark

parser = Lark.open('bitbit/asm.lark')

parser.parse()
