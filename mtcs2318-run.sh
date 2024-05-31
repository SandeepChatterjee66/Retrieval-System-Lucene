#!/bin/bash

# Set variables  (change below paths acc to your environment)
DOCS_PATH="trec678rb/documents" #documents corpus
INDEX_PATH="trec678rb/index-mtcs2318" #folder to store indices
OUTPUT_PATH="trec678rb/mtcs2318-output.txt" # final output
RESULTS_PATH="trec678rb/mtcs2318-results.txt" #intermediate result / search results

# Uncomment and use the following for combined, queries
# else comment back
TOPICS_PATH="trec678rb/topics/topics-combined.xml"
QRELS_PATH="trec678rb/qrels/trec678-combined.qrel"

# Uncomment and use the following for robust, 601-700
# else comment back
# TOPICS_PATH="trec678rb/topics/robust.xml"
# QRELS_PATH="trec678rb/qrels/robust_601-700.qrel"

# # Uncomment and use the following for trec678, 301-450
# # else comment back
# TOPICS_PATH="trec678rb/topics/trec678.xml"
# QRELS_PATH="trec678rb/qrels/trec678_301-450.qrel"
# DO NOT CHANGE ANYTHING BELOW

# Indexing
rm -r $INDEX_PATH #clear out old index path
python3 mtcs2318-indexer.py $DOCS_PATH $INDEX_PATH
ls -l $INDEX_PATH

# Searching
python3 mtcs2318-searcher.py $INDEX_PATH $TOPICS_PATH > $RESULTS_PATH
less $RESULTS_PATH

# Evaluate results
trec_eval -q $QRELS_PATH $RESULTS_PATH > $OUTPUT_PATH
cat $OUTPUT_PATH
