from __future__ import division
import os, re, sys
from subprocess import *
from lucene import initVM

class ROCCalculator(): 

    @staticmethod
    def calcRoc(Qrel, resultsDir):

        nrOfPoints = 50
        point = 1

        start = 0.

        curve = open("Curve", 'w')

        while(start <= 1):
            startId = 201
            stopId = 250

            id = startId

            totalFound = 0.
            totalNotFound = 0.
            nrOfResults = 0

            while(id <= stopId):
                result = open(resultsDir + "/" + str(id))
                results = result.readlines()
                result.close()

                part = len(results) / nrOfPoints
                sizeParts = part * point
                nrOfResults += sizeParts

                found = 0
                notFound = 0

                Qrels = open(Qrel)

                for line in Qrels:
                    if line.startswith(str(id)):
                        l = line.split()
                        doc = l[2]
                        doc += "\n"
                        if doc in results[0:int(sizeParts)]:
                            totalFound += 1
                        else:
                            totalNotFound += 1

                Qrels.close()

                id += 1

            #print "Found: " + str(totalFound) + " + not found: " + str(totalNotFound)

            recall = totalFound / (totalFound + totalNotFound)
            precision = totalFound / nrOfResults

            #print "Recall: " +str(recall)
            #print "Precision: " +str(precision)

            print "Run number: " +str(point)

            point += 1

            if recall > start:

                curve.write(str(recall)+", "+str(precision)+"\n")

                print "Recall "+str(start)+" calculated."

                start += .1

if __name__ == '__main__':
    initVM()
    
    if len(sys.argv) == 3:
        Qrel = sys.argv[1]
        resultsDir = sys.argv[2]
        ROCCalculator.calcRoc(Qrel, resultsDir)

    else:
        print "Usage: python calc-roc.py <qrel file> <results dir>"