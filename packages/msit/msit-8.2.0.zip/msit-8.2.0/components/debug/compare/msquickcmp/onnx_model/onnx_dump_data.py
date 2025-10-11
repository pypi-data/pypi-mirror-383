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
This class is used to generate GUP dump data of the ONNX model.
"""
import os
import re
import time

import onnx
import onnxruntime
import numpy as np

from msquickcmp.common.dump_data import DumpData
from msquickcmp.common import utils
from msquickcmp.common.utils import AccuracyCompareException
from msquickcmp.common.utils import InputShapeError, load_npy_from_buffer
from msquickcmp.adapter_cli.args_adapter import CmpArgsAdapter
from msquickcmp.common.convert import convert_bin_file_to_npy
from msquickcmp.onnx_model.custom_op import CustomOp
from components.utils.file_open_check import ms_open
from components.utils.util import load_file_to_read_common_check
from components.utils.constants import TENSOR_MAX_SIZE


NODE_TYPE_TO_DTYPE_MAP = {
    "tensor(int)": np.int32,
    "tensor(int8)": np.int8,
    "tensor(int16)": np.int16,
    "tensor(int32)": np.int32,
    "tensor(int64)": np.int64,
    "tensor(uint8)": np.uint8,
    "tensor(uint16)": np.uint16,
    "tensor(uint32)": np.uint32,
    "tensor(uint64)": np.uint64,
    "tensor(float)": np.float32,
    "tensor(float16)": np.float16,
    "tensor(double)": np.double,
    "tensor(bool)": np.bool_,
    "tensor(complex64)": np.complex64,
    "tensor(complex128)": np.complex_,
}
MAX_PROTOBUF = 2000000000
ONNX_DTYPE = {1: np.float32, 2: np.float64}
MAX_FILE_NAME_LEN = 255


class OnnxDumpData(DumpData):
    """
    This class is used to generate dump data of the ONNX model.
    """

    def __init__(self, arguments: CmpArgsAdapter, npu_dump_npy_path=None):
        super().__init__()
        self.model_path, self.out_path, self.input_path = arguments.model_path, arguments.out_path, arguments.input_path
        self.input_shape, self.dym_shape_range = arguments.input_shape, arguments.dym_shape_range
        self.custom_op_type, self.onnx_fusion_switch = arguments.custom_op, arguments.onnx_fusion_switch
        self.dump, self.cann_path = arguments.dump, arguments.cann_path
        self.single_op = arguments.single_op

        self._check_path_exists(self.model_path, extentions="onnx")

        self.input_shapes = utils.parse_input_shape(self.input_shape)
        self.data_dir, self.onnx_dump_data_dir, self.model_dir = self._create_dir()

        self.net_output, self.inputs_map, self.extend_inputs_map = {}, {}, {}
        self.origin_model, origin_model_contents = self._load_onnx(self.model_path)

        if self.custom_op_type:
            # remove custom op and add extend inputs map
            custom_op = CustomOp(self.custom_op_type, self.model_path, npu_dump_npy_path, self.model_dir)
            modify_model_path, self.extend_inputs_map = custom_op.remove_custom_op_and_add_inputs()
            modify_model, modify_model_contents = self._load_onnx(modify_model_path)

            self.dump_model_with_inputs_path = self._new_model_save_path(modify_model_path)
            self.model_with_inputs = modify_model
            self.model_with_inputs_session = self._load_session(modify_model_path)
        else:
            self.dump_model_with_inputs_path = self._new_model_save_path(self.model_path)
            self.model_with_inputs = self.origin_model
            self.model_with_inputs_session = self._load_session(self.model_path)

    @staticmethod
    def _check_input_shape_fix_value(op_name, model_shape, input_shape):
        message = "fixed input tensor dim not equal to model input dim." "tensor_name:%s, %s vs %s" % (
            op_name,
            str(input_shape),
            str(model_shape),
        )
        if len(model_shape) != len(input_shape):
            utils.logger.error(message)
            raise AccuracyCompareException(utils.ACCURACY_COMPARISON_INVALID_DATA_ERROR)
        for index, value in enumerate(model_shape):
            if value is None or isinstance(value, str):
                continue
            if input_shape[index] != value:
                utils.logger.error(message)
                raise AccuracyCompareException(utils.ACCURACY_COMPARISON_INVALID_DATA_ERROR)

    def generate_inputs_data(self, npu_dump_data_path=None, use_aipp=False):
        inputs_tensor_info = self._get_inputs_tensor_info()
        if use_aipp:
            if not npu_dump_data_path:
                utils.logger.error("find no aipp op in dump data, please check if --dump is True")
                raise utils.AccuracyCompareException(utils.ACCURACY_COMPARISON_INVALID_PARAM_ERROR)
            self._check_path_exists(npu_dump_data_path)
            self.inputs_map = self._get_inputs_data_aipp(self.data_dir, inputs_tensor_info, npu_dump_data_path)
        else:
            self.inputs_map = self._get_inputs_data(inputs_tensor_info)

        # extend inputs add by removed custom op
        if self.custom_op_type:
            self.inputs_map.update(self.extend_inputs_map)

    def get_output_map(self, output_list):
        output_map, res_idx, output_list_size = {}, 0, len(output_list)
        for node in self.origin_model.graph.node:
            for node_output in node.output:
                output_map[node_output] = output_list[res_idx]
                res_idx += 1
                if res_idx >= output_list_size:
                    return output_map
        return output_map

    def get_input_map(self, input_map, output_list):
        output_map = self.get_output_map(output_list)
        input_map = self.augment_input_map(input_map, output_map)
        return input_map

    def augment_input_map(self, input_map, output_map):
        for temp in self.origin_model.graph.initializer:
            npy_data = load_npy_from_buffer(temp.raw_data, ONNX_DTYPE.get(temp.data_type), temp.dims)
            input_map[temp.name] = npy_data
        input_map = {**input_map, **output_map}
        return input_map
    
    def generate_dump_data(self, npu_dump_path=None, om_parser=None):
        self._modify_model_add_outputs_nodes(
            self.model_with_inputs, self.dump_model_with_inputs_path
        )
        session = self._load_session(self.dump_model_with_inputs_path)
        dump_bins = self._run_model(session, self.inputs_map)
        augment_inputs_map = self.get_input_map(self.inputs_map, dump_bins)
        net_output_node = [output_item.name for output_item in self.model_with_inputs_session.get_outputs()]
        self._save_dump_data(dump_bins, self.model_with_inputs, net_output_node, augment_inputs_map)

        return self.onnx_dump_data_dir

    def _load_session(self, model_path):
        options = onnxruntime.SessionOptions()
        if not self.onnx_fusion_switch:
            options.graph_optimization_level = onnxruntime.GraphOptimizationLevel.ORT_DISABLE_ALL
        try:
            model_path = load_file_to_read_common_check(model_path)
            infersession = onnxruntime.InferenceSession(model_path, options)
        except Exception as e:
            utils.logger.error(f"Please check onnx model can run in local env. Error: {e}")
            raise utils.AccuracyCompareException(utils.ACCURACY_COMPARISON_MODEL_TYPE_ERROR)
        return infersession

    def _load_onnx(self, model_path):
        # model_path str -> read as bytes -> deserialize to onnx_model
        #                                 -> onnxruntime load as session
        model_path = load_file_to_read_common_check(model_path)
        with ms_open(model_path, "rb", max_size=TENSOR_MAX_SIZE) as ff:
            model_contents = ff.read()
        onnx_model = onnx.load_model(model_path)
        unique_index = 999
        name_set = set((node.name for node in onnx_model.graph.node))

        def get_unique_name(ori_name, index):
            new_name = f"{ori_name}_{index}"
            if new_name not in name_set:
                return new_name, index + 1
            else:
                return get_unique_name(ori_name, index + 1)

        for index, node in enumerate(onnx_model.graph.node):
            if node.name:
                continue
            new_name = node.op_type + "_" + str(index)
            if new_name in name_set:
                new_name, unique_index = get_unique_name(new_name, unique_index)
            name_set.add(new_name)
            node.name = new_name
        return onnx_model, model_contents

    def _new_model_save_path(self, origin_path):
        save_name = "new_" + os.path.basename(origin_path)
        return os.path.join(self.model_dir, save_name)

    def _create_dir(self):
        # create input directory
        data_dir = os.path.join(self.out_path, "input")
        utils.create_directory(data_dir)

        # create dump_data/onnx directory
        onnx_dump_data_dir = os.path.join(self.out_path, "dump_data/onnx")
        utils.create_directory(onnx_dump_data_dir)

        # create model directory
        model_dir = ""
        if self.dym_shape_range:
            model_relative_name = "../model"
        else:
            model_relative_name = "model"
            if self.dump:
                model_dir = os.path.join(self.out_path, model_relative_name)
                utils.create_directory(model_dir)
        return data_dir, onnx_dump_data_dir, model_dir

    def _modify_model_add_outputs_nodes(self, onnx_model, save_path):
        if self.dump:
            del onnx_model.graph.output[:]
            
            onnx_model.graph.output.extend(
                onnx.ValueInfoProto(name=tensor_name) 
                for node in onnx_model.graph.node 
                for tensor_name in node.output
            )
        
        model_size = onnx_model.ByteSize()
        save_external_flag = model_size < 0 or model_size > MAX_PROTOBUF
        
        utils.logger.debug("Modfied model has size over 2G: %s", save_external_flag)
        
        onnx.save_model(
            onnx_model, 
            save_path,
            save_as_external_data=save_external_flag
        )
        
        utils.logger.info("Modified model has being saved successfully at: %s", os.path.abspath(save_path))
        
    def _get_inputs_tensor_info(self):
        inputs_tensor_info = []
        input_tensor_names = [item.name for item in self.model_with_inputs_session.get_inputs()]
        for _, tensor_name in enumerate(self.input_shapes):
            utils.check_input_name_in_model(input_tensor_names, tensor_name)
        for input_item in self.model_with_inputs_session.get_inputs():
            tensor_name = input_item.name
            tensor_type = input_item.type
            tensor_shape = tuple(input_item.shape)
            # skip extend inputs add by custom op
            if tensor_name in self.extend_inputs_map.keys():
                continue

            if utils.check_dynamic_shape(tensor_shape):
                if not self.input_shapes:
                    utils.logger.error(
                        "The dynamic shape {} are not supported. Please "
                        "set '-is' or '--input-shape' to fix the dynamic shape.".format(tensor_shape)
                    )
                    raise utils.AccuracyCompareException(utils.ACCURACY_COMPARISON_INVALID_PARAM_ERROR)
            if self.input_shapes and tensor_name in self.input_shapes:
                input_shape = self.input_shapes.get(tensor_name)
                try:
                    number_shape = [int(dim) for dim in input_shape]
                except (ValueError, TypeError) as error:
                    utils.logger.error(
                        utils.get_shape_not_match_message(InputShapeError.FORMAT_NOT_MATCH, self.input_shape)
                    )
                    raise utils.AccuracyCompareException(utils.ACCURACY_COMPARISON_INVALID_PARAM_ERROR) from error
                self._check_input_shape_fix_value(tensor_name, tensor_shape, number_shape)
                tensor_info = {"name": tensor_name, "shape": tuple(number_shape), "type": tensor_type}
                utils.logger.info("Fix dynamic input shape of %s to %s" % (tensor_name, number_shape))
            else:
                tensor_info = {"name": tensor_name, "shape": tensor_shape, "type": tensor_type}
            inputs_tensor_info.append(tensor_info)
        utils.logger.info("model inputs tensor info:\n{}\n".format(inputs_tensor_info))
        return inputs_tensor_info

    def _get_inputs_data(self, inputs_tensor_info):
        names = [ii["name"] for ii in inputs_tensor_info]
        shapes = [ii["shape"] for ii in inputs_tensor_info]
        dtypes = [self._convert_to_numpy_type(ii["type"]) for ii in inputs_tensor_info]

        bin_file_path_array = []
        if "" == self.input_path:
            utils.check_file_or_directory_path(os.path.realpath(self.data_dir), True)
            input_bin_files = os.listdir(self.data_dir)
            if len(input_bin_files) == 0:
                return self._generate_random_input_data(self.data_dir, names, shapes, dtypes)
            input_bin_files.sort(key=lambda file: int((re.findall("\\d+", file))[0]))
            bin_file_path_array = [os.path.join(self.data_dir, item) for item in input_bin_files]

        else:
            input_initial_path = self.input_path.split(",")
            for input_item in input_initial_path:
                input_item_path = os.path.realpath(input_item)
                if input_item_path.endswith('.bin'):
                    bin_file_path_array.append(input_item_path)
                else:
                    utils.get_input_path(input_item_path, bin_file_path_array)

        self._check_input_data_path(bin_file_path_array, inputs_tensor_info)
        return self._read_input_data(bin_file_path_array, names, shapes, dtypes)

    def _get_inputs_data_aipp(self, data_dir, inputs_tensor_info, npu_dump_data_path):
        inputs_map = {}
        aipp_input = []
        for bin_file in os.listdir(npu_dump_data_path):
            if bin_file.startswith("Aipp"):
                aipp_input.append(os.path.join(npu_dump_data_path, bin_file))
        if len(aipp_input) != len(inputs_tensor_info):
            utils.logger.error("lengths of aipp_input and input_tensor_info unequal, please check.")
            raise utils.AccuracyCompareException(utils.ACCURACY_COMPARISON_INDEX_OUT_OF_BOUNDS_ERROR)
        for i, tensor_info in enumerate(inputs_tensor_info):
            convert_bin_file_to_npy(aipp_input[i], os.path.join(self.out_path, "input"), self.cann_path)
            aipp_output_path = os.path.join(self.out_path, "input", aipp_input[i].rsplit("/", 1)[1]) + ".output.0.npy"
            aipp_output_path = load_file_to_read_common_check(aipp_output_path)
            aipp_output = np.load(aipp_output_path)
            nchw_prod = np.prod(tensor_info["shape"])
            nchwc_prod_without_c1 = np.prod(aipp_output.shape[:-1])
            try:
                c0 = int(nchw_prod / nchwc_prod_without_c1)
            except ZeroDivisionError as e:
                utils.logger.error("Aipp output has wrong shape, file path: {}".format(aipp_output_path))
                raise utils.AccuracyCompareException(utils.ACCURACY_COMPARISON_INVALID_DATA_ERROR) from e
            onnx_input = aipp_output[..., :c0].transpose((0, 4, 2, 3, 1)).squeeze(-1).astype(np.float32)
            inputs_map[tensor_info["name"]] = onnx_input
        return inputs_map

    def _convert_to_numpy_type(self, tensor_type):
        numpy_data_type = NODE_TYPE_TO_DTYPE_MAP.get(tensor_type)
        if numpy_data_type:
            return numpy_data_type
        else:
            utils.logger.error("unsupported tensor type: {}".format(tensor_type))
            raise AccuracyCompareException(utils.ACCURACY_COMPARISON_TENSOR_TYPE_ERROR)

    def _run_model(self, session, inputs_map):
        outputs_name = [node.name for node in session.get_outputs()]
        return session.run(outputs_name, inputs_map)

    def _save_dump_data(self, dump_bins, old_onnx_model, net_output_node, input_map):
        res_idx = 0
        file_name_map = []
        for node in old_onnx_model.graph.node:
            #存储onnx的输入dump数据
            for i, node_input in enumerate(node.input):
                if not self.dump:
                    break
                file_name = self._generate_dump_data_file_name("input_" + node.name, i)
                if len(file_name) > MAX_FILE_NAME_LEN:
                    new_file_name = str(round(time.time() * 1e6)) + str(len(file_name_map)) + ".npy"
                    file_name_map.append(f"{new_file_name},{file_name}\n")
                    file_name = new_file_name
                file_path = os.path.join(self.onnx_dump_data_dir, file_name)
                if input_map.get(node_input) is not None:
                    np.save(file_path, input_map.get(node_input))
            for j, output in enumerate(node.output):
                if not self.dump and output not in net_output_node:
                    continue
                file_name = self._generate_dump_data_file_name(node.name, j)
                if len(file_name) > MAX_FILE_NAME_LEN:
                    new_file_name = str(round(time.time() * 1e6)) + str(len(file_name_map)) + ".npy"
                    file_name_map.append(f"{new_file_name},{file_name}\n")
                    file_name = new_file_name

                file_path = os.path.join(self.onnx_dump_data_dir, file_name)
                if output in net_output_node:
                    self.net_output[net_output_node.index(output)] = file_path
                if res_idx <= len(dump_bins) - 1:
                    np.save(file_path, dump_bins[res_idx])
                else:
                    utils.logger.error("res_idx out of bounds of dump_bins and can not save, please check.")
                res_idx += 1

        if len(file_name_map) > 0:
            mapping_file_path = os.path.join(self.onnx_dump_data_dir, "mapping.csv")
            with ms_open(mapping_file_path, mode="w") as map_file:
                map_file.writelines(file_name_map)

        if not self.single_op:
            for key, value in self.net_output.items():
                utils.logger.info("net_output node is:{}, file path is {}".format(key, value))
        utils.logger.info("dump data success")
