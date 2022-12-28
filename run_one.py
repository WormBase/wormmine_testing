
import sys

import testing_queries
from intermine.webservice import Service

service = Service('http://54.196.152.251/tools/wormmine/service')

def run_query(number):


    item = getattr(testing_queries, number)
    print(item)
    return item(service, True)


if __name__ == '__main__':

    number = "query_" + sys.argv[1]
    queries = dir(testing_queries)

    result = run_query(number)

    result