import string
from collections import Counter

def analyze_frequencies(text):
    text = "".join([char for char in text if char.isalpha()])
    frequency_counter = Counter(text.lower())
    sorted_characters = sorted(frequency_counter, key=frequency_counter.get, reverse=True)
    return sorted_characters

def substitution_cipher_decrypt(ciphertext, mapping):
    plaintext = ""
    for char in ciphertext:
        if char.isalpha():
            decrypted_char = mapping[char.lower()]
            plaintext += decrypted_char.upper() if char.isupper() else decrypted_char
        else:
            plaintext += char
    return plaintext

english_frequencies = "etaoinshrdlcumwfgypbvkjxqz"
cryptogram = "jtx xll dbdimmwk epq buxpjxa nc p dbavkpsa'q vekxu etv epkjxa niqwkxqq xpuswxu wk jtx apc."

ciphertext_frequencies = analyze_frequencies(cryptogram)
char_mapping = dict(zip(ciphertext_frequencies, english_frequencies))

decrypted_text = substitution_cipher_decrypt(cryptogram, char_mapping)
print(decrypted_text)
