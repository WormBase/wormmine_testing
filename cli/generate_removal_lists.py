#!/usr/bin/env python3
"""
Generate removal lists for WormMine post-processing

Runs all WormMine testing queries and saves failures to removal list files.

Usage:
    python generate_removal_lists.py <wormmine_url> [--output-dir <dir>]

Example:
    python generate_removal_lists.py http://localhost:8080/wormmine
"""

import sys
import os
import argparse
import logging
from pathlib import Path
from intermine.webservice import Service

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Import query functions from testing_queries
from testing_queries import (
    query_01, query_02, query_03, query_04,
    query_08, query_09, query_10, query_11,
    query_15, query_16, query_17, query_18, query_19,
    query_21, query_22, query_23, query_24,
    query_25, query_26, query_27, query_29,
    query_30, query_31, query_32, query_35, query_41
)


def run_all_queries(service_url, output_dir):
    """Run all queries that should return 0 and save failures"""
    logger.info(f"Connecting to {service_url}")
    service = Service(f"{service_url}/service")

    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Change to output dir so save_txt_file writes there
    original_dir = os.getcwd()
    os.chdir(output_dir)

    # Clear existing removal lists
    for f in output_dir.glob("to_remove_*.txt"):
        f.unlink()

    # All queries that expect 0 results - run with save_file=True
    queries = [
        (query_01, "01", "C. elegans genes with bad primaryIdentifier"),
        (query_02, "02", "C. elegans genes without symbol"),
        (query_03, "03", "C. elegans genes without primaryIdentifier"),
        (query_04, "04", "C. elegans transcripts without chromosome"),
        (query_08, "08", "Genes with WBGene in secondaryIdentifier"),
        (query_09, "09", "Genes with WBGene in symbol"),
        (query_10, "10", "Transcripts with bad primaryIdentifier"),
        (query_11, "11", "CDS with bad primaryIdentifier"),
        (query_15, "15", "Genes without organism"),
        (query_16, "16", "C. elegans CDS without gene"),
        (query_17, "17", "C. elegans transcripts without gene"),
        (query_18, "18", "C. elegans CDS without protein"),
        (query_19, "19", "C. elegans CDS without transcripts"),
        (query_21, "21", "C. elegans proteins with bad primaryAccession"),
        (query_22, "22", "C. elegans proteins with bad primaryIdentifier"),
        (query_23, "23", "C. elegans proteins without CDSs"),
        (query_24, "24", "C. elegans proteins without sequence"),
        (query_25, "25", "CDS without organism"),
        (query_26, "26", "Transcripts without organism"),
        (query_27, "27", "Proteins without primaryIdentifier"),
        (query_29, "29", "CDS with duplicate prefix"),
        (query_30, "30", "C. elegans MRNA without gene"),
        (query_31, "31", "MRNA without organism"),
        (query_32, "32", "MRNA without CDSs"),
        (query_35, "35", "Organisms without name"),
        (query_41, "41", "AnatomyTerm with CDATA"),
    ]

    for query_func, num, desc in queries:
        logger.info(f"[{num}] {desc}")
        try:
            query_func(service, save_file=True)
        except Exception as e:
            logger.error(f"[{num}] Error: {e}")

    os.chdir(original_dir)

    # Report what was saved
    logger.info("=" * 60)
    logger.info("Removal lists generated:")
    for f in sorted(output_dir.glob("to_remove_*.txt")):
        count = len(f.read_text().strip().split('\n')) if f.stat().st_size > 0 else 0
        logger.info(f"  {f.name}: {count} items")


def main():
    parser = argparse.ArgumentParser(description='Generate removal lists from WormMine')
    parser.add_argument('url', help='WormMine URL (e.g., http://localhost:8080/wormmine)')
    parser.add_argument('--output-dir', '-o', default='./removal_lists', help='Output directory')
    args = parser.parse_args()

    run_all_queries(args.url, args.output_dir)


if __name__ == '__main__':
    main()
