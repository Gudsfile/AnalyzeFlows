__author__ = "Gudsfile and Wigow "

##########################
# Import                 #
##########################

# python libs
import argparse
import json
import logging
import logging.config
from os import path, listdir

# local libs
import script_elasticsearch as es
from script_graph import create_graph_log
from script_parse import parse_xml_to_dict, get_data_from_shelve_file, set_shelve_file
from script_print import RED, GREEN, YELLOW, BLUE, PURPLE, CYAN, RAZ, pretty_dict

##########################
# Log config             #
##########################

LOGGING_CONFIG = { 
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': { 
        'standard': { 
            'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
        },
    },
    'handlers': { 
        'console': { 
            'level': 'INFO',
            'formatter': 'standard',
            'class': 'logging.StreamHandler',
            'stream': 'ext://sys.stdout',
        },
        'file': { 
            'level': 'DEBUG',
            'formatter': 'standard',
            'class': 'logging.FileHandler',
            'filename': 'logs/analyze_flows.log',
            'mode': 'w'
        },
    },
    'loggers': { 
        '': {
            'handlers': ['console', 'file'],
            'level': 'DEBUG',
            'propagate': False
        }
    } 
}
logging.config.dictConfig(LOGGING_CONFIG)


##########################
# Args config            #
##########################

parser = argparse.ArgumentParser(description='AnalyzeFlows is a school projet.'
                                             ' It allows you to analyze your f'
                                             'lows from files, shelve or elast'
                                             'icsearch.')
parser_group = parser.add_mutually_exclusive_group(required=True)
parser_group.add_argument(
    "-f", "--file",
    help="xml file to parse",
    type=str,
    dest='file',
    action='store'
)
parser_group.add_argument(
    "-d", "--directory",
    help="directory of xml files to parse",
    type=str,
    dest='folder',
    action='store'
)
parser_group.add_argument(
    "-s", "--shelve",
    help="shelve file",
    type=str,
    dest='shelve',
    action='store'
)
parser_group.add_argument(
    "-e", "--elasticsearch",
    help="open data with elasticsearch",
    dest='elasticsearch',
    action='store_true',
    required=False
)
parser.add_argument(
    "--save-shelve",
    help="name of the shelve file to save data",
    type=str,
    dest='save_shelve',
    action='store',
    required=False
)
parser.add_argument(
    "--save-elastic",
    help="save data with elasticsearch",
    dest='save_elastic',
    action='store_true',
    required=False
)
parser.add_argument(
    "--config-elastic",
    help="config of elasticsearch (ex: \'{\"index\":\"my_index\"}\')",
    type=str,
    dest='config_elastic',
    action='store',
    required=False
)
parser.add_argument(
    "--prune-elastic",
    help="prune the elastic index used before process",
    dest='prune_elastic',
    action='store_true',
    required=False
)
parser.add_argument(
    "--test",
    help="start test process",
    dest='test_start',
    action='store_true',
    required=False
)


##########################
# Functions              #
##########################

def get_files_list(folder_path: str):
    """
    Get the list of xml files in the given folder.

    :param folder_path:
    :return:
    """
    res = list()
    for file_name in listdir(folder_path):
        if not file_name.endswith('.xml'):
            continue
        res.append(path.join(folder_path, file_name))
    return res


##########################
# Tests                  #
##########################

def test1(flows):
    """

    :param flows:
    :return:
    """
    import script_analyze as sa

    print(f'{GREEN}Protocol names:{RAZ}')
    print(sa.get_protocol_names(flows))
    print(f'{YELLOW}Flows of udp_ip:{RAZ}')
    print(sa.get_flows_by_protocol(flows, "udp_ip"))
    print(f'{BLUE}Number of flows per protocol names:{RAZ}')
    print(sa.get_number_flows(flows, 'protocolName'))

    print(f'{PURPLE}Sorted flows by totalSourceBytes loading...{RAZ}')
    print(sa.sort_by_key(flows, 'totalSourceBytes'))
    print(f'{CYAN}Graph on totalSourceBytes{RAZ}')
    data = sa.get_number_flows(flows, 'totalSourceBytes')
    create_graph_log([d['doc_count'] for d in data], 'graphs/graph_tmp.png')


def test2():
    """

    :return:
    """
    import script_analyze_elasticsearch as sae

    print(f'{GREEN}Protocol names:{RAZ}')
    es.pretty_print(sae.get_protocol_names(es))
    print(f'{YELLOW}Flows of udp_ip:{RAZ}')
    es.pretty_print(sae.get_flows_by_protocol(es, "udp_ip"))
    print(f'{BLUE}Number of flows per protocol names:{RAZ}')
    es.pretty_print(sae.get_number_flows(es, "protocolName.keyword"))

    print(f'{PURPLE}Count flows for totalSourceBytes loading...{RAZ}')
    es.pretty_print(sae.histogram_total_source_bytes(es))
    print(f'{CYAN}Graph on totalSourceBytes{RAZ}')
    create_graph_log(
        [
            d['doc_count']
            for d in sae.histogram_total_source_bytes(es)
        ],
        'graphs/graph_es_tmp.png'
    )


##########################
# Main                   #
##########################

if __name__ == "__main__":
    args = parser.parse_args()
    print(f'{RED} {open("credits", "r").read()}{RAZ}')

    if args.config_elastic:
        config_elastic = json.loads(args.config_elastic)
        es.ES_CONFIG['host'] = config_elastic.get('host', es.ES_CONFIG['host'])
        es.ES_CONFIG['port'] = config_elastic.get('port', es.ES_CONFIG['port'])
        es.ES_INDEX = config_elastic.get('index', es.ES_INDEX)
        es.ES_TYPE = config_elastic.get('type', es.ES_TYPE)
        es.ES_URL = f'http://{es.ES_CONFIG["host"]}:{es.ES_CONFIG["port"]}'

    if args.prune_elastic:
        try:
            es.prune()
        except Exception as err:
            logging.warning(str(err))

    if not args.elasticsearch:
        if args.shelve:
            logging.info('Get data from shelve - start')
            flows = get_data_from_shelve_file(args.shelve)
            logging.info('Get data from shelve - done')
        else:
            if args.folder:
                files = get_files_list(args.folder)
            else:
                files = [args.file]

            logging.info('Get and parse data from files - start')
            flows = parse_xml_to_dict(files)
            logging.info('Get and parse data from files - done')

            if args.save_shelve:
                logging.info('Save data to shelve - start')
                set_shelve_file(args.save_shelve, flows)
                logging.info('Save data to shelve - done')

        if args.save_elastic:
            logging.info('Save data to elastic - start')
            es.set_multidata(flows)
            logging.info('Save data to elastic - done')

    if args.test_start:
        if args.elasticsearch:
            test2()
        else:
            test1(flows)

    print(f'{RED}done{RAZ}')
