__author__ = "Gudsfile and Wigow "

##########################
# Import                 #
##########################

# python libs
import argparse
import time
import logging
import logging.config

# local libs
from metrics import benchmark

# 3rd party libs
from elasticsearch import Elasticsearch

from sklearn.utils import Bunch
from sklearn.model_selection import train_test_split

from sklearn.metrics import accuracy_score
from sklearn.metrics import f1_score
from sklearn.metrics import confusion_matrix
from sklearn.preprocessing import normalize

from sklearn.naive_bayes import GaussianNB
from sklearn.neighbors import KNeighborsClassifier
from sklearn.svm import LinearSVC
from sklearn.linear_model import SGDClassifier
from sklearn.neural_network import MLPClassifier

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
            'filename': 'logs/learn_flows.log',
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
# Elastic config         #
##########################

ES_CONFIG = {
    'host': 'localhost',
    'port': 9200
}
ES_TYPE = 'flows'
ES_INDEX = 'sp1flows'
ES = Elasticsearch([ES_CONFIG])

##########################
# Script args            #
##########################

parser = argparse.ArgumentParser(description='LearnFlows is a school projet.')
parser.add_argument(
    help="Elastic index for data to train",
    dest='index_train',
    action='store'
)
parser.add_argument(
    help="Elastic index for data to test",
    dest='index_test',
    action='store'
)


###############################

def get_data_train(data_key, target_key, match, index=ES_INDEX):
    """
    Get data and target from all elasticsearch data

    :param data_key: key where find data
    :param target_key: key where find target
    :param match: match parameter
    :param index: index of the elasticsearch
    :return: list of data and target from elasticsearch
    """
    body = {
        '_source': [data_key, target_key],
        'size': 10000,
        'query': {
            'bool': {
                'must': [{'match': match}]
            }
        }
    }

    scroll = '1m'

    data = []
    target = []

    result = ES.search(index=index, body=body, scroll=scroll)
    hits = result['hits']['hits']

    for hit in hits:
        data.append(hit['_source'][data_key])
        target.append(hit['_source'][target_key])

    scroll_size = len(hits)
    sid = result['_scroll_id']
    total_scroll_size = scroll_size

    while scroll_size > 0:

        result = ES.scroll(scroll_id=sid, scroll='1m')
        sid = result['_scroll_id']
        hits = result['hits']['hits']
        scroll_size = len(hits)

        for hit in hits:
            data.append(hit['_source']['vector'])
            target.append(hit['_source']['Tag'])

        total_scroll_size += scroll_size

    return data, target, total_scroll_size


def get_data_test(data_key, match, index=ES_INDEX):
    """
    Get data from all elasticsearch data

    :param data_key: key where find data
    :param match: match parameter
    :param index: index of the elasticsearch
    :return: list of data from elasticsearch
    """
    body = {
        '_source': [data_key],
        'size': 10000,
        'query': {
            'bool': {
                'must': [{'match': match}]
            }
        }
    }

    scroll = '1m'

    data = []

    result = ES.search(index=index, body=body, scroll=scroll)
    hits = result['hits']['hits']

    for hit in hits:
        data.append(hit['_source'][data_key])

    scroll_size = len(hits)
    sid = result['_scroll_id']
    total_scroll_size = scroll_size

    while scroll_size > 0:

        result = ES.scroll(scroll_id=sid, scroll='1m')
        sid = result['_scroll_id']
        hits = result['hits']['hits']
        scroll_size = len(hits)

        for hit in hits:
            data.append(hit['_source']['vector'])

        total_scroll_size += scroll_size

    return data, total_scroll_size


def preparing(descr: str, data: list, feature_names: list, target: list, target_names: list):
    """
    Prepares data and target for the learning and training process

    :param descr: description
    :param data: data to prepare
    :param feature_names: names of data components
    :param target: given labels for the given data
    :param target_names: classification labels
    :return: data_train, target_train, data_test, target_test
    """
    bunch = Bunch(DESCR=descr, data=data, feature_names=feature_names, target=target, target_names=target_names)
    return train_test_split(bunch.data, bunch.target, random_state=0, train_size=0.2)


def scoring(result, target_test):
    """

    :param result:
    :param target_test:
    :return:
    """
    acc_score = accuracy_score(result, target_test)
    f_score = f1_score(result, target_test) # moyenne entre la precision (nbr de fausses alarmes) et le rappel
    conf = confusion_matrix(target_test, result)
    return acc_score, f_score, conf


@benchmark
def knn_classifier(data_test, data_train, target_train, proba=False):
    """

    :param data_test:
    :param data_train:
    :param target_train:
    :param proba:
    :return:
    """
    logging.info('KNeighborsClassifier')
    knn = KNeighborsClassifier(n_neighbors=1)

    duration = time.time()
    knn.fit(data_train, target_train)
    duration = time.time()-duration
    logging.info(f'duration fit: {duration}')

    if proba:
        duration = time.time()
        result = knn.predict(data_test)
        duration = time.time()-duration
        logging.info(f'duration predict: {duration}')
        proba = knn.predict_proba(data_test)[:, 1]
        return result, proba
    duration = time.time()
    result = knn.predict(data_test)
    duration = time.time()-duration
    logging.info(f'duration predict: {duration}')
    return result


@benchmark
def gaussian_nb(data_test, data_train, target_train, proba=False):
    """

    :param data_test:
    :param data_train:
    :param target_train:
    :param proba:
    :return:
    """
    logging.info('GaussianNB')
    gnb = GaussianNB()

    duration = time.time()
    gnb.fit(data_train, target_train)
    duration = time.time()-duration
    logging.info(f'duration fit: {duration}')

    if proba:
        duration = time.time()
        result = gnb.predict(data_test)
        duration = time.time()-duration
        logging.info(f'duration predict: {duration}')
        proba = gnb.predict_proba(data_test)[:, 1]
        return result, proba
    duration = time.time()
    result = gnb.predict(data_test)
    duration = time.time()-duration
    logging.info(f'duration predict: {duration}')
    return result

@benchmark
def linear_svc(data_test, data_train, target_train, proba=False):
    """

    :param data_test:
    :param data_train:
    :param target_train:
    :param proba:
    :return:
    """
    logging.info('LinearSVC')
    svc = LinearSVC()

    duration = time.time()
    svc.fit(data_train, target_train)
    duration = time.time()-duration
    logging.info(f'duration fit: {duration}')

    if proba:
        duration = time.time()
        result = svc.predict(data_test)
        duration = time.time()-duration
        logging.info(f'duration predict: {duration}')
        proba = svc.decision_function(data_test)
        return result, proba
    duration = time.time()
    result = svc.predict(data_test)
    duration = time.time()-duration
    logging.info(f'duration predict: {duration}')
    return result


@benchmark
def linear_sgd(data_test, data_train, target_train, proba=False):
    """
    
    :param data_test:
    :param data_train:
    :param target_train:
    :param proba:
    :return:
    """
    logging.info('SGDClassifier')
    sgd = SGDClassifier()

    duration = time.time()
    sgd.fit(data_train, target_train)
    duration = time.time()-duration
    logging.info(f'duration fit: {duration}')

    if proba:
        duration = time.time()
        result = sgd.predict(data_test)
        duration = time.time()-duration
        logging.info(f'duration predict: {duration}')
        proba = sgd.decision_function(data_test)
        return result, proba
    duration = time.time()
    result = sgd.predict(data_test)
    duration = time.time()-duration
    logging.info(f'duration predict: {duration}')
    return result


@benchmark
def mlp_classifier(data_test, data_train, target_train, proba=False):
    """

    :param data_test:
    :param data_train:
    :param target_train:
    :param proba:
    :return:
    """
    logging.info('MLPClassifier')
    mlp = MLPClassifier(solver='lbfgs', alpha=1e-5, hidden_layer_sizes=(100, 50), random_state=1)

    duration = time.time()
    mlp.fit(data_train, target_train)
    duration = time.time()-duration
    logging.info(f'duration fit: {duration}')

    if proba:
        duration = time.time()
        result = mlp.predict(data_test)
        duration = time.time()-duration
        logging.info(f'duration predict: {duration}')
        proba = mlp.predict_proba(data_test)[:, 1]
        return result, proba
    duration = time.time()
    result = mlp.predict(data_test)
    duration = time.time()-duration
    logging.info(f'duration predict: {duration}')
    return result


def save_heatpmap(figname, conf):
    """

    :param figname:
    :param conf:
    :return:
    """
    import seaborn
    import matplotlib.pyplot as plt

    seaborn.set()
    seaborn.heatmap(conf, square=True, annot=True, cbar=False, linecolor='white', linewidths=1,
                    xticklabels=target_names, yticklabels=target_names)
    plt.savefig(figname)


def save_result(filename, data, proba):
    """

    :param data:
    :param proba:
    :param filename:
    :return:
    """
    with open(filename, 'w') as f:
        for d, p in zip(data, proba):
            f.write(f'{p} {d}\n')


def binarize_label(target):
    """

    :param target:
    :return:
    """
    for i in range(len(target)):
        target[i] = 0 if target[i] == 'Normal' else 1
    return target


###############################

# Les noms des paramètres de nos données/enregistrements
feature_names = []
feature_names += ['totalSourceBytes']
feature_names += ['totalDestinationBytes']
feature_names += ['totalSourcePackets']
feature_names += ['totalDestinationPackets']
feature_names += ['sourcePort']
feature_names += ['destinationPort']
feature_names += ['source'] * 4
feature_names += ['destination'] * 4
feature_names += ['startDateTime'] * 5
feature_names += ['stopDateTime'] * 5
feature_names += ['sourcePayloadAsBase64'] * 255
feature_names += ['destinationPayloadAsBase64'] * 255
feature_names += ['direction'] * 2

# Les labels de classification
target_names = ['Normal', 'Attack']

# La description
descr = ''

##########################
# Main                   #
##########################

if __name__ == "__main__":
    args = parser.parse_args()

    if args.index_train == args.index_test:
        # Initialize data
        data, target, size = get_data_train('vector', 'Tag', {'appName': 'HTTPWeb'}, args.index_train)
        logging.info(f'Total scroll size: {size}')
        data_train, data_test, target_train, target_test = preparing(descr, normalize(data), feature_names, binarize_label(target), binarize_label(target_names))

        # Naive Bayes classification
        acc_score, f_score, conf = scoring(gaussian_nb(data_test, data_train, target_train), target_test)
        logging.info(f'accurency: {acc_score}')
        logging.info(f'f1: {f_score}')
        logging.debug(f'conf:{conf}')
        save_heatpmap('graphs/heatmap_GaussianNB.png', conf)

        # k-NN classification
        acc_score, f_score, conf = scoring(knn_classifier(data_test, data_train, target_train), target_test)
        logging.info(f'accurency: {acc_score}')
        logging.info(f'f1: {f_score}')
        logging.debug(f'conf:{conf}')
        save_heatpmap('graphs/heatmap_KNeighborsClassifier.png', conf)

        # Linear SVM classification
        acc_score, f_score, conf = scoring(linear_svc(data_test, data_train, target_train), target_test)
        logging.info(f'accurency: {acc_score}')
        logging.info(f'f1: {f_score}')
        logging.debug(f'conf:{conf}')
        save_heatpmap('graphs/heatmap_LinearSVC.png', conf)

        # SGD classification
        acc_score, f_score, conf = scoring(linear_sgd(data_test, data_train, target_train), target_test)
        logging.info(f'accurency: {acc_score}')
        logging.info(f'f1: {f_score}')
        logging.debug(f'conf:{conf}')
        save_heatpmap('graphs/heatmap_LinearSGD.png', conf)

        # Multilayer Perceptron classification
        acc_score, f_score, conf = scoring(mlp_classifier(data_test, data_train, target_train), target_test)
        logging.info(f'accurency: {acc_score}')
        logging.info(f'f1: {f_score}')
        logging.debug(f'conf:{conf}')
        save_heatpmap('graphs/heatmap_MLPClassifier.png', conf)

    else:
        # Initialize data
        data_train, target_train, size = get_data_train('vector', 'Tag', {'appName': 'HTTPWeb'}, args.index_train)

        target_train = binarize_label(target_train)
        data_train = normalize(data_train)

        logging.info(f'Total train size: {size}')
        data_test, size = get_data_test('vector', {'appName': 'HTTPWeb'}, args.index_test)
        data_test = normalize(data_test)
        logging.info(f'Total test size: {size}')

        # Naive Bayes classification
        target_result, proba_result = gaussian_nb(data_test, data_train, target_train, proba=True)
        logging.debug(target_result)
        logging.debug(proba_result)
        save_result('tmp/GUDSFILE_GaussianNB.txt', target_result, proba_result)

        # k-NN classification
        target_result, proba_result = knn_classifier(data_test, data_train, target_train, proba=True)
        logging.debug(target_result)
        logging.debug(proba_result)
        save_result('tmp/GUDSFILE_KNeighborsClassifier.txt', target_result, proba_result)

        # Linear SVM classification
        target_result, proba_result = linear_svc(data_test, data_train, target_train, proba=True)
        logging.debug(target_result)
        logging.debug(proba_result)
        save_result('tmp/GUDSFILE_LinearSVC.txt', target_result, proba_result)

        # SGD classification
        target_result, proba_result = linear_sgd(data_test, data_train, target_train, proba=True)
        logging.debug(target_result)
        logging.debug(proba_result)
        save_result('tmp/GUDSFILE_SGDClassifier.txt', target_result, proba_result)

        # Multilayer Perceptron classification
        target_result, proba_result = mlp_classifier(data_test, data_train, target_train, proba=True)
        logging.debug(target_result)
        logging.debug(proba_result)
        save_result('tmp/GUDSFILE_MLPClassifier.txt', target_result, proba_result)


# python AnalyzeFlows.py -f tmp/ISCX_HTTPWeb_train.xml --save-elastic --config-elastic '{"index": "train"}' --prune-elastic
# python AnalyzeFlows.py -f tmp/ISCX_HTTPWeb_test.xml --save-elastic --config-elastic '{"index": "test"}' --prune-elastic
# python LearnFlows.py train test
