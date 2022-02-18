from asf_search.search.CMR.Query import format_query_params, format_list_params, translate_param
from asf_search.search.CMR.translate import input_map

def run_test_query_translate_param(asfListParam, cmrListParam):
    formatted = format_list_params(asfListParam)
    assert formatted == cmrListParam
    # for param, param_val in asfListParam.items():
        # translated_param = translate_param(param, param_val)
        # assert translated_param[0] == { input_map()[param][0]: cmrListParam[input_map()[param][0]]}