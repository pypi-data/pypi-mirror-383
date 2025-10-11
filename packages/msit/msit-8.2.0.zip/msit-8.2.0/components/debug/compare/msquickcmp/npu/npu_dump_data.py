# -*- coding: utf-8 -*-
# Copyright (c) 2024-2024 Huawei Technologies Co., Ltd.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Function:
This class mainly involves generate npu dump data function.
"""
import json
import sys
import os
import stat
import re
import shutil

import numpy as np

from msquickcmp.atc import atc_utils
from msquickcmp.common import utils
from msquickcmp.common.dump_data import DumpData
from msquickcmp.common.utils import AccuracyCompareException, parse_input_shape_to_list
from msquickcmp.common.dynamic_argument_bean import DynamicArgumentEnum
from msquickcmp.npu.om_parser import OmParser

from components.utils.check.rule import Rule
from components.utils.util import load_file_to_read_common_check
from components.utils.file_open_check import ms_open


BENCHMARK_DIR = "benchmark"
ACL_JSON_PATH = "acl.json"
NPU_DUMP_DATA_BASE_PATH = "dump_data/npu"
NPU_DUMP_DATA_GOLDEN_PATH = "dump_data/npu_golden"
RESULT_DIR = "result"
INPUT = "input"
INPUT_SHAPE = "--input_shape"
OUTPUT_SIZE = "--outputSize"
INPUT_FORMAT_TO_RGB_RATIO_DICT = {"YUV420SP_U8": 2, "RGB888_U8": 1, "YUV400_U8": 3, "XRGB8888_U8": 3 / 4}
OPEN_FLAGS = os.O_WRONLY | os.O_CREAT | os.O_TRUNC
OPEN_MODES = stat.S_IWUSR | stat.S_IRUSR
DTYPE_MAP = {
    "dtype.float32": np.float32,
    "dtype.float16": np.float16,
    "dtype.float64": np.float64,
    "dtype.int8": np.int8,
    "dtype.int16": np.int16,
    "dtype.int32": np.int32,
    "dtype.int64": np.int64,
    "dtype.uint8": np.uint8,
    "dtype.uint16": np.uint16,
    "dtype.uint32": np.uint32,
    "dtype.uint64": np.uint64,
    "dtype.bool": np.bool_,
}


class DynamicInput(object):
    def __init__(self, om_parser, input_shape):
        self.input_shape = input_shape
        self.om_parser = om_parser
        self.atc_dynamic_arg, self.cur_dynamic_arg = self.get_dynamic_arg_from_om(om_parser)
        self.dynamic_arg_value = self.get_arg_value(om_parser, input_shape)

    @staticmethod
    def get_dynamic_arg_from_om(om_parser):
        atc_cmd_args = om_parser.get_atc_cmdline().split(" ")
        for i, atc_arg in enumerate(atc_cmd_args):
            for dym_arg in DynamicArgumentEnum:
                if dym_arg.value.atc_arg in atc_arg:
                    if dym_arg.value.atc_arg == atc_arg:
                        atc_arg += '=' + atc_cmd_args[i + 1]
                    return atc_arg, dym_arg
        return "", None

    @staticmethod
    def get_input_shape_from_om(om_parser):
        # get atc input shape from atc cmdline
        atc_input_shape = ""
        atc_cmd_args = om_parser.get_atc_cmdline().split(" ")
        for i, atc_arg in enumerate(atc_cmd_args):
            if INPUT_SHAPE == atc_arg:
                atc_input_shape = atc_cmd_args[i + 1]
                break
            if atc_arg.startswith(INPUT_SHAPE + utils.EQUAL):
                atc_input_shape = atc_arg.split(utils.EQUAL)[1]
                break
        return atc_input_shape

    @staticmethod
    def get_arg_value(om_parser, input_shape):
        is_dynamic_scenario, scenario = om_parser.get_dynamic_scenario_info()
        if not is_dynamic_scenario:
            utils.logger.info("The input of model is not dynamic.")
            return ""
        if om_parser.shape_range or scenario == DynamicArgumentEnum.DYM_DIMS:
            return input_shape
        atc_input_shape = DynamicInput.get_input_shape_from_om(om_parser)
        # from atc input shape and current input shape to get input batch size
        # if dim in shape is -1, the shape in the index of current input shape is the batch size
        atc_input_shape_dict = utils.parse_input_shape(atc_input_shape)
        quickcmp_input_shape_dict = utils.parse_input_shape(input_shape)
        batch_size_set = set()
        for op_name in atc_input_shape_dict.keys():
            DynamicInput.get_dynamic_dim_values(
                atc_input_shape_dict.get(op_name), quickcmp_input_shape_dict.get(op_name), batch_size_set
            )
        if len(batch_size_set) == 1:
            for batch_size in batch_size_set:
                return str(batch_size)
        utils.logger.error("Please check your input_shape arg is valid.")
        raise AccuracyCompareException(utils.ACCURACY_COMPARISON_INVALID_PARAM_ERROR)

    @staticmethod
    def get_dynamic_dim_values(dym_shape, cur_shape, shape_values):
        for dim, _ in enumerate(dym_shape):
            if dym_shape[dim] != "-1":
                continue
            if isinstance(shape_values, list):
                shape_values.append(int(cur_shape[dim]))
            else:
                shape_values.add(cur_shape[dim])

    def add_dynamic_arg_for_benchmark(self, benchmark_cmd: list):
        if self.is_dynamic_shape_scenario():
            self.check_input_dynamic_arg_valid()
            benchmark_cmd.append(self.cur_dynamic_arg.value.benchmark_arg)
            benchmark_cmd.append(self.dynamic_arg_value)

    def is_dynamic_shape_scenario(self):
        """
        if atc cmdline contain dynamic argument
        """
        return self.atc_dynamic_arg != ""

    def judge_dynamic_shape_scenario(self, atc_dym_arg):
        """
        check the dynamic shape scenario
        """
        return self.atc_dynamic_arg.split(utils.EQUAL)[0] == atc_dym_arg

    def check_input_dynamic_arg_valid(self):
        if self.cur_dynamic_arg is DynamicArgumentEnum.DYM_SHAPE:
            return
        # check dynamic input value is valid, "--arg=value" ,split by '='
        dynamic_arg_values = self.atc_dynamic_arg.split(utils.EQUAL)[1]
        if self.judge_dynamic_shape_scenario(DynamicArgumentEnum.DYM_DIMS.value.atc_arg):
            self.check_dynamic_dims_valid(dynamic_arg_values)
            return
        if self.judge_dynamic_shape_scenario(DynamicArgumentEnum.DYM_BATCH.value.atc_arg):
            self.check_dynamic_batch_valid(dynamic_arg_values)

    def check_dynamic_batch_valid(self, atc_dynamic_arg_values):
        dynamic_arg_values = atc_dynamic_arg_values.replace(utils.COMMA, utils.SEMICOLON)
        try:
            atc_value_list = utils.parse_arg_value(dynamic_arg_values)
            cur_input = utils.parse_value_by_comma(self.dynamic_arg_value)
        except AccuracyCompareException as err:
            utils.logger.error(
                "Please input the valid shape, " "the valid dynamic value range are {}".format(dynamic_arg_values)
            )
            raise AccuracyCompareException(utils.ACCURACY_COMPARISON_INVALID_PARAM_ERROR) from err
        for value in atc_value_list:
            if cur_input == value:
                return

    def check_dynamic_dims_valid(self, atc_dynamic_arg_values):
        atc_input_shape = DynamicInput.get_input_shape_from_om(self.om_parser)
        try:
            atc_input_shape_dict = utils.parse_input_shape(atc_input_shape)
            quickcmp_input_shape_dict = utils.parse_input_shape(self.dynamic_arg_value)
            dym_dims = []
            for op_name in atc_input_shape_dict.keys():
                DynamicInput.get_dynamic_dim_values(
                    atc_input_shape_dict.get(op_name), quickcmp_input_shape_dict.get(op_name), dym_dims
                )
            atc_value_list = utils.parse_arg_value(atc_dynamic_arg_values)
        except AccuracyCompareException as err:
            utils.logger.error(
                "Please input the valid shape, " "the valid dynamic value range are {}".format(atc_dynamic_arg_values)
            )
            raise AccuracyCompareException(utils.ACCURACY_COMPARISON_INVALID_PARAM_ERROR) from err
        for value in atc_value_list:
            if dym_dims == value:
                return


class NpuDumpData(DumpData):
    """
    Class for generate npu dump data
    """

    def __init__(self, arguments, is_golden=False):
        super().__init__()
        self.offline_model_path = arguments.model_path if is_golden else arguments.offline_model_path
        self.out_path = arguments.out_path
        self.input_shape, self.input_path = arguments.input_shape, arguments.input_path
        self.dump, self.output_size = arguments.dump, arguments.output_size
        self.device, self.is_golden = arguments.device, is_golden
        self.single_op = arguments.single_op

        self.benchmark_input_path = ""
        output_json_path = atc_utils.convert_model_to_json(arguments.cann_path, self.offline_model_path, self.out_path)
        self.om_parser = OmParser(output_json_path)
        self.dynamic_input = DynamicInput(self.om_parser, self.input_shape)
        self.python_version = sys.executable or "python3"
        self.data_dir = self._create_dir()

    @staticmethod
    def _write_content_to_acl_json(acl_json_path, model_name, npu_data_output_dir, sub_model_name_list=None):
        load_dict = {
            "dump": {
                "dump_list": [{"model_name": model_name}],
                "dump_path": npu_data_output_dir,
                "dump_mode": "all",
                "dump_op_switch": "off",
            }
        }
        load_dict["dump"]["dump_list"].extend([{"model_name": ii} for ii in sub_model_name_list])

        if os.access(acl_json_path, os.W_OK):
            json_stat = os.stat(acl_json_path)
            if json_stat.st_uid == os.getuid():
                os.remove(acl_json_path)
            else:
                raise AccuracyCompareException(utils.ACCURACY_COMPARISON_PARSER_JSON_FILE_ERROR)
            try:
                with ms_open(acl_json_path, "w") as write_json:
                    try:
                        json.dump(load_dict, write_json)
                    except ValueError as exc:
                        utils.logger.error(str(exc))
                        raise AccuracyCompareException(utils.ACCURACY_COMPARISON_WRITE_JSON_FILE_ERROR) from exc
            except IOError as acl_json_file_except:
                utils.logger.error('Failed to open"' + acl_json_path + '", ' + str(acl_json_file_except))
                raise AccuracyCompareException(utils.ACCURACY_COMPARISON_OPEN_FILE_ERROR) from acl_json_file_except
        else:
            utils.logger.error(
                "The path {} does not have permission to write.Please check the path permission".format(acl_json_path)
            )
            raise AccuracyCompareException(utils.ACCURACY_COMPARISON_INVALID_PATH_ERROR)

    def generate_inputs_data(self, npu_dump_data_path=None, use_aipp=False):
        if self.input_path:
            input_path = self.input_path.split(",")
            for i, input_file in enumerate(input_path):
                if not os.path.isfile(input_file):
                    utils.logger.error("no such file exists: {}".format(input_file))
                    raise utils.AccuracyCompareException(utils.ACCURACY_COMPARISON_INVALID_PARAM_ERROR)
                file_name = "input_" + str(i) + ".bin"
                dest_file = os.path.join(self.out_path, "input", file_name)
                shutil.copy(input_file, dest_file)
                os.chmod(dest_file, 0o640)
            return
        if use_aipp:
            self._generate_inputs_data_for_aipp(self.data_dir)
        else:
            self._generate_inputs_data_without_aipp(self.data_dir)

    def generate_dump_data(self, npu_dump_path=None, om_parser=None, use_cli=True):
        """
        Function Description:
            compile and rum benchmark project
        Return Value:
            npu dump data path
        """
        self._check_input_path_param()
        if not use_cli:
            benchmark_dir = os.path.join(os.path.realpath("../../"), BENCHMARK_DIR)
            self.benchmark_install_sh(benchmark_dir)
        return self.benchmark_run()

    def get_expect_output_name(self):
        """
        Function Description:
            get expect output node name in golden net
        Return Value:
            output node name in golden net
        """
        return self.om_parser.get_expect_net_output_name()

    def benchmark_install_sh(self, benchmark_dir):
        """
        Function Description:
            compile benchmark backend project
        Parameter:
            benchmark_dir: benchmark project directory
        """
        execute_path = benchmark_dir
        utils.logger.info("Start to install benchmark backend execute_path: %s" % execute_path)
        install_sh_cmd = ["sh", "install.sh", "-p", self.python_version]

        retval = os.getcwd()
        os.chdir(execute_path)

        # do install.sh command
        utils.logger.info("Run command line: cd %s && %s" % (execute_path, " ".join(install_sh_cmd)))
        utils.execute_command(install_sh_cmd)
        utils.logger.info("Finish to install benchmark backend execute_path: %s." % benchmark_dir)
        os.chdir(retval)
        utils.logger.info("Run command line: cd %s (back to the working directory)" % (retval))

    def benchmark_run(self):
        """
        Function Description:
            run benchmark project
        Return Value:
            npu dump data path
        Exception Description:
            when invalid npu dump data path throw exception
        """
        try:
            import ais_bench
        except ModuleNotFoundError as err:
            raise err

        self._compare_shape_vs_file()
        npu_data_output_dir = os.path.join(
            self.out_path, NPU_DUMP_DATA_GOLDEN_PATH if self.is_golden else NPU_DUMP_DATA_BASE_PATH
        )
        utils.create_directory(npu_data_output_dir)
        model_name, extension = utils.get_model_name_and_extension(self.offline_model_path)
        acl_json_path = os.path.join(npu_data_output_dir, ACL_JSON_PATH)
        if not os.path.exists(acl_json_path):
            os.mknod(acl_json_path, mode=0o600)
        benchmark_cmd = [
            self.python_version,
            "-m",
            "ais_bench",
            "--model",
            self.offline_model_path,
            "--input",
            self.benchmark_input_path,
            "--device",
            self.device,
            "--output",
            npu_data_output_dir,
            "--warmup_count",
            "0",
        ]
        if self.dump:
            cur_dir = os.getcwd()
            acl_json_path = os.path.join(cur_dir, acl_json_path)
            sub_model_name_list = self.om_parser.get_sub_graph_name()
            self._write_content_to_acl_json(acl_json_path, model_name, npu_data_output_dir, sub_model_name_list)
            benchmark_cmd.extend(["--acl_json_path", acl_json_path])

        self.dynamic_input.add_dynamic_arg_for_benchmark(benchmark_cmd)
        if self.output_size or self.dynamic_input.is_dynamic_shape_scenario():
            self._make_benchmark_cmd_for_shape_range(benchmark_cmd)

        # do benchmark command
        utils.execute_command(benchmark_cmd, False)

        npu_dump_data_path = ""
        if self.dump:
            npu_dump_data_path, file_is_exist = utils.get_dump_data_path(npu_data_output_dir, False, model_name)
            if not file_is_exist:
                if self.single_op:
                    return "", ""
                utils.logger.error("The path {} dump data is not exist.".format(npu_dump_data_path))
                raise AccuracyCompareException(utils.ACCURACY_COMPARISON_INVALID_PATH_ERROR)
        # net output data path
        npu_net_output_data_path, file_is_exist = utils.get_dump_data_path(npu_data_output_dir, True, model_name)
        if not file_is_exist:
            if self.single_op:
                return "", ""
            utils.logger.error("The path {} net output data is not exist.".format(npu_net_output_data_path))
            raise AccuracyCompareException(utils.ACCURACY_COMPARISON_INVALID_PATH_ERROR)
        self._convert_net_output_to_numpy(npu_net_output_data_path, npu_dump_data_path)
        if self.is_golden:
            return npu_dump_data_path, ""
        else:
            return npu_dump_data_path, npu_net_output_data_path

    def _create_dir(self):
        data_dir = os.path.join(self.out_path, "input")
        utils.create_directory(data_dir)
        return data_dir

    def _get_inputs_info_from_aclruntime(self):
        import aclruntime

        options = aclruntime.session_options()
        Rule.input_file().check(self.offline_model_path, will_raise=True)
        self.offline_model_path = load_file_to_read_common_check(self.offline_model_path)
        aa = aclruntime.InferenceSession(self.offline_model_path, int(self.device), options)
        shape_list = [ii.shape for ii in aa.get_inputs()]
        dtype_list = [ii.datatype.name for ii in aa.get_inputs()]

        aa.free_resource()
        return shape_list, dtype_list

    def _generate_inputs_data_without_aipp(self, input_dir):
        if os.listdir(input_dir):
            return

        inputs_list, data_type_list = self._get_inputs_info_from_aclruntime()
        if self.dynamic_input.is_dynamic_shape_scenario() and not self.input_shape:
            utils.logger.error("Please set '-is' or '--input-shape' to fix the dynamic shape.")
            raise utils.AccuracyCompareException(utils.ACCURACY_COMPARISON_INVALID_PARAM_ERROR)

        if self.input_shape:
            inputs_list = parse_input_shape_to_list(self.input_shape)

        for i, (input_shape, data_type) in enumerate(zip(inputs_list, data_type_list)):
            input_data = np.random.random(input_shape).astype(data_type)
            file_name = "input_" + str(i) + ".bin"
            input_data.tofile(os.path.join(input_dir, file_name))
            os.chmod(os.path.join(input_dir, file_name), 0o640)

    def _generate_inputs_data_for_aipp(self, input_dir):
        aipp_contents = self.om_parser.get_aipp_config_content()
        src_image_size_h = []
        src_image_size_w = []
        input_format = []
        for aipp_content in aipp_contents:
            aipp_list = aipp_content.split(",")
            for aipp_info in aipp_list:
                aipp_infos_split_by_colon = aipp_info.split(":")
                if len(aipp_infos_split_by_colon) < 2:
                    continue
                if "src_image_size_h" in aipp_info:
                    src_image_size_h.append(aipp_infos_split_by_colon[1])
                if "src_image_size_w" in aipp_info:
                    src_image_size_w.append(aipp_infos_split_by_colon[1])
                if "input_format" in aipp_info:
                    input_format.append(aipp_infos_split_by_colon[1].strip('\\"'))
            if not src_image_size_h or not src_image_size_w:
                utils.logger.error("atc insert_op_config file contains no src_image_size_h or src_image_size_w")
                raise utils.AccuracyCompareException(utils.ACCURACY_COMPARISON_WRONG_AIPP_CONTENT)
            if len(src_image_size_h) != len(src_image_size_w):
                utils.logger.error(
                    "atc insert_op_config file's src_image_size_h number does not equal src_image_size_w")
                raise utils.AccuracyCompareException(utils.ACCURACY_COMPARISON_WRONG_AIPP_CONTENT)
        if self.input_shape:
            inputs_list = parse_input_shape_to_list(self.input_shape)
        else:
            inputs_list = self.om_parser.get_shape_list()
            if len(inputs_list) != len(src_image_size_h):
                utils.logger.error("inputs number is not equal to aipp inputs number, please check the -is param")
                raise utils.AccuracyCompareException(utils.ACCURACY_COMPARISON_WRONG_AIPP_CONTENT)
        # currently, onnx only support input format nchw
        h_position = 2
        w_position = 3
        input_dir = os.path.join(self.out_path, "input")
        for i, item in enumerate(inputs_list):
            item[h_position] = int(src_image_size_h[i])
            item[w_position] = int(src_image_size_w[i])
            div_input_format = INPUT_FORMAT_TO_RGB_RATIO_DICT.get(input_format[i])
            if not div_input_format:
                utils.logger.error("aipp input format only support: YUV420SP_U8, RGB888_U8, YUV400_U8, XRGB8888_U8")
                raise utils.AccuracyCompareException(utils.ACCURACY_COMPARISON_WRONG_AIPP_CONTENT)
            input_data = np.random.randint(0, 256, int(np.prod(item) / div_input_format)).astype(np.uint8)
            file_name = "input_" + str(i) + ".bin"
            input_data.tofile(os.path.join(input_dir, file_name))
            os.chmod(os.path.join(input_dir, file_name), 0o640)

    def _make_benchmark_cmd_for_shape_range(self, benchmark_cmd):
        pattern = re.compile(r'^[0-9]+$')
        count = self.om_parser.get_net_output_count()
        if not self.output_size:
            if count > 0:
                count_list = []
                for _ in range(count):
                    count_list.append("90000000")
                self.output_size = ",".join(count_list)
        if self.output_size:
            output_size_list = self.output_size.split(',')
            if len(output_size_list) != count:
                utils.logger.error(
                    'The output size (%d) is not equal %d in model. Please check the "--output-size" argument.'
                    % (len(output_size_list), count)
                )
                raise AccuracyCompareException(utils.ACCURACY_COMPARISON_INVALID_PARAM_ERROR)
            for item in output_size_list:
                item = item.strip()
                match = pattern.match(item)
                if match is None:
                    utils.logger.error("The size (%s) is invalid. Please check the output size." % self.output_size)
                    raise AccuracyCompareException(utils.ACCURACY_COMPARISON_INVALID_PARAM_ERROR)
                if int(item) <= 0:
                    utils.logger.error(
                        "The size (%s) must be large than zero. Please check the output size." % self.output_size
                    )
                    raise AccuracyCompareException(utils.ACCURACY_COMPARISON_INVALID_PARAM_ERROR)
            benchmark_cmd.append(OUTPUT_SIZE)
            benchmark_cmd.append(self.output_size)

    def _convert_net_output_to_numpy(self, npu_net_output_data_path, npu_dump_data_path):
        net_output_data = None
        npu_net_output_data_info = self.om_parser.get_net_output_data_info(npu_dump_data_path)
        for dir_path, _, files in os.walk(npu_net_output_data_path):
            for index, each_file in enumerate(sorted(files)):
                data_type = npu_net_output_data_info.get(index)[0]
                shape = npu_net_output_data_info.get(index)[1]
                data_len = utils.get_data_len_by_shape(shape)
                each_file_path = os.path.join(dir_path, each_file)
                if Rule.input_file().check(each_file_path, will_raise=True):
                    original_net_output_data = np.fromfile(each_file_path, data_type, data_len)
                try:
                    net_output_data = original_net_output_data.reshape(shape)
                except ValueError:
                    utils.logger.warning("The shape of net_output data from file {} is {}.".format(each_file, shape))
                    net_output_data = original_net_output_data
                    
                each_file_index = each_file.split('_')[-1]
                new_each_file = "output_" + each_file_index
                file_name = os.path.basename(new_each_file).split('.')[0]
                numpy_file_path = os.path.join(npu_net_output_data_path, file_name)
                utils.save_numpy_data(numpy_file_path, net_output_data)
                new_each_file_path = os.path.join(dir_path, new_each_file)
                os.rename(each_file_path, new_each_file_path)

    def _check_input_path_param(self):
        if self.input_path == "":
            input_path = os.path.join(self.out_path, INPUT)
            utils.check_file_or_directory_path(os.path.realpath(input_path), True)
            input_bin_files = os.listdir(input_path)
            input_bin_files.sort(key=lambda file: int((re.findall("\\d+", file))[0]))
            bin_file_path_array = []
            for item in input_bin_files:
                bin_file_path_array.append(os.path.join(input_path, item))
            self.benchmark_input_path = ",".join(bin_file_path_array)
        else:
            bin_file_path_array = utils.check_input_bin_file_path(self.input_path)
            self.benchmark_input_path = ",".join(bin_file_path_array)

    def _compare_shape_vs_file(self):
        shape_size_array = self.om_parser.get_shape_size()
        if self.om_parser.contain_negative_1:
            return
        files_size_array = self._get_file_size()
        if not self.om_parser.get_aipp_config_content:
            self._shape_size_vs_file_size(shape_size_array, files_size_array)

    def _get_file_size(self):
        file_size = []
        files = self.benchmark_input_path.split(",")
        for item in files:
            if item.endswith("bin") or item.endswith("BIN"):
                file_size.append(os.path.getsize(item))
            elif item.endswith("npy") or item.endswith("NPY"):
                try:
                    Rule.input_file().check(item, will_raise=True)
                    file_size.append(np.load(item).size)
                except (ValueError, FileNotFoundError) as e:
                    utils.logger.error("The path {} can not get its size through numpy".format(item))
                    raise AccuracyCompareException(utils.ACCURACY_COMPARISON_INVALID_PATH_ERROR) from e
            else:
                utils.logger.error("Input_path parameter only support bin or npy file, " "but got {}".format(item))
                raise AccuracyCompareException(utils.ACCURACY_COMPARISON_INVALID_PATH_ERROR)
        return file_size

    def _shape_size_vs_file_size(self, shape_size_array, files_size_array):
        if len(shape_size_array) < len(files_size_array):
            utils.logger.error("The number of input files is incorrect.")
            raise AccuracyCompareException(utils.ACCURACY_COMPARISON_BIN_FILE_ERROR)
        if self.om_parser.shape_range:
            for file_size in files_size_array:
                if file_size not in shape_size_array:
                    utils.logger.error("The size (%d) of file can not match the input of the model." % file_size)
                    raise AccuracyCompareException(utils.ACCURACY_COMPARISON_BIN_FILE_ERROR)
        elif self.dynamic_input.is_dynamic_shape_scenario():
            for shape_size in shape_size_array:
                for file_size in files_size_array:
                    if file_size <= shape_size:
                        return
            utils.logger.warning("The size of bin file can not match the input of the model.")
        else:
            for shape_size, file_size in zip(shape_size_array, files_size_array):
                if shape_size == 0:
                    continue
                if shape_size != file_size:
                    utils.logger.error("The shape value is different from the size of the file.")
                    raise AccuracyCompareException(utils.ACCURACY_COMPARISON_BIN_FILE_ERROR)
