
$ErrorActionPreference = "Stop"

cc -O2 run.c -o out/run.exe
python3 asm.py $args[0]
./out/run.exe out/out.bb32
