__author__ = "Gudsfile and Wigow "

##########################
# Colors                 #
##########################

BLACK = '\033[90m'
RED = '\033[91m'
GREEN = '\033[92m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
PURPLE = '\033[95m'
CYAN = '\033[96m'
RAZ = '\033[00m'


##########################
# Functions              #
##########################

def pretty_dict(data):
    """
    Return a string version of the given dict or list with json format.

    :param data:
    :return:
    """
    from json import dumps
    return dumps(data, indent=4)
