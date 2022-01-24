def translate_product(item: dict) -> dict:
    umm = item['umm']

    coordinates = umm['SpatialExtent']['HorizontalSpatialDomain']['Geometry']['GPolygons'][0]['Boundary']['Points']
    coordinates = [[c['Longitude'], c['Latitude']] for c in coordinates]
    geometry = {'coordinates': [coordinates], 'type': 'Polygon'}

    properties = {
        'beamModeType': get(umm, 'AdditionalAttributes', ('Name', 'BEAM_MODE_TYPE'), 'Values', 0),
        'browse': get(umm, 'RelatedUrls', ('Type', 'GET RELATED VISUALIZATION'), 'URL'),
        'bytes': cast(int, get(umm, 'AdditionalAttributes', ('Name', 'BYTES'), 'Values', 0)),
        'centerLat': cast(float, get(umm, 'AdditionalAttributes', ('Name', 'CENTER_LAT'), 'Values', 0)),
        'centerLon': cast(float, get(umm, 'AdditionalAttributes', ('Name', 'CENTER_LON'), 'Values', 0)),
        'faradayRotation': cast(float, get(umm, 'AdditionalAttributes', ('Name', 'FARADAY_ROTATION'), 'Values', 0)),
        'fileID': get(umm, 'GranuleUR'),
        'flightDirection': get(umm, 'AdditionalAttributes', ('Name', 'FLIGHT_DIRECTION'), 'Values', 0),
        'groupID': get(umm, 'AdditionalAttributes', ('Name', 'GROUP_ID'), 'Values', 0),
        'granuleType': get(umm, 'AdditionalAttributes', ('Name', 'GRANULE_TYPE'), 'Values', 0),
        'insarStackId': get(umm, 'AdditionalAttributes', ('Name', 'INSAR_STACK_ID'), 'Values', 0),
        'md5sum': get(umm, 'AdditionalAttributes', ('Name', 'MD5SUM'), 'Values', 0),
        'offNadirAngle': cast(float, get(umm, 'AdditionalAttributes', ('Name', 'OFF_NADIR_ANGLE'), 'Values', 0)),
        'orbit': cast(int, get(umm, 'OrbitCalculatedSpatialDomains', 0, 'OrbitNumber')),
        'pathNumber': cast(int, get(umm, 'AdditionalAttributes', ('Name', 'PATH_NUMBER'), 'Values', 0)),
        'platform': get(umm, 'AdditionalAttributes', ('Name', 'ASF_PLATFORM'), 'Values', 0),
        'pointingAngle': cast(float, get(umm, 'AdditionalAttributes', ('Name', 'POINTING_ANGLE'), 'Values', 0)),
        'polarization': get(umm, 'AdditionalAttributes', ('Name', 'POLARIZATION'), 'Values', 0),
        'processingDate': get(umm, 'DataGranule', 'ProductionDateTime'),
        'processingLevel': get(umm, 'AdditionalAttributes', ('Name', 'PROCESSING_TYPE'), 'Values', 0),
        'sceneName': get(umm, 'DataGranule', 'Identifiers', ('IdentifierType', 'ProducerGranuleId'), 'Identifier'),
        'sensor': get(umm, 'Platforms', 0, 'Instruments', 0, 'ShortName'),
        'startTime': get(umm, 'TemporalExtent', 'RangeDateTime', 'BeginningDateTime'),
        'stopTime': get(umm, 'TemporalExtent', 'RangeDateTime', 'EndingDateTime'),
        'url': get(umm, 'RelatedUrls', ('Type', 'GET DATA'), 'URL')
    }

    # TODO: abstract the above list into a generic outputter class, with subclasses for each format (csv, geojson, kml, metalink, etc)

    properties['fileName'] = properties['url'].split('/')[-1]

    asf_frame_platforms = ['Sentinel-1A', 'Sentinel-1B', 'ALOS']
    if properties['platform'] in asf_frame_platforms:
        properties['frameNumber'] = get(umm, 'AdditionalAttributes', ('Name', 'FRAME_NUMBER'), 'Values', 0)
    else:
        properties['frameNumber'] = get(umm, 'AdditionalAttributes', ('Name', 'CENTER_ESA_FRAME'), 'Values', 0)

    return {'geometry': geometry, 'properties': properties, 'type': 'Feature'}


def cast(f, v):
    try:
        return f(v)
    except TypeError:
        return None


def get(item: dict, *args):
    """
    Used to drill through CMR style UMM JSON to find specific fields and values. Accepts a list of field names, tuples, or indices. Matches each arg in order, working further into the data structure with each step.
    - If the arg is a string, the first item matching that name is selected
    - If the arg is an integer, it is expected that the current match is a list, and the item at the specified index is selected
    - If the arg is a tuple, the first item with a child field named by the first value in the tuple that has a value specified by the second value in the tuple is selected
    Example:
    Given the following data structure, each line has the corresponding set of arguments to return that item:
    data = {
      'item1': 'foo',            # 'item1'
      'item2': 'bar',            # 'item2'
      'item3': [                 # 'item3'
        {                        # 'item3', ('name', 'somefield1')     or 'item3', 0
          'name': 'somefield1',
          'value': 'a'           # 'item3', ('name', 'somefield1'), 'value'
        },
        {                        # 'item3', ('name', 'somefield2')     or 'item3', 1
          'name': 'somefield2',
          'value': [             # 'item3', ('name', 'somefield2'), 'value'
            'x',                 # 'item3', ('name', 'somefield2'), 'value', 0
            'y',                 # 'item3', ('name', 'somefield2'), 'value', 1
            'z'                  # 'item3', ('name', 'somefield2'), 'value', 2
          ]
      ]
    }
    :param item: The item from which to begin the search. Typically the `umm` field of CMR search results.
    :param args: A series of field names, identifying tuples, or numeric indices
    :return: The found item, or None if it does not exist or contains a no-value value such as "NA"
    """
    for key in args:
        if isinstance(key, int):
            item = item[key] if key < len(item) else None
        elif isinstance(key, tuple):
            (a, b) = key
            found = False
            for child in item:
                if get(child, a) == b:
                    item = child
                    found = True
                    break
            if not found:
                return None
        else:
            item = item.get(key)
        if item is None:
            return None
    if item in [None, 'NA', 'N/A', '']:
        item = None
    return item
