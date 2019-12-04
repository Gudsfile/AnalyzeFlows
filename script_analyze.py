__author__ = "Gudsfile and Wigow "

##########################
# Import                 #
##########################

# python libs
from typing import List


##########################
# Functions              #
##########################

def get_protocol_names(flows: List[dict]):
    """
    Get the list of all the (distinct) protocols.

    :param flows:
    :return:
    """
    protocol_names = list()
    for flow in flows:
        protocol_names.append(flow['protocolName'])
    return set(protocol_names)


def get_flows_by_protocol(flows: List[dict], protocol_name: str):
    """
    Get the list of flows for a given protocol.

    :param flows:
    :param protocol_name:
    :return:
    """
    res = list()
    for flow in flows:
        if flow['protocolName'] == protocol_name:
            res.append(flow)
    return res


def get_number_flows(flows: List[dict], key: str):
    """
    Get number of flows for each different values of thee given key.

    :param flows:
    :param key:
    :return:
    """
    res = []
    for flow in flows:
        if not any(r['key'] == flow[key] for r in res):
            res.append({'key': flow[key], 'doc_count': 1})
        else:
            for r in res:
                if r['key'] != flow[key]:
                    continue
                r['doc_count'] += 1
    return sorted(res, key=lambda i: i['key'][-1], reverse=False)


def sort_by_key(flows: List[dict], key, reverse: bool = False):
    """
    Sorts flows by the given key in int.

    :param flows:
    :param key:
    :param reverse:
    :return:
    """
    try:
        return sorted(flows, key=lambda i: int(i[key]), reverse=reverse)
    except ValueError:
        return sorted(flows, key=lambda i: i[key], reverse=reverse)
