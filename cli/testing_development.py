import settings
import logging
import coloredlogs

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
coloredlogs.install(level='DEBUG')

logging.getLogger('intermine').setLevel(logging.INFO)
logging.getLogger('JSONIterator').setLevel(logging.INFO)
logging.getLogger('Model').setLevel(logging.INFO)

def assert_result(query_number, number_of_rows, expected_result):

    try:
        assert len(number_of_rows) == expected_result
        logger.info('Query #' + query_number + ' PASSED. Returned ' + str(len(number_of_rows)))
    except Exception as e:
        settings.to_check.append('query_' + str(query_number))
        logger.warning('Query #' + query_number + ' FAILED. Expected ' + str(expected_result) + ' returned ' + str(len(number_of_rows)))


def assert_greater(query_number, number_of_rows, minimum):

    try:
        assert len(number_of_rows) >= minimum
        logger.info('Query #' + query_number + ' PASSED. Returned ' + str(len(number_of_rows)))
    except Exception as e:
        settings.to_check.append('query_' + str(query_number))
        logger.warning('Query #' + query_number + ' FAILED. Expected ' + str(minimum) + ' returned ' + str(len(number_of_rows)))


def query_01(service):

    query = service.new_query("Gene")
    query.add_view("primaryIdentifier", "secondaryIdentifier", "symbol", "organism.name")
    query.add_constraint("organism.name", "=", "Caenorhabditis elegans", code="A")
    query.add_constraint("primaryIdentifier", "NOT LIKE", "WBGene*", code="B")
    return assert_result('01', query.rows(), 0)


def query_02(service):

    query = service.new_query("Gene")
    query.add_view("primaryIdentifier", "secondaryIdentifier", "symbol", "organism.name")
    query.add_constraint("organism.name", "=", "Caenorhabditis elegans", code="A")
    query.add_constraint("symbol", "IS NULL", code="B")
    return assert_result('02', query.rows(), 0)


def query_03(service):

    query = service.new_query("Gene")
    query.add_view("primaryIdentifier", "secondaryIdentifier", "symbol", "organism.name")
    query.add_constraint("organism.name", "=", "Caenorhabditis elegans", code="A")
    query.add_constraint("primaryIdentifier", "IS NULL", code="B")
    return assert_result('03', query.rows(), 0)


def query_04(service):

    query = service.new_query("Transcript")
    query.add_view("primaryIdentifier", "symbol", "organism.name")
    query.add_constraint("organism.name", "=", "Caenorhabditis elegans", code="A")
    query.add_constraint("chromosome", "IS NULL", code="B")
    return assert_result('04', query.rows(), 0)


def query_05(service):

    query = service.new_query("CDS")
    query.add_view("primaryIdentifier", "symbol")
    query.add_constraint("primaryIdentifier", "CONTAINS", "2L52.1a", code="A")
    return assert_result('05', query.rows(), 1)


def query_06(service):

    query = service.new_query("Transcript")
    query.add_view("primaryIdentifier", "symbol")
    query.add_constraint("primaryIdentifier", "CONTAINS", "B0207.4", code="B")
    query.add_constraint("symbol", "CONTAINS", "B0207.4", code="A")
    query.set_logic("A or B")
    return assert_result('06', query.rows(), 2)


def query_07(service):

    query = service.new_query("Allele")
    query.add_view("primaryIdentifier", "gene.primaryIdentifier", "gene.secondaryIdentifier")
    query.add_constraint("primaryIdentifier", "=", "WBVar01498288", code="A")
    return assert_result('07', query.rows(), 75)


def query_08(service):

    query = service.new_query("Gene")
    query.add_view("primaryIdentifier", "secondaryIdentifier", "symbol")
    query.add_constraint("secondaryIdentifier", "CONTAINS", "WBGene", code="A")
    return assert_result('08', query.rows(), 0)


def query_09(service):

    query = service.new_query("Gene")
    query.add_view("primaryIdentifier", "secondaryIdentifier", "symbol")
    query.add_constraint("symbol", "CONTAINS", "WBGene", code="A")
    return assert_result('09', query.rows(), 0)


def query_10(service):

    query = service.new_query("Transcript")
    query.add_view("primaryIdentifier", "symbol")
    query.add_constraint("primaryIdentifier", "NOT LIKE", "Transcript:*", code="A")
    return assert_result('10', query.rows(), 0)


def query_11(service):

    query = service.new_query("CDS")
    query.add_view("primaryIdentifier", "symbol")
    query.add_constraint("primaryIdentifier", "NOT LIKE", "CDS:*", code="A")
    return assert_result('11', query.rows(), 0)


def query_12(service):

    query = service.new_query("Gene")
    query.add_view("primaryIdentifier", "secondaryIdentifier", "symbol")
    query.add_constraint("organism.name", "=", "Caenorhabditis elegans", code="A")
    query.add_constraint("CDSs", "IS NOT NULL", code="B")
    return assert_greater('12', query.rows(), 20000)


def query_13(service):

    query = service.new_query("CDS")
    query.add_view("primaryIdentifier", "symbol", "sequence.length")
    query.add_constraint("symbol", "=", "ZC416.4", code="A")

    for row in query.rows():
        try:
            assert (row['length'] >= 999)
            return 'Query #13' + ' PASSED. Returned ' + str(row['length'])
        except:
            return 'Query #13' + ' FAILED. Returned ' + str(row['length'])


def query_14(service):

    query = service.new_query("Gene")
    query.add_view("primaryIdentifier", "secondaryIdentifier", "symbol", "length")
    query.add_constraint("organism.name", "=", "Caenorhabditis elegans", code="A")
    query.add_constraint("length", "IS NOT NULL", code="B")
    return assert_greater('14', query.rows(), 46500)


def query_15(service):

    query = service.new_query("Gene")
    query.add_view("primaryIdentifier", "secondaryIdentifier", "symbol")
    query.add_constraint("organism", "IS NULL", code="A")
    return assert_result('15', query.rows(), 0)


def query_16(service):

    query = service.new_query("CDS")
    query.add_view("primaryIdentifier", "symbol")
    query.add_constraint("organism.name", "=", "Caenorhabditis elegans", code="A")
    query.add_constraint("gene", "IS NULL", code="B")
    return assert_result('16', query.rows(), 0)


def query_17(service):

    query = service.new_query("Transcript")
    query.add_view("primaryIdentifier", "symbol")
    query.add_constraint("organism.name", "=", "Caenorhabditis elegans", code="A")
    query.add_constraint("gene", "IS NULL", code="B")
    return assert_result('17', query.rows(), 0)


def query_18(service):

    query = service.new_query("CDS")
    query.add_view("primaryIdentifier", "symbol")
    query.add_constraint("organism.name", "=", "Caenorhabditis elegans", code="A")
    query.add_constraint("protein", "IS NULL", code="B")
    return  assert_result('18', query.rows(), 0)


def query_19(service):

    query = service.new_query("CDS")
    query.add_view("primaryIdentifier", "symbol")
    query.add_constraint("organism.name", "=", "Caenorhabditis elegans", code="A")
    query.add_constraint("transcripts", "IS NULL", code="B")
    return assert_result('19', query.rows(), 0)


def query_20(service):

    query = service.new_query("Transcript")
    query.add_view("primaryIdentifier", "symbol")
    query.add_constraint("CDSs", "IS NOT NULL", code="A")
    query.add_constraint("organism.name", "=", "Caenorhabditis elegans", code="B")
    return assert_greater('20', query.rows(), 43000)


def query_21(service):

    query = service.new_query("Protein")
    query.add_view("primaryAccession", "primaryIdentifier", "secondaryIdentifier", "symbol")
    query.add_constraint("organism.name", "=", "Caenorhabditis elegans", code="A")
    query.add_constraint("primaryAccession", "NOT LIKE", "CE*", code="B")
    return assert_result('21', query.rows(), 0)


def query_22(service):

    query = service.new_query("Protein")
    query.add_view("primaryAccession", "primaryIdentifier", "secondaryIdentifier", "symbol")
    query.add_constraint("organism.name", "=", "Caenorhabditis elegans", code="A")
    query.add_constraint("primaryIdentifier", "NOT LIKE", "CE*", code="B")
    return assert_result('22', query.rows(), 0)


def query_23(service):

    query = service.new_query("Protein")
    query.add_view("primaryAccession", "primaryIdentifier", "secondaryIdentifier", "symbol")
    query.add_constraint("organism.name", "=", "Caenorhabditis elegans", code="A")
    query.add_constraint("CDSs", "IS NULL", code="B")
    return assert_result('23', query.rows(), 0)


def query_24(service):

    query = service.new_query("Protein")
    query.add_view("primaryAccession", "primaryIdentifier", "secondaryIdentifier", "symbol")
    query.add_constraint("organism.name", "=", "Caenorhabditis elegans", code="A")
    query.add_constraint("sequence", "IS NULL", code="B")
    return assert_result('24', query.rows(), 0)


def query_25(service):

    query = service.new_query("CDS")
    query.add_view("primaryIdentifier", "symbol")
    query.add_constraint("organism", "IS NULL", code="A")
    return assert_result('25', query.rows(), 0)


def query_26(service):

    query = service.new_query("Transcript")
    query.add_view("primaryIdentifier", "symbol")
    query.add_constraint("organism", "IS NULL", code="A")
    return assert_result('26', query.rows(), 0)


def query_27(service):

    query = service.new_query("Protein")
    query.add_view("primaryAccession", "primaryIdentifier", "secondaryIdentifier", "symbol")
    query.add_sort_order("Protein.primaryIdentifier", "ASC")
    query.add_constraint("primaryIdentifier", "IS NULL", code="A")
    return assert_result('27', query.rows(), 0)


def query_28(service):

    query = service.new_query("Allele")
    query.add_view("primaryIdentifier", "symbol")
    query.add_constraint("symbol", "=", "e1370", code="A")
    return assert_result('28', query.rows(), 1)


def query_29(service):

    query = service.new_query("CDS")
    query.add_view("primaryIdentifier", "symbol")
    query.add_constraint("primaryIdentifier", "LIKE", "CDS:CDS:*", code="A")
    return assert_result('29', query.rows(), 0)


def query_30(service):

    query = service.new_query("MRNA")
    query.add_view("primaryIdentifier", "symbol")
    query.add_constraint("organism.name", "=", "Caenorhabditis elegans", code="A")
    query.add_constraint("gene", "IS NULL", code="B")
    return assert_result('30', query.rows(), 0)


def query_31(service):

    query = service.new_query("MRNA")
    query.add_view("primaryIdentifier", "symbol")
    query.add_constraint("organism", "IS NULL", code="A")
    return assert_result('31', query.rows(), 0)


def query_32(service):

    query = service.new_query("MRNA")
    query.add_view("primaryIdentifier", "symbol")
    query.add_constraint("CDSs", "IS NULL", code="A")
    return assert_result('32', query.rows(), 0)


def query_33(service):

    query = service.new_query("Protein")
    query.add_view("primaryIdentifier", "CDSs.primaryIdentifier", "CDSs.symbol")
    query.add_constraint("primaryIdentifier", "=", "CE46852", code="A")
    return assert_result('33', query.rows(), 1)


def query_34(service):

    query = service.new_query("CDS")
    query.add_view("primaryIdentifier", "symbol", "protein.primaryIdentifier")
    query.add_constraint("protein.primaryIdentifier", "=", "CE46852", code="A")
    return assert_result('34', query.rows(), 1)


def query_35(service):

    query = service.new_query("Organism")
    query.add_view("name", "taxonId")
    query.add_constraint("name", "IS NULL", code="A")
    return assert_result('35', query.rows(), 0)


def query_36(service):

    query = service.new_query("Organism")
    query.add_view("name", "taxonId")
    print('Query #36')
    result = {}
    for row in query.rows():
       result[row["name"]] = row["taxonId"]

    for i in result:
       print('\t' + i + '\t' + str(result[i]))


def query_37(service):

    query = service.new_query("Chromosome")
    query.add_view("primaryIdentifier", "organism.name")
    query.add_constraint("organism.name", "=", "Caenorhabditis elegans", code="A")
    print('Query #37')

    result = {}
    for row in query.rows():
       result[row["primaryIdentifier"]] = row["organism.name"]

    for i in result:
       try:
           print('\t' + i + '\t' + str(result[i]))
       except:
           print('\t' + i)


def query_38(service):

    query = service.new_query("Allele")
    query.add_view("primaryIdentifier", "symbol", "phenotype.identifier", "phenotype.name")
    query.add_constraint("primaryIdentifier", "=", "WBVar00143949", code="A")
    return assert_result('38', query.rows(), 84)


def query_39(service):

    query = service.new_query("ExpressionPattern")
    query.add_view("primaryIdentifier", "genes.primaryIdentifier", "genes.secondaryIdentifier", "genes.symbol")
    query.add_constraint("primaryIdentifier", "=", "Expr3417", code="A")
    return assert_result('39', query.rows(), 47)


def query_40(service):

    query = service.new_query("Gene")
    query.add_view("primaryIdentifier", "secondaryIdentifier", "symbol","allele.primaryIdentifier", "allele.symbol")
    query.add_constraint("symbol", "=", "cdk-4", code="A")
    query.add_constraint("allele.primaryIdentifier", "=", "WBVar02146689", code="B")
    return assert_result('40', query.rows(), 1)


def query_41(service):
    query = service.new_query("AnatomyTerm")
    query.add_view("primaryIdentifier", "name", "synonym", "definition")
    query.add_constraint("definition", "CONTAINS", "CDATA", code="A")
    return assert_result('41', query.rows(), 0)


    # print('\nTesting complete')
    # print('These queries need to be checked: {0}'.format(', '.join(to_check)))


if __name__ == '__main__':

    service = Service("http://im-dev1.wormbase.org/tools/wormmine/service")
    run_queries()
