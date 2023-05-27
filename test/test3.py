import string
import re
import random
from collections import Counter

def preprocess_text(text):
    return re.sub(r'[^a-zA-Z]', '', text).lower()

def get_bigram_frequencies(text):
    bigrams = [text[i:i+2] for i in range(len(text) - 1)]
    return Counter(bigrams)

def get_bigram_score(text, reference_bigram_frequencies):
    text_bigram_frequencies = get_bigram_frequencies(text)
    score = 0
    for bigram, freq in text_bigram_frequencies.items():
        score += reference_bigram_frequencies.get(bigram, 0) * freq
    return score

def substitution_cipher_decrypt(ciphertext, mapping):
    plaintext = ""
    for char in ciphertext:
        if char.isalpha():
            decrypted_char = mapping.get(char.lower(), '?')
            plaintext += decrypted_char.upper() if char.isupper() else decrypted_char
        else:
            plaintext += char
    return plaintext

def get_best_decryption(ciphertext, reference_bigram_frequencies, iterations=10000):
    alphabet = list(string.ascii_lowercase)
    best_mapping = dict(zip(string.ascii_lowercase, alphabet))
    best_decryption = substitution_cipher_decrypt(ciphertext, best_mapping)
    best_score = get_bigram_score(preprocess_text(best_decryption), reference_bigram_frequencies)

    for _ in range(iterations):
        new_alphabet = alphabet[:]
        random.shuffle(new_alphabet)
        mapping = dict(zip(string.ascii_lowercase, new_alphabet))
        decrypted_text = substitution_cipher_decrypt(ciphertext, mapping)
        score = get_bigram_score(preprocess_text(decrypted_text), reference_bigram_frequencies)

        if score > best_score:
            best_score = score
            best_mapping = mapping
            best_decryption = decrypted_text

    return best_decryption

# Define the cryptogram and English bigram frequencies
cryptogram = "jtx xll dbdimmwk epq buxpjxa nc p dbavkpsa'q vekxu etv epkjxa niqwkxqq xpuswxu wk jtx apc."
reference_bigram_frequencies = {
    "th": 1.52, "he": 1.28, "in": 0.94, "er": 0.94, "an": 0.82, "re": 0.68, "ed": 0.53, "on": 0.49, "es": 0.47, "st": 0.46,
    "en": 0.43, "at": 0.43, "to": 0.43, "nt": 0.42, "ha": 0.41, "nd": 0.38, "ou": 0.37, "ea": 0.36, "ng": 0.35, "as": 0.33,
    "or": 0.32, "ti": 0.31, "is": 
