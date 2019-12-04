__author__ = "Gudsfile and Wigow "

##########################
# IMPORT                 #
##########################

# python libs
import shelve
from datetime import datetime
from os import path

# local libs
from metrics import benchmark

# 3rd party libs
import xmltodict


##########################
# Functions              #
##########################

@benchmark
def parse_xml_to_dict(files_path: list):
    """
    Get a list of flows from given files.
    :param files_path:
    :return:
    """
    flows = list()

    for file_path in files_path:
        print(file_path)
        with open(file_path, 'r') as f:
            data_xml = f.read()
        data_dict = xmltodict.parse(data_xml)

        file_name = path.basename(file_path.split('.')[0])

        # TODO
        flows += [parse_and_check_flow(flow) for flow in data_dict['dataroot'][file_name]]
        # flows += [parse_and_check_flow(flow) for flow in data_dict['test']['item']]
        # flows += [parse_and_check_flow(flow) for flow in data_dict['train']['item']]

    return flows


def parse_and_check_flow(flow: dict):
    """

    :param flow:
    :return:
    """
    required_keys = ['source', 'protocolName', 'sourcePort', 'destination',
                     'destinationPort', 'startDateTime', 'stopDateTime']
    if any(required_key not in flow for required_key in required_keys):
        raise Exception(f'Error - one or more required keys are not in the given flow: {flow}')

    flow['vector'] = vectorization(flow)

    return flow


def vectorization(flow):
    """
    Check format of the given flow and convert date and ip to a numerical

    :param flow:
    :return:
    """

    vector = [
        int(flow['totalSourceBytes']),
        int(flow['totalDestinationBytes']),
        int(flow['totalSourcePackets']),
        int(flow['totalDestinationPackets']),
        int(flow['sourcePort']),
        int(flow['destinationPort'])
    ]
    vector += ip_to_ipstamp(flow['source'])
    vector += ip_to_ipstamp(flow['destination'])
    vector += date_to_timestamp(flow['startDateTime'])
    vector += date_to_timestamp(flow['stopDateTime'])
    vector += payload_to_asciistamp(flow['sourcePayloadAsBase64'])
    vector += payload_to_asciistamp(flow['destinationPayloadAsBase64'])
    vector += direction_to_dirstamp(flow['direction'])

    # Useless fields:
    # appName
    # protocolName
    # Tag
    # sourcePayloadAsUTF8
    # destinationPayloadAsUTF8
    # <sourceTCPFlagsDescription>F,A</sourceTCPFlagsDescription>
    # <destinationTCPFlagsDescription>F,A</destinationTCPFlagsDescription>
    
    # TODO Check is sourceTCPFlagsDescription is important and sourceUDP etc
    #  exists TCAF

    return tuple(vector)


def direction_to_dirstamp(direction: str):
    """
    Convert the given direction into a integer. Replace L and R with 0 and 1.
    Return an list.
    Ex: for 'L2R' the result is [0, 1]

    :param direction:
    :return:
    """
    return [0 if d == 'L' else 1 for d in direction.replace('2', '')]


def date_to_timestamp(date: str):
    """
    Get a numerical version of the given date.
    Return an list.
    Ex: for 2010-06-12T23:58:53 the result is [2010, 6, 12, 23, 58, 53].

    :param date:
    :return:
    """
    date_format = '%Y-%m-%dT%H:%M:%S'
    date_time = datetime.strptime(date, date_format)
    return [
        date_time.year,
        date_time.month,
        date_time.day,
        date_time.hour,
        date_time.minute,
        date_time.second
    ]


def ip_to_ipstamp(ip: str):
    """
    Get a vetorial version of the given ip.
    Return an list of four dimensions for each part of the ip.
    Ex: for 192.168.1.0 the result is [192, 168, 1, 0].

    :param ip:
    :return:
    """
    return [int(i) for i in ip.split('.')]


def payload_to_asciistamp(raw: str):
    """
    Get a vectorial version of the given payload.

    :param raw:
    :return:
    """
    res_tab = [0] * 255
    if not raw:
        return res_tab
    for char in raw:
        try:
            res_tab[ord(char)] += 1
        except:
            raise Exception(f'Error - payload:{raw} format')
    return res_tab


@benchmark
def get_data_from_shelve_file(filename: str):
    """

    :param filename:
    :return:
    """
    with shelve.open(filename) as db:
        return db['key']


@benchmark
def set_shelve_file(filename: str, data: dict):
    """

    :param filename:
    :param data:
    :return:
    """
    with shelve.open(filename) as db:
        db['key'] = data
