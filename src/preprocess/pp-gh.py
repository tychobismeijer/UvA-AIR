#!/usr/bin/python

# Input: A list of gh95 files.
# Output: A list of documents. On the first line is the document id, the second
# line contains the documents, the third is empty. On the fourth line the next
# entry starts.

import sys
import re
import codecs

def warning(message):
    print("Warning: " + message)

pat_doc_id = re.compile('<DOCID>(.*)</DOCID>')
str_text_start = '<TEXT>'
str_text_stop = '</TEXT>'

def preprocess(doc_in, doc_out):
    """Preprocesses the GH95 document of CLEF"""
    def output(text, doc_id):
        doc_out.write(doc_id + "\n")
        doc_out.write(text.replace("\n", " ") + "\n\n")

    doc_id = None
    reading_text = False
    text = ""
    for line in doc_in:
        if(str_text_start in line):
            if(reading_text):
                warning("Found " + str_text_start + " in text")
            if(not doc_id):
                warning("Reading text without knowing id")
                continue
            reading_text = True
            continue
        if((str_text_stop in line) and reading_text):
            output(text, doc_id)
            text = ""
            reading_text = False
            doc_id = None
        doc_id_match = pat_doc_id.match(line)
        if(doc_id_match):
            doc_id = doc_id_match.group(1)
            if(reading_text):
                warning("Found doc id in text")
            continue
        if(reading_text):
            text = text + line
        


def main():
    for fn in sys.argv[1:]:
        preprocess(codecs.open(fn, "r", "latin1"), sys.stdout)

if __name__ == "__main__":
    main()
