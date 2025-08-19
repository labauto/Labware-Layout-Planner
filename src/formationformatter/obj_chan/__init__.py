"""
[1] obje-kun プロセスフローからオブジェクトリストを出すやつ
入力：自然言語のプロセスフロー + 制約条件
e.g. 新しいチューブに10 mLの培地と1 mLのサプリメントを入れる … + この機械は50 mlチューブを使えない
出力：[{“オブジェクト名”: “xx”, “個数”: “xx”, “制約”: “???”}, …]
e.g. [{“オブジェクト名”: “10 mlチューブ”, “個数”: 2, “制約”: “0 ml以上10 mlまで”}, …]
オブジェクトリストでプロセスフローが実行可能かをどう判定する？
言語モデルでつくるとこれが難しそう
使えるものの種類と在庫を先に与える？
であればルールベースでいけそう
"""

import json
import os
from dataclasses import MISSING, dataclass, field, fields
from datetime import datetime
from typing import Dict, List, Tuple, Union

import sys
import os
print('File', os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
# from .config import OPENAI_KEY
from src.formationformatter.config import config
OPENAI_KEY = config.openai_key
import openai
from src.formationformatter.utils import custom_print
from .prompts import PROMPT

def object_labware_default():
    return {"id": 0, "name": "generic"}

@dataclass
class Object:
    name: str = "Unknown"  # e.g. 1.5 ml tube
    quantity: int = 0  # e.g. 1.5
    init_content: str = "Unknown"  # e.g. DMEM
    labware: dict = field(default_factory=object_labware_default)  # e.g. {"id": 1, "name": "1.5_ml_tube"}
    unit: str = "unitless"  # e.g. ml

    def search_constraints(self, constraints: List[Tuple['Object', List[int]]]) -> List[int]:
        matching_stations = []
        for constraint_obj, restricted_stations in constraints:
            is_match = True
            for f in fields(self):
                attr_name = f.name
                constraint_value = getattr(constraint_obj, attr_name)

                # デフォルト値の取得
                if f.default is not MISSING:
                    default_value = f.default
                elif f.default_factory is not MISSING:
                    default_value = f.default_factory()
                else:
                    default_value = None

                # もしフィールドが dict 型（例: labware）の場合はキー単位でチェックを行う
                if isinstance(default_value, dict) and isinstance(constraint_value, dict):
                    # constraint の各キーについて、デフォルト値と異なる値のみチェックする
                    for key, c_val in constraint_value.items():
                        default_key_val = default_value.get(key)
                        # キーの値がデフォルトならチェック対象外
                        if c_val == default_key_val:
                            continue
                        # 対象オブジェクトの辞書から同じキーの値を取得してチェック
                        self_labware_value = getattr(self, attr_name).get(key)
                        if self_labware_value != c_val:
                            is_match = False
                            break
                    if not is_match:
                        break
                    # dict のフィールドはここで処理済みなので次のフィールドへ
                    continue

                # dict 以外の場合は以下の比較ロジックを適用
                # constraint の値がデフォルト値ならチェック対象外
                if constraint_value == default_value:
                    continue
                # 対象オブジェクトの属性と一致していればマッチ
                elif getattr(self, attr_name) == constraint_value:
                    continue
                # それ以外は不一致
                else:
                    is_match = False
                    break

            if is_match:
                print(f"Matching station found: {constraint_obj.name} with positions {restricted_stations}")
                matching_stations.extend(restricted_stations)
        # 重複のないリストを返す
        return list(set(matching_stations))


# JSONファイルからデータを読み込み、List[Object]に変換する関数
def load_objects(file_path: str) -> List[Object]:
    with open(file_path, "r", encoding="utf-8") as f:
        raw_data = json.load(f)
    
    # デフォルト値を埋めてObjectに変換
    objects = []
    for item in raw_data:
        obj = Object(
            name=item.get("name", "Unknown"),  # デフォルト値: "Unknown"
            quantity=item.get("quantity", 0),  # デフォルト値: 0
            init_content=item.get("init_content", "Unknown"),  # デフォルト値: "Unknown"
            labware=item.get("labware", {"id": 0, "name": "generic"}),  # デフォルト値: 汎用ラボ器具
            unit=item.get("unit", "unitless")  # デフォルト値: "unitless"
        )
        objects.append(obj)
    return objects


@dataclass
class Constraints:
    allowed_objects: List[Object]

    def __post_init__(self):
        # ファイルパスが与えられた場合は、オブジェクトリストを読み込む
        if isinstance(self.allowed_objects, str):
            self.allowed_objects = load_objects(self.allowed_objects)
        

def init_settings():
    openai.api_key = OPENAI_KEY

    # model_list = openai.Model.list()
    # custom_print(file_path=log_file_path, text=f'OpenAI Model List: ', model_list)
    return

def _post_process_gpt_response(result: str) -> str:
    """
    Post process GPT response.
    """
    # delete ```json``` if any
    result = result.replace('```json', '').replace('```', '')
    # replace all None with ''
    result = result.replace('None', "''")
    return result

def _extract_results_from_gpt_response(result: str, log_file_path: str) -> List[Object]:
    """
    Extract JSON results from GPT response.
    
    {   "labware":
            [
                {"name": "1.5 ml tube sample", "quantity": 1.5, "unit": "ml", "init_content": "sample", "labware": {"id": 1, "name": "1.5_ml_tube"}},
                {"name": "96 well plate medium", "quantity": 1, "unit": "ml", "init_content": "medium", "labware": {"id": 2, "name": "corning_96_wellplate_360ul_flat"}},
                {"name": "15 ml tube", "quantity": 0, "unit": "", "init_content": "", "labware": {"id": 3, "name": "15_ml_tube"}}
            ]
    }
    """
    # pre process
    # delete ```json``` if any
    result = result.replace('```json', '').replace('```', '')

    custom_print(file_path=log_file_path, text=f'obj-chan preprocess result:\n{result}')
    # replace all None with ''
    result = _post_process_gpt_response(result)
    custom_print(file_path=log_file_path, text=f'obj-chan postprocess result:\n{result}')

    text_to_dict = lambda x: json.loads(x.replace('\'', '\"'))
    results = text_to_dict(result.replace('extracted_results:', '').replace('extracted_results_end:', '').strip())
    results = results['labware']
    objects = [Object(
        name=object['name'],
        quantity=object['quantity'],
        init_content=object['init_content'],
        labware=object['labware'],
        unit=object['unit']
    ) for object in results]
    return objects

def check_constraints_and_generate_error_messages(object_list: List[Object], constraints: Constraints, remove=False) -> List[str]:
    """
    Given the extracted object list and constraints, check if the object list satisfies the constraints.
    If not, generate error messages and return them.
    """
    allowed_object_names = [object.name for object in constraints.allowed_objects]
    allowed_objects_original_quantity = {object.name: object.quantity for object in constraints.allowed_objects}
    allowed_objects_quantity = {object.name: object.quantity for object in constraints.allowed_objects}
    err_messages = []
    for object in object_list:
        if object.name not in allowed_object_names:
            if remove:
                object_list.remove(object)
                err_msg = f'Removed {object.name} from object list because it is not allowed. Please use different object instead.'
            else:
                err_msg = f'You have used {object.name} that is not allowed. Please use different object instead.'
            err_messages.append(err_msg)

        if object.name not in allowed_objects_quantity:
            err_msg = f'You have used {object.name} that is not allowed. Please use different object instead.'
            err_messages.append(err_msg)
            continue

        allowed_objects_quantity[object.name] -= object.quantity
        if allowed_objects_quantity[object.name] < 0:
            err_msg = f'You have used {object.name} more than allowed quantity. Please use different object instead.'
            err_messages.append(err_msg)

    return err_messages

def get_process_flow_text(model='gpt-3.5-turbo-16k') -> str:
    # ask GPT
    prompt = """
Could you generate a process flow text of biological experiments? For example,

Example 1:

Process flow text:
```
1) Add 100 uL of sample from 1.5 ml tube to 96 well plate.
2) Transfer 10 ml medium to 15 ml tube.
3) Add 300 µl of the medium from 15 ml tube to 96 well plate.
```

Example 2:

Process flow text:
```
Add 5 ml DMEM from 15 ml tube to 90 mm dish.
And then add 5 ml MEMa from 15 ml tube to the same dish.
Finally, add 10 µl sample from 1.5 ml tube to the same dish.
```

Please make sure you only generate process flow text without any other text so that we can extract the results correctly.

Now it's your turn to fill the process flow text.

Process flow text:
    """
    res = openai.ChatCompletion.create(
        model=model,
        messages=[
            {"role": "system", "content": "You are a helpful assistant who is an expert in biology, computer science, and engineering."},
            {
                "role": "user",
                "content": prompt,
            },
        ],
    )
    should_be_process_flow: str = res['choices'][0]['message']['content']
    return should_be_process_flow


def save_result(
    prompt: str,
    constraints: Constraints,
    result: str,
    errors: str,
    version: str = 'v1',
    model: str = 'gpt-3.5-turbo-16k'
):
    current_datetime = datetime.now().strftime('%Y%m%d%H%M%S')
    filename = f'result_{version}_{model}_{current_datetime}.txt'
    file_path = os.path.join(RESULT_SAVE_PATH, filename)
    with open(file_path, 'w') as f:
        f.write(f'*************PROMPT*************\n{prompt}\n\n*************CONSTRAINTS*************\n{str(constraints)}\n\n*************RESULT*************\n{result}\n\n*************ERRORS*************\n{errors}')


def get_object_list(process_flow: str, constraints: Constraints, messages: List[Dict], model='gpt-3.5-turbo-16k', log_file_path: str = '') -> List[Object]:
    """
    process_flow: str
    constraints: dict
    messages: List of conversation messages
    """
    prompt = PROMPT['v6.labwarelist'].replace('{__process_flow_text__}', process_flow).replace('{__available_labware_list__}', str([object.name for object in constraints.allowed_objects]))
    # Update messages with the latest user prompt
    messages.append({"role": "user", "content": prompt})

    # ask GPT
    res = openai.ChatCompletion.create(
        model=model,
        messages=messages,
    )
    answer = res['choices'][0]['message']['content']
    messages.append({"role": "assistant", "content": answer})

    results = _extract_results_from_gpt_response(answer, log_file_path)
    errors = check_constraints_and_generate_error_messages(results, constraints)

    return results, errors


def run(process_flow: str, constraints: Constraints, messages: List[Dict] = None, log_file_path=None):
    if messages is None:
        messages = [
            # {"role": "system", "content": "You are a helpful assistant who is an expert in biology, computer science, and engineering."},
            {"role": "user", "content": process_flow},
        ]

    res, errors = get_object_list(process_flow, constraints, messages, log_file_path=log_file_path)
    custom_print(file_path=log_file_path, text=f'\n\nProcess Flow ******************\n{process_flow}\n\nConstraints ******************\n{constraints}\n\nExtracted Object List******************\n{res}')
    return res, errors

if __name__ == '__main__':
    init_settings()
    test_obj = Object()
    test_obj.name = '1.5 ml tube'
    default_obj = Object()

    constraint = list()
    constraint.append((default_obj, [0, 1, 2]))

    print(test_obj.search_constraints(constraint))
    
    test_obj2 = Object()
    test_obj2.name = '1.5 ml tube'
    test_obj2.quantity = 1.5

    print(test_obj2.search_constraints(constraint))
