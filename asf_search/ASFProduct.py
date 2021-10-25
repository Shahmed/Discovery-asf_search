from shapely.geometry import shape, Point
import json

from asf_search import ASFSearchResults
from asf_search import ASFSession


class ASFProduct:
    def __init__(self, args: dict):
        self.properties = args['properties']
        self.geometry = args['geometry']

    def __str__(self):
        return json.dumps(self.geojson(), indent=2, sort_keys=True)

    def geojson(self) -> dict:
        """
        Generates a geojson snippet describing the product
        :return:
        """
        return {
            'type': 'Feature',
            'geometry': self.geometry,
            'properties': self.properties
        }

    def download(
            self,
            path: str,
            filename: str = None,
            session: ASFSession = None
    ) -> None:
        """
        Downloads this product to the specified path and optional filename.

        :param path: The directory into which this product should be downloaded.
        :param filename: Optional filename to use instead of the original filename of this product.
        :param session: The session to use, in most cases should be authenticated beforehand

        :return: None
        """
        from asf_search.download import download_url

        if filename is None:
            filename = self.properties['fileName']

        download_url(url=self.properties['url'], path=path, filename=filename, session=session)

    def stack(
            self,
            start: None,
            end: None,
            strategy=None,  # TODO: add support for alternate reference scene selection strategies
            host: str = None,
            cmr_token: str = None,
            cmr_provider: str = None
    ) -> ASFSearchResults:
        """
        Finds a baseline stack from a reference ASFProduct

        :param start: Earliest date to include in the stack. Default includes all time. If this date excludes the reference, it will not be included in the stack.
        :param end: Latest date to include in the stack. Default includes all time. If this date excludes the reference, it will not be included in the stack.
        :param strategy: If the requested reference can not be used to calculate perpendicular baselines, this sort function will be used to pick an alternative reference from the stack. 'None' implies that no attempt will be made to find an alternative reference.
        :param host: SearchAPI host, defaults to Production SearchAPI. This option is intended for dev/test purposes.
        :param cmr_token: EDL Auth Token for authenticated searches, see https://urs.earthdata.nasa.gov/user_tokens
        :param cmr_provider: Custom provider name to constrain CMR results to, for more info on how this is used, see https://cmr.earthdata.nasa.gov/search/site/docs/search/api.html#c-provider

        :return: ASFSearchResults(dict) of search results
        """

        from asf_search.search import search, get_stack_params, calc_temporal_baselines

        stack_params = get_stack_params(self)
        stack_params['start'] = start
        stack_params['end'] = end
        stack = search(**stack_params, host=host, cmr_token=cmr_token, cmr_provider=cmr_provider)
        calc_temporal_baselines(self, stack)
        stack.sort(key=lambda product: product.properties['temporalBaseline'])

        return stack

    def nearest_neighbors(
            self,
            depth: int = 1,
            host: str = None,
            cmr_token: str = None,
            cmr_provider: str = None
    ) -> ASFSearchResults:
        """
        Returns `depth` temporally nearest neighbors prior to this product

        :param depth: The number of neighbors to find
        :param host: SearchAPI host, defaults to Production SearchAPI. This option is intended for dev/test purposes.
        :param cmr_token: EDL Auth Token for authenticated searches, see https://urs.earthdata.nasa.gov/user_tokens
        :param cmr_provider: Custom provider name to constrain CMR results to, for more info on how this is used, see https://cmr.earthdata.nasa.gov/search/site/docs/search/api.html#c-provider


        :return: ASFSearchResults(list) containing the preceding neighbors
        """
        stack = self.stack(
            end=self.properties['end'],
            host=host,
            cmr_token=cmr_token,
            cmr_provider=cmr_provider)

        return stack[-(depth+1):-1:]

    def centroid(self) -> Point:
        """
        Finds the centroid of a product
        """
        return shape(self.geometry).centroid
