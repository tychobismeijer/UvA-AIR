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
                print("read topic")
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





def main():
    out = codecs.getwriter('utf8')(sys.stdout)
    for fn in sys.argv[1:]:
        print(parse_topics(codecs.open(fn, "r", "latin1")))

if __name__ == "__main__":
    main()

        
        
