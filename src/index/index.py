import os, re, sys
from subprocess import *
from lucene import IndexWriter, IndexReader, StandardAnalyzer, Document, Field
from lucene import SimpleFSDirectory, File, initVM, Version


class IndexHelper():

    @staticmethod
    def index(source, writer):

        p = re.compile("(GH\d+\-\d+)\n(.*?)\n+", re.DOTALL)
        res = p.findall(source)
        
        i = 0
        for pair in res:
            i += 1
            doc = Document()
            doc.add(Field("id", pair[0], Field.Store.YES, Field.Index.NOT_ANALYZED))
            for t in pair[1].split():
                doc.add(Field("content", t.replace("-","_"), Field.Store.YES, Field.Index.ANALYZED));
                #doc.add(Field("content", pair[1], Field.Store.NO, Field.Index.ANALYZED));
                
            writer.addDocument(doc)
            
        print str(i)+ " docs indexed"

        return i

if __name__ == '__main__':

    initVM()
       
    if len(sys.argv) == 3:            
        
        if sys.argv[1] == 'build':

            if(sys.argv[2] == "words"):                
                f = open("./words.txt").read()
                indexName = "words"

                IndexHelper.index(f, indexName)

            elif (sys.argv[2] == "senses"):
                # customized for 1995 WSD dataset

                indexName = "senses-gh95"

                if(not os.path.exists(indexName)):
                    os.mkdir(indexName)

                writer = IndexWriter(SimpleFSDirectory(File(indexName)),StandardAnalyzer(Version.LUCENE_CURRENT), True,IndexWriter.MaxFieldLength.LIMITED)

                noDocs = 0
                nrFiles = 0
                j = 950101
                while(True):
                    j += 1
                    if(j > 951230):
                        break
                    filename = str(j) + "-wsd"
                    try:
                        f = open("./gh-1995-wsd/" + filename).read()

                        addedDocs = IndexHelper.index(f, writer)
                        noDocs += addedDocs

                        nrFiles += 1

                    except IOError:
                        print "File " + filename + " does not exist. Skipping..."

                writer.close()

                print str(nrFiles) + " files containing " + str(noDocs) + " documents added to index "

            
        elif sys.argv[1] == 'read':
            reader = IndexReader.open(SimpleFSDirectory(File("senses-gh95")))

            doc = reader.document(0)
            content = doc.getValues("content")
            id = doc.getValues("id")
            print content

            nrDocs = reader.numDocs()
            print "Number of docs: "+str(nrDocs)
            print "Doc 1: "+str(id[0])

            #Print all terms (takes some time :-) )
            #terms = reader.terms()
            #while(terms.next()):
            #    t = terms.term()
            #    freq = terms.docFreq()
            #    print t.text()+" freq: "+str(freq)

    else:
        print "Usage: python index.py {build | read} {words | senses}"


