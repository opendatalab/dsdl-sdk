import os

try:
    import ruamel_yaml as yaml
    from ruamel_yaml import YAML
except ImportError:
    import ruamel.yaml as yaml
    from ruamel.yaml import YAML


class Generation:
    LINESEP_NUM = 1

    def __init__(self, dsdl_version, meta_info, def_info, class_info, data_info, working_dir):
        self._working_dir = working_dir
        self._dsdl_version = dsdl_version
        self._meta_info = meta_info
        self._def_info = def_info
        self._data_info = data_info
        self._class_info = class_info
        self._yaml_obj = self._prepare_yaml_obj()

    def _prepare_yaml_obj(self):
        default_yaml = YAML()
        class_dom_yaml = YAML()
        class_dom_yaml.indent(mapping=4, sequence=4, offset=4)
        sample_yaml = YAML()
        sample_yaml.indent(mapping=4, sequence=4, offset=2)

        result = {"class_dom": class_dom_yaml, "dsdl_version": default_yaml, "meta_info": default_yaml,
                  "struct_def": class_dom_yaml, "samples": sample_yaml, "import": class_dom_yaml}
        return result

    def write_meta(self, file_name=None, path=None):
        meta_info = self._meta_info.copy()
        for k, v in meta_info.items():
            meta_info[k] = self.add_quotes(v)
        if file_name is not None:
            path = os.path.join(self._working_dir, file_name + ".yaml")
        else:
            assert path is not None, "you must provide `file_name` or `path` args"
        with open(path, 'a') as fp:
            self._yaml_obj["meta_info"].dump(meta_info, fp)
            fp.writelines([os.linesep] * self.LINESEP_NUM)

    def write_dsdl_version(self, file_name=None, path=None):
        dsdl_version_info = self._dsdl_version.copy()
        for k, v in dsdl_version_info.items():
            dsdl_version_info[k] = self.add_quotes(v)
        if file_name is not None:
            path = os.path.join(self._working_dir, file_name + ".yaml")
        else:
            assert path is not None, "you must provide `file_name` or `path` args"
        with open(path, 'a') as fp:
            self._yaml_obj["dsdl_version"].dump(dsdl_version_info, fp)
            fp.writelines([os.linesep] * self.LINESEP_NUM)

    @staticmethod
    def add_quotes(string):
        # string = f'"{string}"'
        string = yaml.scalarstring.DoubleQuotedScalarString(string)
        return string

    @staticmethod
    def flist(x):
        x = [Generation.add_quotes(_) for _ in x]
        retval = yaml.comments.CommentedSeq(x)
        retval.fa.set_flow_style()  # fa -> format attribute
        return retval

    @staticmethod
    def fmap(x):
        retval = yaml.comments.CommentedMap(x)
        retval.fa.set_flow_style()  # fa -> format attribute
        return retval

    def write_class_dom(self, file_name=None):
        class_info = self._class_info.copy()
        class_dom_name = class_info.pop('$name')
        file_name = file_name if file_name else class_dom_name
        dst = os.path.join(self._working_dir, file_name + ".yaml")
        self.write_dsdl_version(path=dst)
        with open(dst, "a") as fp:
            self._yaml_obj["class_dom"].dump({class_dom_name: class_info}, fp)
            fp.writelines([os.linesep] * self.LINESEP_NUM)
        return file_name

    def _write_struct_item(self, struct_item, file_name=None, path=None):
        if file_name is not None:
            path = os.path.join(self._working_dir, file_name + ".yaml")
        else:
            assert path is not None, "you must provide `file_name` or `path` args"
        struct_item = struct_item.copy()
        if "$params" in struct_item and isinstance(struct_item["$params"], list):
            struct_item["$params"] = self.flist(struct_item["$params"])
        if "$optional" in struct_item and isinstance(struct_item["$optional"], list):
            struct_item["$optional"] = self.flist(struct_item["$optional"])
        struct_name = struct_item.pop("$name")
        with open(path, "a") as fp:
            self._yaml_obj["struct_def"].dump({struct_name: struct_item}, fp)
            fp.writelines([os.linesep] * self.LINESEP_NUM)

    @staticmethod
    def is_list_of(obj, cls):
        if isinstance(obj, list):
            return isinstance(obj[0], cls)
        return False

    def write_struct_def(self, file_name):

        dst = os.path.join(self._working_dir, file_name + ".yaml")
        self.write_dsdl_version(path=dst)

        for struct_def_item in self._def_info:
            self._write_struct_item(struct_def_item, file_name)
        return file_name

    def write_import_list(self, import_list=None, file_name=None, path=None):
        if not import_list:
            return
        if file_name is not None:
            path = os.path.join(self._working_dir, file_name + ".yaml")
        else:
            assert path is not None, "you must provide `file_name` or `path` args"
        with open(path, "a") as fp:
            self._yaml_obj["import"].dump({"$import": import_list}, fp)
            fp.writelines([os.linesep] * self.LINESEP_NUM)
        return file_name

    def write_samples(self, file_name, import_list=None):

        dst = os.path.join(self._working_dir, file_name + ".yaml")
        self.write_dsdl_version(path=dst)
        self.write_import_list(import_list, path=dst)
        data_info = {"sample-type": self._data_info["sample-type"], "samples": []}
        samples = self._data_info["samples"]
        for sample in samples:
            sample_ = {}
            for k, v in sample.items():
                if self.is_list_of(v, dict):
                    sample_[k] = [self.fmap(_) for _ in v]
                elif isinstance(v, str):
                    sample_[k] = self.add_quotes(v)
                else:
                    sample_[k] = v
            data_info["samples"].append(sample_)

        with open(dst, "a") as fp:
            self._yaml_obj["samples"].dump({"data": data_info}, fp)
