#!/usr/bin/env python3
""" cryptogram.py

    A small tool to help you solve your cryptogram for Python 3.

    Usage:

        ./cryptogram.py <cryptogram_text>

    From there you'll get a prompt until you've solved the puzzle at hand
    (which is up to you to determine).

    At the prompt:

    > XY  --> (any two letters); Swap letters X and Y in the working solution.
    > r   --> Retype the original cryptogram text.
    > q   --> Quit.
"""


# ____________________________________________________________
# Imports

import sys


# ____________________________________________________________
# Functions

def swap(s, x, y):
    """ Return string s with letters x and y swapped. """
    s = s.replace(y, '_')
    s = s.replace(x, y)
    return s.replace('_', x)


# ____________________________________________________________
# Main

if len(sys.argv) < 2:
    print(__doc__)
    sys.exit(0)

crypt = ' '.join(sys.argv[1:])
swaps = []
soln  = crypt

while True:

    try:
        inp = input('> ')
    except (EOFError, KeyboardInterrupt):
        print('Have a great rest of your day! :)')
        sys.exit(0)

    if inp == 'r':
        print(f'Original cryptogram:\n{crypt}')
        crypt = input('Replacement cryptogram: ')
        soln = crypt
        for pair in swaps:
            soln = swap(soln, pair[0], pair[1])

    elif inp == 'q':
        print('Have a great day! :D')
        sys.exit(0)
        
    elif len(inp) == 2:
        swaps.append(inp)
        soln = swap(soln, inp[0], inp[1])

    print(soln)
