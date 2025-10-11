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

import os
import time
from msit_llm.transform.torch_to_float_atb import utils
from msit_llm.transform.utils import write_file
from components.utils.install import get_public_url


def float_layer_cpp_gen(parsed_model, save_name=None, save_dir=None):
    from msit_llm.transform.torch_to_float_atb import float_layer_cpp_templates
    
    model_name_lower = parsed_model.get("name", "model").lower()

    rr = ""
    rr += float_layer_cpp_templates.CPP_COPYRIGHT_HEADER.format(
        year=time.localtime().tm_year,
        licenses_url=get_public_url('msit_licenses_url')
    ) + "\n"
    rr += "\n".join([f'''#include "{i}"''' for i in float_layer_cpp_templates.all_atb_operation_headers])
    rr += f'''\n#include "models/{model_name_lower}/layer/decoder_layer.h"'''

    layer_core_components = float_layer_cpp_templates.DECODER_LAYER_FORMATTER.format(
        attention_formatter=float_layer_cpp_templates.ATTENTION_FORMATTER.format(),
        residual_add_formatter=float_layer_cpp_templates.RESIDUAL_ADD_FORMATTER.format(),
        mlp_formatter=float_layer_cpp_templates.MLP_FORMATTER.format(),
        mlp_residual_add_formatter=float_layer_cpp_templates.MLP_RESIDUAL_ADD_FORMATTER.format()
    )

    post_properties = "\n".join([
        float_layer_cpp_templates.PARSE_PARAM_FORMATTER.format(),
        float_layer_cpp_templates.BIND_PARAM_HOST_TENSOR_FORMATTER.format(),
    ])

    rr += float_layer_cpp_templates.BASIC_CLASS_FORMATTER.format(
        model_name_lower=model_name_lower,
        decoder_layer=layer_core_components,
        post_properties=post_properties,
    )

    save_name = utils.init_save_name(save_name if save_name else "decoder_layer") + ".cpp"
    save_dir = utils.init_save_dir(model_name_lower if save_dir is None else save_dir, sub_dir="layer")
    save_path = os.path.join(save_dir, save_name)
    write_file(save_path, rr)
    return save_path, rr
