
from lark import Lark, Tree, Token
from lark.visitors import Visitor, Interpreter, Transformer
from sys import argv
from typing import Callable, Tuple
from os.path import dirname, join, abspath

parser = Lark.open('asm.lark', rel_to=__file__, parser='lalr')

class Macro:
    name: str
    params: list[str]
    body: list[Tree | Token]

    def __init__(self, name, params, body):
        self.name = name
        self.params = params
        self.body = body

class Includes(Transformer):
    def __init__(self, file):
        self.path = [abspath(file)]

    def include(self, children):
        path = str(children[0])[1:-1]
        path = join(dirname(self.path[-1]), path)
        with open(path, 'r') as f:
            self.path.append(path)
            got = self.transform(parser.parse(f.read()))
            self.path.pop()
        for i in got.children:
            if isinstance(i, Tree):
                return i
        raise Exception('internal error in include')

    def instrs(self, children):
        instrs = []

        def add_all(ch):
            for c in ch:
                if isinstance(c, Tree) and c.data == 'instrs':
                    add_all(c.children)
                else:
                    instrs.append(c)

        add_all(children)

        return Tree('instrs', instrs)
        
class Macros(Visitor):
    macros: dict[tuple[str, int], Macro]

    def __init__(self):
        super().__init__()
        self.macros = {}

    def lookup(self, name, num_args):
        signature = (name, num_args)
        if signature in self.macros:
            return self.macros[signature]
        else:
            raise NameError(f'there is no instruction with {num_args} immediates called: {name}')

    def macro(self, tree):
        name, *params, instrs = tree.children
        name = str(name)
        signature = (name, len(params))
        self.macros[signature] = Macro(name, params, instrs)

class Argument:
    @property
    def value(self):
        return -1

    def __str__(self):
        return f'Argument({self.value})'

class Const(Argument):
    const: int

    def __init__(self, const):
        self.const = const

    @property
    def value(self):
        return self.const

class Label(Argument):
    name: str
    location: int

    def __init__(self, name):
        self.name = name
        self.location = -1
        self.unique = object()

    @property
    def value(self):
        if self.location < 0:
            raise NameError(f'label not defined: {self.name}')
        return self.location
    
class Invoke(Argument):
    name: str
    args: list[Argument]
    func: Callable[[*Tuple[Argument, ...]], Argument]
    cached: Argument | None

    def __init__(self, func, *args):
        self.func = func
        self.args = args
        self.cached = None

    @property
    def value(self):
        if self.cached is None:
            self.cached = self.func(*(i.value for i in self.args))
        return self.cached

class Assembler(Interpreter):
    macros: Macros
    
    stops: list[int]
    built: list[Argument]

    scopes: list[dict[str, Argument]]
    stack: list[Argument]

    def __init__(self, macros):
        self.macros = macros

    def lookup(self, name):
        for scope in reversed(self.scopes):
            if name in scope:
                return scope[name]
        raise NameError(f'not defined: {name}')

    def start(self, tree):
        self.stops = set()
        self.built = []
        self.scopes = [{
            'WORD': Const(32),
        }]
        self.stack = []
        for child in tree.children:
            if isinstance(child, Tree):
                self.visit(child)

    def loop(self, tree):
        name, args, body = tree.children
        name = str(name)
        args = args.children
        start = Const(0)
        stop = Const(0)
        step = Const(1)
        if len(args) == 0:
            raise Exception('.loop: needs a bounds')
        elif len(args) == 1:
            self.visit(args[0])
            stop = self.stack.pop()
        elif len(args) == 2:
            self.visit(args[0])
            start = self.stack.pop()

            self.visit(args[1])
            stop = self.stack.pop()
        elif len(args) == 3:
            self.visit(args[0])
            start = self.stack.pop()

            self.visit(args[1])
            stop = self.stack.pop()

            self.visit(args[2])
            step = self.stack.pop()
        else:
            raise Exception('.loop: bounds takes upto 3 arguments')
        for i in range(start.value, stop.value, step.value):
            scope = {
                str(name): Const(i),
            }
            self.scopes.append(scope)
            self.visit(body)
            self.scopes.pop()

    def instrs(self, tree):
        local_scope = {}
        for label in tree.children:
            if isinstance(label, Tree) and label.data == 'label':
                label_name = str(label.children[0])
                local_scope[label_name] = Label(label_name)
        self.scopes.append(local_scope)
        for child in tree.children:
            self.visit(child)
        self.scopes.pop()

    def instr(self, tree):
        name, args = tree.children
        args = list(args.children)
        macro = self.macros.lookup(name, len(args))
        arg_scope = {}
        for param, arg in zip(macro.params, args):
            self.visit(arg)
            arg_scope[param] = self.stack.pop()
        self.scopes.append(arg_scope)
        self.visit(macro.body)
        self.scopes.pop()

    def label(self, tree):
        label_name = str(tree.children[0])
        self.scopes[-1][label_name].location = len(self.built) * 32
        # print(label_name, hex(len(self.built) * 32))

    def raw(self, tree):
        self.stops.add(len(self.built))
        for child in tree.children[0].children:
            if isinstance(child, Token) and child.type == "STR":
                for char in str(child)[1:-1]:
                    self.built.append(Const(ord(char)))
            else:
                self.visit(child)
                value = self.stack.pop()
                self.built.append(value)

    def arg(self, tree):
        self.visit(tree.children[0])

    def handle_math(self, children):
        self.visit(children[0])
        cur = 1
        while cur < len(children):
            op = str(children[cur])
            cur += 1
            self.visit(children[cur])
            cur += 1
            rhs = self.stack.pop()
            lhs = self.stack.pop()
            match op:
                case "<<":
                    self.stack.append(Invoke(lambda x, y: x << y, lhs, rhs))
                case ">>":
                    self.stack.append(Invoke(lambda x, y: x >> y, lhs, rhs))
                case "&":
                    self.stack.append(Invoke(lambda x, y: x & y, lhs, rhs))
                case "|":
                    self.stack.append(Invoke(lambda x, y: x | y, lhs, rhs))
                case "^":
                    self.stack.append(Invoke(lambda x, y: x ^ y, lhs, rhs))
                case "*":
                    self.stack.append(Invoke(lambda x, y: x * y, lhs, rhs))
                case "/":
                    self.stack.append(Invoke(lambda x, y: x // y, lhs, rhs))
                case "%":
                    self.stack.append(Invoke(lambda x, y: x % y, lhs, rhs))
                case "+":
                    self.stack.append(Invoke(lambda x, y: x + y, lhs, rhs))
                case "-":
                    self.stack.append(Invoke(lambda x, y: x - y, lhs, rhs))
                case _:
                    raise Exception("internal error")

    def math_add(self, tree):
        self.handle_math(tree.children)

    def math_mul(self, tree):
        self.handle_math(tree.children)

    def single(self, tree):
        inner = tree.children[0]
        if isinstance(inner, Token):
            match inner.type:
                case 'NAME':
                    found = self.lookup(str(inner))
                case 'INT':
                    found = Const(int(inner, 10))
                case 'HEX':
                    found = Const(int(inner, 16))
                case 'BIN':
                    found = Const(int(inner, 2))
        else:
            self.visit(tree.children[0])
        self.stack.append(found)

    def local(self, tree):
        name, value = tree.children
        self.visit(value)
        self.scopes[-1][str(name)] = self.stack.pop()

    def macro(self, tree):
        pass

    def align(self, tree):
        self.visit(tree.children[0])
        n = self.stack.pop().value
        while len(self.built) % n != 0:
            self.built.append(Const(0))
        
    def __default__(self, tree):
        raise Exception(f'unknown tree type: {tree.data}')

def main():
    path = abspath(argv[1])
    with open(path) as f:
        ast = parser.parse(f.read())
    includes = Includes(path)
    ast = includes.transform(ast)

    macros = Macros()
    macros.visit(ast)

    assembler = Assembler(macros)
    assembler.visit(ast)

    with open('out/out.bbs', 'w') as f:
        for index, value in enumerate(assembler.built):
            if index in assembler.stops:
                f.write('.raw ')
            f.write(str(value.value))
            if (index + 1) in assembler.stops:
                f.write('\n')
            else:
                f.write(' ')
        f.write('\n')
    
    with open('out/out.bb32', 'wb') as f:
        f.write((0).to_bytes(4, byteorder='little'))
        for value in assembler.built:
            f.write(value.value.to_bytes(4, byteorder='little'))

if __name__ == '__main__':
    main()
