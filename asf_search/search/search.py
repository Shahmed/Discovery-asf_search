from typing import Union, Iterable, Tuple
from copy import copy
import requests
from requests.exceptions import HTTPError
import datetime
import math

from asf_search import __version__
from asf_search.ASFSearchResults import ASFSearchResults
from asf_search.ASFSearchOptions import ASFSearchOptions
from asf_search.ASFSession import ASFSession
from asf_search.ASFProduct import ASFProduct
from asf_search.exceptions import ASFSearch4xxError, ASFSearch5xxError, ASFServerError
from asf_search.constants import INTERNAL


def search(opts: Union[ASFSearchOptions, dict]) -> ASFSearchResults:
    """
    Performs a generic search using the ASF SearchAPI

    :return: ASFSearchResults(list) of search results
    """
    # Make sure data is a ASFSearchOptions 'dict', to get the params verified:
    if type(opts) is not ASFSearchOptions:
        data = ASFSearchOptions(**opts)
    else:
        # Don't add defaults to the original object:
        opts = copy(opts)
    # Set some defaults:
    if opts.session is None:
        opts.session = ASFSession()

    listify_fields = [
        'absoluteOrbit',
        'asfFrame',
        'beamMode',
        'collectionName',
        'frame',
        'granule_list',
        'groupID',
        'instrument',
        'lookDirection',
        'offNadirAngle',
        'platform',
        'polarization',
        'processingLevel',
        'product_list',
        'relativeOrbit'
    ]
    for key in listify_fields:
        if key in opts and not isinstance(opts[key], list):
            opts[key] = [opts[key]]

    flatten_fields = [
        'absoluteOrbit',
        'asfFrame',
        'frame',
        'offNadirAngle',
        'relativeOrbit']
    for key in flatten_fields:
        if key in opts:
            opts[key] = flatten_list(opts[key])

    join_fields = [
        'beamMode',
        'collectionName',
        'flightDirection',
        'granule_list',
        'groupID',
        'instrument',
        'lookDirection',
        'platform',
        'polarization',
        'processingLevel',
        'product_list']
    for key in join_fields:
        if key in opts:
            opts[key] = ','.join(opts[key])

    # Special case to unravel WKT field a little for compatibility
    if opts.get('intersectsWith') is not None:
        (shapeType, shape) = opts['intersectsWith'].split(':')
        del opts['intersectsWith']
        opts[shapeType] = shape

    opts['output'] = 'geojson'
    # Join the url, to guarantee *exactly* one '/' between each url fragment:
    host = '/'.join(s.strip('/') for s in [f'https://{opts.host}', f'{INTERNAL.SEARCH_PATH}'])
    response = opts.session.post(host, data=data)

    try:
        response.raise_for_status()
    except HTTPError:
        if 400 <= response.status_code <= 499:
            raise ASFSearch4xxError(f'HTTP {response.status_code}: {response.json()["error"]["report"]}')
        if 500 <= response.status_code <= 599:
            raise ASFSearch5xxError(f'HTTP {response.status_code}: {response.json()["error"]["report"]}')
        raise ASFServerError(f'HTTP {response.status_code}: {response.json()["error"]["report"]}')

    products = [ASFProduct(f) for f in response.json()['features']]
    return ASFSearchResults(products)


def flatten_list(items: Iterable[Union[float, Tuple[float, float]]]) -> str:
    """
    Converts a list of numbers and/or min/max tuples to a string of comma-separated numbers and/or ranges.
    Example: [1,2,3,(10,20)] -> '1,2,3,10-20'

    :param items: The list of numbers and/or min/max tuples to flatten

    :return: String containing comma-separated representation of input, min/max tuples converted to 'min-max' format

    :raises ValueError: if input list contains tuples with fewer or more than 2 values, or if a min/max tuple in the input list is descending
    :raises TypeError: if input list contains non-numeric values
    """

    for item in items:
        if isinstance(item, tuple):
            if len(item) < 2:
                raise ValueError(f'Not enough values in min/max tuple: {item}')
            if len(item) > 2:
                raise ValueError(f'Too many values in min/max tuple: {item}')
            if not isinstance(item[0], (int, float, complex)) and not isinstance(item[0], bool):
                raise TypeError(f'Expected numeric min in tuple, got {type(item[0])}: {item}')
            if not isinstance(item[1], (int, float, complex)) and not isinstance(item[1], bool):
                raise TypeError(f'Expected numeric max in tuple, got {type(item[1])}: {item}')
            if math.isinf(item[0]) or math.isnan(item[0]):
                raise ValueError(f'Expected finite numeric min in min/max tuple, got {item[0]}: {item}')
            if math.isinf(item[1]) or math.isnan(item[1]):
                raise ValueError(f'Expected finite numeric max in min/max tuple, got {item[1]}: {item}')
            if item[0] > item[1]:
                raise ValueError(f'Min must be less than max when using min/max tuples to search: {item}')
        elif isinstance(item, (int, float, complex)) and not isinstance(item, bool):
            if math.isinf(item) or math.isnan(item):
                raise ValueError(f'Expected finite numeric value, got {item}')
        elif not isinstance(item, (int, float, complex)) and not isinstance(item, bool):
            raise TypeError(f'Expected number or min/max tuple, got {type(item)}')

    return ','.join([f'{item[0]}-{item[1]}' if isinstance(item, tuple) else f'{item}' for item in items])
