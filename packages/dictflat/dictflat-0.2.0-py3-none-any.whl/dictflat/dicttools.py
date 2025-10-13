from typing import Any, Dict, List, Optional, Tuple


def get_dict(d: Optional[Dict] = None) -> Dict:
    """
    Safely returns a dictionary from the input, ensuring a valid dictionary is returned.

    Args:
        d: An optional dictionary to validate. If None or not a dictionary, returns an empty dict.
    Returns:
        A dictionary. If the input is None or not a dictionary, returns an empty dictionary.
        Otherwise, returns the input dictionary unchanged.
    """
    if d is None or not isinstance(d, dict):
        return {}
    return d


def simple_flat(d: Optional[Dict], sep: str = '.', process_lists: bool = True) -> Dict:
    """
    Recursively flattens a nested dictionary structure into a single-level dictionary.
    This function processes a dictionary and converts nested dictionary structures into
    a flat format by concatenating nested keys with the specified separator. When a
    value is a dictionary, its keys are prefixed with the parent key and separator.
    Lists can optionally be processed to flatten any dictionary elements they contain.

    Args:
        d: The dictionary to flatten. If None or not a dictionary, returns an empty dict.
        sep: The string separator used to join nested keys (default: '.').
        process_lists: Whether to process dictionaries inside lists (default: True).
                      If False, dictionaries inside lists will remain unflattened.

    Returns:
        A new dictionary with all nested keys flattened into a single level.
        Nested dictionary keys are combined with their parent keys using the separator.
        For example, {'a': {'b': 1}} becomes {'a.b': 1}.

    Examples:
        >>> simple_flat({'a': {'b': 1, 'c': 2}, 'd': 3})
        {'a.b': 1, 'a.c': 2, 'd': 3}

        >>> simple_flat({'a': {'b': {'c': 1}}, 'd': [1, {'e': 2}]})
        {'a.b.c': 1, 'd': [1, {'e': 2}]}

        >>> simple_flat({'users': [{'name': 'Alice', 'info': {'age': 30}}, {'name': 'Bob'}]})
        {'users': [{'name': 'Alice', 'info.age': 30}, {'name': 'Bob'}]}

        >>> simple_flat({'users': [{'name': 'Alice', 'info': {'age': 30}}]}, process_lists=False)
        {'users': [{'name': 'Alice', 'info': {'age': 30}}]}
    """
    internal_d: Dict = get_dict(d)
    keys: List = list(internal_d.keys())
    for key in keys:
        v: Any = internal_d[key]
        if isinstance(v, dict):
            simple_flat(v, sep=sep, process_lists=process_lists)
            for sk in v:
                internal_d['%s%s%s' % (key, sep, sk)] = v[sk]
            internal_d.pop(key)
        elif process_lists and isinstance(v, list):
            # Handle lists: if an element is a dictionary, apply simple_flat to it
            new_list: List[Any] = []
            for item in v:
                if isinstance(item, dict):
                    new_list.append(simple_flat(item, sep=sep, process_lists=process_lists))
                else:
                    new_list.append(item)
            internal_d[key] = new_list
    return internal_d


def extract_list(d: Optional[Dict]) -> Tuple[Dict, Dict]:
    """
    Extracts and separates list values from a dictionary.

    Processes a dictionary and separates any values that are lists into a separate dictionary,
    while removing those entries from the original dictionary.

    Args:
        d: An optional dictionary to process. If None or not a dictionary, returns empty dicts.

    Returns:
        A tuple containing two dictionaries:
        - First dictionary: Contains only the key-value pairs where the value was a list
        - Second dictionary: Contains all other key-value pairs from the original dictionary

    Example:
        >>> extract_list({'a': [1, 2], 'b': 3, 'c': ['x', 'y']})
        ({'a': [1, 2], 'c': ['x', 'y']}, {'b': 3})
    """
    internal_d: Dict = get_dict(d)
    lists: Dict = {}
    keys: List = list(internal_d.keys())
    for key in keys:
        v: Any = internal_d[key]
        if isinstance(v, list):
            lists[key] = v
            internal_d.pop(key)
    return (lists, internal_d)
