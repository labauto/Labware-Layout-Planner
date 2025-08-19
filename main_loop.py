from datetime import datetime
import shutil
from src.formationformatter.obj_chan import Object as ObjchanObject
from src.formationformatter.obj_chan import run as obj_chan, Constraints
from src.formationformatter.haichi_kun import sort_objects_by_constraints, permutations
from src.formationformatter.code_chan import CodeChan
from src.formationformatter.check_chan import Chack_chan, Object, Station
import uuid
import json
from pathlib import Path
import os
from typing import Any, List, Optional, Tuple
# from input import PROCESS_FLOW_DICT, PROCESS_FLOW_NAME, CELL, MEDIUM, OT2_STATIONS as stations, PROMPT, PROMPT_TEMPLATE_SCRIPT, PROMPT_HAICHI, PROMPT_骨子_HAICHI_REPLACE
from src.formationformatter.utils import save_initial_position, call_llm, save_object_initial_position_with_text, write_file, custom_print
from src.formationformatter.functions import get_object_list, get_haichi, get_骨子_script, get_OT2_script, get_OT2_with_haichi_script, run_check_chan, load_restricted_stations, get_OT2_with_haichi_based_on_骨子_script
from src.formationformatter.config import config
# full_path = os.path.dirname(os.path.realpath(__file__))
# path, filename = os.path.split(full_path)
# print(f"{full_path=}")
# BASE_DIR = os.path.join(full_path, "results")
BASE_DIR = config.base_dir
AUTO_MODE = config.auto_mode
os.makedirs(BASE_DIR, exist_ok=True)
print(f"BASE_DIR: {BASE_DIR}")


"""
設定
"""
from src.formationformatter.config import config as config
process_flow = config.process_flow
replace_word = "___processflow___"
if replace_word not in config.prompt:
    raise ValueError(f"replace_word: {replace_word} is not in the prompt.")
prompt = config.prompt.replace(replace_word, process_flow)
replace_word = "___processflow___"
if replace_word not in config.prompt_template:
    raise ValueError(f"replace_word: {replace_word} is not in the prompt_template.")
# prompt_template_script = config.prompt_template.replace(replace_word, process_flow)
prompt_template_script = config.prompt_template
replace_word = "___processflow___"
if replace_word not in config.prompt_haichi:
    raise ValueError(f"replace_word: {replace_word} is not in the prompt_haichi.")
prompt_haichi = config.prompt_haichi.replace(replace_word, process_flow)
prompt_骨子_haichi_replace = config.prompt_骨子_haichi_replace.replace("___processflow___", process_flow)
model = config.model
base_id = datetime.now().strftime('%Y_%m_%d_%H_%M_%S_') + str(uuid.uuid4()) + '/iteration_'
is_error = False


def main_loop():

    """
    FF のメインループ
    入力された自然言語 (process flow)をもとに、各componentを呼ぶ
    """
    for i in range(config.max_iter):
        next_loop = False
        continue_input = ""
        """ ループさせる """
        id = base_id + str(i)

        log_file_path = os.path.join(BASE_DIR, f'{id}/log.txt')
        os.makedirs(os.path.join(BASE_DIR), exist_ok=True)
        # Path(os.path.join(BASE_DIR)).makedirs(exist_ok=True)
        Path(os.path.join(BASE_DIR, f"{id}")).mkdir(parents=True, exist_ok=True)
        custom_print(file_path=log_file_path, text=f"{os.path.join(BASE_DIR, f'{id}')=}")
        custom_print(file_path=log_file_path, text=f'*********************** {id} **************************')
        custom_print(file_path=log_file_path, text=f'******************************************************')

        with open(os.path.join(BASE_DIR, f"{id}/process_flow.txt"), "w") as f:
            f.write(process_flow)

        """ ここで各要素を実行する """
        """ 1. obj-chan """
        object_list = get_object_list(process_flow, id, log_file_path=log_file_path)
        while True:
            if AUTO_MODE:
                continue_input = "y"
                if len(object_list) == 0:
                    continue_input = "y"
                    next_loop = True
                    break
            else:
                continue_input = input("Continue? (y/n): ")

            if continue_input == "y" or continue_input == "":
                break
            elif continue_input == "n":
                while True:
                    continue_input = input("next loop? (y/n): ")
                    if continue_input == "y" or continue_input == "":
                        next_loop = True
                        break
                    elif continue_input == "n":
                        return
                break
            elif continue_input == "del":
                shutil.rmtree(os.path.join(BASE_DIR, f"{id}"))
                custom_print(file_path=log_file_path, text=f"Deleted: {os.path.join(BASE_DIR, f'{id}')}")
                while True:
                    continue_input = input("next loop? (y/n): ")
                    if continue_input == "y" or continue_input == "":
                        next_loop = True
                        break
                    elif continue_input == "n":
                        return
                break
            else:
                custom_print(file_path=log_file_path, text="Please input y or n")
        custom_print(file_path=log_file_path, text=f"object_list_num: {len(object_list)}")
        prompt_template_script = prompt_template_script.replace("___object_list___", str(object_list))
        if next_loop:
            continue
        restricted_stations: List[Tuple[ObjchanObject, List[int]]] = load_restricted_stations(object_list=object_list, resticted_stations_path=Path(config.absolute_restriction_path))
        """ 2. haichi-kun"""
        stations = Chack_chan()
        # List[List[Tuple[ObjchanObject, List[int]]]] を返すようにする
        haichi = get_haichi(stations, restricted_stations, id, log_file_path=log_file_path)

        while True:
            if AUTO_MODE:
                continue_input = "y"
            else:
                continue_input = input("Continue? (y/n): ")

            if continue_input == "y" or continue_input == "":
                break
            elif continue_input == "n":
                return
            else:
                custom_print(file_path=log_file_path, text="Please input y or n")

        if next_loop:
            continue

        """ check chanを実行する """
        """ 4. check-chan"""
        pass_check = False
        passed_first_ten_haichi = []
        Path(os.path.join(BASE_DIR, f"{id}", "initial_positions")).mkdir(exist_ok=True)
        success_count = 1
        for i, haichi_i in enumerate(haichi):
            # ここで、haichi_i は List[Tuple[ObjchanObject, List[int]]] となっているため、run_check_chanの引数を変更してobject_listを削除（haichiと併合）
            check_chan_result, visualization = run_check_chan(
                haichi_i,
                id,
                base_path="",
                log_file_path=log_file_path,
            )
            if all(check_chan_result):
                """ 初期配置の図を保存 """
                with open(os.path.join(BASE_DIR, f"{id}/initial_positions/initial_position_{success_count}_visualization.md"), "w") as f:
                    f.write(visualization)
                passed_first_ten_haichi.append(haichi_i)
                success_count += 1

            if success_count > 10:
                break

        if len(passed_first_ten_haichi) > 0:
            pass_check = True
            save_initial_position(passed_first_ten_haichi, os.path.join(BASE_DIR, f"{id}/initial_positions/initial_positions.json"))
            natural_language_instruction = save_object_initial_position_with_text(
                object_list=object_list,
                initial_positions=passed_first_ten_haichi[0],
                protocol=process_flow,
                base_path=BASE_DIR,
                id=id,
                filename="representative_initial_position.txt",
                log_file_path=log_file_path,
            )
        else:
            """ TODO: ここでエラーが出たら記録して、次のループにエラー情報を渡せるようにする """
            is_error = True
            custom_print(file_path=log_file_path, text=f"Error: I couldn't find any initial position that satisfies the constraints.")
            continue
    
        if pass_check:
            custom_print(file_path=log_file_path, text=f"OK: {haichi_i}")
            """ 5. OT2スクリプト with 配置 replaced from 骨子_script"""
            # OT2_script = get_OT2_script(prompt, 骨子_script, process_flow, model, id)

            err_msg = ""
            骨子_script = ""
            for iteratation in range(10):
                """ 3. code-chan """
                """ 3.1 骨子スクリプト """
                flow = f"\n# Process flow:\n```{process_flow}\n```" + "" if err_msg == "" else f"\n# This is the error message: \n ```{err_msg}\n```\n# original protocol: \n ```{骨子_script}\n```\n"
                custom_print(file_path=log_file_path, text=f"Generate 骨子スクリプト from \n~~~~~~~~~~\n{flow}\n~~~~~~~~~~")
                骨子_script = get_骨子_script(prompt_template_script, flow, model, id, log_file_path)
                OT2_with_replaced_haichi_script_based_on_haichi_and_骨子_script, output_path, output_text, result_type = get_OT2_with_haichi_based_on_骨子_script(
                    prompt=prompt_骨子_haichi_replace,
                    process_flow=process_flow,
                    haichi=haichi_i,
                    骨子script=骨子_script,
                    model=model,
                    id=id,
                    log_file_path=log_file_path,
                    results_dir=BASE_DIR,
                )
                if result_type == "ok":
                    # final_obj_list, errors = get_object_list(OT2_with_replaced_haichi_script_based_on_haichi_and_骨子_script, id, filename='final_obj_list.json')
                    break
                else:
                    err_msg = output_text
                    custom_print(file_path=log_file_path, text=f"Errorがでたので骨子スクリプトを再生成します: {err_msg}")
                    continue
            is_error = True
            continue
        """ 次のループへ行く """


if __name__ == "__main__":
    main_loop()

