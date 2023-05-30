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
from collections import defaultdict
from glob import glob


# ____________________________________________________________
# Globals and constants

# I use globals for these because it's a small program and this way I don't have
# to recalculate their values.
crypt = None  # XXX Needed?
num_crypt_letters = None
N = None  # XXX Needed?

N_MATCHES_TO_SHOW = 20


# ____________________________________________________________
# Functions

def is_match(cipher, word, num_cipher_letters, n):
    if len(word) != len(cipher):
        return False
    num_word_letters = len(set(list(word)))
    if num_word_letters != num_cipher_letters:
        return False
    for i in range(n):
        if cipher[i].isupper() and cipher[i].lower() != word[i]:
            return False
        for j in range(i, n):
            if cipher[i] == cipher[j] and word[i] != word[j]:
                return False
    return True

# This expects two dicts, and a cipher/plain_word pair.
# The `decoder` maps cipher letters to plain letters.
# The `encoder` maps plain letters to cipher letters.
# If the cipher->plain_word map is compatible with the encoder/decoder,
# they are modified and this returns True.
# Otherwise, this returns False.
def did_update_map(decoder, encoder, cipher, plain_word):
    # print(f'did_update_map({letter_map}, {cipher}, {plain_word})')
    assert len(cipher) == len(plain_word)
    for cipher_let, plain_let in zip(cipher, plain_word):
        if decoder.setdefault(cipher_let, plain_let) != plain_let:
            # print(f'Found conflict; cipher->plain {cipher_let}->{plain_let}')
            return False
        if encoder.setdefault(plain_let, cipher_let) != cipher_let:
            return False
    # print(f'No conflict, returning updated map {letter_map}')
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
                words[len(w)].append(w)


# ____________________________________________________________
# Main

if len(sys.argv) < 2:
    print(__doc__)
    sys.exit(0)

ciphers = sys.argv[1:]
load_dictionary()

# Build up a list of all possibilities. Each candidate is stored as
# (max_rank, word_list), where max_rank is the maximum rank among all
# the words in word_list. This allows us to sort by decreasing max_rank
# and display more likely plaintext candidates first.

num_words   = len(ciphers)
plain_words = []  # plain_words[i] = [(len_i_plain_word, rank)*]
for cipher in ciphers:
    n = len(cipher)
    num_cipher_letters = len(set(list(cipher)))
    len_n_words = words[n]
    plain_words.append([
        w
        for w in len_n_words
        if is_match(cipher, w, num_cipher_letters, n)
    ])

# XXX
print(f'len(plain_words) = {len(plain_words)}')
for i, word_list in enumerate(plain_words):
    print(f'For {ciphers[i]}:')
    for w in word_list[:3]:
        print(f'    {w}')
print('\nList lengths:')
for i, word_list in enumerate(plain_words):
    print(f'{ciphers[i]}: {len(word_list)}')

# Iterate over all tuples from plain_words, and pick out the compatible ones.

decrypts = []  # Each item is (max_rank, word_list).
idx = [0] * num_words
max_depth = 0
max_max_depth = max(map(len, plain_words))
seen = set()
while True:
    if tuple(idx) not in seen:
        status = f'[{max_depth:3d}] ' + ' '.join(map(str, idx)) + ' ' * 5
        print('\r' + status, end='', flush=True)
        encoder, decoder = {}, {}
        letter_map = {}
        max_rank   = 0
        decrypt    = []
        for i in range(num_words):
            plain_word = plain_words[i][idx[i]]
            if did_update_map(decoder, encoder, ciphers[i], plain_word):
                max_rank = max(max_rank, idx[i])
                decrypt.append(plain_word)
            else:
                break
        else:  # Didn't break out.
            decrypts.append((max_rank, decrypt))
            print('\r' + '*****' + ' '.join(decrypt) + ' ' *20)  # XXX
    seen.add(tuple(idx))
    incrementables = [j for j in range(num_words)
                      if idx[j] < min(len(plain_words[j]), max_depth) - 1]
    if len(incrementables) == 0:
        if max_depth == max_max_depth:
            break
        max_depth += 1
        idx = [0] * num_words
    else:
        j = incrementables[-1]
        idx[j] += 1
        for k in range(j + 1, num_words):
            idx[k] = 0
print()  # XXX

# Sort the potential decrypts, putting more likely matches first.
decrypts.sort()

# Print out the top results.
for i, decrypt in enumerate(decrypts[:N_MATCHES_TO_SHOW]):
    print(f'{i + 1:2d}.', ' '.join(decrypt[1]))


# TODO HERE
# * [x] Make is_match() check for capital letter matches.
# * [x] Write a function that accepts a partial letter mapping
#       along with a cipher/plain pair, and returns either False
#       if they are incompatible, or a combined letter mapping.
# * [x] Use the above to build a [(max_rank, word_list)*] list.
# * [x] Sort that sucka.
# * [x] Print out the top N_MATCHES_TO_SHOW results.
# * [x] Comment out old code below (if False it).
# * [ ] Debug.
# * [ ] Review script and drop unused globals and functions.


if False:

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
