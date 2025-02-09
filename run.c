
#include <stdio.h>
#include <stdbool.h>
#include <stdint.h>
#include <time.h>

#define PROFILE 3
#define USE_SAFE 0
#define MEMORY_WORDS (1 << 22)

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
        if (fread(((uint8_t *)mem) + write_head, 1, 1, f) != 1) {
            break;
        }
        write_head += 1;
    }
#if PROFILE & 2
    clock_t t1 = clock();
#endif
    uint32_t pc = 0;
#if PROFILE & 1
    size_t num = 0;
#endif
    while (true) {
#if PROFILE & 1
        num += 1;
#endif
        uint32_t last_pc = pc;

        uint32_t a = mem[pc / 32 + 0];
        uint32_t b = mem[pc / 32 + 1];
        uint32_t c = mem[pc / 32 + 2];

        // printf("0x%zx 0x%zx 0x%zx\n", (size_t) a, (size_t) b, (size_t) c);

#if USE_SAFE
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
#endif

        pc = c;

        if (a == b) {
            if (pc == last_pc) {
                break;
            }
            if (a != 0) {
                uint8_t *pvalue = &((uint8_t *) mem)[a / 8];
                // printf("[addr = %zx; value = %zu]", (size_t) a, (size_t) *pvalue);
                if (*pvalue != 0) {
                    putchar(*pvalue);
                } else {
                    *pvalue = getchar();
                }
            }
        } else {
            if ((mem[b / 32] & (1 << b % 32)) != 0) {
                mem[a / 32] |= (1 << a % 32);
            } else {
                mem[a / 32] &= ~(1 << a % 32);
            }
        }
    }
#if PROFILE & 1
    printf("instrs: %zu\n", num);
#endif
#if PROFILE & 2
    clock_t t2 = clock();
    printf("seconds: %f\n", (double) (t2 - t1) / (double) CLOCKS_PER_SEC);
#endif
}
