#!/usr/bin/python3

# A script that should get the word senses
# For now it just reads from stdin and returns 'tokenized' and sentence split
# results.

import freeling
import sys
import configparser
from pprint import pprint as pp


config_fn='wsd_bag.ini'

def print_split_results(results, out):
    for sentence in results:
        for word in sentence.get_words():
            out.write(word.get_form() + "|")
        out.write("||\n")

def print_pos_results(results, out):
    for sentence in results:
        for word in sentence.get_words():
            out.write(word.get_form() + "[" + word.get_tag() + "] ")
        out.write("||\n")


def analyze(text, tools):
    t = tools['tk'].tokenize(text)
    t = tools['sp'].split(t, True)
    t = tools['mf'].analyze(t)
    t = tools['pos'].analyze(t)
    return t

def main():
    config = configparser.ConfigParser()
    config.read(config_fn)
    language = config['wsd']['language']
    data = config['freeling']['datadir']
    data_l = data + '/' + language

    tools = {}
    freeling.util_init_locale("default")
    tools['tk'] = freeling.tokenizer(data_l + "/tokenizer.dat")
    tools['sp'] = freeling.splitter(data_l + "/splitter.dat")
    tools['pos'] = freeling.hmm_tagger(language, data_l + "/tagger.dat", 1,
                                       2)
    op = freeling.maco_options(language);
    op.set_active_modules(
        0, # UserMap (for analysis of domain-specific tokens)
        1, # AffixAnalysis
        1, # MultiwordsDetection
        1, # NumbersDetection
        1, # PuctuationDetection
        1, # DatesDetection
        1, # QuantitiesDetection
        1, # DictionarySearch
        1, # ProbabilityAssignment (Essential for PoS)
        1, # OrthographicCorrection (Misspelling etc.)
        0) # NERecognition (Named Enitity Recognition)
    op.set_data_files(
        "",
        data_l+"/locucions.dat",
        data_l+"/quantities.dat",
        data_l+"/afixos.dat",
        data_l+"/probabilitats.dat",
        data_l+"/dicc.src",
        data_l+"/np.dat",
        data+"/common/punct.dat",
        data_l+"/corrector/corrector.dat");
    tools['mf'] = freeling.maco(op)

    for line in sys.stdin:
        a = analyze(line, tools)
        print_pos_results(a, sys.stdout)

if __name__ == "__main__":
    main()
