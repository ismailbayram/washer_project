def ordereddict_to_dict(value):
    for k, v in value.items():
        if isinstance(v, dict):
            value[k] = ordereddict_to_dict(v)
    return dict(value)

def thumbnail_file_name_by_orginal_name(orginal_name, thumb_name):
    """
    :param orginal_name: String
    :param thumb_name: String
    :return: String
    ex:
    ("kadir.jpg", "20x30")  # kadir_20x30.jpg
    """
    pure_name = "".join(orginal_name.split(".")[0:-1])
    ext_name = orginal_name.split(".")[-1]
    return "{0}_{1}.{2}".format(pure_name, thumb_name, ext_name)
