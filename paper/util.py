
def merge_dictionary(target, new_dict):
    for k, v in new_dict.items():
        if isinstance(target.get(k, None), dict) and isinstance(v, dict):
            merge_dictionary(target[k], v)
        elif isinstance(v, list):
            if isinstance(target.get(k, None), list):
                 target[k].extend(v)
            else:
                target[k] = v
        else:
            if k in target and v.startswith("[") and v.endswith("]"):
                continue
            target[k] = v
