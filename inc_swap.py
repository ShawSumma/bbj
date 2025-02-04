
from random import randrange

class Memory:
    bits: int
    memory: list[int]

    def __init__(self, bits: int) -> None:
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

    def run(self, iters: int = 1) -> None:
        mem = self.memory
        bits = self.bits
        pc = 0
        for _ in range(iters):
            a = mem[pc + 0]
            b = mem[pc + 1]
            c = mem[pc + 2]
            print(a, b, c)
            a_byte = a // bits
            a_bit = a % bits
            b_byte = b // bits
            b_bit = b % bits
            if mem[b_byte] & (1 << (b_bit)) != 0:
                mem[a_byte] |= 1 << a_bit
            else:
                mem[a_byte] &= ~(1 << a_bit)
            pc = c

def main() -> None:
    mem = Memory(8)
    with open('inc_swap.txt') as f:
        n = int(f.readline())
        addr = 0
        for line in f.read().split():
            mem.set(addr, int(line))
            addr += 1
    for i in range(n):
        mem.run()

if __name__ == '__main__':
    main()