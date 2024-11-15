# Retrieval-System-Lucene
A very very efficient search engine which can intelligently rank based on novel term weighting scheme, and with this implementation it can scale for large data very well with parallelized map-reduce paradigm. 

# Objective
Implementing term weighting scheme for measuring query-document similarity by modeling the dependency between occurrences of a term. It uses a parameterized decay function to decrease the information content of subsequent occurrences. Evaluated on various web collections, it outperforms several known retrieval models, including strong TF-IDF models

# Information Retrieval System

This repository contains the code for an IR system in Lucene Framework developed for comparing the term weighting scheme performance. The system indexes and searches through a collection of documents using Apache Lucene. It has been developed for the trec678rb document collection. The indexing process accommodates multiple tag fields within each document, and each file can contain multiple documents marked by `<doc>` tags.

## Maintainer
**Name**: S. Chatterjee    
**Github**: [sandeepchatterjee66](https://github.com/SandeepChatterjee66)
**Affil**: Indian Statistical Institute, Kolkata, India  
**Based on**: Jiaul H. Paik, Dept CSE, IIT KGP, India

## Steps to Run

1. **Prepare the Corpus**:
    - Unzip the source zip file.
    - Open the `documents` folder, delete the empty txt file there, and copy the entire corpus into this folder.

2. **Configure the Script**:
    - Open the `run.sh` file with a text editor.
    - Set the paths correctly.
    - Uncomment the relevant sections based on which query file and relevant file you need to execute.
    - Ensure the launcher for the `trec_eval` command is correctly set to your alias.

3. **Execute the Script**:
    - Save the `run.sh` file.
    - Set execute permission with `chmod +x run.sh`, or run it directly with bash:
      ```bash
      bash run.sh
      ```

4. **Monitor the Process**:
    - The script will handle indexing first; you can check the progress since it completes quickly.
    - Once indexing is done, the searcher runs automatically and displays the search results. Press 'q' to exit the page viewer.
    - Finally, `trec_eval` runs automatically and displays the evaluation output.

5. **Check Outputs**:
    - The final output and search results are automatically saved in text files.

## Implementation Details

1. **Indexing**:
    - Standard Analyzer and common functions of Lucene are used for indexing.
    - The indexer processes documents with multiple tag fields within `<doc>` tags.

2. **Searching**:
    - A custom scoring function is implemented based on Paik, 2016.
    - The scoring function is defined as:
      ```
      W(t) = 0.5 * F_t(nf1(t,d)) + 0.5 * F_t(nf2(t,d))

      nf1(t,d) = log(1 + tf(d)) / log(delta + mtf(d))
      nf2(t,d) = tf(t,d) * log(1 + adl / l(d))

      F_t(x) = 1 / (λ * (2 - m)) * (f0_t^(2 - m) - z^((2 - m) / (1 - m))) if m > 2
             = 1 / λ * (log(f0_t) - (1 / (1 - m)) * log(z)) if m = 2
             = 1 / λ * f0_t * (1 - e^(-λ * x)) if m = 1

      z = -λ * (1 - m) * x + (f0_t)^(1 - m)
      f0_t = log(N / df)
      ```

## Requirements

1. **PyLucene**: Version 7 or 9 (ensure by `import lucene`).
2. **TREC_Eval Tool**: Ensure it's installed and executable (`make` command).
3. **Corpus**: TREC678RB documents (~1.85GB).

## Improvements Made

1. **Indexer**:
    - Enhanced to index multiple tag fields within each document.
    - Handles multiple documents within each file marked by `<doc>` tags.
    - Regex is used for fast match, for empty match of docno , it is indexed as None

2. **Searcher**:
    - Made robust by fixing bugs for handling queries with slashes ("/").
    - Parses query files from XML format specific to TREC.
    - Outputs results in TREC format.

3. **Additional Features**:
    - Added a progress bar to monitor indexing progress.
    - Intermediate search results are saved for use with the `trec_eval` tool.
    - Try, Catch has been added for graceful exits.

## Manual Running
You can run the operations one by one too, the shell script is given below, replace the variables with your actual paths
```
# Indexing
rm -r $INDEX_PATH #clear out old index path
python3 mtcs2318-indexer.py $DOCS_PATH $INDEX_PATH
ls -l $INDEX_PATH

# Searching
python3 mtcs2318-searcher.py $INDEX_PATH $TOPICS_PATH > $RESULTS_PATH
less $RESULTS_PATH

# Evaluate results
trec_eval/trec_eval -q $QRELS_PATH $RESULTS_PATH > $OUTPUT_PATH
cat $OUTPUT_PATH
```

![Screenshot](/mcs2318-screenshot-10.png "Step-by-step manual running of the Retrieval System")

## References
  - Parameterized Decay Model for Information Retrieval, Jiaul H. Paik , https://ir.webis.de/anthology/2016.tist_journal-ir0anthology0volumeA7A3.1/
  - Trec Eval tool, https://github.com/usnistgov/trec_eval
  - Trec Collection, https://trec.nist.gov/data/test_coll.html
