import json
import os
import os.path as osp

from ...types import Struct
from ...objectio import BaseFileReader


def check_struct(sample_type: Struct, sample: dict, file_reader: BaseFileReader):
    report = {"error_flag": False, "warning_flag": False, "normal_flag": True}

    try:
        struct_sample = sample_type(file_reader=file_reader, **sample)
    except Exception as e:
        report["error_msg"] = repr(e)
        report["error_flag"] = True
        report["normal_flag"] = False
        report["sample_content"] = sample
        return None, report

    field_not_matching_msg = []
    field_mappings = sample_type.__mappings__
    optional_mappings = sample_type.__optional__
    for k in field_mappings:
        if k not in sample and k not in optional_mappings:
            warn_msg = f"Field not matching warning: required field '{k}' not found in sample."
            field_not_matching_msg.append(warn_msg)
            report["warning_flag"] = True
            report["normal_flag"] = False
    for k in sample:
        if k not in field_mappings:
            warn_msg = f"Field not matching warning: field key '{k}' in sample is not found in {sample_type.__name__} struct's fields."
            field_not_matching_msg.append(warn_msg)
            report["warning_flag"] = True
            report["normal_flag"] = False
    if not report["normal_flag"]:
        report["sample_content"] = sample
    if field_not_matching_msg:
        report["warning_msgs"] = field_not_matching_msg

    return struct_sample, report


class Report:
    def __init__(self, output_path):
        self.parser_info = None
        self.sample_info = []
        self.image_info = []
        self.output_path = output_path

    def add_sample_info(self, item):
        self.sample_info.append(item)

    def add_image_info(self, item):
        self.image_info.append(item)

    def set_parser_info(self, item):
        self.parser_info = item

    def parse_sample_info(self):
        work_dir = osp.split(self.output_path)[0]
        log_path = osp.join(work_dir, "samples_log.md")
        total_num, normal_num, warn_num, error_num = len(self.sample_info), 0, 0, 0
        with open(log_path, "w") as f:
            f.write("具体异常日志信息如下：" + os.linesep)
            f.write("```json\n")
            for idx, info in enumerate(self.sample_info):
                if info["normal_flag"]:
                    normal_num += int(info["normal_flag"])
                    # f.write(f"status SUCCESS" + os.linesep)
                    continue
                elif info["warning_flag"]:
                    f.write(f"sample {idx}: ")
                    warn_num += int(info["warning_flag"])
                    f.write(f"status WARNING" + "\n")
                    f.write("\twarning messages:" + "\n")
                    for msg in info["warning_msgs"]:
                        f.write("\t\t" + msg + "\n")
                    f.write("\tsample content:" + "\n")
                    f.write("\t\t" + f"{str(info['sample_content'])}" + "\n")
                elif info["error_flag"]:
                    f.write(f"sample {idx}: ")
                    error_num += int(info["error_flag"])
                    f.write("status ERROR" + "\n")
                    f.write("\terror messages:" + "\n")
                    f.write("\t\t" + f"{info['error_msg']}" + "\n")
                    f.write("\tsample content:" + "\n")
                    f.write("\t\t" + f"{str(info['sample_content'])}" + "\n")
            f.write("```" + os.linesep)
        return {"total": total_num, "error": error_num, "warn": warn_num, "normal": normal_num}

    def parse_image_info(self):
        work_dir, _ = osp.split(self.output_path)
        img_dir = osp.join(work_dir, "imgs")
        if not osp.exists(img_dir):
            os.mkdir(img_dir)
        res = []
        msgs = []
        statis = {"success": 0, "fail": 0}
        for idx, img_info in enumerate(self.image_info):
            success_flag = img_info["status"] == "success"
            im = img_info["img"]
            if success_flag:
                img_path = osp.join(img_dir, f"{idx}.png")
                rel_img_path = osp.join("imgs", f"{idx}.png")
                res.append(rel_img_path)
                im.save(img_path)
                msgs.append(f"image {idx} view success!")
                statis["success"] = statis["success"] + 1
            else:
                msgs.append(f"image {idx} view fail! detailed exception info is shown below:"
                            f"{os.linesep}" + img_info['msg'])
                statis["fail"] = statis["fail"] + 1
        return res, msgs, statis

    def generate_parser_info(self, file_handler):
        file_handler.write("## 1.解析器验证结果" + os.linesep)
        success_flag = self.parser_info["flag"] == 1
        file_handler.write(
            f"解析结果：{'<font color=green>SUCCESS</font>' if success_flag else '<font color=red>FAIL</font>'}" + os.linesep)
        file_handler.write("具体信息如下：" + os.linesep)
        file_handler.write("```python" + os.linesep)
        file_handler.write(json.dumps(self.parser_info, indent=2, ensure_ascii=False))
        file_handler.write(os.linesep + "```" + os.linesep)
        return success_flag

    def generate_sample_info(self, file_handler):
        if not self.sample_info:
            return False
        file_handler.write("## 2.样本验证结果" + os.linesep)
        res = self.parse_sample_info()
        total_num, normal_num, warn_num, error_num = res["total"], res["normal"], res["warn"], res["error"]
        file_handler.write("samples验证结果如下：" + os.linesep)
        res_str = f"共实例化<font color=blue>{total_num}</font>个样本，" \
                  f"其中<font color=green>{normal_num}</font>个样本实例化正常，" \
                  f"<font color=orange>{warn_num}</font>个样本出现警报信息，" \
                  f"<font color=red>{error_num}</font>个样本实例化失败。"
        file_handler.write(res_str + os.linesep)
        file_handler.write("查看具体日志信息请[点击链接](./samples_log.md)" + os.linesep)
        return True

    def generate_image_info(self, file_handler):
        if not self.image_info:
            return False

        res, msgs, statis = self.parse_image_info()
        file_handler.write("## 3.部分样本可视化结果" + os.linesep)
        file_handler.write(f"共可视化<font color=blue>{len(self.image_info)}</font>个样本，"
                           f"其中<font color=green>{statis['success']}</font>个样本可视化成功，"
                           f"<font color=red>{statis['fail']}</font>个样本可视化失败" + os.linesep)
        for img in res:
            img_name = osp.split(img)[-1]
            file_handler.write(f"![{img_name}]({img})" + os.linesep)
        file_handler.write(f"具体日志信息如下：" + os.linesep + "```\n")
        for msg in msgs:
            file_handler.write(msg + "\n")
        file_handler.write("```" + os.linesep)
        return True

    def generate(self):
        with open(self.output_path, "w", encoding="utf-8") as f:
            f.write("# 数据集验证报告" + os.linesep)
            if self.parser_info:
                self.generate_parser_info(f)
            if self.sample_info:
                self.generate_sample_info(f)
            if self.image_info:
                self.generate_image_info(f)
        return
