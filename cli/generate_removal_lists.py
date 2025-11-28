#!/usr/bin/env python3
"""
Generate removal lists for WormMine post-processing

Runs all WormMine testing queries that expect 0 results and saves
failures to removal list files for post-processing.

Usage:
    python generate_removal_lists.py <wormmine_url> [--output-dir <dir>]

Example:
    python generate_removal_lists.py http://localhost:8080/wormmine
    python generate_removal_lists.py http://localhost:8080/wormmine --output-dir ./removal_lists
"""

import sys
import argparse
import logging
from pathlib import Path
from intermine.webservice import Service

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def save_to_removal_list(output_dir, model, rows):
    """Save unique identifiers to removal list file"""
    output_file = output_dir / f"to_remove_{model.lower()}.txt"

    # Read existing items
    existing = set()
    if output_file.exists():
        existing = set(output_file.read_text().strip().split('\n'))

    # Collect new unique items
    new_items = set()
    for row in rows:
        identifier = row['primaryIdentifier']
        if identifier and identifier not in existing:
            new_items.add(identifier)

    # Append new items
    if new_items:
        with open(output_file, 'a') as f:
            for identifier in sorted(new_items):
                f.write(f"{identifier}\n")

    return len(new_items)


def run_query(service, query_num, model, views, constraints, logic=None):
    """Run a query and return rows"""
    query = service.new_query(model)
    for view in views:
        query.add_view(view)

    for i, (path, op, value) in enumerate(constraints):
        code = chr(65 + i)  # A, B, C...
        if value is None:
            query.add_constraint(path, op, code=code)
        else:
            query.add_constraint(path, op, value, code=code)

    if logic:
        query.set_logic(logic)

    return list(query.rows())


def run_all_queries(service_url, output_dir):
    """Run all queries that expect 0 results"""
    logger.info(f"Connecting to {service_url}")
    service = Service(f"{service_url}/service")

    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Clear existing removal lists
    for f in output_dir.glob("to_remove_*.txt"):
        f.unlink()
        logger.debug(f"Removed {f.name}")

    total_issues = 0

    # Query 01: C. elegans genes with bad primaryIdentifier
    logger.info("[01] C. elegans genes with primaryIdentifier NOT LIKE WBGene*")
    rows = run_query(service, 1, 'Gene',
        ['primaryIdentifier', 'secondaryIdentifier', 'symbol', 'organism.name'],
        [('organism.name', '=', 'Caenorhabditis elegans'), ('primaryIdentifier', 'NOT LIKE', 'WBGene*')])
    if rows:
        count = save_to_removal_list(output_dir, 'gene', rows)
        logger.warning(f"[01] FAILED: {len(rows)} results, saved {count} to removal list")
        total_issues += len(rows)
    else:
        logger.info("[01] PASSED (0 results)")

    # Query 02: C. elegans genes without symbol
    logger.info("[02] C. elegans genes without symbol")
    rows = run_query(service, 2, 'Gene',
        ['primaryIdentifier', 'secondaryIdentifier', 'symbol', 'organism.name'],
        [('organism.name', '=', 'Caenorhabditis elegans'), ('symbol', 'IS NULL', None)])
    if rows:
        count = save_to_removal_list(output_dir, 'gene', rows)
        logger.warning(f"[02] FAILED: {len(rows)} results, saved {count} to removal list")
        total_issues += len(rows)
    else:
        logger.info("[02] PASSED (0 results)")

    # Query 03: C. elegans genes without primaryIdentifier
    logger.info("[03] C. elegans genes without primaryIdentifier")
    rows = run_query(service, 3, 'Gene',
        ['primaryIdentifier', 'secondaryIdentifier', 'symbol', 'organism.name'],
        [('organism.name', '=', 'Caenorhabditis elegans'), ('primaryIdentifier', 'IS NULL', None)])
    if rows:
        count = save_to_removal_list(output_dir, 'gene', rows)
        logger.warning(f"[03] FAILED: {len(rows)} results, saved {count} to removal list")
        total_issues += len(rows)
    else:
        logger.info("[03] PASSED (0 results)")

    # Query 04: C. elegans transcripts without chromosome
    logger.info("[04] C. elegans transcripts without chromosome")
    rows = run_query(service, 4, 'Transcript',
        ['primaryIdentifier', 'symbol', 'organism.name'],
        [('organism.name', '=', 'Caenorhabditis elegans'), ('chromosome', 'IS NULL', None)])
    if rows:
        count = save_to_removal_list(output_dir, 'transcript', rows)
        logger.warning(f"[04] FAILED: {len(rows)} results, saved {count} to removal list")
        total_issues += len(rows)
    else:
        logger.info("[04] PASSED (0 results)")

    # Query 08: Genes with WBGene in secondaryIdentifier
    logger.info("[08] Genes with WBGene in secondaryIdentifier")
    rows = run_query(service, 8, 'Gene',
        ['primaryIdentifier', 'secondaryIdentifier', 'symbol'],
        [('secondaryIdentifier', 'CONTAINS', 'WBGene')])
    if rows:
        count = save_to_removal_list(output_dir, 'gene', rows)
        logger.warning(f"[08] FAILED: {len(rows)} results, saved {count} to removal list")
        total_issues += len(rows)
    else:
        logger.info("[08] PASSED (0 results)")

    # Query 09: Genes with WBGene in symbol
    logger.info("[09] Genes with WBGene in symbol")
    rows = run_query(service, 9, 'Gene',
        ['primaryIdentifier', 'secondaryIdentifier', 'symbol'],
        [('symbol', 'CONTAINS', 'WBGene')])
    if rows:
        count = save_to_removal_list(output_dir, 'gene', rows)
        logger.warning(f"[09] FAILED: {len(rows)} results, saved {count} to removal list")
        total_issues += len(rows)
    else:
        logger.info("[09] PASSED (0 results)")

    # Query 10: Transcripts with bad primaryIdentifier
    logger.info("[10] Transcripts with primaryIdentifier NOT LIKE Transcript:*")
    rows = run_query(service, 10, 'Transcript',
        ['primaryIdentifier', 'symbol'],
        [('primaryIdentifier', 'NOT LIKE', 'Transcript:*')])
    if rows:
        count = save_to_removal_list(output_dir, 'transcript', rows)
        logger.warning(f"[10] FAILED: {len(rows)} results, saved {count} to removal list")
        total_issues += len(rows)
    else:
        logger.info("[10] PASSED (0 results)")

    # Query 11: CDS with bad primaryIdentifier
    logger.info("[11] CDS with primaryIdentifier NOT LIKE CDS:*")
    rows = run_query(service, 11, 'CDS',
        ['primaryIdentifier', 'symbol'],
        [('primaryIdentifier', 'NOT LIKE', 'CDS:*')])
    if rows:
        count = save_to_removal_list(output_dir, 'cds', rows)
        logger.warning(f"[11] FAILED: {len(rows)} results, saved {count} to removal list")
        total_issues += len(rows)
    else:
        logger.info("[11] PASSED (0 results)")

    # Query 15: Genes without organism
    logger.info("[15] Genes without organism")
    rows = run_query(service, 15, 'Gene',
        ['primaryIdentifier', 'secondaryIdentifier', 'symbol'],
        [('organism', 'IS NULL', None)])
    if rows:
        count = save_to_removal_list(output_dir, 'gene', rows)
        logger.warning(f"[15] FAILED: {len(rows)} results, saved {count} to removal list")
        total_issues += len(rows)
    else:
        logger.info("[15] PASSED (0 results)")

    # Query 16: C. elegans CDS without gene
    logger.info("[16] C. elegans CDS without gene")
    rows = run_query(service, 16, 'CDS',
        ['primaryIdentifier', 'symbol'],
        [('organism.name', '=', 'Caenorhabditis elegans'), ('gene', 'IS NULL', None)])
    if rows:
        count = save_to_removal_list(output_dir, 'cds', rows)
        logger.warning(f"[16] FAILED: {len(rows)} results, saved {count} to removal list")
        total_issues += len(rows)
    else:
        logger.info("[16] PASSED (0 results)")

    # Query 17: C. elegans transcripts without gene
    logger.info("[17] C. elegans transcripts without gene")
    rows = run_query(service, 17, 'Transcript',
        ['primaryIdentifier', 'symbol'],
        [('organism.name', '=', 'Caenorhabditis elegans'), ('gene', 'IS NULL', None)])
    if rows:
        count = save_to_removal_list(output_dir, 'transcript', rows)
        logger.warning(f"[17] FAILED: {len(rows)} results, saved {count} to removal list")
        total_issues += len(rows)
    else:
        logger.info("[17] PASSED (0 results)")

    # Query 18: C. elegans CDS without protein
    logger.info("[18] C. elegans CDS without protein")
    rows = run_query(service, 18, 'CDS',
        ['primaryIdentifier', 'symbol'],
        [('organism.name', '=', 'Caenorhabditis elegans'), ('protein', 'IS NULL', None)])
    if rows:
        count = save_to_removal_list(output_dir, 'cds', rows)
        logger.warning(f"[18] FAILED: {len(rows)} results, saved {count} to removal list")
        total_issues += len(rows)
    else:
        logger.info("[18] PASSED (0 results)")

    # Query 19: C. elegans CDS without transcripts
    logger.info("[19] C. elegans CDS without transcripts")
    rows = run_query(service, 19, 'CDS',
        ['primaryIdentifier', 'symbol'],
        [('organism.name', '=', 'Caenorhabditis elegans'), ('transcripts', 'IS NULL', None)])
    if rows:
        count = save_to_removal_list(output_dir, 'cds', rows)
        logger.warning(f"[19] FAILED: {len(rows)} results, saved {count} to removal list")
        total_issues += len(rows)
    else:
        logger.info("[19] PASSED (0 results)")

    # Query 21: C. elegans proteins with bad primaryAccession
    logger.info("[21] C. elegans proteins with primaryAccession NOT LIKE CE*")
    rows = run_query(service, 21, 'Protein',
        ['primaryAccession', 'primaryIdentifier', 'secondaryIdentifier', 'symbol'],
        [('organism.name', '=', 'Caenorhabditis elegans'), ('primaryAccession', 'NOT LIKE', 'CE*')])
    if rows:
        count = save_to_removal_list(output_dir, 'protein', rows)
        logger.warning(f"[21] FAILED: {len(rows)} results, saved {count} to removal list")
        total_issues += len(rows)
    else:
        logger.info("[21] PASSED (0 results)")

    # Query 22: C. elegans proteins with bad primaryIdentifier
    logger.info("[22] C. elegans proteins with primaryIdentifier NOT LIKE CE*")
    rows = run_query(service, 22, 'Protein',
        ['primaryAccession', 'primaryIdentifier', 'secondaryIdentifier', 'symbol'],
        [('organism.name', '=', 'Caenorhabditis elegans'), ('primaryIdentifier', 'NOT LIKE', 'CE*')])
    if rows:
        count = save_to_removal_list(output_dir, 'protein', rows)
        logger.warning(f"[22] FAILED: {len(rows)} results, saved {count} to removal list")
        total_issues += len(rows)
    else:
        logger.info("[22] PASSED (0 results)")

    # Query 23: C. elegans proteins without CDSs
    logger.info("[23] C. elegans proteins without CDSs")
    rows = run_query(service, 23, 'Protein',
        ['primaryAccession', 'primaryIdentifier', 'secondaryIdentifier', 'symbol'],
        [('organism.name', '=', 'Caenorhabditis elegans'), ('CDSs', 'IS NULL', None)])
    if rows:
        count = save_to_removal_list(output_dir, 'protein', rows)
        logger.warning(f"[23] FAILED: {len(rows)} results, saved {count} to removal list")
        total_issues += len(rows)
    else:
        logger.info("[23] PASSED (0 results)")

    # Query 24: C. elegans proteins without sequence
    logger.info("[24] C. elegans proteins without sequence")
    rows = run_query(service, 24, 'Protein',
        ['primaryAccession', 'primaryIdentifier', 'secondaryIdentifier', 'symbol'],
        [('organism.name', '=', 'Caenorhabditis elegans'), ('sequence', 'IS NULL', None)])
    if rows:
        count = save_to_removal_list(output_dir, 'protein', rows)
        logger.warning(f"[24] FAILED: {len(rows)} results, saved {count} to removal list")
        total_issues += len(rows)
    else:
        logger.info("[24] PASSED (0 results)")

    # Query 25: CDS without organism
    logger.info("[25] CDS without organism")
    rows = run_query(service, 25, 'CDS',
        ['primaryIdentifier', 'symbol'],
        [('organism', 'IS NULL', None)])
    if rows:
        count = save_to_removal_list(output_dir, 'cds', rows)
        logger.warning(f"[25] FAILED: {len(rows)} results, saved {count} to removal list")
        total_issues += len(rows)
    else:
        logger.info("[25] PASSED (0 results)")

    # Query 26: Transcripts without organism
    logger.info("[26] Transcripts without organism")
    rows = run_query(service, 26, 'Transcript',
        ['primaryIdentifier', 'symbol'],
        [('organism', 'IS NULL', None)])
    if rows:
        count = save_to_removal_list(output_dir, 'transcript', rows)
        logger.warning(f"[26] FAILED: {len(rows)} results, saved {count} to removal list")
        total_issues += len(rows)
    else:
        logger.info("[26] PASSED (0 results)")

    # Query 27: Proteins without primaryIdentifier
    logger.info("[27] Proteins without primaryIdentifier")
    rows = run_query(service, 27, 'Protein',
        ['primaryAccession', 'primaryIdentifier', 'secondaryIdentifier', 'symbol'],
        [('primaryIdentifier', 'IS NULL', None)])
    if rows:
        count = save_to_removal_list(output_dir, 'protein', rows)
        logger.warning(f"[27] FAILED: {len(rows)} results, saved {count} to removal list")
        total_issues += len(rows)
    else:
        logger.info("[27] PASSED (0 results)")

    # Query 29: CDS with duplicate prefix
    logger.info("[29] CDS with duplicate CDS:CDS: prefix")
    rows = run_query(service, 29, 'CDS',
        ['primaryIdentifier', 'symbol'],
        [('primaryIdentifier', 'LIKE', 'CDS:CDS:*')])
    if rows:
        count = save_to_removal_list(output_dir, 'cds', rows)
        logger.warning(f"[29] FAILED: {len(rows)} results, saved {count} to removal list")
        total_issues += len(rows)
    else:
        logger.info("[29] PASSED (0 results)")

    # Query 30: C. elegans MRNA without gene
    logger.info("[30] C. elegans MRNA without gene")
    rows = run_query(service, 30, 'MRNA',
        ['primaryIdentifier', 'symbol'],
        [('organism.name', '=', 'Caenorhabditis elegans'), ('gene', 'IS NULL', None)])
    if rows:
        count = save_to_removal_list(output_dir, 'mrna', rows)
        logger.warning(f"[30] FAILED: {len(rows)} results, saved {count} to removal list")
        total_issues += len(rows)
    else:
        logger.info("[30] PASSED (0 results)")

    # Query 31: MRNA without organism
    logger.info("[31] MRNA without organism")
    rows = run_query(service, 31, 'MRNA',
        ['primaryIdentifier', 'symbol'],
        [('organism', 'IS NULL', None)])
    if rows:
        count = save_to_removal_list(output_dir, 'mrna', rows)
        logger.warning(f"[31] FAILED: {len(rows)} results, saved {count} to removal list")
        total_issues += len(rows)
    else:
        logger.info("[31] PASSED (0 results)")

    # Query 32: MRNA without CDSs
    logger.info("[32] MRNA without CDSs")
    rows = run_query(service, 32, 'MRNA',
        ['primaryIdentifier', 'symbol'],
        [('CDSs', 'IS NULL', None)])
    if rows:
        count = save_to_removal_list(output_dir, 'mrna', rows)
        logger.warning(f"[32] FAILED: {len(rows)} results, saved {count} to removal list")
        total_issues += len(rows)
    else:
        logger.info("[32] PASSED (0 results)")

    # Query 35: Organisms without name
    logger.info("[35] Organisms without name")
    rows = run_query(service, 35, 'Organism',
        ['name', 'taxonId'],
        [('name', 'IS NULL', None)])
    if rows:
        logger.warning(f"[35] FAILED: {len(rows)} results (organisms need manual review)")
        total_issues += len(rows)
    else:
        logger.info("[35] PASSED (0 results)")

    # Query 41: AnatomyTerm with CDATA
    logger.info("[41] AnatomyTerm with CDATA in definition")
    rows = run_query(service, 41, 'AnatomyTerm',
        ['primaryIdentifier', 'name', 'synonym', 'definition'],
        [('definition', 'CONTAINS', 'CDATA')])
    if rows:
        count = save_to_removal_list(output_dir, 'anatomyterm', rows)
        logger.warning(f"[41] FAILED: {len(rows)} results, saved {count} to removal list")
        total_issues += len(rows)
    else:
        logger.info("[41] PASSED (0 results)")

    logger.info("=" * 60)
    if total_issues > 0:
        logger.warning(f"Total issues found: {total_issues}")
        logger.info(f"Removal lists saved to: {output_dir}")
    else:
        logger.info("All queries passed!")

    return total_issues


def main():
    parser = argparse.ArgumentParser(
        description='Generate removal lists from WormMine testing queries',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )

    parser.add_argument(
        'url',
        help='WormMine URL (e.g., http://localhost:8080/wormmine)'
    )

    parser.add_argument(
        '--output-dir', '-o',
        default='./removal_lists',
        help='Output directory for removal lists (default: ./removal_lists)'
    )

    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose logging'
    )

    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    issues = run_all_queries(args.url, args.output_dir)
    sys.exit(0 if issues == 0 else 1)


if __name__ == '__main__':
    main()
