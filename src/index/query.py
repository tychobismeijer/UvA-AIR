import os, re, sys
from subprocess import *
from lucene import IndexSearcher, IndexReader, StandardAnalyzer, Document, Field, QueryParser, Sort, TopScoreDocCollector, Term, TermQuery
from lucene import SimpleFSDirectory, File, initVM, Version

class QueryHelper(): 

    @staticmethod
    def query(indexName, queryFile, runName):
        indReader = IndexReader.open(SimpleFSDirectory(File(indexName)))
        indSearcher = IndexSearcher(indReader)
        ir = indSearcher.getIndexReader()

        qp = QueryParser(Version.LUCENE_CURRENT, "content", StandardAnalyzer(Version.LUCENE_CURRENT))

        f = open('results-'+runName, 'w')

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

            returnedDocs = 1000
            collector = TopScoreDocCollector.create(returnedDocs, True)

            indSearcher.search(query, collector)

            hits = collector.topDocs().scoreDocs

            size = len(hits)
            print "Total hits for query " +id+ ": "+str(size)

            i = 0
            for hit in hits:        
                docId = hits[i].doc
                score = hits[i].score
                doc = ir.document(docId)
                j = i + 1
                f.write(id + " 0 " + doc.get('id') + " " + str(j) + " " + str(score) +" " + runName +"\n")
                i+=1

        f.close()

if __name__ == '__main__':
    initVM()
    
    if len(sys.argv) == 4:
        indexName = sys.argv[1]
        queryFile = sys.argv[2]
        runName = sys.argv[3]
        QueryHelper.query(indexName, open(queryFile), runName)

    else:
        print "Usage: python query.py <indexName> <queryFile> <RunName>"
