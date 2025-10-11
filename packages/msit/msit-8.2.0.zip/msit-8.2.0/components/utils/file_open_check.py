# Copyright (c) 2023-2024 Huawei Technologies Co., Ltd.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#     http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
import sys
import stat
import re
import logging
from enum import Enum

import pandas as pd

from components.utils.log import logger
from components.utils.constants import PATH_WHITE_LIST_REGEX
from components.utils.check import Rule
from components.utils.constants import CONFIG_FILE_MAX_SIZE



MAX_SIZE_UNLIMITE = -1  # 不限制，必须显式表示不限制，读取必须传入
MAX_SIZE_LIMITE_CONFIG_FILE = 10 * 1024 * 1024  # 10M 普通配置文件，可以根据实际要求变更
MAX_SIZE_LIMITE_NORMAL_FILE = 4 * 1024 * 1024 * 1024  # 4G 普通模型文件，可以根据实际要求变更
MAX_SIZE_LIMITE_MODEL_FILE = 100 * 1024 * 1024 * 1024  # 100G 超大模型文件，需要确定能处理大文件，可以根据实际要求变更

PATH_WHITE_LIST_REGEX_WIN = re.compile(r"[^_:\\A-Za-z0-9/.-]")

PERMISSION_NORMAL = 0o640  # 普通文件
PERMISSION_KEY = 0o600  # 密钥文件
READ_FILE_NOT_PERMITTED_STAT = stat.S_IWGRP | stat.S_IWOTH
WRITE_FILE_NOT_PERMITTED_STAT = stat.S_IWGRP | stat.S_IWOTH

SOLUTION_LEVEL = 35
SOLUTION_LEVEL_WIN = 45
logging.addLevelName(SOLUTION_LEVEL, "\033[1;32m" + "SOLUTION" + "\033[0m")  # green [SOLUTION]
logging.addLevelName(SOLUTION_LEVEL_WIN, "SOLUTION_WIN")

SOLUTION_BASE_LOC = '\"gitcode repo: Ascend/msit, wiki: ait_security_error_log_solution, chapter:'
SOFT_LINK_SUB_CHAPTER = 'soft_link_error_log_solution\"'
PATH_LENGTH_SUB_CHAPTER = 'path_length_overflow_error_log_solution\"'
OWNER_SUB_CHAPTER = 'owner_or_ownergroup_error_log_solution\"'
PERMISSION_SUB_CHAPTER = 'path_permission_error_log_solution\"'
ILLEGAL_CHAR_SUB_CHAPTER = 'path_contain_illegal_char_error_log_solution\"'

RAW_INPUT_PATH = "RAW_INPUT_PATH"

MALICIOUS_CSV_PATTERN = re.compile(r'^[＝＋－+-=%@];[＝＋－+-=%@]')


def solution_log(content):
    logger.log(SOLUTION_LEVEL, "visit %s for detailed solution", content)


def solution_log_win(content):
    logger.log(SOLUTION_LEVEL_WIN, "visit %s for detailed solution", content)


def is_legal_path_length(path):
    if len(path) > 4096 and not sys.platform.startswith("win"):  # linux total path length limit
        logger.error("file total path %s length out of range (4096), please check the file(or directory) path", path)
        solution_log(SOLUTION_BASE_LOC + PATH_LENGTH_SUB_CHAPTER)
        return False

    if len(path) > 260 and sys.platform.startswith("win"):  # windows total path length limit
        logger.error("file total path %s length out of range (260), please check the file(or directory) path", path)
        solution_log_win(SOLUTION_BASE_LOC + PATH_LENGTH_SUB_CHAPTER)
        return False

    dirnames = path.split("/")
    for dirname in dirnames:
        if len(dirname) > 255:  # linux single file path length limit
            logger.error("file name %s length out of range (255), please check the file(or directory) path", dirname)
            solution_log(SOLUTION_BASE_LOC + PATH_LENGTH_SUB_CHAPTER)
            return False
    return True


def is_match_path_white_list(path):
    if PATH_WHITE_LIST_REGEX.search(path) and not sys.platform.startswith("win"):
        logger.error("path: %s contains illegal char, legal chars include A-Z a-z 0-9 _ - / .", path)
        solution_log(SOLUTION_BASE_LOC + ILLEGAL_CHAR_SUB_CHAPTER)
        return False
    if PATH_WHITE_LIST_REGEX_WIN.search(path) and sys.platform.startswith("win"):
        logger.error("path: %s contains illegal char, legal chars include A-Z a-z 0-9 _ - / . : \\", path)
        solution_log_win(SOLUTION_BASE_LOC + ILLEGAL_CHAR_SUB_CHAPTER)
        return False
    return True


def is_legal_args_path_string(path):
    # only check path string
    if not path:
        return True
    if not is_legal_path_length(path):
        return False
    if not is_match_path_white_list(path):
        return False
    return True


class SanitizeErrorType(Enum):
    """
    The errors parameter Enum of the function sanitize_csv_value
    """
    strict = "strict"
    ignore = "ignore"
    replace = "replace"
    
    
def sanitize_cell_for_dataframe(df: pd.DataFrame):
    for _, row in df.iterrows():           # 遍历每一行
        for col_name in df.columns:                # 遍历每一列
            cell_value = row[col_name]             # 获取单元格值
            sanitize_csv_value(cell_value)         # 校验每个格子内容


def sanitize_csv_value(value: str, errors=SanitizeErrorType.strict.value):
    
    if errors == SanitizeErrorType.ignore.value or not isinstance(value, str):
        return value

    sanitized_value = value
    try:
        float(value) # in case value is a digit but in str format
    except ValueError as e: # not digit
        if not MALICIOUS_CSV_PATTERN.search(value):
            pass
        elif errors == SanitizeErrorType.replace.value:
            sanitized_value = ' ' + value
        else:
            msg = f'Malicious value is not allowed to be written to the csv {value}'
            logger.error("Please check the value written to the csv")
            raise ValueError(msg) from e

    return sanitized_value


class OpenException(Exception):
    pass


class FileStat:
    def __init__(self, file) -> None:
        if not is_legal_path_length(file) or not is_match_path_white_list(file):
            raise OpenException("Path name is too long or contains invalid characters.")
        self.file = file
        self.is_file_exist = os.path.exists(file)
        if self.is_file_exist:
            self.file_stat = os.stat(file)
            self.realpath = os.path.realpath(file)
        else:
            self.file_stat = None

    @property
    def is_exists(self):
        return self.is_file_exist

    @property
    def is_softlink(self):
        return os.path.islink(self.file) if self.file_stat else False

    @property
    def is_file(self):
        return stat.S_ISREG(self.file_stat.st_mode) if self.file_stat else False

    @property
    def is_dir(self):
        return stat.S_ISDIR(self.file_stat.st_mode) if self.file_stat else False

    @property
    def file_size(self):
        return self.file_stat.st_size if self.file_stat else 0

    @property
    def permission(self):
        return stat.S_IMODE(self.file_stat.st_mode) if self.file_stat else 0o777

    @property
    def owner(self):
        return self.file_stat.st_uid if self.file_stat else -1

    @property
    def group_owner(self):
        return self.file_stat.st_gid if self.file_stat else -1

    @property
    def is_owner(self):
        return self.owner == (os.geteuid() if hasattr(os, "geteuid") else 0)

    @property
    def is_group_owner(self):
        return self.group_owner in (os.getgroups() if hasattr(os, "getgroups") else [0])

    @property
    def is_user_or_group_owner(self):
        return self.is_owner or self.is_group_owner

    @property
    def is_user_and_group_owner(self):
        return self.is_owner and self.is_group_owner

    def check_owner_or_root(self):
        if os.getuid() == self.file_stat.st_uid:
            return True
        elif os.getuid() == 0:
            logger.warning("You are currently operating this tool using the root user."
                            " Please be aware of the risk of privilege escalation.")
            return True
        else:
            logging.error("The file owner is not consistent with the current user.")
            solution_log(SOLUTION_BASE_LOC + OWNER_SUB_CHAPTER)
            return False

    def is_basically_legal(self, perm='none', strict_permission=True):
        if sys.platform.startswith("win"):
            return self.check_windows_permission(perm)
        else:
            return self.check_linux_permission(perm, strict_permission=strict_permission)
        
    def check_basic_permission(self, perm='none'):
        if not self.is_exists and perm != 'write':
            logger.error("path: %s not exist, please check if file or dir is exist", self.file)
            return False
        if self.is_softlink:
            whitelist_path = os.environ.get(RAW_INPUT_PATH, "")
            if whitelist_path == "":
                logger.error("path : %s is a soft link, not supported, please import file(or directory) "
                             "directly", self.file)
                solution_log(SOLUTION_BASE_LOC + SOFT_LINK_SUB_CHAPTER)
                return False
            target = os.readlink(self.file)
            target_path = os.path.abspath(os.path.normpath(target)) # normpath更加规范
            file_path = os.path.abspath(os.path.normpath(self.file))
            sub_paths = whitelist_path.split("|")
            illegal_softlink = True
            for sub_path in sub_paths:
                sub_path_abs = os.path.abspath(os.path.normpath(sub_path))
                # 检查子路径本身是否是软链接
                if os.path.islink(sub_path_abs):
                    continue
                # 使用 os.path.commonpath 来比较路径
                common_path_target = os.path.commonpath([sub_path_abs, target_path])
                common_path_file = os.path.commonpath([sub_path_abs, file_path])
                # 确保公共路径与子路径相同，表示目标路径和文件路径都在子路径内
                if common_path_target == sub_path_abs and common_path_file == sub_path_abs:
                    illegal_softlink = False
                    break  # 已找到合法路径，退出循环
            if illegal_softlink:
                logger.error("path : %s is a soft link, not supported, please import file(or directory) "
                             "directly", self.file)
                solution_log(SOLUTION_BASE_LOC + SOFT_LINK_SUB_CHAPTER)
                return False
        return True

    def check_linux_permission(self, perm='none', strict_permission=True):
        if not self.check_basic_permission(perm=perm):
            return False
        if not self.is_user_or_group_owner and self.is_exists:
            logger.error("current user isn't path: %s's owner or ownergroup", self.file)
            solution_log(SOLUTION_BASE_LOC + OWNER_SUB_CHAPTER)
            return False
        if self.is_exists and not self.check_owner_or_root():
            return False
        if perm == 'read':
            if strict_permission and self.permission & READ_FILE_NOT_PERMITTED_STAT > 0:
                logger.error("The file %s is group writable, or is others writable, "
                             "as import file(or directory) permission should not be over 0o755(rwxr-xr-x)", self.file)
                solution_log(SOLUTION_BASE_LOC + PERMISSION_SUB_CHAPTER)
                return False
            if not os.access(self.realpath, os.R_OK) or self.permission & stat.S_IRUSR == 0:
                logger.error("Current user doesn't have read permission to the file %s, "
                             "as import file(or directory) permission should be at least 0o400(r--------)", self.file)
                solution_log(SOLUTION_BASE_LOC + PERMISSION_SUB_CHAPTER)
                return False
        elif perm == 'write' and self.is_exists:
            if (strict_permission or self.is_file) and self.permission & WRITE_FILE_NOT_PERMITTED_STAT > 0:
                logger.error("The file %s is group writable, or is others writable, "
                             "as export file(or directory) permission should not be over 0o755(rwxr-xr-x)", self.file)
                solution_log(SOLUTION_BASE_LOC + PERMISSION_SUB_CHAPTER)
                return False
            if not os.access(self.realpath, os.W_OK):
                logger.error("Current user doesn't have write permission to the file %s, "
                             "as export file(or directory) permission should be at least 0o200(-w-------)", self.file)
                solution_log(SOLUTION_BASE_LOC + PERMISSION_SUB_CHAPTER)
                return False
        return True

    def check_windows_permission(self, perm='none'):
        if not self.check_basic_permission(perm=perm):
            return False
        return True

    def is_legal_file_size(self, max_size):
        if not self.is_file:
            logger.error("path: %s is not a file", self.file)
            return False
        if self.file_size > max_size:
            logger.error("file_size: %s byte out of max limit %s byte", self.file_size, max_size)
            return False
        else:
            return True

    def is_legal_file_type(self, file_types: list):
        if not self.is_file and self.is_exists:
            logger.error("path: %s is not a file", self.file)
            return False
        for file_type in file_types:
            if os.path.splitext(self.file)[1] == f".{file_type}":
                return True
        logger.error("path: %s, file type not in %s", self.file, file_types)
        return False


def ms_open(file, mode="r", max_size=CONFIG_FILE_MAX_SIZE, softlink=False, 
            write_permission=PERMISSION_NORMAL, **kwargs):
    file_stat = FileStat(file)

    if file_stat.is_exists and file_stat.is_dir:
        raise OpenException(f"Expecting a file, but it's a folder. {file}")

    if file_stat.is_exists and not file_stat.check_owner_or_root():
        raise OpenException(f"There is a problem with the owner of the file. Please check it.")

    if "r" in mode:
        if not file_stat.is_exists:
            raise OpenException(f"No such file or directory {file}")
        if max_size is None:
            raise OpenException(f"Reading files must have a size limit control. {file}")
        if max_size != MAX_SIZE_UNLIMITE and max_size < file_stat.file_size:
            raise OpenException(f"The file size has exceeded the specifications and cannot be read. {file}")

    if "w" in mode and file_stat.is_exists:
        if not file_stat.is_owner:
            raise OpenException(
                f"The file owner is inconsistent with the current process user and is not allowed to write. {file}"
            )
        os.remove(file)

    if not softlink and file_stat.is_softlink:
        raise OpenException(f"Softlink is not allowed to be opened. {file}")

    if "a" in mode and file_stat.is_exists:
        if not file_stat.is_owner:
            raise OpenException(
                f"The file owner is inconsistent with the current process user and is not allowed to write. {file}"
            )
        if file_stat.permission != (file_stat.permission & write_permission):
            os.chmod(file, file_stat.permission & write_permission)

    safe_parent_msg = Rule.path().is_safe_parent_dir().check(file)
    if not safe_parent_msg:
        logger.warning(f"parent dir of {os.path.realpath(file)} is not safe. {str(safe_parent_msg)}")

    if "+" in mode:
        flags = os.O_RDONLY | os.O_RDWR
    elif "w" in mode or "a" in mode or "x" in mode:
        flags = os.O_RDONLY | os.O_WRONLY
    else:
        flags = os.O_RDONLY

    if "w" in mode or "x" in mode:
        flags = flags | os.O_TRUNC | os.O_CREAT
    if "a" in mode:
        flags = flags | os.O_APPEND | os.O_CREAT
    return os.fdopen(os.open(file, flags, mode=write_permission), mode, **kwargs)


