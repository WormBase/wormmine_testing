# Paulo Nuin June 2020

import logging
import click
import testing_queries
import settings
from intermine.webservice import Service
import coloredlogs

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
coloredlogs.install(level='DEBUG')
logging.getLogger("intermine").setLevel(logging.INFO)

@click.command()
@click.option('--host', type=click.Choice(['dev', 'production']),  help='set host (production, dev) for testing')
def development(host):

    if host == 'dev':
        service = Service('http://im-dev1.wormbase.org/tools/wormmine/service')
    else:
        service = Service('http://intermine.wormbase.org/tools/wormmine/service')
    logger.info('Testing ' + str(service))
    settings.init()
    for x in dir(testing_queries):
        item = getattr(testing_queries, x)
        if callable(item):
            if item.__name__ not in ['assert_result', 'Service', 'assert_greater', 'save_txt_file']:
                item(service)

    # test = [('query_01', 'Gene'), ('query_02', 'Gene')]
    logger.info(str(len(settings.to_check)) + ' query(ies) failed')
    for query in settings.to_check:
        logger.warning(query[0] + ' ' + query[1])
        item = getattr(testing_development, query[0])
        item(service, True)


if __name__ == '__main__':

    development()
