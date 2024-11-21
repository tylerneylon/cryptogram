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

N_MATCHES_TO_SHOW = 300


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

    # This implementation is a little verbose, but I found it to be a bit faster
    # than a smaller version that relies on setdefault calls.

    for i in range(len(cipher)):
        cipher_letter = cipher[i]
        plain_letter  = plain_word[i]

        if cipher_letter in decoder:
            if decoder[cipher_letter] != plain_letter:
                return False
        else:
            decoder[cipher_letter] = plain_letter

        if plain_letter in encoder:
            if encoder[plain_letter] != cipher_letter:
                return False
        else:
            encoder[plain_letter] = cipher_letter

    return True

def load_dictionary():

    global words

    words = defaultdict(list)  # This maps n to the words of length n.
    for fname in glob('data/*'):
        with open(fname) as f:
            for word in f:
                w = word.lower().strip()
                words[len(w)].append(w)

def itoa(i):
    """ Return a length-3 string version of i, expected to be in [0, 1000). """
    return f'{i:3d}'


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

print('\nList lengths:')
k = max(map(len, ciphers))
fmt = f'%-{k}s'
for i, word_list in enumerate(plain_words):
    print(fmt % ciphers[i], len(word_list))
print()

# Iterate over all tuples from plain_words, and pick out the compatible ones.

def find_matches():
    decrypts = []  # Each item is (max_rank, word_list).
    idx = [0] * num_words
    max_depth = 0
    max_max_depth = max(map(len, plain_words))
    max_max_depth = 35  # XXX
    seen = set()
    num_found = 0
    print_count = 0
    while True:
        if tuple(idx) not in seen:

            if print_count % 10_000 == 0:
                status = f'[{max_depth:3d}] ' + ' '.join(map(itoa, idx)) + ' ' * 5
                print('\r' + status, end='', flush=True)
            print_count += 1

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
                num_found += 1
                print('\r' + f'{num_found:2d}.' + ' '.join(decrypt) + ' ' * 20)
                if num_found == N_MATCHES_TO_SHOW:
                    print()
                    print(f'(Stopping after finding {N_MATCHES_TO_SHOW} matches.)')
                    sys.exit(0)
        seen.add(tuple(idx))

        # This next block updates idx, counting up while keep each element <=
        # max_depth. Note that we will repeat some idx values, but skip those
        # quickly by looking at `seen`. However, I wonder if there's a better
        # way to do this that avoids the need for `seen` at all.
        incrementables = [
                j
                for j in range(num_words)
                # Don't use `min` here; this is faster without it.
                if idx[j] < len(plain_words[j]) - 1 and idx[j] < max_depth - 1
        ]
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

find_matches()
