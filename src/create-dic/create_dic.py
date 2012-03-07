import re
import sys
import codecs
from apiclient.discovery import build

xml_tag_re = re.compile("<(\w|[\-/])+?>")
filter_re = re.compile("(C\d+)|\.|\?|!|\||\"|,")

def parse_topics(topics_text):
    words = set()
    while (True):
        l = topics_text.readline()
        if (not l):
            break
        l = xml_tag_re.sub(" ", l)
        l = filter_re.sub(" ", l)
        words |= set(l.split())
    return words

def translate(words):
    service = build('translate', 'v2',
        developerKey='XXX')
    words = list(words)
    words_t = []
    while(True):
        w = words[0:10]
        del words[0:10]
        translation = service.translations().list(
            source='fr',
            target='en',
            q=w
        ).execute()
        for t in translation["translations"]:
            words_t.append(t["translatedText"])
        if (len(words) == 0):
            break
    return words_t

def main():
    out = codecs.getwriter('utf8')(sys.stdout)
    for fn in sys.argv[1:]:
        words = list(parse_topics(codecs.open(fn, "r", "latin1")))
        translation = translate(words)
        for x in range(len(words)):
            out.write(words[x] + "|" + translation[x] + "\n")

if __name__ == "__main__":
    main()

        
        
