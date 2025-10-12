import json


def save_to_file(data, filename):
    """Saves data to a file in JSON format.

    Args:
        data (list): List of dictionaries to save.
        filename (str): Name of the file to save the data to.
    """   
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


def load_from_file(filename):
    """Loads data from a file in JSON format.

    Args:
        filename (str): Name of the file to load the data from.

    Returns:
        list of dicionary: List of dictionaries loaded from the file.
        If the file does not exist or is empty, returns an empty list.
    """  
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data
    except FileNotFoundError:
        return []
    except json.JSONDecodeError:
        return []
