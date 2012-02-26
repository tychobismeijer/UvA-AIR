#!/usr/bin/python3

# A script that should get the word senses
# For now it just reads from stdin and returns 'tokenized' and sentence split
# results.

import freeling
import sys
import configparser
from pprint import pprint as pp

CONFIG='wsd_bag.ini'


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

def print_wsd_results(results, out):
    for sentence in results:
        for word in sentence.get_words():
            out.write(word.get_form() + "[")
            senses = parse_senses_string(word.get_senses_string())
            if (senses):
                out.write(senses[0][1])
            out.write("] ")
        out.write("||\n")

def parse_senses_string(senses):
    if (senses == ''):
        return []
    s_list = []
    for s in senses.split('/'):
        s_id, s_prob = s.split(':')
        s_list.append((float(s_prob), s_id))
    return s_list

def get_senses(sentences):
    "Returns a list with the most probable sense for the words in the sentence."
    senses = []
    for sentence in sentences:
        for word in sentence.get_words():
            w_senses = parse_senses_string(word.get_senses_string())
            if (w_senses):
                senses.append(w_senses[0][1])
    return senses


def analyze(text, tools):
    t = tools['tk'].tokenize(text)
    t = tools['sp'].split(t, True)
    t = tools['mf'].analyze(t)
    t = tools['pos'].analyze(t)
    t = tools['wsd'].analyze(t)
    return t

def setup_tools(config_fn):
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
    tools['wsd'] = freeling.ukb_wrap(data_l+'/ukb.dat')

    return tools

def wsd_bag(docs_in, docs_out, tools):
    while(True):
        doc_id = docs_in.readline()
        if (doc_id == ''):
            break
        docs_out.write(doc_id)
        a = analyze(docs_in.readline(), tools)
        for ws in get_senses(a): docs_out.write(ws + " ")
        docs_out.write("\n\n")
        docs_in.readline() # Skip over empty line

def main():
    tools = setup_tools(CONFIG)
    for fn in sys.argv[1:]:
        wsd_bag(open(fn), sys.stdout, tools)

if __name__ == "__main__":
    main()
