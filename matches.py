#!/usr/bin/env python3
""" matches.py

    A helper tool to assist with cryptograms.

    Usage:

        ./matches.py cipher_word [ciper_word*]

    This searches for possible decodings of the given cipher words. It assumes
    that all words must be simultaneously deciphered. It attempts to provide the
    most likely plaintext translations first.

    Lowercase letters may be matched to anything except letters already matched
    to different lowercase letters (for example, abbcd will match "moose" but
    not "geese").

    Uppercase letters will strictly match exactly that letter.
"""


# ____________________________________________________________
# Imports

import sys
from glob import glob


# ____________________________________________________________
# Globals and constants

# I use globals for these because it's a small program and this way I don't have
# to recalculate their values.
crypt = None
num_crypt_letters = None
N = None


# ____________________________________________________________
# Functions

def is_match(cipher, word, num_cipher_letters, n):
    if len(word) != len(cipher):
        return False
    num_word_letters = len(set(list(word)))
    if num_word_letters != num_cipher_letters:
        return False
    for i in range(N):
        for j in range(i, N):
            if cipher[i] == cipher[j] and word[i] != word[j]:
                return False
    return True

def is_match_old(word):
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

def load_dictionary():

    global words

    words = defaultdict(list)  # This maps n to the words of length n.
    for fname in glob('data/*'):
        with open(fname) as f:
            for word in f:
                w = word.lower().strip()
                words[len(n)].append(w)


# ____________________________________________________________
# Main

if len(sys.argv) < 2:
    print(__doc__)
    sys.exit(0)

ciphers = sys.argv[2:]
load_dictionary()

# Build up a list of all possibilities. Each candidate is stored as
# (max_rank, word_list), where max_rank is the maximum rank among all
# the words in word_list. This allows us to sort by decreasing max_rank
# and display more likely plaintext candidates first.

plain_words = []  # plain_words[i] = [(plain_word, rank)*]
for cipher in ciphers:
    n = len(cipher)
    num_cipher_letters = len(set(list(cipher)))
    len_n_words = words[n]
    plain_words.append([
        w
        for w in len_n_words
        if is_match(cipher, w, num_cipher_letters, n)
    ])

# TODO HERE
# * Make is_match() check for capital letter matches.
# * Write a function that accepts a partial letter mapping
#   along with a cipher/plain pair, and returns either False
#   if they are incompatible, or a combined letter mapping.
# * Use the above to build a [(max_rank, word_list)*] list.
# * Sort that sucka.
# * Print out the top 20 results.





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
