#!/usr/bin/env python3

# /**
#     usage:  python3 mtc2318-searcher.py  /path/to/trec-index-collection/ 
#                     /path/to/directory/where/query/files/are/stored\
# example : chatterjee@SChatterjee:~/Codes$ python3  mtcs2318-searcher.py \
#                           trec678rb/index-cs2318           trec678rb/topics/robust.xml
# **/

# Also , please note that, search() function contains an argument for roll
#       In scoring function
# optimal value of m reported in paper was 0.8-1.0
# optimal value of lambda reported in paper was 0.3-0.5

import lucene
import sys, lucene, argparse
from org.apache.pylucene.search.similarities import PythonClassicSimilarity

import lucene
from java.nio.file import Paths
from org.apache.lucene.analysis.standard import StandardAnalyzer
from org.apache.lucene.index import DirectoryReader
from org.apache.lucene.search import IndexSearcher
from org.apache.lucene.queryparser.classic import QueryParser
from org.apache.lucene.store import FSDirectory
from org.apache.lucene.search.similarities import SimilarityBase, BasicStats
from tqdm import tqdm
import math
import xml.etree.ElementTree as ET

# Initialize the VM
lucene.initVM()

from org.apache.lucene.search.similarities import TFIDFSimilarity

class SimpleSimilarity(PythonClassicSimilarity):
    def lengthNorm(self, numTerms):
        return 1.0
    
    def __init__(self, delta=1.0, adl=1.0, m=0.9, lambda_param=0.4, N=1.0):
        super().__init__()
        self.delta = delta
        self.adl = adl
        self.m = m
        self.lambda_param = lambda_param
        self.N = N

    def score(self, stats, freq, docLen):
        tf = freq
        mtf = stats.totalTermFreq / stats.numberOfFieldTokens
        l = docLen

        nf1_val = self.nf1(tf, mtf)
        nf2_val = self.nf2(tf, l)

        f0_t = math.log(self.N / stats.docFreq)

        F_t_nf1 = self.F_t(nf1_val, f0_t)
        F_t_nf2 = self.F_t(nf2_val, f0_t)

        return 0.5 * F_t_nf1 + 0.5 * F_t_nf2

    def explain(self, stats, doc, freq, docLen):
        explanation = f"CustomSimilarity explanation: tf={freq}, docLen={docLen}"
        return explanation

    def toString(self):
        return "CustomSimilarity"

    def nf1(self, tf, mtf):
        return math.log(1 + tf) / math.log(self.delta + mtf)

    def nf2(self, tf, l):
        return tf * math.log(1 + self.adl / l)

    def F_t(self, x, f0_t):
        if self.m > 2:
            return (1 / (self.lambda_param * (2 - self.m))) * (f0_t**(2 - self.m) - x**((2 - self.m) / (1 - self.m)))
        elif self.m == 2:
            return (1 / self.lambda_param) * (math.log(f0_t) - (1 / (1 - self.m)) * math.log(x))
        elif self.m == 1:
            return (1 / self.lambda_param) * f0_t * (1 - math.exp(-self.lambda_param * x))
        else:
            raise ValueError("Unsupported value for m")

# Instantiate the custom similarity
sim = SimpleSimilarity()

def read_queries(query_file_path):
    queries = []
    tree = ET.parse(query_file_path)
    root = tree.getroot()
    for top in root.findall('top'):
        num = top.find('num').text.strip()
        title = top.find('title').text.strip()
        queries.append((num, title))
    return queries

def search(index_path, queries):
    try:
        analyzer = StandardAnalyzer()
        #print(f"Opening index directory: {index_path}")
        directory = FSDirectory.open(Paths.get(index_path))
        searcher = IndexSearcher(DirectoryReader.open(directory))
        
        N = searcher.getIndexReader().numDocs()
        searcher.setSimilarity(SimpleSimilarity(delta=1.0, adl=1.0, m=0.9, lambda_param=0.4, N=N))

        for qid, query_text in queries:
            # Escape special characters in the query text
            escaped_query_text = QueryParser.escape(query_text)
            query = QueryParser("contents", analyzer).parse(escaped_query_text)
            scoreDocs = searcher.search(query, 1000).scoreDocs

            for rank, scoreDoc in enumerate(scoreDocs, start=1):
                doc = searcher.doc(scoreDoc.doc)
                docno = doc.get("docno") if doc.get("docno") else "None"
                print(f"{qid}\tQ0\t{docno}\t{rank}\t{scoreDoc.score}\tcs2318")

    except Exception as e:
        print(f"An error occurred while searching: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Search documents using Lucene.")
    parser.add_argument("index_path", type=str, help="Path to the directory where the index is stored.")
    parser.add_argument("query_file_path", type=str, help="Path to the TREC format query file.")
    args = parser.parse_args()

    index_path = args.index_path
    query_file_path = args.query_file_path

    queries = read_queries(query_file_path)
    search(index_path, queries)
