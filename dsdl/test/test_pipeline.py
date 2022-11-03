import pytest
from dataclasses import dataclass, field
from click.testing import CliRunner
from glob import glob
from typing import List, TextIO, Union
import os
from enum import Enum
from tunas2dsdl.cli import convert
from tunas2dsdl_c.dsdl_yaml_script import ConvertV3toDsdlYaml
from ..parser import dsdl_parse
from ..tools import view
from pylint import epylint as lint
from ..test.config import config
import pathlib



@dataclass()
class DsdlTask:
    data_tunas_path: str
    data_dsdl_path: str
    data_name_list: List[str] = field(default_factory=list)

    def __post_init__(self):
        self.test_dir_list = []
        for dataset_name in self.data_name_list:
            dst = os.path.join(self.data_tunas_path, dataset_name)
            dst_dsdl = os.path.join(self.data_dsdl_path, dataset_name)
            self.test_dir_list.append((dst, dst_dsdl))


class TaskEnum(Enum):
    CLS = "classification"
    DETE = "detection"
    SEG = "segmentation"
    KP = "keypoints"


CLAS_TASK = DsdlTask(
    data_tunas_path=config.v3_folder_classification,
    data_dsdl_path=config.dsdl_folder_classification,
    data_name_list=config.dataset_list_cls,
)
DETE_TASK = DsdlTask(
    data_tunas_path=config.v3_folder_detection,
    data_dsdl_path=config.dsdl_folder_detection,
    data_name_list=config.dataset_list_det,
)
SEG_TASK = DsdlTask(
    data_tunas_path=config.v3_folder_detection,
    data_dsdl_path=config.dsdl_folder_detection,
    data_name_list=config.dataset_list_det,
)


def _validate_view(yaml_path: str, task_type: TaskEnum, logger: TextIO):
    logger.write(f"Test view {yaml_path}: \n")
    runner = CliRunner()
    if task_type == TaskEnum.DETE:
        result = runner.invoke(
            view,
            [
                "-y",
                yaml_path,
                "-c",
                config.config_path,
                "-l",
                "ali-oss",
                "-n",
                5,
                "-f",
                "Label BBox Polygon",
                "-p",
                os.path.dirname(yaml_path),
            ],
        )
    elif task_type == TaskEnum.CLS:
        result = runner.invoke(
            view,
            [
                "-y",
                yaml_path,
                "-c",
                config.config_path,
                "-l",
                "ali-oss",
                "-n",
                5,
                "-f",
                "Label",
                "-p",
                os.path.dirname(yaml_path),
            ],
        )
    else:
        raise TypeError(f"Unsupported task type: {task_type}.")
    if result.exit_code == 0:
        logger.write("success.\n")
        # logger.write(f"{result.output}\n")
    else:
        err_msg = f"Error in view code task: {yaml_path})."
        logger.write(f"{err_msg}\n\n")
        raise Exception(err_msg)


def test_python_file(temp_file: Union[str, pathlib.Path], logger: TextIO):
    (pylint_stdout, pylint_stderr) = lint.py_run(
        f"{temp_file} --errors-only", return_std=True
    )  # --msg-template={msg_id}
    if len(pylint_stdout.getvalue()) != 0:
        logger.write(f"{pylint_stdout.getvalue()}\n")
        raise Exception(pylint_stdout.getvalue())


def _validate_parser(yaml_path: Union[str, pathlib.Path], logger: TextIO):
    logger.write(f"Test parse {yaml_path}: \n")
    try:
        temp_file_path = "temp.py"
        library_path = os.path.dirname(yaml_path)
        dsdl_parse(yaml_path, library_path, temp_file_path)
        test_python_file(temp_file_path, logger)
        os.remove(temp_file_path)
        logger.write(f"success\n")
    except Exception:
        err_msg = f"Error in parser code task: {yaml_path}."
        logger.write(f"{err_msg}\n\n")
        raise Exception(err_msg)


class TestPipe:
    def setup_class(self):
        print("\nhere is setup_class")
        self.CLAS_TASK = DsdlTask(
            data_tunas_path=config.v3_folder_classification,
            data_dsdl_path=config.dsdl_folder_classification,
            data_name_list=config.dataset_list_cls,
        )
        self.DETE_TASK = DsdlTask(
            data_tunas_path=config.v3_folder_detection,
            data_dsdl_path=config.dsdl_folder_detection,
            data_name_list=config.dataset_list_det,
        )
        self.SEG_TASK = DsdlTask(
            data_tunas_path=config.v3_folder_detection,
            data_dsdl_path=config.dsdl_folder_detection,
            data_name_list=config.dataset_list_det,
        )
        if os.path.isfile(config.logger_path):
            os.remove(config.logger_path)
        if os.path.isfile(config.logger_path):
            os.remove(config.logger_path)
        self.logger = open(config.logger_path, "a")

    @pytest.mark.parametrize('tunas_dir, dsdl_dir', CLAS_TASK.test_dir_list)
    def test_cls_tunas2dsdl(self, tunas_dir, dsdl_dir):
        self.logger.write(f"Test {TaskEnum.CLS} tunas2dsdl\n")
        try:
            self.logger.write(f"convert {os.path.basename(tunas_dir)}: \n")
            v3toyaml = ConvertV3toDsdlYaml(
                dataset_path=tunas_dir, output_path=dsdl_dir
            )
            v3toyaml.convert_pipeline()
        except Exception:
            err_msg = f"Error in tunas to dsdl code ({TaskEnum.CLS} task)."
            self.logger.write(f"{err_msg}\n\n")
            raise Exception(err_msg)
        else:
            self.logger.write("success.\n\n")

    @pytest.mark.parametrize('tunas_dir, dsdl_dir', DETE_TASK.test_dir_list)
    def test_det_tunas2dsdl(self, tunas_dir, dsdl_dir):
        self.logger.write(f"Test {TaskEnum.DETE} tunas2dsdl\n")
        runner = CliRunner()
        result = runner.invoke(convert,
                ["-d", str(tunas_dir), "-w", str(dsdl_dir), "-t", "detection", "-s"]
        )
        if result.exit_code == 0:
            self.logger.write("success.\n")
            self.logger.write(result.output)
        else:
            self.logger.write(f"failed: ")
            err_msg = f"Error in tunas to dsdl code ({TaskEnum.DETE}: {os.path.basename(tunas_dir)})."
            self.logger.write(f"{err_msg}\n")
            raise Exception(err_msg)

    @pytest.mark.skip(reason="tunas2dsdl seg api is unfinished model")
    def test_seg_tunas2dsdl(self):
        for tunas_dir, dsdl_dir in self.SEG_TASK.test_dir_list:
            runner = CliRunner()
            result = runner.invoke(convert,
                    ["-d", str(tunas_dir), "-w", str(dsdl_dir), "-t", "detection", "-s"]
            )
            if result.exit_code == 0:
                self.logger.write("success.")
                self.logger.write(result.output)
            else:
                self.logger.write("failed.")

    @pytest.mark.parametrize('_, dsdl_folder', CLAS_TASK.test_dir_list)
    def test_parser_cls_dsdl(self, _, dsdl_folder):
        for file in glob(os.path.join(dsdl_folder, "*_data.yaml")):
            _validate_parser(file, self.logger)

    @pytest.mark.parametrize('_, dsdl_folder', DETE_TASK.test_dir_list)
    def test_parser_det_dsdl(self, _, dsdl_folder):
        for seg_folder in os.listdir(dsdl_folder):
            if os.path.isdir(os.path.join(dsdl_folder, seg_folder)):
                file = os.path.join(dsdl_folder, seg_folder, seg_folder + ".yaml")
                if os.path.exists(file):
                    _validate_parser(file, self.logger)

    @pytest.mark.parametrize('_, dsdl_folder', CLAS_TASK.test_dir_list)
    def test_view_cls_dsdl(self, _, dsdl_folder):
        for file in glob(os.path.join(dsdl_folder, "*_data.yaml")):
            _validate_view(file, TaskEnum.CLS, self.logger)

    @pytest.mark.parametrize('_, dsdl_folder', DETE_TASK.test_dir_list)
    def test_view_det_dsdl(self, _, dsdl_folder):
        for seg_folder in os.listdir(dsdl_folder):
            if os.path.isdir(os.path.join(dsdl_folder, seg_folder)):
                file = os.path.join(dsdl_folder, seg_folder, seg_folder + ".yaml")
                if os.path.exists(file):
                    _validate_view(file, TaskEnum.DETE, self.logger)

    def teardown_class(self):
        self.logger.close()
