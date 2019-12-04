__author__ = "Gudsfile and Wigow "

##########################
# Import                 #
##########################

# local libs
from script_search_elasticsearch import SearchES


##########################
# Functions              #
##########################

def get_protocol_names(client):
    """
    Get the list of all the (distinct) protocols.

    :param client:
    :return:
    """
    request = SearchES().size(0).terms_aggregations('protocolName.keyword').to_str()
    return client.get(request)['aggregations']['group_by']['buckets']


def get_flows_by_protocol(client, protocol_name: str):
    """
    Get the list of flows for a given protocol.

    :param client:
    :param protocol_name:
    :return:
    """
    request = SearchES().must({'protocolName': protocol_name}).select(exclude_fields=['vector']).to_str()
    return client.get(request)['hits']['hits']


def get_number_flows(client, field: str):
    """
    Get number of flows for each given field.

    :param client:
    :param field:
    :return:
    """
    request = SearchES().size(0).terms_aggregations(field).to_str()
    return client.get(request)['aggregations']['group_by']['buckets']


def get_number_flows_by_protocol_names(client):
    """
    Get number of flows for each protocol names.

    :param client:
    :return:
    """
    return get_number_flows(client, 'protocolName')


def sort_by_key(client, field: str, reverse: bool = False, size: int = 10, script: bool = False):
    """
    Sorts flows by the given field.

    :param client:
    :param field:
    :param reverse:
    :param size:
    :param script:
    :return:
    """
    request = SearchES().order(field, order='desc' if reverse else 'asc', script=script)\
        .select(exclude_fields=['vector'])\
        .size(size)\
        .to_str()
    return client.get(request)['hits']['hits']


def histogram_total_source_bytes(client):
    """

    :param client:
    :return:
    """
    request = SearchES().size(0).terms_aggregations('totalSourceBytes.keyword', size=10000).to_str()
    return client.get(request)['aggregations']['group_by']['buckets']


def get_all(client):
    """

    :param client:
    :return:
    """
    request = SearchES().all().to_str()
    return client.get(request)
