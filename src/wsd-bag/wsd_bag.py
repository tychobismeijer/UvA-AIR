#!/usr/bin/python3

import freeling
import sys
import configparser

CONFIG='wsd_bag.ini'

def print_split_results(results, out):
    """Formatted output of sentence splitting"""
    for sentence in results:
        for word in sentence.get_words():
            out.write(word.get_form() + "|")
        out.write("||\n")

def print_pos_results(results, out):
    """Formatted output of part of speech tagging"""
    for sentence in results:
        for word in sentence.get_words():
            out.write(word.get_form() + "[" + word.get_tag() + "] ")
        out.write("||\n")

def print_wsd_results(results, out):
    """Formatted output of senses"""
    for sentence in results:
        for word in sentence.get_words():
            out.write(word.get_form() + "[")
            senses = parse_senses_string(word.get_senses_string())
            if (senses):
                out.write(senses[0][1])
            out.write("] ")
        out.write("||\n")

# Use this method because the array access to senses gives a memory leak.
def parse_senses_string(senses):
    """Parses the senses output of ukb to an array"""
    if (senses == ''):
        return []
    s_list = []
    for s in senses.split('/'):
        s_id, s_prob = s.split(':')
        s_list.append((float(s_prob), s_id))
    return s_list


# Ignore words without sense and with on of these PoS tags
pos_tags_ignored = ["CC", "CD", "DT", "EX", "TO", "Fz", "Fx", "Fat", "Fc",
        "Fd", "Fe", "Fg", "Fit", "Fp", "Fs", "Fx", "Fz"]

def get_senses(sentences):
    """Get senses out of sentences and return the most probable.

    Get the most probable sense of every word in the sentences. If no sense can
    be found the stemmed word itself is used."""
    senses = []
    for sentence in sentences:
        for word in sentence.get_words():
            w_senses = parse_senses_string(word.get_senses_string())
            if (w_senses):
                senses.append(w_senses[0][1])
            elif (not word.get_tag() in pos_tags_ignored):
                senses.append(word.get_lemma() + "[" + word.get_short_tag() + "]")
    return senses


def analyze(text, tools):
    """Run analysis on string text and return a list of sentences.

    The tools to be used are in the dictionary tools, which should be set up
    with setup_tools().
    """
    t = tools['tk'].tokenize(text)
    t = tools['sp'].split(t, True)
    t = tools['mf'].analyze(t)
    t = tools['pos'].analyze(t)
    t = tools['wsd'].analyze(t)
    return t

def setup_tools(config_fn):
    """Setup Freeling tools according to a config file.

        The tools returned is a dictionary with the following keys:
        tk : The tokenizer
        sp : The sentence splitter
        pos : The part of speech tagger
        mf : The morphological analysis tools (freeling.maco)
        wsd : word sense tagger
    """
    config = configparser.ConfigParser()
    config.read(config_fn)
    language = config['wsd']['language']
    data = config['freeling']['datadir']
    data_l = data + '/' + language

    tools = {}
    freeling.util_init_locale("default")
    tools['tk'] = freeling.tokenizer(data_l + "/tokenizer.dat")
    tools['sp'] = freeling.splitter(data_l + "/splitter.dat")
    tools['pos'] = freeling.hmm_tagger(language, data_l + "/tagger.dat",
            True, # Retokenize
            2)    # Force selecting one PoS tag after retokenization
    op = freeling.maco_options(language);
    op.set_active_modules(
        0, # UserMap (for analysis of domain-specific tokens)
        1, # AffixAnalysis
        1, # MultiwordsDetection
        1, # NumbersDetection
        1, # PuctuationDetection
        0, # DatesDetection, gives problems with words like "Monday"
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
    """WSD the docs from docs_in and write the result to docs_out.
        
    Tools should be set up using setup_tools(). The document list should be
    preprocessed."""
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
