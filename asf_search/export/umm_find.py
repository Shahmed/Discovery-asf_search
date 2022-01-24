from typing import Callable


def umm_find(item: dict, cast: Callable = None, *args):
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
    :param cast: A function to pass the final selected item through for post-processing, such as casting to an int
    :param args: A series of field names, identifying tuples, or numeric indices
    :return: The found item, or None if it does not exist or contains a no-value value such as "NA"
    """
    for key in args:
        if isinstance(key, int):
            item = item[key] if key < len(item) else None
        elif isinstance(key, list):
            (a, b) = key
            found = False
            for child in item:
                if umm_find(child, a) == b:
                    item = child
                    found = True
                    break
            if not found:
                return None
        else:
            item = umm_find(item, key)
        if item is None:
            return None
    if item in [None, 'NA', 'N/A', '']:
        item = None

    if cast is not None:
        return cast(item)

    return item
