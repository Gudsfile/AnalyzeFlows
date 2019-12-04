__author__ = "Gudsfile and Wigow "

##########################
# Import                 #
##########################

# python libs
import logging
import time


##########################
# Function               #
##########################

def benchmark(func):
    """
    Un décorateur qui affiche le temps qu'une fonction met à s'éxécuter
    """
    def wrapper(*args, **kwargs):
        t = time.clock()
        res = func(*args, **kwargs)
        logging.info(f'{func.__name__}, {time.clock() - t}')
        return res

    return wrapper
