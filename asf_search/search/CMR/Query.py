from typing import List
import itertools
import logging

from asf_search.constants import INTERNAL
from .Subquery import CMRSubQuery


class CMRQuery:
    def __init__(
            self,
            opts
    ):
        self.cmr_host = opts.cmr_host
        self.cmr_provider = opts.provider
        self.cmr_token = opts.token
        self.maxResults = opts.maxResults

        # These additional params will be applied to each subquery
        self.extra_params = [
            ('provider', self.cmr_provider),
            ('options[temporal][and]', 'true'),
            ('sort_key[]', '-end_date'),
            ('sort_key[]', 'granule_ur'),
            ('options[platform][ignore_case]', 'true')
        ]

        # Check for small result set
        self.page_size = INTERNAL.CMR_PAGE_SIZE
        if self.maxResults is not None and self.maxResults > INTERNAL.CMR_PAGE_SIZE:
            self.extra_params.append(('page_size', INTERNAL.CMR_PAGE_SIZE))
            self.extra_params.append(('scroll', 'true'))  # CMR team has requested we leave this off entirely if false
        else:
            self.page_size = self.maxResults
            self.extra_params.append(('page_size', self.page_size))

        self.resultsYielded = 0

        self.sub_queries = [
            CMRSubQuery(
                params,
                params=list(query),
                extra_params=self.extra_params
            )
            for query in subquery_list_from(params)
        ]

        logging.debug('New CMRQuery object ready to go')

    def get_count(self):
        return sum([sq.get_count() for sq in self.sub_queries])

    def get_results(self):
        for query_num, subquery in enumerate(self.sub_queries):
            logging.debug('Running subquery {0}'.format(query_num+1))

            # taking a page at a time from each subquery,
            # yield one result at a time until we max out
            for result in subquery.get_results():

                if self.max_results_reached():
                    logging.debug('Max results reached, terminating')
                    return

                if result is None:
                    continue

                self.resultsYielded += 1
                yield result

                # it's a little silly but run this check again here so we don't accidentally fetch an extra page
                if self.max_results_reached():
                    logging.debug('Max results reached, terminating')
                    return

            logging.debug('End of available results reached')

    def max_results_reached(self):
        return (
                self.maxResults is not None and
                self.resultsYielded >= self.maxResults
        )


def subquery_list_from(params: dict) -> List:
    """
    Use the cartesian product of all the list parameters to determine subqueries

    :param params: A dictionary of search parameters

    :return: A list of dictionaries representing subquery parameters
    """
    logging.debug('Building subqueries using params:')
    logging.debug(params)

    subquery_params, list_params = {}, {}

    def chunk_list(source_list, n):
        return [source_list[i * n:(i + 1) * n] for i in range((len(source_list) + n - 1) // n)]

    chunk_lists = ['granule_list', 'product_list'] # these list parameters will be broken into chunks for subquerying
    for chunk_type in chunk_lists:
        if chunk_type in params:
            params[chunk_type] = chunk_list(list(set(params[chunk_type])), 500) # distinct and split

    list_param_names = ['platform'] # these parameters will dodge the subquery system

    for k, v in params.items():
        if k in list_param_names:
            list_params[k] = v
        else:
            subquery_params[k] = v

    sub_queries = cartesian_product(subquery_params)
    formatted_list_params = format_list_params(list_params)

    final_sub_queries = [
        query + formatted_list_params for query in sub_queries
    ]

    logging.debug(f'{len(final_sub_queries)} subqueries built')

    return final_sub_queries
# TODO: this is where I stopped, dunno wtf the rest is

def cartesian_product(params):
    formatted_params = format_query_params(params)

    return list(itertools.product(*formatted_params))


def format_list_params(list_params):
    formatted_params = sum(format_query_params(list_params), [])

    return tuple(formatted_params)


def format_query_params(params):
    listed_params = []

    for param_name, param_val in params.items():
        plist = translate_param(param_name, param_val)
        listed_params.append(plist)

    return listed_params


def translate_param(param_name, param_val):
    param_list = []

    cmr_input_map = input_map()

    param_input_map = cmr_input_map[param_name]
    cmr_param = param_input_map[0]
    cmr_format_str = param_input_map[1]

    if not isinstance(param_val, list):
        param_val = [param_val]

    for l in param_val:
        format_val = l

        if isinstance(l, list):
            format_val = ','.join([f'{t}' for t in l])

        param_list.append({
            cmr_param: cmr_format_str.format(format_val)
        })

    return param_list
