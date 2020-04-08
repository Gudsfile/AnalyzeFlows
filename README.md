# AnalyzeFlows

🖥 AnalyzeFlows is an artificial intelligence and intrusion detection project 
developed during the month of November 2019.
The project consists in analyzing flows from.xml files and detecting offensive flows.

⚙️ The following technologies were used to carry out this project:

* Python
* Elasticsearch
* Scikit-Learn

👨‍💻 Teamwork with [Antoine](https://github.com/antoine5600).


## Setup and requirements

Python3 is required

Install virtualenv with pip
```bash
pip install virtualenv
```

Create an virtual env
```bash
virtualenv -p python3 venv
```

Activate virtualenv
```bash
source venv/bin/activate # linux & macOS
./venv/Scripts/activate  # windows
```

Check python and pip version (expected: 3)
```bash
python --version
pip --version
```

Install required libraries
```bash
pip install -r requirements
```

## Elasticsearch

Elasticsearch must be started.

### Install

ubuntu:
```bash
```

macOS:
```bash
brew tap elastic/tap/
brew install elastic/tap/elasticsearch-full
```

windows:
```shell
```

docker:
```shell
```

### Start

```bash
elasticsearch
```

Go to http://localhost:9200/

## Start AnalyzeFlows

The AnalyzeFlows script allows you to analyze the data from the.xml files and record the flows to a shelve file or an Elasticsearch server.


```bash
source venv/bin/activate
python AnalyzeFlows -f file_name.xml
```

```bash
usage: AnalyzeFlows.py [-h] (-f FILE | -d FOLDER | -s SHELVE | -e)
                       [--save-shelve SAVE_SHELVE] [--save-elastic]
                       [--config-elastic CONFIG_ELASTIC] [--prune-elastic]
                       [--test]

optional arguments:
  -h, --help            show this help message and exit
  -f FILE, --file FILE  xml file to parse
  -d FOLDER, --directory FOLDER
                        directory of xml files to parse
  -s SHELVE, --shelve SHELVE
                        shelve file
  -e, --elasticsearch   Open data with elasticsearch
  --save-shelve SAVE_SHELVE
                        Name of the shelve file to save data
  --save-elastic        Save data with elasticsearch
  --config-elastic CONFIG_ELASTIC
                        config of elasticsearch (ex: '{"index":"my_index"}')
  --prune-elastic       prune the elastic index used before process
  --test                start test process
```

## Start LearnFlows

The LearnFlows script allows you to compare different ways of learning and testing data prediction.


```bash
source venv/bin/activate
python LearnFlows index_train index_test
```

```bash
usage: LearnFlows.py [-h] index_train index_test

LearnFlows is a school projet.

positional arguments:
  index_train  Elastic index for data to train
  index_test   Elastic index for data to test

optional arguments:
  -h, --help   show this help message and exit
```

