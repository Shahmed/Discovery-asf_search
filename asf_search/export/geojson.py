from typing import Union
import json

from asf_search import ASFSearchResults, ASFProduct
from .umm_find import umm_find

fields = {
    'beamModeType': ['AdditionalAttributes', ['Name', 'BEAM_MODE_TYPE'], 'Values', 0],
    'browse': ['RelatedUrls', ['Type', 'GET RELATED VISUALIZATION'], 'URL'],
    'bytes': [{'cast': int}, 'AdditionalAttributes', ['Name', 'BYTES'], 'Values', 0],
    'centerLat': [{'cast': float}, 'AdditionalAttributes', ['Name', 'CENTER_LAT'], 'Values', 0],
    'centerLon': [{'cast': float}, 'AdditionalAttributes', ['Name', 'CENTER_LON'], 'Values', 0],
    'faradayRotation': [{'cast': float}, 'AdditionalAttributes', ['Name', 'FARADAY_ROTATION'], 'Values', 0],
    'fileID': ['GranuleUR'],
    'flightDirection': ['AdditionalAttributes', ['Name', 'FLIGHT_DIRECTION'], 'Values', 0],
    'frame': ['AdditionalAttributes', ['Name', 'CENTER_ESA_FRAME'], 'Values', 0],
    'asfFrame': ['AdditionalAttributes', ['Name', 'FRAME_NUMBER'], 'Values', 0],
    'groupID': ['AdditionalAttributes', ['Name', 'GROUP_ID'], 'Values', 0],
    'granuleType': ['AdditionalAttributes', ['Name', 'GRANULE_TYPE'], 'Values', 0],
    'insarStackId': ['AdditionalAttributes', ['Name', 'INSAR_STACK_ID'], 'Values', 0],
    'md5sum': ['AdditionalAttributes', ['Name', 'MD5SUM'], 'Values', 0],
    'offNadirAngle': [{'cast': float}, 'AdditionalAttributes', ['Name', 'OFF_NADIR_ANGLE'], 'Values', 0],
    'orbit': [{'cast': int}, 'OrbitCalculatedSpatialDomains', 0, 'OrbitNumber'],
    'pathNumber': [{'cast': int}, 'AdditionalAttributes', ['Name', 'PATH_NUMBER'], 'Values', 0],
    'platform': ['AdditionalAttributes', ['Name', 'ASF_PLATFORM'], 'Values', 0],
    'pointingAngle': [{'cast': float}, 'AdditionalAttributes', ['Name', 'POINTING_ANGLE'], 'Values', 0],
    'polarization': ['AdditionalAttributes', ['Name', 'POLARIZATION'], 'Values', 0],
    'processingDate': ['DataGranule', 'ProductionDateTime'],
    'processingLevel': ['AdditionalAttributes', ['Name', 'PROCESSING_TYPE'], 'Values', 0],
    'sceneName': ['DataGranule', 'Identifiers', ['IdentifierType', 'ProducerGranuleId'], 'Identifier'],
    'sensor': ['Platforms', 0, 'Instruments', 0, 'ShortName'],
    'startTime': ['TemporalExtent', 'RangeDateTime', 'BeginningDateTime'],
    'stopTime': ['TemporalExtent', 'RangeDateTime', 'EndingDateTime'],
    'url': ['RelatedUrls', ['Type', 'GET DATA'], 'URL']
}


def geojson_dict(products: Union[ASFSearchResults, ASFProduct]):
    if isinstance(products, ASFProduct):
        products = ASFSearchResults(products)

    output = {
            'type': 'FeatureCollection',
            'features': []
    }

    for product in products:
        item = {
            'properties': {},
            'geometry': {
                'coordinates': [],
                'type': 'Polygon'
            }
        }

        coordinates = product.umm['SpatialExtent']['HorizontalSpatialDomain']['Geometry']['GPolygons'][0]['Boundary']['Points']
        coordinates = [[c['Longitude'], c['Latitude']] for c in coordinates]
        item['geometry']['coordinates'] = [coordinates]

        for key in fields:
            item['properties'][key] = umm_find(product.umm, *fields[key])

        item['properties']['fileName'] = item['properties']['url'].split('/')[-1]

        output['features'].append(item)

    return output


def export_geojson(products: Union[ASFSearchResults, ASFProduct]):
    return json.dumps(geojson_dict(products), indent=2, sort_keys=True)
