import numpy as np

from dsdl.geometry.registry import CLASSDOMAIN, LABEL
from dsdl.geometry.label import Label
from dsdl.geometry.class_domain_attributes import Skeleton
from jsonschema import validate, FormatChecker

CLASSDOMAIN_ATTRIBUTES = {
    "skeleton": Skeleton,
}


class ClassDomainMeta(type):
    data_schema = {
        "$id": "/classdomain",
        "title": "ClassDomain",
        "description": "Class domain in dsdl.",
        "type": "object",
        "properties": {
            "name": {"type": "string"},
            "classes": {"type": "array", "items": {"type": "string"}},
            "skeleton": {
                "type": "array",
                "items": {
                    "type": "array",
                    "items": {"type": "integer", "minimum": 1},
                    "minItems": 2,
                    "maxItems": 2,
                }
            }
        },
        "required": ["classes", "name"]
    }

    @staticmethod
    def validate_schema(data, schema):
        validate(data, schema, format_checker=FormatChecker())

    def __new__(mcs, name, bases, attributes):
        super_new = super().__new__
        parents = [b for b in bases if isinstance(b, ClassDomainMeta)]
        if not parents:
            return super_new(mcs, name, bases, attributes)
        validate(attributes, mcs.data_schema)
        classes = attributes.pop("classes")
        classes = [Label(_, domain_name=name) for _ in classes]
        mapping = {}
        cat2ind = {}
        for ind, label in enumerate(classes):
            mapping[label.name] = label
            cat2ind[label.name] = ind + 1
            LABEL.registry(label)

        attributes["__cat2ind_mapping__"] = cat2ind
        attributes["__mapping__"] = mapping
        attributes["__list__"] = classes

        attr_dic = {attr_k: CLASSDOMAIN_ATTRIBUTES[attr_k](attributes.pop(attr_k)) for attr_k in
                    CLASSDOMAIN_ATTRIBUTES if attr_k in attributes}
        for attr_k in attr_dic:
            attr_dic[attr_k].set_domain(name)
        attributes["__attributes__"] = attr_dic

        new_cls = super_new(mcs, name, bases, attributes)
        CLASSDOMAIN.register(name, new_cls)
        return new_cls

    def __contains__(cls, item):
        container = getattr(cls, "__mapping__")
        if isinstance(item, str):
            return item in container
        elif hasattr(item, "category_name"):
            return item.category_name in container
        else:
            return False

    def __len__(cls):
        container = getattr(cls, "__list__")
        return len(container)

    def get_labels(cls):
        return getattr(cls, "__list__")

    def get_label_names(cls):
        labels = cls.get_labels()
        return [_.name for _ in labels]

    def get_cat2ind_mapping(cls):
        return getattr(cls, '__cat2ind_mapping__')

    def get_label(cls, name):
        if isinstance(name, str):
            container = getattr(cls, "__mapping__")
            if name in container:
                return container[name]
            else:
                raise KeyError(f"`{cls.__name__}` Domain doesn't have `{name}` category.")
        elif isinstance(name, int):
            container = getattr(cls, "__list__")
            if 1 <= name <= len(container):
                return container[name - 1]
            else:
                raise IndexError(f"There are only {len(container)} categories in `{cls.__name__}` domain.")
        else:
            raise RuntimeError(f"Invalid key {name}, only int/str keys are permitted.")

    def get_attribute(cls, attr_name):
        attr_dic = getattr(cls, "__attributes__")
        return attr_dic.get(attr_name, None)
    
    def get_hierarchy_info(cls):
        class_names_in = [i.category_name for i in cls.__list__]
        single_name_dict = {}
        name_2_index_dict = {}
        for curr_name in class_names_in:
            arrs = curr_name.split(".")[1:]
            for cname in arrs:
                if cname not in single_name_dict:
                    single_name_dict[cname] = 0
        single_class_nums = len(single_name_dict)
        class_names_sort = sorted(list(single_name_dict.keys()))
        relation_metric = np.eye(single_class_nums, single_class_nums)
        for index, key in enumerate(class_names_sort):
            name_2_index_dict[key] = index

        for idx, item in enumerate(class_names_sort):
            curr_dict = {}
            index_list = []
            for class_name in class_names_in:
                name_arrs = class_name.split(".")[1:]
                if item in name_arrs:
                    curr_index = name_arrs.index(item)
                    curr_used_names = name_arrs[:curr_index+1]
                    for used_name in curr_used_names:
                        if used_name not in curr_dict:
                            curr_dict[used_name] = 0
            for ckey in curr_dict:
                m_index = name_2_index_dict[ckey]
                index_list.append(m_index)
                relation_metric[idx, m_index] = 1
        return class_names_sort, relation_metric


def ClassDomain(name, **kwargs):
    class ClassDomainParent(metaclass=ClassDomainMeta):
        pass

    kwargs.update({"__module__": __name__, "__qualname__": name, "name": name})
    return ClassDomainMeta(name, (ClassDomainParent,), kwargs)
