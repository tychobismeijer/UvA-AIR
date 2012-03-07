import re
import sys
import codecs

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

def load_wolf(wolf_xml):
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

def normalize(word):
    w = word.lower()
    w = w.strip("\"'.,")
    if(w.startswith("l'")):
        w = w[2:]
    if(w.startswith("d'")):
        w = w[2:]
    return w

def word_senses(word):
    return sense_dict.get(word, [])

stop_words = ["le", "la", "les", "un", "une", "de", "des"]

def words_wsexpand(words):
    expansion = []
    for word in words.split():
        word_n = normalize(word)
        if(word_n in stop_words):
            continue # Remove stop words
        ws = word_senses(word_n)
        if(ws):
            expansion = expansion + ws
            continue
        expansion.append(word_n)
    return expansion

def topics_wsexpand(topics, out):
    for topic in topics:
        expansion = words_wsexpand(topic["title"])
        expansion = expansion + words_wsexpand(topic["desc"])
        expansion = expansion + words_wsexpand(topic["narr"])
        out.write(topic['num'] + "\n")
        for w in expansion: out.write(w + " ")
        out.write("\n\n")

def main():
    if(len(sys.argv) != 3):
        print("Usage: pp-query wsexpand topicfilename")
        exit(1)
    out = sys.stdout
    topics = parse_topics(codecs.open(sys.argv[2], "r", "latin1"))
    if(sys.argv[1] == 'wsexpand'):
        load_wolf(open('wolf.xml'))
        topics_wsexpand(topics, out)

if __name__ == "__main__":
    main()
