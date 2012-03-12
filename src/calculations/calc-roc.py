from __future__ import division
import os, re, sys
from subprocess import *
from lucene import initVM

class ROCCalculator(): 

    @staticmethod
    def calcRoc(Qrel, resultsDir):
        startId = 201
        stopId = 250

        id = startId

        totalFound = 0.
        totalNotFound = 0.
        nrOfResults = 0

        while(id <= stopId):
            print "Calculating id: " + str(id)

            result = open(resultsDir + "/" + str(id))
            results = result.readlines()
            result.close()

            nrOfResults += len(results)

            found = 0
            notFound = 0

            Qrels = open(Qrel)

            for line in Qrels:
                if line.startswith(str(id)):
                    l = line.split()
                    doc = l[2]
                    doc += "\n"
                    if doc in results:
                        totalFound += 1
                    else:
                        totalNotFound += 1

            Qrels.close()

            #print "Found: " + str(found) + " + not found: " + str(notFound)

            #recall = found / (found + notFound)
            #precision = found / len(results)

            #print "Recall: " +str(recall)
            #print "Precision: " +str(precision)

            id += 1

        print "Found: " + str(totalFound) + " + not found: " + str(totalNotFound)

        recall = totalFound / (totalFound + totalNotFound)
        precision = totalFound / nrOfResults

        print "Recall: " +str(recall)
        print "Precision: " +str(precision)

if __name__ == '__main__':
    initVM()
    
    if len(sys.argv) == 3:
        Qrel = sys.argv[1]
        resultsDir = sys.argv[2]
        ROCCalculator.calcRoc(Qrel, resultsDir)

    else:
        print "Usage: python calc-roc.py <qrel file> <results dir>"