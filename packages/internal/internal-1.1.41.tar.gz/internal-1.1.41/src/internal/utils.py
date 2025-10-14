# -*- coding: utf-8 -*-
import json
import hashlib
from datetime import datetime, timezone

import arrow

from .base_config import BaseConfig
from .const import STR_EMPTY, ARR_EXPORT_DATETIME_FMT, STR_DASH, REDIS_LPR_DATA_LIST_PREFIX


def is_today(time, system_time_zone):
    if not time:
        return False

    return arrow.now(system_time_zone).floor("day") == arrow.get(time).to(system_time_zone).floor("day")


def get_tz_day_boundary(date_time, time_zone, out_tz="UTC"):
    """
    傳入date_time，取其在dt_tz時區的當天的floor與ceil，以out_tz時區回傳
    比對區間需使用gte/lte
    """
    date_time = arrow.get(date_time) if date_time else arrow.get()
    tz_time = date_time.to(time_zone)
    return tz_time.floor("day").to(out_tz), tz_time.ceil("day").to(out_tz)


def timestamp_interval(start, end, interval_sec):
    while start < end:
        yield start
        start += interval_sec


def export_time_format(date, time_zone, fmt=ARR_EXPORT_DATETIME_FMT):
    if not date:
        return STR_EMPTY

    return arrow.get(date).to(time_zone).format(fmt)


def update_dict_with_cast(curr_settings: BaseConfig, new_conf: dict):
    if issubclass(type(curr_settings), BaseConfig):
        for key, value in new_conf.items():
            if hasattr(curr_settings, key):
                key_type = type(getattr(curr_settings, key))
                cast_func = key_type if key_type in (str, int) else json.loads
                setattr(curr_settings, key, cast_func(value))


def sanitize_plate_no(plate_no):
    return plate_no.replace(STR_DASH, STR_EMPTY).upper()


def get_current_utc() -> datetime:
    return datetime.now(timezone.utc)


def get_lpr_data_list_redis_key(organization_id, plate_no):
    return f"{REDIS_LPR_DATA_LIST_PREFIX}_{organization_id}_{plate_no}"


async def mask_name(input_string: str, start_index: int = 1, end_index: int = None, mask_char: str = "o"):
    """
    将姓名的前 start_index 个字符保留，其余字符替换为 'o'，用于隐码处理。

    :param mask_char: 隱碼替換字符
    :param input_string: 要隐码的姓名字符串
    :param start_index: 从第几位开始进行隐码处理（默认值为 1）
    :param end_index:  从第几位結束进行隐码处理（默认值为 None）
    :return: 隐码处理后的字符串
    """
    if not input_string:
        return None

    if end_index is None or end_index > len(input_string):
        end_index = len(input_string)

    # 保留前 start_index 个字符
    visible_part_start = input_string[:start_index]

    # 保留从 end_index 之后的字符
    visible_part_end = input_string[end_index:]

    # 创建隐码部分，其余字符替换为 mask_char
    masked_part = mask_char * (end_index - start_index)

    return visible_part_start + masked_part + visible_part_end


def get_dealer_by_organization_id(organization_id: str) -> str:
    """
    將組織代碼為 3 段（例如 'BMW_LONGDER_NH'）時，裁切為前兩段（'BMW_LONGDER'）。
    否則回傳原本的 organization_id。
    """
    if not organization_id or not isinstance(organization_id, str):
        return organization_id

    parts = organization_id.strip().split("_")

    if len(parts) < 2:
        raise ValueError("organization_id is invalid")

    if len(parts) >= 3:
        return "_".join(parts[:2])

    return organization_id


def extract_title(name):
    if '小姐' in name:
        return '小姐'
    elif '女士' in name:
        return '女士'
    elif '先生' in name:
        return '先生'
    else:
        return None


def extract_name(name):
    """从姓名中提取真实姓名"""
    # 检查是否包含 '小姐' 或 '先生' 并提取姓名
    if '小姐' in name:
        return name.split('小姐')[0].strip()
    elif '女士' in name:
        return name.split('女士')[0].strip()
    elif '先生' in name:
        return name.split('先生')[0].strip()
    else:
        return name.strip()


def hash_login_password(passwd):
    prefix = '___'
    postfix = '_______'
    data = str(passwd)
    sha_256 = hashlib.sha256()
    sha_256.update(prefix.encode())
    sha_256.update(data.encode())
    sha_256.update(postfix.encode())

    return sha_256.hexdigest()


def hash_secret_key(passwd):
    prefix = '___'
    postfix = '_______'
    data = str(passwd)
    sha_256 = hashlib.sha256()
    sha_256.update(prefix.encode())
    sha_256.update(data.encode())
    sha_256.update(postfix.encode())

    return sha_256.hexdigest()
