
#include <stdio.h>
#include <stdbool.h>
#include <stdint.h>

#define MEMORY_WORDS (1 << 24)

uint32_t mem[MEMORY_WORDS + 4] = {0};

int main(int argc, char **argv) {
    if (argv[0] == NULL) {
        return 1;
    }
    if (argv[1] == NULL) {
        fprintf(stderr, "please give bb32 a file at the command line\n");
        return 1;
    }
    FILE *f = fopen(argv[1], "rb");
    if (f == NULL) {
        fprintf(stderr, "no such file: %s\n", argv[1]);
        return 1;
    }
    size_t write_head = 0;
    while (true) {
        if (fread(mem + write_head, 4, 256, f) != 4 * 256) {
            break;
        }
        write_head += 4 * 256;
    }
    uint32_t pc = 0;
    while (true) {
        uint32_t last_pc = pc;

        uint32_t a = mem[pc / 32];
        uint32_t b = mem[pc / 32 + 1];
        uint32_t c = mem[pc / 32 + 2];

        // printf("0x%zx 0x%zx 0x%zx\n", (size_t) a, (size_t) b, (size_t) c);

        if (a / 32 >= MEMORY_WORDS) {
            fprintf(stderr, "invalid write to 0x%zx\n", (size_t) a);
            return 1;
        }

        if (b / 32 >= MEMORY_WORDS) {
            fprintf(stderr, "invalid read from 0x%zx\n", (size_t) b);
            return 1;
        }

        if (c / 32 >= MEMORY_WORDS) {
            fprintf(stderr, "invalid jump to 0x%zx\n", (size_t) c);
            return 1;
        }

        pc = c;

        if (a == b) {
            if (pc == last_pc) {
                return 0;
            } else if (a != 0) {
                // printf("read %zu = %zu\n", (size_t) a, (size_t) mem[a / 32]);
                putchar(((uint8_t *)mem) [a / 8]);
            }
        } else {
            if ((mem[b / 32] & (1 << b % 32)) != 0) {
                mem[a / 32] |= (1 << a % 32);
            } else {
                mem[a / 32] &= ~(1 << a % 32);
            }
        }
    }
}
