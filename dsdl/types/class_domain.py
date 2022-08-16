from ..geometry import Label
from .registry import CLASSDOMAIN, LABEL


class ClassDomainMeta(type):
    def __new__(mcs, name, bases, attributes):
        super_new = super().__new__
        parents = [b for b in bases if isinstance(b, ClassDomainMeta)]
        if not parents:
            return super_new(mcs, name, bases, attributes)

        classes = attributes.pop('Classes', [])
        classes = [_ for _ in classes if isinstance(_, Label)]
        mapping = {}
        for label in classes:
            label.set_domain(name)
            mapping[label.name] = label
            LABEL.registry(label)

        attributes["__mapping__"] = mapping
        attributes["__list__"] = classes
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


class ClassDomain(metaclass=ClassDomainMeta):

    @classmethod
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
                return [name-1]
            else:
                raise IndexError(f"There are only {len(container)} categories in `{cls.__name__}` domain.")
        else:
            raise RuntimeError(f"Invalid key {name}, only int/str keys are permitted.")
