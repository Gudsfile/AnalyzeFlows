__author__ = "Gudsfile and Wigow "


class SearchES:
    """
    Body for an elasticsearch search.
    """

    def __init__(self):
        self.main = {}

    def __str__(self):
        from json import dumps
        return dumps(self.main, indent=4)

    def to_str(self):
        """
        Get the body request in string.

        :return:
        """
        return self.__str__()

    def to_dict(self):
        """
        Get the body request in dict.

        :return:
        """
        return self.main

    def all(self):
        """
        Add all option to the request.

        :return:
        """
        query = self.main.get('query', {})
        query['match_all'] = {}
        self.main['query'] = query

        return self

    def must(self, *args):
        """

        :param args:
        :return:
        """
        query = self.main.get('query', {})
        bool = query.get('bool', {})
        must = bool.get('must', [])

        for a in args:
            must.append({'match': a})

        bool['must'] = must
        query['bool'] = bool
        self.main['query'] = query

        return self

    def should(self, *args):
        """

        :param args:
        :return:
        """
        query = self.main.get('query', {})
        bool = query.get('bool', {})
        should = bool.get('should', [])

        for a in args:
            should.append({'match': a})

        bool['should'] = should
        query['bool'] = bool
        self.main['query'] = query

        return self

    def aggregations(self, field, aggs_type: str, aggs_index: str = 'group_by'):
        """
        aggs_type : terms, histogram, range, ...
        see all family and type here https://www.elastic.co/guide/en/elasticsearch/reference/current/search-aggregations.html

        :param field:
        :param aggs_type:
        :param aggs_index:
        :return:
        """
        aggs = self.main.get('aggs', {})
        index = aggs.get(aggs_index, {})

        index[aggs_type] = field

        aggs[aggs_index] = index
        self.main['aggs'] = aggs

        return self

    def terms_aggregations(self, field: str, aggs_index: str = 'group_by', size=10):
        """

        :param field:
        :param aggs_index:
        :return:
        """
        terms = {'field': field, 'size':size}
        return self.aggregations(terms, 'terms', aggs_index)

    def filter(self, type, field, value, **kwargs):
        """

        :param type:
        :param field:
        :param value:
        :param kwargs:
        :return:
        """
        query = self.main.get('query', {})

        if type == 'terms_set':
            # field: str
            # value: list
            query_type = {
                field: {
                    'terms': value,
                    'minimum_should_match_field': field
                }
            }
        elif type == 'terms':
            # field: str
            # value: list
            query_type = {
                field: value,
            }
        elif type == 'term':
            # field: str
            # value: str, list
            query_type = {
                field: {
                    'value': value,
                }
            }
        elif type == 'regexp':
            # field: str
            # value: str
            query_type = {
                field: {
                    'value': value,
                }
            }
        elif type == 'range':
            # field: str
            # value: dict -> {'gt':20, 'gte': 21, 'lte':30, 'lt':29, 'boost':2}
            query_type = {
                field : {
                    value
                }
            }
        elif type == 'prefix':
            # field: str
            # value: str
            query_type = {field: value}
        elif type == 'ids':
            # field: N/A
            # value: list(str)
            query_type = {'values': value}
        else:
            raise Exception(f'Error - {type} is not yet supported with filter')

        query[type] = query_type
        self.main['query']=query

        return self

    def size(self, size: int):
        """
        Add option to choose the size of the results list.

        :param size:
        :return:
        """
        self.main['size'] = size
        return self

    def paginate(self, start: int, size: int):
        """

        :param start:
        :param size:
        :return:
        """
        self.main['from'] = start
        self.main['size'] = size
        return self

    def order(self, field, order='asc', script=False):
        """

        :param field:
        :param order:
        :param script:
        :return:
        """

        if script:
            sort = {
                "_script": {
                    "type": "number",
                    "script": {
                        "lang": "painless",
                        field: f"doc['{field}'].value"
                    },
                    "order": order
                }
            }
        else:
            sort = self.main.get('sort', [])
            sort.append({
                field: {
                    'order': order
                }
            })

        self.main['sort'] = sort

        return self

    def select(self, include_fields=None, exclude_fields=None, only_metadata: bool = False):
        """

        :param include_fields:
        :param exclude_fields:
        :param only_metadata:
        :return:
        """
        if exclude_fields is None:
            exclude_fields = []
        if include_fields is None:
            include_fields = []
        if only_metadata:
            self.main['_source'] = False
            return self

        select = self.main.get('_source', {})
        includes = select.get('includes', [])
        excludes = select.get('excludes', [])

        for field in include_fields:
            includes.append(field)

        for field in exclude_fields:
            excludes.append(field)

        select['includes'] = includes
        select['excludes'] = excludes
        self.main['_source'] = select

        return self
