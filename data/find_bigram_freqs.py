#!/usr/bin/env python3
# coding: utf-8
""" find_bigram_freqs.py

    Usage:
        ./find_bigram_freqs.py <plain_text_file.txt>

    This produces the file bigram_freqs.json, which is an object mapping
    lowercase-only letter bigrams aa, ab, ..., zz to their frequencies in the
    given source text. The frequencies will add up to 1, modulo floating point
    imprecision.
"""


# ______________________________________________________________________
# Imports

import json
import re
import sys
from collections import Counter


# ______________________________________________________________________
# Functions

def load_words(filename):
    with open(filename) as f:
        text = f.read()
    words = re.findall(r'[\w\S]+', text)
    return [w.encode('ascii', 'ignore').decode('ascii').lower() for w in words]

def find_bigram_freqs(words):
    c = Counter()
    for w in words:
        for i in range(len(w) - 1):
            bigram = w[i:i+2]
            if re.match(r'[a-z][a-z]', bigram):
                c[bigram] += 1
    total = sum(c.values())
    return {bigram: count / total for bigram, count in c.items()}


# ______________________________________________________________________
# Main

if __name__ == '__main__':

    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(0)

    words = load_words(sys.argv[1])
    bigram_freqs = find_bigram_freqs(words)

    with open('bigram_freqs.json', 'w') as f:
        json.dump(bigram_freqs, f)
