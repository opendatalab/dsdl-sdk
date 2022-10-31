from .registry import CLASSDOMAIN


class Skeleton:

    def __init__(self, skeleton, domain_name=None):
        self._value = skeleton
        self._domain_name = domain_name

    def set_domain(self, domain_name):
        if self._domain_name is None:
            self._domain_name = domain_name

    @property
    def domain_name(self):
        return self._domain_name

    @property
    def class_domain(self):
        return CLASSDOMAIN.get(self.domain_name)

    @property
    def value(self):
        return self._value

    def get_label_pairs(self):
        res = []
        for ind_pair in self._value:
            _p = []
            for ind in ind_pair:
                _p.append(self.class_domain.get_label(ind))
            res.append(_p)
        return res

    def get_point_pairs(self, keypoints):
        label_pairs = self.get_label_pairs()
        res = []
        for pair in label_pairs:
            _p = []
            for label in pair:
                _p.append(keypoints[label.name])
            res.append(_p)
        return res
