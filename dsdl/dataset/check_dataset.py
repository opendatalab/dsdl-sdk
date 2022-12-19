from .base_dataset import Dataset
from .utils import check_struct, Report


class CheckDataset(Dataset):

    def __init__(self, report: Report, *args, **kwargs):
        self.report = report
        super().__init__(*args, **kwargs)

    def _load_sample(self):
        """
        该函数的作用是将yaml文件中的样本转换为Struct对象，并存储到sample_list列表中
        """
        sample_list = []
        for sample in self._samples:
            struct_instance, report_info = check_struct(self.sample_type, sample, self.file_reader)
            self.report.add_sample_info(report_info)
            if struct_instance is not None:
                sample_list.append(struct_instance)
        return sample_list

    def _load_global_info(self):
        if self.global_info_type is not None and self._global_info is not None:
            global_info, report_info = check_struct(self.global_info_type, self._global_info, self.file_reader)
            self.report.set_global_info(report_info)
            return global_info
        else:
            return None
