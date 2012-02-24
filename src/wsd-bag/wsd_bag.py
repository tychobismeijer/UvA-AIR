#!/usr/bin/python3

# A script that should get the word senses
# For now it just reads from stdin and returns 'tokenized' and sentence split
# results.

import freeling
import sys

LANG='en'
FREELINGDIR = "/home/tycho/Programs/Freeling"
DATA = FREELINGDIR+"/share/freeling/"

def print_wsd_results(results, out):
    for sentence in results:
        for word in sentence.get_words():
            out.write(word.get_form() + "|")
        out.write("||\n")

def analyze(text):
    freeling.util_init_locale("default");
    tk=freeling.tokenizer(DATA+LANG+"/tokenizer.dat");
    sp=freeling.splitter(DATA+LANG+"/splitter.dat");
    
    t = tk.tokenize(text)
    t = sp.split(t, text)

    return t


def main():
    for line in sys.stdin:
        a = analyze(line)
        print_wsd_results(a, sys.stdout)

if __name__ == "__main__":
    main()
