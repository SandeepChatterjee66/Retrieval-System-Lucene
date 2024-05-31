#!/usr/bin/env python3

# usage: python3 mtc2318-indexer.py /path/to/trec-robust-collection/ /path/to/directory/where/index/should/be/stored
# example : chatterjee@SChatterjee:~/Codes$ python3  mtcs2318-indexer.py trec678rb/index-cs2318 trec678rb/topics/robust.xml

import lucene
lucene.initVM()

import os
import argparse
from java.nio.file import Paths
from org.apache.lucene.analysis.standard import StandardAnalyzer
from org.apache.lucene.document import Document, Field, FieldType
from org.apache.lucene.index import IndexWriter, IndexWriterConfig, IndexOptions
from org.apache.lucene.store import FSDirectory
from tqdm import tqdm
import re

def index_documents(docs_path, index_path):
    analyzer = StandardAnalyzer()
    index_directory = FSDirectory.open(Paths.get(index_path))
    config = IndexWriterConfig(analyzer)
    index_writer = IndexWriter(index_directory, config)

    try:
        total_files = sum(len(files) for _, _, files in os.walk(docs_path))
        print(f"Total files to index: {total_files}")

        for root, dirs, files in os.walk(docs_path):
            for file_name in tqdm(files, desc="Indexing files"):
                file_path = os.path.join(root, file_name)
                index_document(file_path, index_writer)
    except Exception as e:
        print(f"Error occurred during indexing: {e}")
    finally:
        index_writer.close()
        print("Indexing completed successfully.")

def parse_document(file_content):
    doc_no_match = re.search(r"<DOCNO>\s*(.*?)\s*</DOCNO>", file_content)
    ht_match = re.search(r"<HT>\s*(.*?)\s*</HT>", file_content)
    header_match = re.search(r"<HEADER>(.*?)</HEADER>", file_content, re.DOTALL)
    text_match = re.search(r"<TEXT>(.*?)</TEXT>", file_content, re.DOTALL)
    
    doc_no = doc_no_match.group(1) if doc_no_match else "UNKNOWN"
    ht = ht_match.group(1) if ht_match else "UNKNOWN"
    header = header_match.group(1) if header_match else ""
    text = text_match.group(1) if text_match else ""
    
    return doc_no, ht, header, text

def index_document(file_path, index_writer):
    try:
        doc = Document()
        with open(file_path, 'r', encoding='utf-8', errors='replace') as file:
            file_content = file.read()
        
        doc_no, ht, header, text = parse_document(file_content)

        # Define the field type for content fields
        content_field_type = FieldType()
        content_field_type.setStored(True)
        content_field_type.setTokenized(True)
        content_field_type.setIndexOptions(IndexOptions.DOCS_AND_FREQS_AND_POSITIONS)

        # Define the field type for metadata fields
        metadata_field_type = FieldType()
        metadata_field_type.setStored(True)
        metadata_field_type.setTokenized(False)
        metadata_field_type.setIndexOptions(IndexOptions.DOCS)

        # Add fields to the document
        doc.add(Field("docno", doc_no, metadata_field_type))
        doc.add(Field("ht", ht, metadata_field_type))
        doc.add(Field("header", header, content_field_type))
        doc.add(Field("text", text, content_field_type))
        doc.add(Field("contents", f"{header} {text}", content_field_type))  # Combine header and text for full-text search
        
        index_writer.addDocument(doc)
    except Exception as e:
        print(f"Error indexing file: {file_path}, {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Index documents for Lucene.")
    parser.add_argument("docs_path", type=str, help="Path to the directory containing documents to index.")
    parser.add_argument("index_path", type=str, help="Path to the directory where the index should be stored.")
    args = parser.parse_args()

    docs_path = args.docs_path
    index_path = args.index_path

    print(f'docs_path  input : {docs_path}')
    print(f'index_path output: {index_path}')

    index_documents(docs_path, index_path)
