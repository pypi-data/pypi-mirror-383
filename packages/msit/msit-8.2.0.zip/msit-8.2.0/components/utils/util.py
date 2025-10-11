# Copyright (c) 2023-2025 Huawei Technologies Co., Ltd.
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

import argparse
from collections import defaultdict
from functools import wraps
import os
import pickle
import re

from components.utils.constants import TENSOR_MAX_SIZE, EXT_SIZE_MAPPING, PATH_WHITE_LIST_REGEX, MAX_RECUR_DEPTH
from components.utils.log import logger
from components.utils.file_open_check import is_legal_path_length

# 记录工具函数递归的深度
recursion_depth = defaultdict(int)


def confirmation_interaction(prompt):
    confirm_pattern = re.compile(r'y(?:es)?', re.IGNORECASE)

    try:
        user_action = input(prompt)
    except Exception:
        return False

    return bool(confirm_pattern.match(user_action))


def check_file_ext(path, ext: str):
    if not isinstance(path, str):
        raise TypeError("Expected first positional argument type 'str', got %r instead" % type(path))

    if not isinstance(ext, str):
        raise TypeError("Expected second positional argument type 'str', got %r instead" % type(ext))

    path_ext = os.path.splitext(path)[1]

    if path_ext != ext:
        return False

    return True


def check_file_size_based_on_ext(path, ext=None):
    """Check the file size based on extension. This function uses `os.stat` to get file size may lead to OSError"""

    if not isinstance(path, str):
        raise TypeError("Expected path to be 'str', got %r instead" % type(path))

    ext = ext or os.path.splitext(path)[1]
    size = os.path.getsize(path)  # may lead to errors

    if ext in EXT_SIZE_MAPPING:
        if size > EXT_SIZE_MAPPING[ext]:
            return False
    else:
        if size > TENSOR_MAX_SIZE:
            confirmation_prompt = "The file %r is larger than expected. " \
                                "Attempting to read such a file could potentially impact system performance.\n" \
                                "Please confirm your awareness of the risks associated with this action (y/n): " % path
            return confirmation_interaction(confirmation_prompt)

    return True


def safe_torch_load(path, **kwargs):
    import torch  # Do not move it !!! it may caused Import Error
    kwargs['weights_only'] = True
    tensor = None

    while True:
        try:
            tensor = torch.load(path, **kwargs)
        except pickle.UnpicklingError:
            confirmation_prompt = "Weights only load failed. Re-running `torch.load` with `weights_only` " \
                                  "set to `False` will likely succeed, but it can result in arbitrary code " \
                                  "execution. Do it only if you get the file from a trusted source.\n" \
                                  "Please confirm your awareness of the risks associated with this action ([y]/n): "
            if not confirmation_interaction(confirmation_prompt):
                raise
            kwargs['weights_only'] = False
        else:
            break

    return tensor


def load_file_to_read_common_check(path: str, exts=None):
    if not isinstance(path, str):
        raise TypeError("'path' should be 'str'")

    if isinstance(exts, (tuple, list)):
        if not any(check_file_ext(path, ext) for ext in exts):
            logger.error("Expected extenstion to be one of %r", exts)
            raise ValueError

    elif exts is not None:
        logger.error("Expected 'exts' to be 'List[str]', got %r instead", type(exts))
        raise TypeError

    if re.search(PATH_WHITE_LIST_REGEX, path):
        logger.error("Invalid character: %r", path)
        raise ValueError

    if not is_legal_path_length(path):
        logger.error("Invalid path length.")
        raise ValueError

    path = os.path.realpath(path)

    try:
        file_status = os.stat(path)
    except OSError as e:
        logger.error("%s: %r", e.strerror, path)
        raise

    if not os.st.S_ISREG(file_status.st_mode):
        logger.error("Not a regular file: %r", path)
        raise ValueError

    if not check_file_size_based_on_ext(path):
        logger.error("File too large: %r", path)
        raise ValueError

    if (os.st.S_IWOTH & file_status.st_mode) == os.st.S_IWOTH:
        logger.error("Vulnerable path: %r should not be other writeable", path)
        raise PermissionError

    cur_euid = os.geteuid()
    if file_status.st_uid != cur_euid:
        # not root
        if cur_euid != 0:
            logger.error("File owner and current user are inconsistent: %r", path)
            raise PermissionError

        # root but reading a other writeable file
        elif (os.st.S_IWGRP & file_status.st_mode) == os.st.S_IWGRP or \
             (os.st.S_IWUSR & file_status.st_mode) == os.st.S_IWUSR:
            logger.warning("Privilege escalation risk detected. Trying to read a file that belongs to"
                           " a normal user and is writeable to the user or the user group")

    return path


def filter_cmd(paras):
    whitelist_pattern = re.compile(r"^[a-zA-Z0-9_\-./=:,\[\] ]+$")
    filtered = []
    for arg in paras:
        arg_str = str(arg)
        if whitelist_pattern.fullmatch(arg_str):
            filtered.append(arg_str)
        else:
            raise ValueError(
                f'The command contains invalid characters. Only the "{whitelist_pattern}" pattern is allowed.'
            )
    return filtered


def check_str_for_cmd(strings, var_name):
    whitelist_pattern = re.compile(r"^[a-zA-Z0-9_\-./=:,\[\] ]+$")
    if whitelist_pattern.fullmatch(strings):
        pass
    else:
        raise ValueError(
            f'{var_name} contains invalid characters. Only the "{whitelist_pattern}" pattern is allowed.'
        )


def load_file_to_read_common_check_for_cli(value, exts=None):
    try:
        value = load_file_to_read_common_check(value, exts)
    except Exception as e:
        raise argparse.ArgumentTypeError("%r" % value) from e
    return value


def safe_int(str_value, log_print_variable_name=None):
    try:
        int_value = int(str_value)
    except ValueError as e:
        if log_print_variable_name:  # 报错信息中将变量名称进行打印，适用于环境变量场景
            raise ValueError(f"The value of the variable {log_print_variable_name} is not valid, "
                             "what we need is a value that can be convert to int.") from e
        raise ValueError(f"The value {str_value} is not valid, "
                         "what we need is a value that can be convert to int.") from e
    return int_value


def safe_get(container, key):
    """
    Safely get an item from a list or dict.
    For lists, checks index bounds.
    For dicts, checks key existence.
    Raises IndexError or KeyError if not found.
    """
    if isinstance(container, list):
        if isinstance(key, int) and 0 <= key < len(container):
            return container[key]
        raise IndexError("list index out of range")
    elif isinstance(container, dict):
        if key in container:
            return container[key]
        raise KeyError(f"key '{key}' not found in dict")
    else:
        raise TypeError("container must be a list or dict")


def safe_del(container, key):
    """
    Safely delete an item from a list or dict.
    For lists, checks index bounds.
    For dicts, checks key existence.
    Raises IndexError or KeyError if not found.
    """
    if isinstance(container, list):
        if isinstance(key, int) and 0 <= key < len(container):
            del container[key]
        raise IndexError("list index out of range")
    elif isinstance(container, dict):
        if key in container:
            del container[key]
        raise KeyError(f"key '{key}' not found in dict")
    else:
        raise TypeError("container must be a list or dict")


def recursion_depth_decorator(func_info, max_depth=MAX_RECUR_DEPTH):
    """装饰一个函数，当函数递归调用超过限制时，抛出异常并打印函数信息。"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            func_id = id(func)
            recursion_depth[func_id] += 1
            if recursion_depth[func_id] > max_depth:
                raise RecursionError(
                    f"call {func_info} exceeds the recursion limit."
                )
            try:
                result = func(*args, **kwargs)
            finally:
                recursion_depth[func_id] -= 1
            return result

        return wrapper

    return decorator
