#!/usr/bin/env python3
""" matches.py

    A helper tool to assist with cryptograms.

    Usage:

        ./matches.py <single_encrypted_word>

    This essentially performs a kind of grep on /usr/share/dict/words,
    looking for words that could fit the given encrypted string.
"""


# ____________________________________________________________
# Imports

import sys


# ____________________________________________________________
# Globals and constants

# I use globals for these because it's a small program and this way I don't have
# to recalculate their values.
crypt = None
num_crypt_letters = None
N = None


# ____________________________________________________________
# Functions

def is_match(word):
    global crypt, num_crypt_letters, N

    if len(word) != len(crypt):
        return False
    num_word_letters = len(set(list(word)))
    if num_word_letters != num_crypt_letters:
        return False
    for i in range(N):
        for j in range(i, N):
            if crypt[i] == crypt[j] and word[i] != word[j]:
                return False
    return True


# ____________________________________________________________
# Main

if len(sys.argv) != 2:
    if len(sys.argv) > 2:
        print('ERROR: I can only process one word. Sorry about that!')
    print(__doc__)
    sys.exit(0)

crypt = sys.argv[1]
num_crypt_letters = len(set(list(crypt)))
N = len(crypt)

with open('/usr/share/dict/words') as f:
    words = [word.strip().lower() for word in f]

for word in words:
    if is_match(word):
        print(word)
