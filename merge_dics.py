"""
def merge_events(db_event, new_event):
    result = db_event.copy()
    result.update(new_event)
    return result
"""

"""
# Method using set and tuple conversion to ensure uniqueness
def join_unique_dicts(list1:list[dict], list2:list[dict]):
    #Merge two lists of dictionaries, handling nested dictionaries and lists recursively.
    merged_list = []
    all_items = list1 + list2

    while all_items:
        current = all_items.pop(0)
        if isinstance(current, dict):
            # Check if there's a mergeable dictionary in the merged_list
            mergeable_dict = next((item for item in merged_list if isinstance(item, dict) and item.keys() == current.keys()), None)
            if mergeable_dict:
                merged_list[merged_list.index(mergeable_dict)] = merge_events(mergeable_dict, current)
            else:
                merged_list.append(current)
        else:
            merged_list.append(current)  # Directly add non-dictionary items

    return merged_list


def merge_events(db_event: dict, new_event: dict):
    #Merges two event data structures, with `new_event` taking precedence.
    #This function is expanded to handle deep merging and special cases, including lists with complex structures.
    db_event = db_event.copy()  # Make a copy of the existing event data structure to avoid mutating it

    for key, new_value in new_event.items():
        old_value = db_event.get(key)

        # If both values are dictionaries, merge them recursively
        if isinstance(new_value, dict) and isinstance(old_value, dict):
            db_event[key] = merge_events(old_value, new_value)
        # If both values are lists, extend the old list with unique elements from the new list
        elif isinstance(new_value, list) and isinstance(old_value, list):
            if all(isinstance(item, dict) for item in old_value + new_value):  # Handling list of dictionaries
                db_event[key] = join_unique_dicts(old_value, new_value)  # Use set and tuple conversion to ensure uniqueness
            else:  # Handling list of simple types or mixed types
                extended_list = old_value + [item for item in new_value if item not in old_value]
                db_event[key] = extended_list
        else:
            db_event[key] = new_value  # For all other cases, simply overwrite the value

    return db_event

"""

"""
def merge_events(db_event, new_event, pk = None ):
    d1 = db_event.copy()
    d2 = new_event.copy()
    Merge two dictionaries, where the values are lists that can contain dictionaries
    or other objects. If values are lists, it merges their contents, recursively merging
    dictionaries and appending other objects.
    merged = dict(d1)  # Start with the keys and values of the first dictionary

    for key, value in d2.items():
        if key in d1:
            if isinstance(value, list) and isinstance(d1[key], list):
                # Merge lists
                merged_list = []
                for item1, item2 in zip(d1[key], value):
                    if isinstance(item1, dict) and isinstance(item2, dict):
                        # Recursively merge dictionaries
                        merged_list.append(merge_events(item1, item2))
                    else:
                        # Append non-dict objects
                        merged_list.extend([item1, item2])
                merged[key] = merged_list + d1[key][len(merged_list):] + value[len(merged_list):]
            else:
                # Overwrite if not a list or only one is a list
                merged[key] = value
        else:
            # Add the new key from the second dictionary
            merged[key] = value

    return merged

"""
# Configuration that defines the primary keys for merging specific list of dictionaries
config = {"flight_segments.seats": "seat_number", "flight_segments": "trip_number"}


def merge_events(db_event: dict, new_event: dict, config: dict = config, path=""):
    d1 = db_event.copy()
    d2 = new_event.copy()
    merged = d1.copy()

    for key, value in d2.items():

        new_path = f"{path}.{key}".strip(".")
        if key in d1:
            if isinstance(value, list) and isinstance(d1[key], list):

                merged[key] = merge_dic_lists(d1[key], value, config, new_path)
            elif isinstance(value, dict) and isinstance(d1[key], dict):
                merged[key] = merge_events(d1[key], value, config, new_path)
            else:
                merged[key] = value
        else:
            merged[key] = value

    return merged


def merge_dic_lists(list1: list[dict], list2: list[dict], config, path):
    # Fetch the primary key (pk) for merging from the config using the provided path
    pk = config.get(path)

    # If a primary key is specified, merge dictionaries using that key
    if pk:
        merged = {
            item[pk]: item for item in list1 if pk in item
        }  # Existing items in list1
        for item in list2:
            # If item has the primary key and is already in the merged list, merge them
            if pk in item and item[pk] in merged:
                merged[item[pk]] = merge_events(merged[item[pk]], item, config, path)
            elif pk in item:
                merged[item[pk]] = item

        return list(merged.values())

    # If no primary key,replace the list for second one
    return [item for item in list2 if item not in list1]
