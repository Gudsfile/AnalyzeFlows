__author__ = "Gudsfile and Wigow "

##########################
# Import                 #
##########################

# python libs
import json

# local libs
from metrics import benchmark

# 3rd party libs
import requests
from elasticsearch import Elasticsearch
from elasticsearch import helpers

##########################
# Elastic config         #
##########################

ES_CONFIG = {
    'host': 'localhost',
    'port': 9200
}
ES_URL = f'http://{ES_CONFIG["host"]}:{ES_CONFIG["port"]}'
ES_INDEX = 'sp1flows'
ES_TYPE = 'flows'
ES = Elasticsearch([ES_CONFIG])


##########################
# Functions              #
##########################

def get_elasticsearch_version():
    """
    Get the ElasticSearch (and Lucene) version.

    :return:
    """
    return Elasticsearch().info()


def is_elasticsearch_server_started():
    """
    True if an elasticsearch server is started.

    :return:
    """
    return True if requests.get(ES_URL).status_code == 200 else False


def bulk_factory(data, **kwargs):
    """
    Construct a bulk type dict for given data.
    optional args:
        _index: elasticsearch index
        _type: type of data
        _id: define an id for the data

    :param data:
    :param kwargs:
    :return:
    """
    _ID = 0;
    for d in data:
        _ID += 1;
        yield {
            '_index': kwargs.get('_index', ES_INDEX),
            '_type': kwargs.get('_type', ES_TYPE),
            '_id': kwargs.get('_id', _ID),
            '_source': d
        }


@benchmark
def set_data(data, **kwargs):
    """
    Add one data.
    optional args:
        _index: elasticsearch index
        _type: type of data
        _id: define an id for the data

    :param data:
    :param kwargs:
    :return:
    """
    _index = kwargs.get('_index', ES_INDEX)
    _type = kwargs.get('_type', ES_TYPE)
    _id = kwargs.get('_id', None)
    ES.index(index=_index, body=data, doc_type=_type, id=_id)


@benchmark
def set_multidata(data, request_timeout=10, **kwargs):
    """
    Add some data.

    :param data:
    :param request_timeout:
    :param kwargs:
    :return:
    """
    helpers.bulk(ES, bulk_factory(data, **kwargs), request_timeout=request_timeout)


def get(body, **kwargs):
    """
    Search object with the given body request.
    optional args:
        _index: elasticsearch index

    :param body:
    :param kwargs:
    :return:
    """
    _index = kwargs.get('_index', ES_INDEX)
    return ES.search(index=_index, body=body)


def get_object(_id, **kwargs):
    """
    Get a specific object with its id
    ['_source']

    :param _id:
    :param kwargs:
    :return:
    """
    _index = kwargs.get('_index', ES_INDEX)
    _type = kwargs.get('_type', ES_TYPE)
    return ES.get(index=_index, doc_type=_type, id=_id)


def delete_object(_id, **kwargs):
    """
    Deletes a specific object with its id.
    ['result']

    :param _id:
    :param kwargs:
    :return:
    """
    _index = kwargs.get('_index', ES_INDEX)
    _type = kwargs.get('_type', ES_TYPE)
    return ES.delete(index=_index, doc_type=_type, id=_id)


def prune(**kwargs):
    """
    Delete all indices for an elasticsearch index.
    optional args:
        _index: elasticsearch index

    :param kwargs:
    :return:
    """
    ES.indices.delete(index=kwargs.get('_index', ES_INDEX))


def beautifier(data):
    """

    :param data:
    :return:
    """
    return json.dumps(data, indent=4)


def pretty_print(data):
    """

    :param data:
    :return:
    """
    print(beautifier(data))
