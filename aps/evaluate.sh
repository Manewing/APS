#!/bin/bash

mkdir -p results

# isotropic
python aps.py -n 90 -l 10 --iso -c 100 -s 600 > results/iso_10.txt & # 10%
python aps.py -n 80 -l 20 --iso -c 100 -s 600 > results/iso_20.txt & # 20%
python aps.py -n 70 -l 30 --iso -c 100 -s 600 > results/iso_30.txt & # 30%
python aps.py -n 60 -l 40 --iso -c 100 -s 600 > results/iso_40.txt & # 40%
python aps.py -n 50 -l 50 --iso -c 100 -s 600 > results/iso_50.txt & # 50%

# anisotropic
python aps.py -n 90 -l 10 -c 100 -s 600  > results/aniso_10.txt & # 10%
python aps.py -n 80 -l 20 -c 100 -s 600 > results/aniso_20.txt & # 20%
python aps.py -n 70 -l 30 -c 100 -s 600 > results/aniso_30.txt & # 30%
python aps.py -n 60 -l 40 -c 100 -s 600 > results/aniso_40.txt & # 40%
python aps.py -n 50 -l 50 -c 100 -s 600 > results/aniso_50.txt & # 50%
