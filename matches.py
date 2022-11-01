#!/usr/bin/env python3
""" matches.py

    A helper tool to assist with cryptograms.

    Usage:

        ./matches.py <single_encrypted_word>

    This essentially performs a kind of grep on /usr/share/dict/words,
    looking for words that could fit the given encrypted string.

    Lowercase letters may be matched to anything except letters already matched
    to different lowercase letters (for example, abbcd will match "moose" but
    not "geese").

    Uppercase letters will strictly match exactly that letter.
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
    # Pre-process for any uppercase letters in crypt.
    words = [
            word.strip().lower()
            for word in f
            if len(word.strip()) == N and all(
                crypt[i].islower() or word[i].upper() == crypt[i]
                for i in range(N)
            )
    ]

# Since we've pre-filtered for the exact-match (uppercase) letters, we can now
# safely lowercase `crypt` and match against it.
crypt = crypt.lower()

for word in words:
    if is_match(word):
        print(word)
