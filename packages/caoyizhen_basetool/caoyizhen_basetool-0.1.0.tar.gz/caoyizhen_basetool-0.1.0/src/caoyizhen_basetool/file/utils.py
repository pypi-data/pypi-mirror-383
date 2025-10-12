# -*- encoding: utf-8 -*-
# @Time    :   2025/10/11 19:57:41
# @File    :   utils.py
# @Author  :   ciaoyizhen
# @Contact :   yizhen.ciao@gmail.com
# @Function:   读取文件和保存文件
import json
from pathlib import Path
from typing import List, Dict, Literal

try:
    from tqdm import tqdm
except ImportError:
    # tqdm 没装时，定义一个假的 tqdm 占位符
    def tqdm(iterable=None, *args, **kwargs):
        return iterable if iterable is not None else []

    
def read_file(file_name: str|Path, *, output_type="list", file_type=None, main_key_column=None, encoding="utf-8", **kwargs)-> List|Dict:
    """读取文件，根据传参来判断读取的方式
    最终返回完整的一个list

    Args:
        file_name (str|Path): 文件路径
        
        output_type (Literal["list", "dict"]): 返回类型,当该值为dict的时候,需要指定output_type
        file_type (str): 文件类型,请使用`json`,`jsonl`,`xlsx`,`csv`,`txt`
        encoding (str): 文件编码方式
        key_columns (list): 需要取的列名
        main_key_column (str): 当返回为dict时,这个为key,value为其他的值,类型为dict
        output_type (Literal["list", "dict"]): 返回类型,当该值为dict的时候
        
        kwargs: 其他参数
            - sheet_name (str): 读取xlsx时，可以指定读取哪个sheet_name
        
    Returns:
        list|dict: 根据output_type返回List|Dict
    """
    
    if isinstance(file_name, str):
        file_name = Path(file_name)
        
    if file_type is None:
        file_type = file_name.suffix.lstrip(".")

    match output_type:
        case "list":
            return_data = []
        case "dict":
            return_data = {}
        case _:
            raise RuntimeError(f"output_type 传入了一个不可预知的参数:{output_type=}\n目前仅允许`list`, `dict`")
        
    
        
    match file_type:
        case "jsonl":
            with file_name.open("r", encoding=encoding) as f:
                for line in tqdm(f.readlines()):
                    if line := line.strip():
                        line = json.loads(line)
                        if isinstance(return_data, list):
                            return_data.append(line)
                        elif isinstance(return_data, dict):
                            if main_key_column not in line:
                                raise RuntimeError(f"对象没有{main_key_column=}\n原始数据:{row}")

                            value = line[main_key_column]
                            return_data[value] = line
                return return_data
            
        case "json":
            with file_name.open("r", encoding=encoding) as f:
                data = json.load(f)
                assert isinstance(data, list), "理论上，这里应该是list[dict]结构，但是不是,目前无法解决这个问题，请自己写把!!!"
                if output_type == "dict":
                    for row in tqdm(data):
                        if main_key_column not in row:
                            raise RuntimeError(f"对象没有{main_key_column=}\n原始数据:{row}")
                        value = row[main_key_column]
                        return_data[value] = row     
                            
                    return return_data
                else:
                    return data
                
        case "xlsx":
            # 这里导包, 可以让不用pandas时不安装包
            import pandas as pd
            data = pd.read_excel(file_name, **kwargs)
            
            if isinstance(return_data, list):
                for _, row in tqdm(data.iterrows(), total=data.shape[0]):
                    row = row.to_dict()
                    return_data.append(row)
            elif isinstance(return_data, dict):
                for _, row in tqdm(data.iterrows(), total=data.shape[0]):
                    row = row.to_dict()
                    if main_key_column not in row:
                        raise RuntimeError(f"对象没有{main_key_column=}\n原始数据:{row}")
                    value = row[main_key_column]
                    return_data[value] = row     
            return return_data
            
                
        case "csv":
            import pandas as pd
            data = pd.read_csv(file_name, **kwargs)
            
            if isinstance(return_data, list):
                for _, row in tqdm(data.iterrows(), total=data.shape[0]):
                    row = row.to_dict()
                    return_data.append(row)
            elif isinstance(return_data, dict):
                for _, row in tqdm(data.iterrows(), total=data.shape[0]):
                    row = row.to_dict()
                    
                    if main_key_column not in row:
                        raise RuntimeError(f"对象没有{main_key_column=}\n原始数据:{row}")
                    value = row[main_key_column]
                    return_data[value] = row     
            return return_data

        case _:
            raise RuntimeError(f"无法识别后缀{file_type=}是什么格式的文件,请传入file_type来控制或修改后缀名")
        

def save_file(file_name: str|Path, data: list, file_type=None, *, encoding="utf-8", ensure_ascii=False, json_indent=4, pd_index=False,**kwargs):
    if isinstance(file_name, str):
        file_name = Path(file_name)
    
    if file_type is None:
        file_type = file_name.suffix.lstrip(".")
        
    match file_type:
        case "jsonl":
            with file_name.open("w", encoding=encoding) as f:
                for item in data:
                    f.write(json.dumps(item, ensure_ascii=ensure_ascii) + "\n")
        case "json":
            with file_name.open("w", encoding=encoding) as f:
                json.dump(data, f, ensure_ascii=ensure_ascii, indent=json_indent)
        case "xlsx":
            import pandas as pd
            data = pd.DataFrame(data)
            data.to_excel(file_name, **kwargs, index=pd_index)
        case "csv":
            import pandas as pd
            data = pd.DataFrame(data)
            data.to_csv(file_name, **kwargs, index=pd_index)
    
    
    
    