#!/bin/bash

python -m morpheus -S "O=[#6:1][OH].[#6:2][#8H1:3]>>O=[#6:1][#8:3][#6:2].O" -s "O=CO" "CO" -f csv -o ester.out