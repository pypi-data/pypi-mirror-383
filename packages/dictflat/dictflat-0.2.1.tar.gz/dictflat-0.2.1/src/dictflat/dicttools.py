from typing import Any, Dict, List, Optional, Tuple, Union


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


def get_nested_value(
    d: Optional[Dict],
    path: Union[str, List[str]],
    sep: str = ".",
    default: Any = None
) -> Any:
    """
    Retrieves a nested value from a dictionary using a path, handling multiple levels of nested dictionaries.

    Args:
        d: An optional dictionary to search. If None or not a dictionary, returns the default value.
        path: The path to the nested value, either as a string with separators or a list of keys.
        sep: The separator used in the path string (default: '.').
        default: The default value to return if the path does not exist (default: None).

    Returns:
        The value at the specified path, or the default value if the path does not exist.

    Examples:
        >>> get_nested_value({'a': {'b': {'c': 1}}}, 'a.b.c')
        1

        >>> get_nested_value({'a': {'b': {'c': {'d': 2}}}}, ['a', 'b', 'c', 'd'])
        2

        >>> get_nested_value({'a': {'b': 1}}, 'a.c', default=0)
        0

        >>> get_nested_value({'a': {'b': {'c': {'d': {'e': 5}}}}}, 'a.b.c.d.e')
        5
    """
    if not d:
        return default

    internal_d: Dict = get_dict(d)

    if isinstance(path, str):
        keys: List[str] = path.split(sep)
    else:
        keys = path

    current: Any = internal_d
    for key in keys:
        if not isinstance(current, dict) or key not in current:
            return default
        current = current[key]

    return current


def set_nested_value(
    d: Dict,
    path: Union[str, List[str]],
    value: Any,
    sep: str = ".",
    is_list: bool = False,
    uniq: bool = False,
    transform_to_list: bool = False,
) -> Dict:
    """
    Sets a nested value in a dictionary using a path, handling multiple levels of nested dictionaries.
    Can optionally add the value to a list at the specified path.

    Args:
        d: The dictionary to modify.
        path: The path to the nested value, either as a string with separators or a list of keys.
        value: The value to set at the specified path.
        sep: The separator used in the path string (default: '.').
        is_list: If True, the value will be added to a list at the specified path (default: False).
        uniq: If True and is_list is True, the value will only be added if it's not already in the list (default: False).
        transform_to_list: If True and is_list is True, and the key exists with a non-list value,
                          the existing value will be converted to a list and the new value will be added (default: False).

    Returns:
        The modified dictionary with the nested value set.

    Examples:
        >>> set_nested_value({'a': {'b': {'c': 1}}}, 'a.b.c', 2)
        {'a': {'b': {'c': 2}}}

        >>> set_nested_value({'a': {'b': {'c': {'d': 2}}}}, ['a', 'b', 'c', 'd'], 3)
        {'a': {'b': {'c': {'d': 3}}}}

        >>> set_nested_value({'a': {'b': 1}}, 'a.c', 0)
        {'a': {'b': 1, 'c': 0}}

        >>> set_nested_value({'a': {'b': {'c': {'d': {'e': 5}}}}}, 'a.b.c.d.e', 6)
        {'a': {'b': {'c': {'d': {'e': 6}}}}}

        >>> set_nested_value({'a': {'b': []}}, 'a.b', 1, is_list=True)
        {'a': {'b': [1]}}

        >>> set_nested_value({'a': {'b': [1, 2]}}, 'a.b', 3, is_list=True)
        {'a': {'b': [1, 2, 3]}}

        >>> set_nested_value({'a': {'b': [1, 2]}}, 'a.b', 2, is_list=True, uniq=True)
        {'a': {'b': [1, 2]}}

        >>> set_nested_value({'a': {'b': [1, 2]}}, 'a.b', 2, is_list=True, uniq=False)
        {'a': {'b': [1, 2, 2]}}

        >>> set_nested_value({'a': {'b': 1}}, 'a.b', 2, is_list=True, transform_to_list=True)
        {'a': {'b': [1, 2]}}
    """
    if not isinstance(d, dict):
        raise ValueError("The input must be a dictionary.")

    if isinstance(path, str):
        keys: List[str] = path.split(sep)
    else:
        keys = path

    current: Dict = d
    for key in keys[:-1]:
        if key not in current or not isinstance(current[key], dict):
            current[key] = {}
        current = current[key]

    last_key: str = keys[-1]
    if is_list:
        if last_key not in current:
            current[last_key] = [value]
        elif not isinstance(current[last_key], list):
            if transform_to_list:
                if not uniq or value != current[last_key]:
                    current[last_key] = [current[last_key], value]
                else:
                    current[last_key] = [current[last_key]]
            else:
                current[last_key] = [value]
        elif not uniq or value not in current[last_key]:
            current[last_key].append(value)
    else:
        current[last_key] = value

    return d
