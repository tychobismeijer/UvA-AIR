import os, re, sys
from subprocess import *
from lucene import IndexSearcher, IndexReader, StandardAnalyzer, Document, Field, QueryParser, Sort, TopScoreDocCollector, Term, TermQuery
from lucene import SimpleFSDirectory, File, initVM, Version

class QueryHelper(): 

    @staticmethod
    def query(indexName, queryFile):
        indReader = IndexReader.open(SimpleFSDirectory(File(indexName)))
        indSearcher = IndexSearcher(indReader)
        ir = indSearcher.getIndexReader()

        qp = QueryParser(Version.LUCENE_CURRENT, "content", StandardAnalyzer(Version.LUCENE_CURRENT))

        while(True):
            id = queryFile.readline()

            if id == "":
                break

            id = id.replace("C","")
            id = id.replace("\n","")

            queryString = queryFile.readline()
            queryString = queryString.replace("?","")
            queryString = queryString.replace("*","")
            queryString = queryString.replace("-","_")
            queryString = queryString.replace("\n","")

            query = qp.parse(queryString)

            queryFile.readline()

            returnedDocs = 60000
            collector = TopScoreDocCollector.create(returnedDocs, True)

            indSearcher.search(query, collector)

            hits = collector.topDocs().scoreDocs

            size = len(hits)
            print "Total hits for query " +id+ ": "+str(size)

            f = open('./results/'+id, 'w')

            i = 0
            for hit in hits:        
                docId = hits[i].doc
                doc = ir.document(docId)
                f.write(doc.get('id') + "\n")
                i+=1

            f.close()

if __name__ == '__main__':
    initVM()
    
    if len(sys.argv) == 3:
        indexName = sys.argv[1]
        queryFile = sys.argv[2]
        QueryHelper.query(indexName, open(queryFile))

    else:
        print "Usage: python query.py <indexName> <queryFile>"
