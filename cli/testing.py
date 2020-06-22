# Paulo Nuin June 2020

import testing_development
import settings
from intermine.webservice import Service


# def development():
#     print('Starting')
#     for x in dir(testing_development):
#         item = getattr(testing_development, x)
#         print(item)
#         if callable(item):
#             if not item.__name__ in ['assert_result', 'Service', 'assert_greater']:
#                 time.sleep(1)
#                 yield '%s<br/>\n' % item()

def development():

    service = Service("http://im-dev1.wormbase.org/tools/wormmine/service")
    settings.init()
    for x in dir(testing_development):
        item = getattr(testing_development, x)
        if callable(item):
            if not item.__name__ in ['assert_result', 'Service', 'assert_greater']:
                item(service)

    print(settings.to_check)

if __name__ == '__main__':


    development()