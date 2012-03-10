import os, re, sys
from subprocess import *
from lucene import IndexSearcher, IndexReader, StandardAnalyzer, Document, Field, QueryParser, Sort, TopScoreDocCollector, Term, TermQuery
from lucene import SimpleFSDirectory, File, initVM, Version

class QueryHelper(): 

    @staticmethod
    def query(indexName, queryString):
        indReader = IndexReader.open(SimpleFSDirectory(File("senses-gh95")))
        indSearcher = IndexSearcher(indReader)

        qp = QueryParser(Version.LUCENE_CURRENT, "content", StandardAnalyzer(Version.LUCENE_CURRENT))
        qp.setDefaultOperator(qp.Operator.AND)

        query = qp.parse(queryString.replace("-","_"))

        collector = TopScoreDocCollector.create(20, True)

        indSearcher.search(query, collector)

        hits = collector.topDocs().scoreDocs

        docId = hits[0].doc
        score = hits[0].score

        print "Best hit: " + str(docId)+", score: "+str(score)

        ir = indSearcher.getIndexReader()

        res = []

        i = 0
        for hit in hits:        
            docId = hits[i].doc
            doc = ir.document(docId)
            res.insert(i, doc.get('id'))
            i+=1

        return res


if __name__ == '__main__':
    initVM()
    
    if len(sys.argv) == 3:
        indexName = sys.argv[1]
        queryString = sys.argv[2]
        res = QueryHelper.query(indexName, queryString)
        print res
    else:
        print "Usage: python query.py {words | senses} [query]"


    
