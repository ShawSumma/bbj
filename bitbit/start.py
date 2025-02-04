
from sys import argv

class Memory:
    bits: int
    pc: int
    memory: list[int]

    def __init__(self, bits: int) -> None:
        self.pc = 0
        self.bits = bits
        self.memory = [0] * (2 ** self.bits)

    def print(self, low: int, high: int) -> None:
        for i in range(low, high):
            print(f'{str(i).rjust(len(str(high)))}: {self.memory[i]}')

    def debug(self):
        print('    ' + ' '.join(str(i).rjust(3) for i in self.memory))
        print('    ' + ' ' * ((self.memory[0]) * 4 + 3 - len(str(self.memory[self.memory[0]]))) +  '^' * len(str(self.memory[self.memory[0]])))
        print()

    def set(self, index: int, value: int) -> None:
        self.memory[index] = value

    def fill(self, start: int, values: list[int]) -> None:
        self.memory[start:start+len(values)] = values

    def put(self, *data: list[int]) -> None:
        for byte in data:
            self.memory[self.pc] = byte
            self.pc += 1

    def run(self, max_steps: int = 0) -> None:
        if max_steps == 0:
            max_steps = 256
        mem = self.memory
        bits = self.bits
        for _ in range(max_steps):
            a = mem[self.pc + 0]
            b = mem[self.pc + 1]
            c = mem[self.pc + 2]
            a_byte = a // bits
            a_bit = a % bits
            b_byte = b // bits
            b_bit = b % bits
            if a == b:
                if c == self.pc:
                    return False
                elif a == 0:
                    pass
                else:
                    print(chr(mem[a_byte]), end='')
            else:
                if (mem[b_byte] & (1 << (b_bit))) != 0:
                    mem[a_byte] |= 1 << a_bit
                else:
                    mem[a_byte] &= ~(1 << a_bit)
            self.pc = c
        return True

class Assembler:
    lines: list[list[str]]
    mem: Memory
    cache: dict[str, int]

    def __init__(self, src: str) -> None:
        self.lines = []
        for line in src.split('\n'):
            line = line.strip()
            if len(line) == 0:
                continue
            else:
                self.lines.append(line.split())
        self.cache = {}

    def build_line(self, line) -> None:
        mem = self.mem
        match line[0]:
            case 'addr':
                mem.pc = int(line[1]) // mem.bits
            case 'label':
                self.cache[line[1]] = mem.pc
            case 'jmp':
                mem.put(0, 0, self.cache[line[1]] if line[1] in self.cache else 0)
            case 'mov1' | 'mov2' | 'mov4' | 'mov8' | 'mov16' | 'mov32' | 'mov64':
                dest = int(line[1])
                src = int(line[2])
                for _ in range(0, int(line[0][3:])):
                    mem.put(dest, src, mem.pc + 3)
                    dest += 1
                    src += 1
            case 'byte':
                for i in line[1:]:
                    mem.put(int(i))
            case 'out':
                src = int(line[1])
                mem.put(src, src, mem.pc + 3)

    def build_stage(self) -> None:
        self.mem = Memory(16)
        for line in self.lines:
            self.build_line(line)

    def assemble(self) -> None:
        self.build_stage()
        self.build_stage()
        return self.mem

def main() -> None:
    with open(argv[1]) as f:
        asm = f.read()
    mach = Assembler(asm).assemble()
    while mach.run():
        pass

if __name__ == '__main__':
    main()