#!/usr/bin/python

# Input: A list of gh95 files.
# Output: A list of documents. On the first line is the document id, the second
# line contains the documents, the third is empty. On the fourth line the next
# entry starts.

import sys
import re

def warning(message):
    print("Warning: " + message)

pat_doc_id = re.compile('<DOCNO>(.*)</DOCNO>')
str_ld_start = '<LD>'
str_ld_stop = '</LD>'
str_te_start = '<TE>'
str_te_stop = '</TE>'
str_doc_start = '<DOC>'
str_doc_stop = '</DOC>'

def preprocess(doc_in):
    """Preprocesses the GH95 document of CLEF"""
    output_d = {
        'count' : 1,
        'fn_count' : 1,
        'doc_out' : open("la2002-1-pp", 'w')
    }
    def output(text, doc_id, o=output_d):
        print(o['count'])
        o['count'] = o['count'] + 1
        if (o['count'] > 1000):
            o['count'] = 1
            o['fn_count'] = o['fn_count'] + 1
            o['doc_out'] = open("la2002-" + str(o['fn_count']) + "-pp", 'w')
        o['doc_out'].write(doc_id + "\n")
        o['doc_out'].write(text.replace("\n", " ") + "\n\n")

    doc_id = None
    reading_doc = False
    reading_text = False
    text = ""
    for line in doc_in:
        if ((not reading_doc) and str_doc_start in line):
            reading_doc = True
            text = ""
            doc_id = None
            continue
        if(str_ld_start in line and str_ld_stop in line):
            text = text + " " + line.replace(str_ld_start, "").replace(str_ld_stop,
                    "").strip()
            continue
        if(str_te_start in line and str_te_stop in line):
            text = text + " " + line.replace(str_te_start, "").replace(str_te_stop,
                    "").strip()
            continue
        if(str_ld_start in line):
            reading_text = True
            text = text + " " + line.replace(str_ld_start, "").strip()
            continue
        if(str_te_start in line):
            reading_text = True
            text = text + " " + line.replace(str_te_start, "").strip()
            continue
        if(str_te_stop in line):
            reading_text = False
            text = text + " " + line.replace(str_te_stop, "").strip()
            continue
        if(str_ld_stop in line):
            reading_text = False
            text = text + " " + line.replace(str_ld_stop, "").strip()
            continue
        
        doc_id_match = pat_doc_id.match(line)
        if(doc_id_match):
            doc_id = "LA2002-" + doc_id_match.group(1)
            continue
        if(reading_text):
            text = text + " " + line.strip()
            continue
        if(str_doc_stop in line):
            output(text, doc_id)
            text = ""
            reading_text = False
            reading_doc = False
            doc_id = None
        


def main():
    for fn in sys.argv[1:]:
        preprocess(open(fn))

if __name__ == "__main__":
    main()
