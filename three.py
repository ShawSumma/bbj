
class Three:
    def __init__(self, cells):
        self.memory = [0] * cells
        self.pc = 0

    def one(self):
        mem = self.memory
        arg = mem[self.pc]
        addr = mem[arg]
        data = mem[addr]
        mem[addr] = (data + 1) % len(mem)
        self.pc = (self.pc + 1) % len(mem)
        return data
    
    def char_width(self):
        return len(hex(len(self.memory)))

    def chars(self):
        return [hex(i).rjust(self.char_width()) for i in self.memory]

    def debug(self):
        cw = self.char_width() + 1
        print('data = ', ' '.join(self.chars()))
        print('  pc = ', ' ' * cw * self.pc + '^' * cw)
        print('   * = ', ' ' * cw * self.memory[self.pc] + '^' * cw)
        print('  ** = ', ' ' * cw * self.memory[self.memory[self.pc]] + '^' * cw)
        print(' *** = ', ' ' * cw * self.memory[self.memory[self.memory[self.pc]]] + '^' * cw)

    def load(self, name):
        self.memory = [0] * len(self.memory)
        with open(name) as f:
            for index, data in f.read().split():
                self.memory[index] = int(data)

def zeros256():
    t = Three(256)
    print('Starting...')
    while True:
        input()
        print(t.one())

def zeros16():
    t = Three(16)
    print('Starting...')
    while True:
        t.debug()
        input()
        t.one()

def file256(name):
    t = Three(256)
    while True:
        src = input('> ')
        for x in src.split(';'):
            x = x.strip()
            if x == '':
                t.one()
                print(f'#{t.pc} => {t.memory[t.pc]} => {t.memory[t.memory[t.pc]]} => {t.memory[t.memory[t.memory[t.pc]]]}')
            elif x == 'l':
                t = Three(256)
                t.load(x[1:].strip())
            elif x == 'm':
                for x in range(16):
                    for y in range(16):
                        print(hex(t.memory[y + x * 16]).replace('0x', '').rjust(2), end=' ')
                    print()
            else:
                n = None
                try:
                    n = eval(x)
                finally:
                    if isinstance(n, int):
                        for i in range(n):
                            t.one()

def main():
    file256('three.txt')

if __name__ == '__main__':
    main()
