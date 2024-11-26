#!/usr/bin/env python3
""" cryptogram.py

    A small tool to help you solve your cryptogram for Python 3.

    Usage:

        ./cryptogram.py <cryptogram_text>

    From there you'll get a prompt until you've solved the puzzle at hand
    (which is up to you to determine).

    At the prompt:

    > XY  --> (any two letters); Swap letters X and Y in the working solution.
    > XX  --> (same letter twice); Toggle wheter X is highlighted as correct.
    > r   --> Retype the original cryptogram text.
    > f   --> Show letter frequency alongside English letter ranking.
    > ?   --> Show help (this message).
    > s   --> Shuffle all letters randomly.
    > c   --> Show common short English words.
    > h   --> Print an abbreviated work history, for sharing your process.
    > b   --> Toggle showing bigram frequency data.
    > q   --> Quit.
"""
# TODO:
#   * Currently, when printing out your history (the `h` command),
#     shuffles will appear as a long list of swaps. It would be nicer
#     to have a single line for a shuffle that presents it as such.
#   * I think that, in printing the history, letter highlights don't currently
#     display correctly. It would be nice if they did.
#   * It would be cool to add an optional timer so I could see how
#     long it took me to solve a puzzle. I could use H (capital) to print
#     out a history that includes timing info.
#   * Don't count punctuation in the progress bar for the history command.
#
#   * Fix typos in the readme; update the example history image.
#   * Add that pressing R will re-run all the saved commands for the given
#     input. This fails with a message without any saved commands; if there are
#     both current commands and saved commands, this prompts for confirmation to
#     discard the current commands. Otherwise it re-enacts all previous
#     commands, including those to highlight letters (not just swaps).
#   * Add that pressing t will print out the top N words for each single cipher
#     word, all neatly underneath the current cipher text. I could consider also
#     printing out the most common letter mappings below that. This could act as
#     a kind of strong hint.


# ____________________________________________________________
# Imports

import json
import math
import random
import re
import string
import subprocess
import sys

from collections import Counter


# ____________________________________________________________
# Globals and constants

# These will store terminal escape codes.
# Currently these are used by print_with_highlights().
blue_seq  = None
green_seq = None
reset_seq = None
white_seq = None

bigram_mode = False
en_bigram_freqs = None


# ____________________________________________________________
# Functions

def log(obj):
    log_file.write(json.dumps(obj) + '\n')

def swap(s, marked_l, x, y):
    """ Return (s', marked_l'), where x and y are swapped; if
        x == y then x is toggled within the set marked_l).
    """
    if x == y:
        marked_l ^= {x}
    s = s.replace(y, '_')
    s = s.replace(x, y)
    return (s.replace('_', x), marked_l)

def show_letter_frequencies(s):
    """ Show the top 10 letters in s, sorted most-frequent first. """
    letter_counts = Counter(s.replace(' ', ''))
    letters = [letter for letter, _ in letter_counts.most_common()[:10]]
    print('Cipher letters: ', ' '.join(letters))
    print('English letters:', 'e t a o i n s r h d')

def show_bigram_tables(s):
    """ Display bigram frequency tables for s and for English. """

    # Ensure the English bigram frequencies are loaded.
    global en_bigram_freqs
    if not en_bigram_freqs:
        with open('data/bigram_freqs.json') as f:
            en_bigram_freqs = json.load(f)

    # Calculate bigram frequencies for the current string.
    bigram_counts = Counter()
    tokens = get_tokens(s)
    for token in tokens:
        if not is_word_token(token):
            continue
        for i in range(len(token) - 1):
            bigram_counts[token[i:i+2]] += 1
    total_bigrams = sum(bigram_counts.values())
    bigram_freqs = {
            bigram: count / total_bigrams
            for bigram, count in bigram_counts.items()
    }

    # Normalize and map frequencies to the color range [232, 255].
    max_fr = max(bigram_freqs.values(), default=1)
    color_map = lambda freq: int(232 + freq / max_fr * 23)
    en_max_fr = max(en_bigram_freqs.values())
    en_color_map = lambda freq: int(232 + freq / en_max_fr * 23)

    # Prepare the bigram tables.
    color_count = Counter()
    for row in range(26):
        row_str = ''
        for col in range(26):
            bigram = chr(97 + row) + chr(97 + col)
            # print(f'bigram={bigram}')
            # print('raw freq:', bigram_freqs.get(bigram, 0))
            color = color_map(bigram_freqs.get(bigram, 0))
            # print(f'color={color}')
            color_count[color] += 1
            if color == 232:
                fg_color = 232 if (row + col) % 2 == 0 else 243
                row_str += f"\033[38;5;{fg_color}m"
            row_str += f'\033[48;5;{color}m{bigram}\033[0m'
        row_str += '  '
        for col in range(26):
            bigram = chr(97 + row) + chr(97 + col)
            color = en_color_map(en_bigram_freqs.get(bigram, 0))
            if color == 232:
                fg_color = 232 if (row + col) % 2 == 0 else 243
                row_str += f"\033[38;5;{fg_color}m"
            row_str += f'\033[48;5;{color}m{bigram}\033[0m'
        print(row_str)

def get_cmd_output(cmd):
    """ Return stdout, as a bytes object, from running `cmd`. """
    process_completion = subprocess.run(cmd.split(), capture_output=True)
    return process_completion.stdout

def print_curr_str(s, marked_l):
    """ This expects `s` = (soln, marked_lets).
        This prints out `soln`, highlighting the letters in marked_lets.
    """
    global blue_seq, reset_seq

    if blue_seq is None:
        blue_seq  = get_cmd_output('tput setaf 33')
        reset_seq = get_cmd_output('tput sgr0')

    bytes_to_print = []
    for c in s:
        c_byte = c.encode()
        if c in marked_l:
            bytes_to_print += [blue_seq, c_byte, reset_seq]
        else:
            bytes_to_print.append(c_byte)
    sys.stdout.buffer.write(b''.join(bytes_to_print + [b'\n']))

def get_tokens(s):
    """
		Breaks the string s into a list of substrings such that:
		- Each substring either has no spaces or punctuation, or
		- Each substring is entirely spaces or punctuation.
    """
    return re.findall(r'[^\s\W]+|[\s\W]+', s)

def is_word_token(s):
    return bool(re.match(r'[^\s\W]+', s))

def print_with_highlights(s, white_lets, green_lets, correct_token_idx):
    """ Print out the string `s` while highlighting characters in white or green
        (ish) if they're in white_lets or green_lets, respectively.
        tokens with indexes in correct_token_idx will also receive a highlighted
        background color.
    """
    global white_seq, green_seq, gray_seq, hilite_seq, reset_seq

    if white_seq is None:
        white_seq  = get_cmd_output('tput setaf 7')
        green_seq  = get_cmd_output('tput setaf 118')
        gray_seq   = get_cmd_output('tput setaf 12')
        hilite_seq = get_cmd_output('tput setab 239')
        reset_seq  = get_cmd_output('tput sgr0')

    bytes_to_print = []
    for token_idx, token in enumerate(get_tokens(s)):
        if token_idx in correct_token_idx:
            bytes_to_print.append(hilite_seq)
        for c in token:
            c_byte = c.encode()
            if c in white_lets:
                bytes_to_print.extend([white_seq, c_byte])
            elif c in green_lets:
                bytes_to_print.extend([green_seq, c_byte])
            else:
                bytes_to_print.extend([gray_seq, c_byte])
        bytes_to_print.append(reset_seq)
    sys.stdout.buffer.write(b''.join(bytes_to_print))

def print_progress_bar(perc_done):
    block = '█'
    half  = '▌'
    width = 30
    n = width * perc_done
    s = block * math.floor(n)
    if (n - len(s)) > 0.5:
        s += half
    s += ' ' * (width - len(s))
    print(' |' + s + '|')

def show_history(crypt, swaps, final):
    """ Show the swap history of the cryptogram. """

    good_tokens = get_tokens(final)
    s = crypt

    print(f'Start   {s}')

    for pair in swaps:
        s, _ = swap(s, set(), pair[0], pair[1])
        tokens = get_tokens(s)

        # Find the subset of correct tokens in `s`.
        is_word = r'[^\s\W]+'
        correct_token_idx = {
                i
                for i, token in enumerate(tokens)
                if token == good_tokens[i] and re.match(is_word, token)
        }

        # Print the current swap.
        print(f'{pair[0]}<->{pair[1]}   ', end='', flush=True)

        # Print the current string `s`, highlighting correct letters.
        correct_lets = {let for (i, let) in enumerate(s) if let == final[i]}
        print_with_highlights(s, pair, correct_lets, correct_token_idx)

        # Print out a progress bar of how far we've come so far.
        perc_done = sum([let in correct_lets for let in s]) / len(s)
        print_progress_bar(perc_done)

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

    double_letters = [
            'ss', 'ee', 'tt', 'ff', 'll', 'mm', 'oo', 'rr', 'nn', 'pp'
    ]
    print()
    print('Common double letters:')
    show_in_columns(double_letters)

    print()


# ____________________________________________________________
# Main

if len(sys.argv) < 2:
    print(__doc__)
    sys.exit(0)

log_file = open('cryptogram_log.jsonl', 'a')
crypt    = ' '.join(sys.argv[1:])
swaps    = []
curr_str = crypt
marked_l = set()

log({'action': 'init', 'crypt': crypt})

while True:

    try:
        inp = input('> ')
    except (EOFError, KeyboardInterrupt):
        print('Have a great rest of your day! :)')
        sys.exit(0)

    if inp == 'r':
        print(f'Original cryptogram:\n{crypt}')
        curr_str = crypt = input('Replacement cryptogram: ')
        log({'action': 'replace', 'crypt': crypt})
        for pair in swaps:
            curr_str, marked_l = swap(curr_str, marked_l, pair[0], pair[1])

    elif inp == 'f':
        show_letter_frequencies(curr_str)

    elif inp == 'b':
        bigram_mode = not bigram_mode
        print(f"Bigram mode {'on' if bigram_mode else 'off'}.")

    elif inp == '?':
        print(__doc__)

    elif inp == 's':
        # Replace swaps with random swaps, one for each letter.
        swaps = [(i, random.choice(range(26))) for i in range(26)]
        swaps = [(chr(i + ord('a')), chr(j + ord('a'))) for i, j in swaps]
        soln = (crypt, set())
        for pair in swaps:
            soln = swap(soln, pair[0], pair[1])
        curr_str, marked_l = soln[0], set()  # No marked letters.

    elif inp == 'c':
        show_common_elements()

    elif inp == 'h':
        show_history(crypt, swaps, curr_str)

    elif inp == 'q':
        print('Have a great day! :D')
        sys.exit(0)
        
    elif len(inp) == 2:
        swaps.append(inp)
        log({'action': 'swap', 'letters': inp})
        curr_str, marked_l = swap(curr_str, marked_l, inp[0], inp[1])

    print_curr_str(curr_str, marked_l)

    if bigram_mode:
        show_bigram_tables(curr_str)
