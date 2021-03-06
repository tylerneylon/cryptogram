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
    > f   --> Show letter frequency alongside English letter ranking.
    > ?   --> Show help (this message).
    > s   --> Shuffle all letters randomly.
    > c   --> Show common short English words.
    > q   --> Quit.
"""


# ____________________________________________________________
# Imports

import random
import sys

from collections import Counter


# ____________________________________________________________
# Functions

def swap(s, x, y):
    """ Return string s with letters x and y swapped. """
    s = s.replace(y, '_')
    s = s.replace(x, y)
    return s.replace('_', x)

def show_letter_frequencies(s):
    """ Show the top 10 letters in s, sorted most-frequent first. """
    letter_counts = Counter(s.replace(' ', ''))
    letters = [letter for letter, _ in letter_counts.most_common()[:10]]
    print('Cipher letters: ', ' '.join(letters))
    print('English letters:', 'e t a o i n s r h d')

def show_in_columns(words, col_width=6, max_width=65, indent=4):
    """ Print the words in `words` in colums of width `col_width`, in lines of
        maximum width `max_width`. Each line is indented by `indent` spaces; the
        indent is included as part of the max width. The output will only look
        good if all the words are shorter than col_width.
    """
    curr_line = ''
    fmt = '%%-%ds' % col_width  # Make a format string like '%-6s'.
    for word in words:
        if indent + len(curr_line + (fmt % word)) > max_width:
            assert len(curr_line.strip()) > 0
            print(' ' * indent + curr_line)
            curr_line = ''
        curr_line += fmt % word
    if len(curr_line) > 0:
            print(' ' * indent + curr_line)

def show_common_elements():
    """ Show common 2-, 3-, and 4-letter words and common double letters.

    I found these word lists here:
    https://www3.nd.edu/~busiforc/handouts/cryptography/cryptography%20hints.html
    """

    two_letters = ['of', 'to', 'in', 'it', 'is', 'be', 'as', 'at', 'so', 'we',
            'he', 'by', 'or', 'on', 'do', 'if', 'me', 'my', 'up', 'an', 'go',
            'no', 'us', 'am']
    print()
    print('Common 2-letter words:')
    show_in_columns(two_letters)

    three_letters = ['the', 'and', 'for', 'are', 'but', 'not', 'you', 'all',
            'any', 'can', 'had', 'her', 'was', 'one', 'our', 'out', 'day',
            'get', 'has', 'him', 'his', 'how', 'man', 'new', 'now', 'old',
            'see', 'two', 'way', 'who', 'boy', 'did', 'its', 'let', 'put',
            'say', 'she', 'too', 'use']
    print()
    print('Common 3-letter words:')
    show_in_columns(three_letters)

    four_letters = ['that', 'with', 'have', 'this', 'will', 'your', 'from',
            'they', 'know', 'want', 'been', 'good', 'much', 'some', 'time']
    print()
    print('Common 4-letter words:')
    show_in_columns(four_letters)

    double_letters = ['ss', 'ee', 'tt', 'ff', 'll', 'mm', 'oo']
    print()
    print('Common double letters:')
    show_in_columns(double_letters)

    print()


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

    elif inp == 'f':
        show_letter_frequencies(soln)

    elif inp == '?':
        print(__doc__)

    elif inp == 's':
        # Replace swaps with random swaps, one for each letter.
        swaps = [(i, random.choice(range(26))) for i in range(26)]
        swaps = [(chr(i + ord('a')), chr(j + ord('a'))) for i, j in swaps]
        for pair in swaps:
            soln = swap(soln, pair[0], pair[1])

    elif inp == 'c':
        show_common_elements()

    elif inp == 'q':
        print('Have a great day! :D')
        sys.exit(0)
        
    elif len(inp) == 2:
        swaps.append(inp)
        soln = swap(soln, inp[0], inp[1])

    print(soln)
