import os, re, sys
from subprocess import *
from lucene import IndexSearcher, StandardAnalyzer, Document, Field, QueryParser, Sort, TopScoreDocCollector, Term, TermQuery
from lucene import SimpleFSDirectory, File, initVM, Version

class QueryHelper(): 

    @staticmethod
    def query(indexName, queryString):

        indSearcher = IndexSearcher(SimpleFSDirectory(File(indexName)))
        qp = QueryParser(Version.LUCENE_CURRENT, "content", StandardAnalyzer(Version.LUCENE_CURRENT))
        qp.setDefaultOperator(qp.Operator.AND)
         
        query = qp.parse(queryString.replace("-","_"))
                
        aux = indSearcher.search(query, 100)
        results = aux.scoreDocs
        hits = aux.totalHits
        
        ir = indSearcher.getIndexReader()

        #results = collector.topDocs()
        i = 0

        res = []
    
        for r in results:        
            doc = ir.document(i)
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


    
