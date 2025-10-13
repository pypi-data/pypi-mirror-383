"""
@Author: 馒头 (chocolate)
@Email: neihanshenshou@163.com
@File: FileOperateFormat.py
@Time: 2023/12/9 18:00
"""

import json
import os
import time
from typing import Union, Any, Literal

import pandas
import yaml


class FileNames:
    """
    文件名称
    """
    LogFile = f"{time.strftime('%F')}.log"
    ScreenShotFile = f"{time.strftime('%F')}.png"
    ExcelFile = f"{time.strftime('%F')}.xlsx"
    CsvFile = f"{time.strftime('%F')}.csv"
    YamlFile = f"{time.strftime('%F')}.yaml"
    JsonFile = f"{time.strftime('%F')}.json"
    TxtFile = f"{time.strftime('%F')}.txt"


class FileOperate:

    @staticmethod
    def _is_json_serializable(data: str):
        """
        判断一个对象 是否能够json格式化
        :param data: 字符串
        :return: bool
        """
        try:
            json.loads(data)
            return True
        except Exception as e:
            return False and e

    @staticmethod
    def _is_yaml_serializable(data: str):
        """
        判断一个对象 是否能够yaml格式化
        :param data: 字符串
        :return: bool
        """
        try:
            yaml.safe_load(data)
            return True
        except Exception as e:
            return False and e

    @staticmethod
    def read_excel(filename, sheet_name='Sheet1'):
        """
            读取Excel文件内容
        :param filename: filename: Excel文件名称
        :param sheet_name: Excel文件sheet表名
        :return: excel.to_dict(orient="list") or excel.to_dict(orient="dict")
        """
        excel = pandas.read_excel(filename, sheet_name=sheet_name, engine='openpyxl')
        return excel

    @staticmethod
    def write_excel(data: dict, filename, sheet_name='Sheet1', show=True):
        """
            写入Excel文件内容
        :param data: {"a": [1, 2, 3], "b": [4, 5, 6]}
        :param filename: Excel文件名称
        :param sheet_name: Excel文件sheet表名
        :param show: 打印结束标志
        :return: None
        """
        df1 = pandas.DataFrame(data)
        df1.to_excel(filename, sheet_name=sheet_name, index=False, engine='openpyxl')
        if show:
            print(f"✅ excel: {filename} 写入完成")

    @staticmethod
    def write_excel_with_many_sheets(filename, data):

        # Create a dictionary of DataFrames
        dfs = {sheet_name: pandas.DataFrame(sheet_data) for sheet_name, sheet_data in data.items()}

        # Write to Excel with multiple sheets
        with pandas.ExcelWriter(filename) as writer:
            for sheet_name, df in dfs.items():
                df.to_excel(writer, sheet_name=sheet_name, index=False)

        print(f'Multiple sheets written to {filename}')

    @staticmethod
    def read_csv(filename, orient: Literal["dict", "list", "series", "split", "tight", "records", "index"] = "list"):
        """
            读取csv文件内容
        :param filename: filename: csv文件名称
        :param orient:
        :return: csv_data type: list or dict
        """
        csv_obj = pandas.read_csv(filepath_or_buffer=filename)
        csv_data = csv_obj.to_dict(orient=orient)
        return csv_data

    @staticmethod
    def write_csv(data: dict, filename, encoding="utf-8", show=True):
        """
            写入Excel文件内容
        :param data: {"a": [1, 2, 3], "b": [4, 5, 6]}
        :param filename: csv 文件名称
        :param encoding: csv 文件编码
        :param show: 打印结束标志
        :return: None
        """
        df1 = pandas.DataFrame(data)
        df1.to_csv(path_or_buf=filename, index=False, encoding=encoding)
        if show:
            print(f"✅ csv: {filename} 写入完成")

    @staticmethod
    def read_file(filename: str = '', key: str = None, mode='r', encoding: Any = "utf-8", jsonify=False, yamlify=False):
        """
        读取文件, 若文件内容可以json格式化、yaml格式化 则返回dict, 反之返回字符串
        :param filename: 文件名称
        :param key: 键值
        :param encoding: 编码
        :param jsonify: json格式化开关
        :param yamlify: yaml格式化开关
        :param mode: 读取模式
        :return: dict or str
        """
        with open(file=filename, mode=mode, encoding=encoding) as f:
            _data = f.read()

        if len(_data) >= 1:
            if FileOperate._is_json_serializable(data=_data) and jsonify:
                js = json.loads(_data)
                return js[key] if key else js
        if FileOperate._is_yaml_serializable(data=_data) and yamlify:
            y = yaml.safe_load(_data)
            return y[key] if key else y

        return _data

    @staticmethod
    def read_json(filename: str, key: str = None, encoding: Any = "utf-8"):
        return FileOperate.read_file(filename=filename, key=key, encoding=encoding, jsonify=True)

    @staticmethod
    def read_yaml(filename: str, key: str = None, encoding: Any = "utf-8"):
        return FileOperate.read_file(filename=filename, key=key, encoding=encoding, yamlify=True)

    @staticmethod
    def read_txt(filename: str, encoding: Any = "utf-8"):
        return FileOperate.read_file(filename=filename, encoding=encoding)

    @staticmethod
    def write_file(filename: str, data: Union[list, dict, str, bytes], mode='w', encoding: Any = "utf-8", show=True):
        """
        写入文件
        :param filename: 文件名称
        :param data: 内容
        :param encoding: 编码格式
        :param mode: 读写模式
        :param show: 打印结束标志
        :return: None

        example:
                FileOperate.write_file(
                    filename="demo.csv",
                    data="a,b,c\n1,2,3"
                )

                FileOperate.write_file(
                    filename="demo.json",
                    data={}
                )

                FileOperate.write_file(
                    filename="demo.yaml",
                    data=[{"name": "a"}, {"name": "b"}]
                )
                and so on ...

        """
        if filename.endswith('json'):
            data = json.dumps(data, ensure_ascii=False)
        if filename.endswith('yaml'):
            data = yaml.safe_dump(data, allow_unicode=True)
        if isinstance(data, (list, dict)):
            data = json.dumps(data, ensure_ascii=False, indent=4)
        with open(file=filename, mode=mode, encoding=encoding) as f:
            f.write(data)
        if show:
            print(f"✅ 文件: {filename} 写入完成!")

    @staticmethod
    def traverse_directory(directory, exclude="venv, idea", show=False):
        """
        遍历指定目录及其子目录中的所有文件
        :param directory: 需要遍历的目录
        :param exclude: 需要排除的目录
        :param show: 是否展示遍历的文件
        """
        result = []
        excludes = [each.strip() for each in exclude.split(",")]
        for root, dirs, files in os.walk(directory):
            for file in files:
                file_path = os.path.join(root, file)
                if all([each not in file_path for each in excludes]):
                    if show:
                        print(file_path)
                    result.append(file_path)
        return result
