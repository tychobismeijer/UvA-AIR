import re
import sys
import codecs

### Reading the list of topics from a file ###

str_topic_start = "<top>"
str_topic_stop  = "</top>"
str_num_start   = "<num>"
str_num_stop    = "</num>"
str_title_start = "<FR-title>"
str_title_stop  = "</FR-title>"
str_desc_start  = "<FR-desc>"
str_desc_stop   = "</FR-desc>"
str_narr_start  = "<FR-narr>"
str_narr_stop   = "</FR-narr>"

def parse_topics(topics_text):
    """Parse a topics xml file into a list of dictionaries.

    Every dictionary is a topic. A topics has an identifier (num), title
    (title), description (desc) and narrative (narr).
    """
    result = []
    read_topic = False
    read_num = False
    read_title = False
    read_narr = False
    read_desc = False
    topic_num = ""
    title = ""
    desc = ""
    narr = ""
    for line in topics_text:
        for word in line.split():
            if(str_topic_start in word):
                read_topic = True
                continue

            if(str_num_start in word):
                read_num = True
                continue
            if(str_num_stop in word):
                read_num = False
                continue
            if(read_num and "C" in word):
                topic_num = word
                continue

            if(str_title_start in word):
                read_title = True
                title = ""
                continue
            if(str_title_stop in word):
                read_title = False
                continue
            if(read_title):
                title = title + " " + word
                continue

            if(str_narr_start in word):
                read_narr = True
                narr = ""
                continue
            if(str_narr_stop in word):
                read_narr = False
                continue
            if(read_narr):
                narr = narr + " " + word
                continue

            if(str_desc_start in word):
                read_desc = True
                desc = ""
                continue
            if(str_desc_stop in word):
                read_desc = False
                continue
            if(read_desc):
                desc = desc + " " + word
                continue

            if(str_topic_stop in word):
                read_topic = False
                result.append({
                    'num' : topic_num,
                    'narr' : narr.strip(),
                    'desc' : desc.strip(),
                    'title' : title.strip() })
                title = ""
                num = ""
                desc = ""
                narr = ""
    return result

### WOLF and finding word senses ###

def load_wolf(wolf_xml):
    """Parse the WOLF xml-like file into a dict of literals to senses.

    For every literal the a list of senses is made.
    """
    global sense_dict
    sense_dict = {}
    id_re = re.compile("<ID>(.*)</ID>")
    literal_re = re.compile("<LITERAL>(.*?)(<SENSE>.*?</SENSE>)?</LITERAL>")
    for line in wolf_xml:
        id_m = id_re.search(line)
        if(not id_m):
            print("ERROR")
            continue
        sense_id = id_m.group(1)
        literal_ms = literal_re.findall(line)
        for literal_g in literal_ms:
            word = literal_g[0]
            sense_dict[word] = sense_dict.get(word, []) + [sense_id,]

def word_senses(word):
    """Return a list of senses for a literal"""
    result = []
    for s in sense_dict.get(word, []):
        result.extend(map_sense(s))
    # Try to deal with simple morphology
    if (result == [] and word[len(word)-1] == 's'):
        for s in sense_dict.get(word[0:len(word)-1], []):
            result.extend(map_sense(s))

    return result

def parse_sensemap(sensemap_m_text, sensemap_p_text):
    """Parse a polysemous and a monosemous sensemap.

    Returns one dictionary mapping senses to a list of senses in the the higher
    versioned wordnet.
    """
    result = {}
    # Parse polysemous sensemap
    for line in sensemap_p_text:
        l = line.split()
        score = l[0] # Score of the polysemous mapping
        sense1 = l[1].split(';')[1]
        if (len(l) > 2):
            senses2 = set([s.split(';')[1] for s in l[2:]])
        if (sense1 in result):
            result[sense1] |= senses2
        else:
            result[sense1] = senses2

    # Parse monosemous sensemap
    for line in sensemap_m_text:
        l = line.split()
        sense1 = l[1]
        senses2 = set([l[3]])
        if (sense1 in result):
            result[sense1] |= senses2
        else:
            result[sense1] = senses2

    return result

def load_sensemap(smt_2_0_noun_m, smt_2_0_verb_m, smt_2_1_noun_m, smt_2_1_verb_m,
        smt_2_0_noun_p, smt_2_0_verb_p, smt_2_1_noun_p, smt_2_1_verb_p):
    """Load all the sensemaps, so they are available for map_sense"""
    global sm_2_0
    global sm_2_1
    sm_2_0 = {
        'noun' : parse_sensemap(smt_2_0_noun_m, smt_2_0_noun_p),
        'verb' : parse_sensemap(smt_2_0_verb_m, smt_2_0_verb_p)
    }
    sm_2_1 = {
        'noun' : parse_sensemap(smt_2_1_noun_m, smt_2_1_noun_p),
        'verb' : parse_sensemap(smt_2_1_verb_m, smt_2_1_verb_p)
    }

sense_wolf_re = re.compile("ENG20-(\d*)-([nva])")
def map_sense(sense_wolf):
    """Maps a sense from Wordnet 2.0 to Wordnet 3.0.

    First use load_sensemap to load the sensemaps before using this function.
    """
    sense_wolf_m = sense_wolf_re.match(sense_wolf)
    if (not sense_wolf_m):
        #print("ERROR: sense not recognized: " + sense_wolf)
        return []
    sense_2_0 = sense_wolf_m.group(1)
    sense_class = sense_wolf_m.group(2)
    if (sense_class == 'n'):
        sm1 = sm_2_0['noun']
        sm2 = sm_2_1['noun']
    elif (sense_class == 'v'):
        sm1 = sm_2_0['verb']
        sm2 = sm_2_1['verb']
    else:
        #print("ERROR: don't know what do with class: " + sense_class)
        return [] 
    senses_2_1 = sm1.get(sense_2_0, [])
    senses_3_0 = []
    for s in senses_2_1:
        for s2 in sm2.get(s, []):
            senses_3_0.append(s2 + "-" + sense_class)
    return senses_3_0

### Loading dictionary and translaton words ###

translate_dict = {}

def load_dict(dict_text):
    """Loads a dictionary for use of translate_word."""
    global translate_dict
    for line in dict_text:
        word, translation = line.split('|')
        translate_dict[word.strip()] = translation.strip()

def translate_word(word):
    """Translate one word by looking it up in the dictionary"""
    return translate_dict.get(word, None)

### Processing of the bag of words in the query ###

def normalize(word):
    """Put a word in a more normal form.

    Put in lower case, remove sticky dots and commas, and remove sticky articles
    """
    w = word.lower()
    w = w.strip("\"'.,")
    if(w.startswith("l'")):
        w = w[2:]
    if(w.startswith("d'")):
        w = w[2:]
    return w

stop_words = ["le", "la", "les", "un", "une", "de", "des"]

def words_expand(words, word_sense_expand=True, translate=True,
        translate_expanded=False):
    """Return a list of words, word sense expanded and translated.

    Options:
    words : The words, in a string.
    word_sense_expand : Try to expand a word into a list of word senses
    translate : Translate not-expanded words
    translate_expanded : Returns word senses and a translation for expandable
        words.
    """
    expansion = []
    for word in words.split():
        word_n = normalize(word)
        if(word_n in stop_words):
            continue # Remove stop words
        if(word_sense_expand):
            ws = word_senses(word_n)
            if(ws):
                expansion = expansion + ws
                if(not translate_expanded):
                    continue
        if(translate):
            translation = translate_word(word)
            if(translation): #found translation
                expansion.append(translation)
                continue
        expansion.append(word_n)
    return expansion

def topics_expand(topics, out, word_sense_expand=True):
    """Expand and translate a list of topics"""
    for topic in topics:
        out.write(topic['num'] + "\n")
        expansion = words_expand(topic["title"], word_sense_expand)
        expansion = expansion + words_expand(topic["desc"], word_sense_expand)
        expansion = expansion + words_expand(topic["narr"], word_sense_expand)
        for w in expansion: out.write(w + " ")
        out.write("\n\n")

### Main program ###

def main():
    if(len(sys.argv) != 3):
        print("Usage: pp-query wsexpand topicfilename")
        exit(1)
    out = sys.stdout
    topics = parse_topics(codecs.open(sys.argv[2], "r", "latin1"))
    if(sys.argv[1] == 'wsexpand'):
        load_sensemap(open('2.0to2.1.noun.mono'), open('2.0to2.1.verb.mono'),
            open('2.1to3.0.noun.mono'), open('2.1to3.0.verb.mono'),
            open('2.0to2.1.noun.poly'), open('2.0to2.1.verb.poly'),
            open('2.1to3.0.noun.poly'), open('2.1to3.0.verb.poly'))
        load_wolf(open('wolf.xml'))
        load_dict(open('dict'))
        topics_expand(topics, out)

    if(sys.argv[1] == 'translate'):
        load_dict(open('dict'))
        topics_expand(topics, out, word_sense_expand=False)


if __name__ == "__main__":
    main()
