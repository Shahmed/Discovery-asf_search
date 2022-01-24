from asf_search.ASFSearchOptions import ASFSearchOptions


"""
Supported input parameters and their associated CMR parameters
"""
#   Search parameter        CMR parameter               CMR format string
cmr_field_map = {
    'absoluteOrbit':        ['orbit_number',            '{0}'],
    'asfFrame':             ['attribute[]',             'int,FRAME_NUMBER,{0}'],
    'beamMode':             ['attribute[]',             'string,BEAM_MODE,{0}'],
    'beamSwath':            ['attribute[]',             'string,BEAM_MODE_TYPE,{0}'],
    'cmr_provider':         ['provider',                '{0}'],
    'collectionName':       ['attribute[]',             'string,MISSION_NAME,{0}'],
    'maxDoppler':           ['attribute[]',             'float,DOPPLER,,{0}'],
    'minDoppler':           ['attribute[]',             'float,DOPPLER,{0},'],
    'maxFaradayRotation':   ['attribute[]',             'float,FARADAY_ROTATION,,{0}'],
    'minFaradayRotation':   ['attribute[]',             'float,FARADAY_ROTATION,{0},'],
    'flightDirection':      ['attribute[]',             'string,ASCENDING_DESCENDING,{0}'],
    'flightLine':           ['attribute[]',             'string,FLIGHT_LINE,{0}'],
    'frame':                ['attribute[]',             'int,CENTER_ESA_FRAME,{0}'],
    'granule_list':         ['readable_granule_name[]', '{0}'],
    'product_list':         ['granule_ur[]',            '{0}'],
    'intersectsWith':       [None,                      '{0}'],
    'lookDirection':        ['attribute[]',             'string,LOOK_DIRECTION,{0}'],
    'offNadirAngle':        ['attribute[]',             'float,OFF_NADIR_ANGLE,{0}'],
    'platform':             ['platform[]',              '{0}'],
    'polarization':         ['attribute[]',             'string,POLARIZATION,{0}'],
    'processingLevel':      ['attribute[]',             'string,PROCESSING_TYPE,{0}'],
    'relativeOrbit':        ['attribute[]',             'int,PATH_NUMBER,{0}'],
    'processingDate':       ['updated_since',           '{0}'],
    'start':                [None,                      '{0}'],
    'end':                  [None,                      '{0}'],
    'season':               [None,                      '{0}'],
    'temporal':             ['temporal',                '{0}'],  # start/end/season end up here
    'groupId':              ['attribute[]',             'string,GROUP_ID,{0}'],
    'insarStackId':         ['attribute[]',             'int,INSAR_STACK_ID,{0}'],
    'instrument':           ['instrument[]',            '{0}']
}


def translate_opts(opts: ASFSearchOptions) -> list:
    # Start by just grabbing the searchable parameters
    dict_opts = dict(opts)

    # convert the above parameters to a list of key/value tuples
    cmr_opts = []
    for (key, val) in dict_opts.items():
        if isinstance(val, list):
            for x in val:
                cmr_opts.append((key, x))
        else:
            cmr_opts.append((key, val))

    # translate the above tuples to CMR key/values
    for i, opt in enumerate(cmr_opts):
        cmr_opts[i] = cmr_field_map[opt[0]]['key'], cmr_field_map[opt[0]]['fmt'].format(opt[1])

    return cmr_opts
