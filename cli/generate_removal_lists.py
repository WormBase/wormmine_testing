#!/usr/bin/env python3
"""
Generate removal lists for WormMine post-processing

Runs all 41 WormMine testing queries, compares results to expected values,
and outputs only failures (results that differ significantly from expected).

Usage:
    python generate_removal_lists.py <wormmine_url> [--output-dir <dir>]

Example:
    python generate_removal_lists.py http://localhost:8080/wormmine
    python generate_removal_lists.py https://intermine.wormbase.org/wormmine --output-dir /tmp/removal_lists
"""

import sys
import argparse
import logging
import json
from pathlib import Path
from urllib.request import urlopen, Request
from urllib.parse import urlencode
from urllib.error import URLError, HTTPError

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class InterMineClient:
    """Simple InterMine REST API client using only stdlib"""

    def __init__(self, base_url):
        self.base_url = base_url.rstrip('/')
        self.service_url = f"{self.base_url}/service"
        self.version = self._get_version()

    def _get_version(self):
        try:
            url = f"{self.service_url}/version"
            with urlopen(url, timeout=30) as response:
                return response.read().decode('utf-8').strip()
        except Exception:
            return "unknown"

    def query(self, xml_query):
        url = f"{self.service_url}/query/results"
        params = {'query': xml_query, 'format': 'json'}
        full_url = f"{url}?{urlencode(params)}"

        try:
            req = Request(full_url)
            req.add_header('Accept', 'application/json')
            with urlopen(req, timeout=120) as response:
                data = json.loads(response.read().decode('utf-8'))
                return data.get('results', [])
        except HTTPError as e:
            logger.error(f"HTTP Error {e.code}: {e.reason}")
            return None
        except URLError as e:
            logger.error(f"URL Error: {e.reason}")
            return None
        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error: {e}")
            return None


# All 41 queries with expected values
# check_type: "exact" = must equal expected, "min" = must be >= expected
QUERIES = [
    # Query 01: C. elegans genes with bad primaryIdentifier (expected 0)
    {
        "id": 1, "name": "gene_bad_primary_id", "model": "Gene",
        "description": "C. elegans genes with primaryIdentifier NOT LIKE WBGene*",
        "views": ["Gene.primaryIdentifier", "Gene.secondaryIdentifier", "Gene.symbol", "Gene.organism.name"],
        "constraints": [("Gene.organism.name", "=", "Caenorhabditis elegans"), ("Gene.primaryIdentifier", "NOT LIKE", "WBGene*")],
        "expected": 0, "check_type": "exact"
    },
    # Query 02: C. elegans genes without symbol (expected 0)
    {
        "id": 2, "name": "gene_no_symbol", "model": "Gene",
        "description": "C. elegans genes without symbol",
        "views": ["Gene.primaryIdentifier", "Gene.secondaryIdentifier", "Gene.symbol", "Gene.organism.name"],
        "constraints": [("Gene.organism.name", "=", "Caenorhabditis elegans"), ("Gene.symbol", "IS NULL", None)],
        "expected": 0, "check_type": "exact"
    },
    # Query 03: C. elegans genes without primaryIdentifier (expected 0)
    {
        "id": 3, "name": "gene_no_primary_id", "model": "Gene",
        "description": "C. elegans genes without primaryIdentifier",
        "views": ["Gene.primaryIdentifier", "Gene.secondaryIdentifier", "Gene.symbol", "Gene.organism.name"],
        "constraints": [("Gene.organism.name", "=", "Caenorhabditis elegans"), ("Gene.primaryIdentifier", "IS NULL", None)],
        "expected": 0, "check_type": "exact"
    },
    # Query 04: C. elegans transcripts without chromosome (expected 0)
    {
        "id": 4, "name": "transcript_no_chromosome", "model": "Transcript",
        "description": "C. elegans transcripts without chromosome",
        "views": ["Transcript.primaryIdentifier", "Transcript.symbol", "Transcript.organism.name"],
        "constraints": [("Transcript.organism.name", "=", "Caenorhabditis elegans"), ("Transcript.chromosome", "IS NULL", None)],
        "expected": 0, "check_type": "exact"
    },
    # Query 05: CDS 2L52.1a check (expected 1)
    {
        "id": 5, "name": "cds_2L52_check", "model": "CDS",
        "description": "CDS containing 2L52.1a (spot check)",
        "views": ["CDS.primaryIdentifier", "CDS.symbol"],
        "constraints": [("CDS.primaryIdentifier", "CONTAINS", "2L52.1a")],
        "expected": 1, "check_type": "exact"
    },
    # Query 06: Transcript B0207.4 check (expected 2)
    {
        "id": 6, "name": "transcript_B0207_check", "model": "Transcript",
        "description": "Transcript B0207.4 (spot check)",
        "views": ["Transcript.primaryIdentifier", "Transcript.symbol"],
        "constraints": [("Transcript.primaryIdentifier", "CONTAINS", "B0207.4"), ("Transcript.symbol", "CONTAINS", "B0207.4")],
        "logic": "A or B",
        "expected": 2, "check_type": "exact"
    },
    # Query 07: Allele WBVar01498288 check (expected 76)
    {
        "id": 7, "name": "allele_WBVar01498288_check", "model": "Allele",
        "description": "Allele WBVar01498288 (spot check)",
        "views": ["Allele.primaryIdentifier", "Allele.gene.primaryIdentifier", "Allele.gene.secondaryIdentifier"],
        "constraints": [("Allele.primaryIdentifier", "=", "WBVar01498288")],
        "expected": 76, "check_type": "exact"
    },
    # Query 08: Genes with WBGene in secondaryIdentifier (expected 0)
    {
        "id": 8, "name": "gene_wbgene_in_secondary", "model": "Gene",
        "description": "Genes with WBGene in secondaryIdentifier (data issue)",
        "views": ["Gene.primaryIdentifier", "Gene.secondaryIdentifier", "Gene.symbol"],
        "constraints": [("Gene.secondaryIdentifier", "CONTAINS", "WBGene")],
        "expected": 0, "check_type": "exact"
    },
    # Query 09: Genes with WBGene in symbol (expected 0)
    {
        "id": 9, "name": "gene_wbgene_in_symbol", "model": "Gene",
        "description": "Genes with WBGene in symbol (data issue)",
        "views": ["Gene.primaryIdentifier", "Gene.secondaryIdentifier", "Gene.symbol"],
        "constraints": [("Gene.symbol", "CONTAINS", "WBGene")],
        "expected": 0, "check_type": "exact"
    },
    # Query 10: Transcripts with bad primaryIdentifier (expected 0)
    {
        "id": 10, "name": "transcript_bad_primary_id", "model": "Transcript",
        "description": "Transcripts with primaryIdentifier NOT LIKE Transcript:*",
        "views": ["Transcript.primaryIdentifier", "Transcript.symbol"],
        "constraints": [("Transcript.primaryIdentifier", "NOT LIKE", "Transcript:*")],
        "expected": 0, "check_type": "exact"
    },
    # Query 11: CDS with bad primaryIdentifier (expected 0)
    {
        "id": 11, "name": "cds_bad_primary_id", "model": "CDS",
        "description": "CDS with primaryIdentifier NOT LIKE CDS:*",
        "views": ["CDS.primaryIdentifier", "CDS.symbol"],
        "constraints": [("CDS.primaryIdentifier", "NOT LIKE", "CDS:*")],
        "expected": 0, "check_type": "exact"
    },
    # Query 12: C. elegans genes with CDSs (min 19998)
    {
        "id": 12, "name": "gene_with_cds_check", "model": "Gene",
        "description": "C. elegans genes with CDSs (validation)",
        "views": ["Gene.primaryIdentifier", "Gene.secondaryIdentifier", "Gene.symbol"],
        "constraints": [("Gene.organism.name", "=", "Caenorhabditis elegans"), ("Gene.CDSs", "IS NOT NULL", None)],
        "expected": 19998, "check_type": "min"
    },
    # Query 13: CDS ZC416.4 sequence check - special handling
    {
        "id": 13, "name": "cds_ZC416_check", "model": "CDS",
        "description": "CDS ZC416.4 sequence length >= 999",
        "views": ["CDS.primaryIdentifier", "CDS.symbol", "CDS.sequence.length"],
        "constraints": [("CDS.symbol", "=", "ZC416.4")],
        "expected": 999, "check_type": "length_check"
    },
    # Query 14: C. elegans genes with length (min 46500)
    {
        "id": 14, "name": "gene_with_length_check", "model": "Gene",
        "description": "C. elegans genes with length (validation)",
        "views": ["Gene.primaryIdentifier", "Gene.secondaryIdentifier", "Gene.symbol", "Gene.length"],
        "constraints": [("Gene.organism.name", "=", "Caenorhabditis elegans"), ("Gene.length", "IS NOT NULL", None)],
        "expected": 46500, "check_type": "min"
    },
    # Query 15: Genes without organism (expected 0)
    {
        "id": 15, "name": "gene_no_organism", "model": "Gene",
        "description": "Genes without organism",
        "views": ["Gene.primaryIdentifier", "Gene.secondaryIdentifier", "Gene.symbol"],
        "constraints": [("Gene.organism", "IS NULL", None)],
        "expected": 0, "check_type": "exact"
    },
    # Query 16: C. elegans CDS without gene (expected 0)
    {
        "id": 16, "name": "cds_no_gene", "model": "CDS",
        "description": "C. elegans CDS without gene",
        "views": ["CDS.primaryIdentifier", "CDS.symbol"],
        "constraints": [("CDS.organism.name", "=", "Caenorhabditis elegans"), ("CDS.gene", "IS NULL", None)],
        "expected": 0, "check_type": "exact"
    },
    # Query 17: C. elegans transcripts without gene (expected 0)
    {
        "id": 17, "name": "transcript_no_gene", "model": "Transcript",
        "description": "C. elegans transcripts without gene",
        "views": ["Transcript.primaryIdentifier", "Transcript.symbol"],
        "constraints": [("Transcript.organism.name", "=", "Caenorhabditis elegans"), ("Transcript.gene", "IS NULL", None)],
        "expected": 0, "check_type": "exact"
    },
    # Query 18: C. elegans CDS without protein (expected 0)
    {
        "id": 18, "name": "cds_no_protein", "model": "CDS",
        "description": "C. elegans CDS without protein",
        "views": ["CDS.primaryIdentifier", "CDS.symbol"],
        "constraints": [("CDS.organism.name", "=", "Caenorhabditis elegans"), ("CDS.protein", "IS NULL", None)],
        "expected": 0, "check_type": "exact"
    },
    # Query 19: C. elegans CDS without transcripts (expected 0)
    {
        "id": 19, "name": "cds_no_transcripts", "model": "CDS",
        "description": "C. elegans CDS without transcripts",
        "views": ["CDS.primaryIdentifier", "CDS.symbol"],
        "constraints": [("CDS.organism.name", "=", "Caenorhabditis elegans"), ("CDS.transcripts", "IS NULL", None)],
        "expected": 0, "check_type": "exact"
    },
    # Query 20: C. elegans transcripts with CDSs (min 38000)
    {
        "id": 20, "name": "transcript_with_cds_check", "model": "Transcript",
        "description": "C. elegans transcripts with CDSs (validation)",
        "views": ["Transcript.primaryIdentifier", "Transcript.symbol"],
        "constraints": [("Transcript.CDSs", "IS NOT NULL", None), ("Transcript.organism.name", "=", "Caenorhabditis elegans")],
        "expected": 38000, "check_type": "min"
    },
    # Query 21: C. elegans proteins with bad primaryAccession (expected 0)
    {
        "id": 21, "name": "protein_bad_accession", "model": "Protein",
        "description": "C. elegans proteins with primaryAccession NOT LIKE CE*",
        "views": ["Protein.primaryAccession", "Protein.primaryIdentifier", "Protein.secondaryIdentifier", "Protein.symbol"],
        "constraints": [("Protein.organism.name", "=", "Caenorhabditis elegans"), ("Protein.primaryAccession", "NOT LIKE", "CE*")],
        "expected": 0, "check_type": "exact"
    },
    # Query 22: C. elegans proteins with bad primaryIdentifier (expected 0)
    {
        "id": 22, "name": "protein_bad_primary_id", "model": "Protein",
        "description": "C. elegans proteins with primaryIdentifier NOT LIKE CE*",
        "views": ["Protein.primaryAccession", "Protein.primaryIdentifier", "Protein.secondaryIdentifier", "Protein.symbol"],
        "constraints": [("Protein.organism.name", "=", "Caenorhabditis elegans"), ("Protein.primaryIdentifier", "NOT LIKE", "CE*")],
        "expected": 0, "check_type": "exact"
    },
    # Query 23: C. elegans proteins without CDSs (expected 0)
    {
        "id": 23, "name": "protein_no_cds", "model": "Protein",
        "description": "C. elegans proteins without CDSs",
        "views": ["Protein.primaryAccession", "Protein.primaryIdentifier", "Protein.secondaryIdentifier", "Protein.symbol"],
        "constraints": [("Protein.organism.name", "=", "Caenorhabditis elegans"), ("Protein.CDSs", "IS NULL", None)],
        "expected": 0, "check_type": "exact"
    },
    # Query 24: C. elegans proteins without sequence (expected 0)
    {
        "id": 24, "name": "protein_no_sequence", "model": "Protein",
        "description": "C. elegans proteins without sequence",
        "views": ["Protein.primaryAccession", "Protein.primaryIdentifier", "Protein.secondaryIdentifier", "Protein.symbol"],
        "constraints": [("Protein.organism.name", "=", "Caenorhabditis elegans"), ("Protein.sequence", "IS NULL", None)],
        "expected": 0, "check_type": "exact"
    },
    # Query 25: CDS without organism (expected 0)
    {
        "id": 25, "name": "cds_no_organism", "model": "CDS",
        "description": "CDS without organism",
        "views": ["CDS.primaryIdentifier", "CDS.symbol"],
        "constraints": [("CDS.organism", "IS NULL", None)],
        "expected": 0, "check_type": "exact"
    },
    # Query 26: Transcripts without organism (expected 0)
    {
        "id": 26, "name": "transcript_no_organism", "model": "Transcript",
        "description": "Transcripts without organism",
        "views": ["Transcript.primaryIdentifier", "Transcript.symbol"],
        "constraints": [("Transcript.organism", "IS NULL", None)],
        "expected": 0, "check_type": "exact"
    },
    # Query 27: Proteins without primaryIdentifier (expected 0)
    {
        "id": 27, "name": "protein_no_primary_id", "model": "Protein",
        "description": "Proteins without primaryIdentifier",
        "views": ["Protein.primaryAccession", "Protein.primaryIdentifier", "Protein.secondaryIdentifier", "Protein.symbol"],
        "constraints": [("Protein.primaryIdentifier", "IS NULL", None)],
        "expected": 0, "check_type": "exact"
    },
    # Query 28: Allele e1370 check (expected 1)
    {
        "id": 28, "name": "allele_e1370_check", "model": "Allele",
        "description": "Allele e1370 (spot check)",
        "views": ["Allele.primaryIdentifier", "Allele.symbol"],
        "constraints": [("Allele.symbol", "=", "e1370")],
        "expected": 1, "check_type": "exact"
    },
    # Query 29: CDS with duplicate prefix (expected 0)
    {
        "id": 29, "name": "cds_duplicate_prefix", "model": "CDS",
        "description": "CDS with duplicate CDS:CDS: prefix",
        "views": ["CDS.primaryIdentifier", "CDS.symbol"],
        "constraints": [("CDS.primaryIdentifier", "LIKE", "CDS:CDS:*")],
        "expected": 0, "check_type": "exact"
    },
    # Query 30: C. elegans MRNA without gene (expected 0)
    {
        "id": 30, "name": "mrna_no_gene", "model": "MRNA",
        "description": "C. elegans MRNA without gene",
        "views": ["MRNA.primaryIdentifier", "MRNA.symbol"],
        "constraints": [("MRNA.organism.name", "=", "Caenorhabditis elegans"), ("MRNA.gene", "IS NULL", None)],
        "expected": 0, "check_type": "exact"
    },
    # Query 31: MRNA without organism (expected 0)
    {
        "id": 31, "name": "mrna_no_organism", "model": "MRNA",
        "description": "MRNA without organism",
        "views": ["MRNA.primaryIdentifier", "MRNA.symbol"],
        "constraints": [("MRNA.organism", "IS NULL", None)],
        "expected": 0, "check_type": "exact"
    },
    # Query 32: MRNA without CDSs (expected 0)
    {
        "id": 32, "name": "mrna_no_cds", "model": "MRNA",
        "description": "MRNA without CDSs",
        "views": ["MRNA.primaryIdentifier", "MRNA.symbol"],
        "constraints": [("MRNA.CDSs", "IS NULL", None)],
        "expected": 0, "check_type": "exact"
    },
    # Query 33: Protein CE46852 CDS check (expected 1)
    {
        "id": 33, "name": "protein_CE46852_check", "model": "Protein",
        "description": "Protein CE46852 CDS (spot check)",
        "views": ["Protein.primaryIdentifier", "Protein.CDSs.primaryIdentifier", "Protein.CDSs.symbol"],
        "constraints": [("Protein.primaryIdentifier", "=", "CE46852")],
        "expected": 1, "check_type": "exact"
    },
    # Query 34: CDS for protein CE46852 check (expected 1)
    {
        "id": 34, "name": "cds_CE46852_check", "model": "CDS",
        "description": "CDS for protein CE46852 (spot check)",
        "views": ["CDS.primaryIdentifier", "CDS.symbol", "CDS.protein.primaryIdentifier"],
        "constraints": [("CDS.protein.primaryIdentifier", "=", "CE46852")],
        "expected": 1, "check_type": "exact"
    },
    # Query 35: Organisms without name (expected 0)
    {
        "id": 35, "name": "organism_no_name", "model": "Organism",
        "description": "Organisms without name",
        "views": ["Organism.name", "Organism.taxonId"],
        "constraints": [("Organism.name", "IS NULL", None)],
        "expected": 0, "check_type": "exact"
    },
    # Query 36: List organisms (info only, no expected)
    {
        "id": 36, "name": "organism_list", "model": "Organism",
        "description": "List all organisms (info only)",
        "views": ["Organism.name", "Organism.taxonId"],
        "constraints": [],
        "expected": None, "check_type": "info"
    },
    # Query 37: C. elegans chromosomes (info only)
    {
        "id": 37, "name": "chromosome_list", "model": "Chromosome",
        "description": "List C. elegans chromosomes (info only)",
        "views": ["Chromosome.primaryIdentifier", "Chromosome.organism.name"],
        "constraints": [("Chromosome.organism.name", "=", "Caenorhabditis elegans")],
        "expected": None, "check_type": "info"
    },
    # Query 38: Allele WBVar00143949 phenotypes (expected 85)
    {
        "id": 38, "name": "allele_phenotype_check", "model": "Allele",
        "description": "Allele WBVar00143949 phenotypes (spot check)",
        "views": ["Allele.primaryIdentifier", "Allele.symbol", "Allele.phenotype.identifier", "Allele.phenotype.name"],
        "constraints": [("Allele.primaryIdentifier", "=", "WBVar00143949")],
        "expected": 85, "check_type": "exact"
    },
    # Query 39: ExpressionPattern Expr3417 genes (expected 47)
    {
        "id": 39, "name": "expression_pattern_check", "model": "ExpressionPattern",
        "description": "ExpressionPattern Expr3417 genes (spot check)",
        "views": ["ExpressionPattern.primaryIdentifier", "ExpressionPattern.genes.primaryIdentifier", "ExpressionPattern.genes.secondaryIdentifier", "ExpressionPattern.genes.symbol"],
        "constraints": [("ExpressionPattern.primaryIdentifier", "=", "Expr3417")],
        "expected": 47, "check_type": "exact"
    },
    # Query 40: Gene cdk-4 allele check (expected 1)
    {
        "id": 40, "name": "gene_allele_check", "model": "Gene",
        "description": "Gene cdk-4 allele WBVar02146689 (spot check)",
        "views": ["Gene.primaryIdentifier", "Gene.secondaryIdentifier", "Gene.symbol", "Gene.allele.primaryIdentifier", "Gene.allele.symbol"],
        "constraints": [("Gene.symbol", "=", "cdk-4"), ("Gene.allele.primaryIdentifier", "=", "WBVar02146689")],
        "expected": 1, "check_type": "exact"
    },
    # Query 41: AnatomyTerm with CDATA in definition (expected 0)
    {
        "id": 41, "name": "anatomy_term_cdata", "model": "AnatomyTerm",
        "description": "AnatomyTerm with CDATA in definition",
        "views": ["AnatomyTerm.primaryIdentifier", "AnatomyTerm.name", "AnatomyTerm.synonym", "AnatomyTerm.definition"],
        "constraints": [("AnatomyTerm.definition", "CONTAINS", "CDATA")],
        "expected": 0, "check_type": "exact"
    },
]


def build_query(query_def):
    """Build PathQuery XML from query definition"""
    views = " ".join(query_def["views"])
    constraint_xml = ""

    for i, constraint in enumerate(query_def["constraints"]):
        code = chr(65 + i)
        path, op, value = constraint
        if value is None:
            constraint_xml += f'  <constraint path="{path}" op="{op}" code="{code}"/>\n'
        else:
            constraint_xml += f'  <constraint path="{path}" op="{op}" value="{value}" code="{code}"/>\n'

    # Handle constraint logic (e.g., "A or B")
    logic = query_def.get("logic", "")
    logic_attr = f' constraintLogic="{logic}"' if logic else ""

    return f'''<query model="genomic" view="{views}" sortOrder="{query_def["views"][0]} ASC"{logic_attr}>
{constraint_xml}</query>'''


def check_result(query_def, count, rows):
    """Check if result matches expected value. Returns (passed, message)"""
    expected = query_def["expected"]
    check_type = query_def["check_type"]

    if check_type == "info":
        return True, f"Info: {count} rows"

    if check_type == "exact":
        if count == expected:
            return True, f"PASSED ({count})"
        else:
            return False, f"FAILED: expected {expected}, got {count}"

    if check_type == "min":
        if count >= expected:
            return True, f"PASSED ({count} >= {expected})"
        else:
            return False, f"FAILED: expected >= {expected}, got {count}"

    if check_type == "length_check":
        # Special check for sequence length
        if rows and len(rows) > 0:
            length = rows[0][2] if isinstance(rows[0], list) else rows[0].get('length', 0)
            if length and length >= expected:
                return True, f"PASSED (length={length})"
            else:
                return False, f"FAILED: expected length >= {expected}, got {length}"
        return False, f"FAILED: no results"

    return False, f"Unknown check type: {check_type}"


def run_query(client, query_def, output_dir, save_failures=True):
    """Run a single query and check result"""
    qid = query_def['id']
    logger.info(f"[{qid:02d}] {query_def['description']}...")

    xml = build_query(query_def)
    rows = client.query(xml)

    if rows is None:
        logger.error(f"[{qid:02d}] Query failed")
        return False, 0

    count = len(rows)
    passed, message = check_result(query_def, count, rows)

    if passed:
        logger.info(f"[{qid:02d}] {message}")
    else:
        logger.warning(f"[{qid:02d}] {message}")

        # Save failures to file if we have unexpected results for "exact 0" checks
        # Use to_remove_<model>.txt format for post_processing compatibility
        if save_failures and query_def["check_type"] == "exact" and query_def["expected"] == 0 and count > 0:
            model = query_def["model"].lower()
            output_file = output_dir / f"to_remove_{model}.txt"

            # Read existing items if file exists
            existing = set()
            if output_file.exists():
                existing = set(output_file.read_text().strip().split('\n'))

            # Add new unique items
            new_items = set()
            for row in rows:
                identifier = row[0] if isinstance(row, list) else str(row)
                if identifier and identifier not in existing:
                    new_items.add(identifier)

            # Append only unique new items
            if new_items:
                with open(output_file, 'a') as f:
                    for identifier in sorted(new_items):
                        f.write(f"{identifier}\n")

            logger.warning(f"[{qid:02d}] Added {len(new_items)} unique items to {output_file.name} ({count - len(new_items)} duplicates skipped)")

    return passed, count


def run_all_checks(service_url, output_dir, query_ids=None):
    """Run all data quality checks"""
    logger.info(f"Connecting to WormMine at {service_url}")

    try:
        client = InterMineClient(service_url)
        logger.info(f"Connected to WormMine version {client.version}")
    except Exception as e:
        logger.error(f"Failed to connect to WormMine: {e}")
        sys.exit(1)

    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    logger.info(f"Output directory: {output_dir}")

    # Clear existing to_remove_*.txt files
    for f in output_dir.glob("to_remove_*.txt"):
        f.unlink()
        logger.debug(f"Removed old file: {f.name}")

    queries_to_run = QUERIES
    if query_ids:
        queries_to_run = [q for q in QUERIES if q['id'] in query_ids]

    logger.info(f"Running {len(queries_to_run)} queries...")
    logger.info("=" * 60)

    passed_count = 0
    failed_count = 0
    failures = []

    for query_def in queries_to_run:
        try:
            passed, count = run_query(client, query_def, output_dir)
            if passed:
                passed_count += 1
            else:
                failed_count += 1
                failures.append((query_def['id'], query_def['name'], query_def['description']))
        except Exception as e:
            logger.error(f"[{query_def['id']:02d}] Error: {e}")
            failed_count += 1
            failures.append((query_def['id'], query_def['name'], str(e)))

    logger.info("=" * 60)
    logger.info(f"Results: {passed_count} passed, {failed_count} failed")

    if failures:
        logger.warning("Failed queries:")
        for qid, name, desc in failures:
            logger.warning(f"  [{qid:02d}] {name}: {desc}")
        logger.info(f"Removal lists saved to: {output_dir}")

    return failed_count


def main():
    parser = argparse.ArgumentParser(
        description='Run WormMine testing queries and generate removal lists for failures',
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

    parser.add_argument(
        '--query', '-q',
        type=int,
        action='append',
        help='Run only specific query by ID (can be repeated, e.g., -q 1 -q 15)'
    )

    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    failures = run_all_checks(args.url, args.output_dir, args.query)
    sys.exit(0 if failures == 0 else 1)


if __name__ == '__main__':
    main()
