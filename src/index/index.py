import os, re, sys
from subprocess import *
from lucene import IndexWriter, IndexReader, StandardAnalyzer, Document, Field
from lucene import SimpleFSDirectory, File, initVM, Version


class IndexHelper():

    @staticmethod
    def index(source, indexName):

        if(not os.path.exists(indexName)):
            os.mkdir(indexName)
            
        indexDir = File(indexName)

        writer = IndexWriter(SimpleFSDirectory(File(indexName)),StandardAnalyzer(Version.LUCENE_CURRENT), True,IndexWriter.MaxFieldLength.LIMITED)
      
        p = re.compile("(GH\d+\-\d+)\n(.*?)\n+", re.DOTALL)
        res = p.findall(source)
        
        i = 0
        for pair in res:
            i += 1
            doc = Document()
            doc.add(Field("id", pair[0], Field.Store.YES, Field.Index.NO))
            for t in pair[1].split():
                doc.add(Field("content", t.replace("-","_"), Field.Store.NO, Field.Index.NOT_ANALYZED));
                #doc.add(Field("content", pair[1], Field.Store.NO, Field.Index.ANALYZED));
                
            writer.addDocument(doc)
            
        writer.close()
        print str(i)+ " docs indexed"
        

if __name__ == '__main__':

    initVM()
       
    if len(sys.argv) == 3:            
        
        if sys.argv[1] == 'build':

            if(sys.argv[2] == "words"):                
                f = open("./words.txt").read()
                indexName = "words"

            elif (sys.argv[2] == "senses"):
                f = open("./word_senses.txt").read()
                indexName = "senses"

            IndexHelper.index(f, indexName)
            
        elif sys.argv[1] == 'read':

            indexName =sys.argv[2]
            reader = IndexReader.open(SimpleFSDirectory(File(indexName)))
            doc = reader.document(0)
            content = doc.getValues("content")     
            
            terms = reader.terms()
            while(terms.next()):
                t = terms.term()
                freq = terms.docFreq()
                print t.text()+" freq: "+str(freq)

    else:
        print "Usage: python index.py {build | read} {words | senses}"


