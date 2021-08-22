def get_value_from_key(key, value, var):
    try:
        if isinstance(var, str):
            return
        for item in var:
            if item == key and var[item] == value:
                return var
            if isinstance(item, dict):
                obj = get_value_from_key(key, value, item)
                if obj:
                    return obj
            elif isinstance(var[item], list):
                for i in var[item]:
                    obj = get_value_from_key(key, value, i)
                    if obj:
                        return obj
    except Exception as e:
        print(e)
        pass
