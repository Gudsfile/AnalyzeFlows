# TODO

* documentation
* hits List(dict) everywhere
* flag ? 
* xml parse

# SOURCES

bulk, yield, helpers
* https://stackoverflow.com/questions/45831701/how-to-do-bulk-indexing-to-elasticsearch-from-python?rq=1

aggs
* https://www.elastic.co/guide/en/elasticsearch/reference/current/getting-started-aggregations.html
* https://www.elastic.co/guide/en/elasticsearch/reference/current/search-aggregations-bucket-terms-aggregation.html#search-aggregations-bucket-terms-aggregation-order
* https://www.elastic.co/guide/en/elasticsearch/reference/current/search-aggregations-bucket-histogram-aggregation.html

* https://medium.com/naukri-engineering/elasticsearch-tutorial-for-beginners-using-python-b9cb48edcedc
* https://blog.elao.com/fr/dev/ameliorez-pertinence-resultat-elastic-search-score/

sklearn
* https://scikit-learn.org/stable/modules/classes.html
* https://scikit-learn.org/stable/modules/classes.html#sklearn-metrics-metrics

# NOTES

* **bool   :** (must &| should &| must_not) + (filter)
* **must   :** liste de conditions liées par ET
* **should :** liste de conditions liées par OU
* **match  :** condition d'équivalence, match:'un deux' correspond à contient 'un' OU 'deux', mais /!\ au score, si score=1 alors équivalence parfaite
* **match_phrase :** comme match mais 'un' ET 'deux'
* **boost  :**
* **filter :** filtres comme range
* **range  :** borne d'une variable donnée
* **gt     :** min
* **gte    :** min equal
* **lt     :** max
* **lte    :** max equal
* **aggs   :** aggregations comme un group_by++ en sql
* **order  :** asc \ desc (dans terms)
* **sum    :**
* se balader dans les dicts:* dict.key dict.*

# NOTES

vector = [
      0       : totalSourceBytes
      1       : totalDestinationBytes
      2       : totalSourcePackets
      3       : totalDestinationPackets
      4       : sourcePort
      5       : destinationPort
      6 -   9 : source
     10 -  13 : destination
     14 -  19 : startDateTime
     20 -  25 : stopDateTime
     26 - 280 : sourcePayloadAsBase64
    281 - 535 : destinationPayloadAsBase64
    536 - 537 : direction
]
