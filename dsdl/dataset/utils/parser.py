class Parser:
    """
    {
        $image: {img: reader_obj},
        $list: {objects: [{bbox: {bbox: xxx}, label: {label: xxx}, extra: {}}]}
        $extra: {}
    }
    -->
    {img: xxx
    objects: []
    }
    """
    @staticmethod
    def flatten_sample(sample, field_name, parse_method=lambda _: _):
        result_dic = {}
        prefix = "."
        Parser._helper(sample, field_name, result_dic, prefix, parse_method)
        return result_dic

    @staticmethod
    def _helper(sample, field_name, result_dic, prefix=".", parse_method=lambda _: _):

        if isinstance(sample, dict):
            for field_type in sample:
                if field_type == field_name:
                    for key, value in sample[field_type].items():
                        k_ = f"{prefix}/{key}"
                        result_dic[k_] = parse_method(value)
                if field_type == "$list":
                    for key, value in sample[field_type].items():
                        k_ = f"{prefix}/{key}"
                        Parser._helper(value, field_name, result_dic, prefix=k_, parse_method=parse_method)

        elif isinstance(sample, list):
            for id, item in enumerate(sample):
                k_ = f"{prefix}/{id}"
                Parser._helper(item, field_name, result_dic, prefix=k_, parse_method=parse_method)


if __name__ == '__main__':
    sample = {
        "$image": {"img2": None, "img1":None},
        "$list": {"objects": [{"$image": {"img1": None}, "$bbox": {"box": None}}],
                  "object2": [{"$bbox":{"box":None}}, {"$bbox":{"box": 1}}], }
    }


    from collections import defaultdict
    dic = defaultdict(defaultdict)


