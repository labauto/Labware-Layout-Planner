import copy
from src.formationformatter.obj_chan import run as obj_chan, Constraints, Object as ObjchanObject
from src.formationformatter.haichi_kun import sort_objects_by_constraints, permutations
from src.formationformatter.code_chan import CodeChan
from src.formationformatter.check_chan import Chack_chan, Object, Station
import uuid
import json
from pathlib import Path
import os
from typing import Any, Optional, List, Tuple

from src.formationformatter.utils import write_file, custom_print, DataclassEncoder
from src.formationformatter.config import config

# full_path = os.path.dirname(os.path.realpath(__file__))
# path, filename = os.path.split(full_path)
# BASE_DIR = os.path.join(os.path.dirname(full_path), "FF", "results")

from src.formationformatter.config import config
BASE_DIR = config.base_dir
print(f"BASE_DIR: {BASE_DIR}")


def get_object_list(process_flow: str, id: str, filename: str = "object_list.json", log_file_path: str = '') -> list:
    """get_object_list

    Args:
        process_flow (str): process_flow
        id (str): uuid

    Returns:
        list: object_list e.g.
    """
    max_retries = 10  # Maximum number of retries
    attempt = 0  # Retry counter
    messages = [
        {"role": "system", "content": "You are a helpful assistant who is an expert in biology, computer science, and engineering."},
        {"role": "user", "content": process_flow},
    ]
    # Load the constraints from path (config.allowed_objects: str)
    constraints = Constraints(config.allowed_objects_path)
    process_flow_modified = copy.deepcopy(process_flow)
        
    while attempt < max_retries:
        try:
            # Call obj_chan (which is run()) with process_flow and messages
            custom_print(file_path=log_file_path, text=f"************ Obj-chan start ************")
            custom_print(file_path=log_file_path, text=f"process_flow: {process_flow_modified}")
            object_list, obj_chan_errors = obj_chan(
                process_flow=process_flow_modified,
                constraints=constraints,
                messages=messages,  # Pass the conversation history,
                log_file_path=log_file_path
            )
            # If successful, break out of loop
            custom_print(file_path=log_file_path, text=f"************ Obj-chan result ************")
            custom_print(file_path=log_file_path, text=f"object_list: {object_list}")
            write_file(
                BASE_DIR,
                id,
                'obj_chan',
                filename,
                "json",
                [object.__dict__ for object in object_list]
            )
            return object_list  # Success
        except Exception as e:
            import traceback
            attempt += 1
            custom_print(file_path=log_file_path, text=f'Attempt {attempt} failed with error: {e}')
            traceback_str = traceback.format_exc()
            process_flow_modified = process_flow + f"\n# Error: {e}\n"
            custom_print(file_path=log_file_path, text=f"process_flow_modified: {process_flow_modified}")
            error_message = f'''
There was an error extracting the object list: {traceback_str}. Please fix the errors. Here's the correct JSON format. Also, make sure not to output anything other than JSON! Output only JSON.
```json
[
    {{"name": "1.5 ml tube sample", "quantity": 1.5, "unit": "ml", "init_content": "sample", "labware": {{"id": 1, "name": "1.5_ml_tube"}}}},
    {{"name": "96 well plate medium", "quantity": 1, "unit": "ml", "init_content": "medium", "labware": {{"id": 2, "name": "corning_96_wellplate_360ul_flat"}}}},
    {{"name": "15 ml tube", "quantity": 0, "unit": "", "init_content": "", "labware": {{"id": 3, "name": "15_ml_tube"}}}}
]
'''
            # Update messages with the error message
            messages.append({"role": "assistant", "content": error_message})
            custom_print(file_path=log_file_path, text=f"Traceback: {traceback_str}")
            custom_print(file_path=log_file_path, text=f"Retrying... (Attempt {attempt}/{max_retries})")
            continue  # Retry the loop

    custom_print(file_path=log_file_path, text=f'***************************************************************************')
    custom_print(file_path=log_file_path, text=f"Failed to extract object list after {max_retries} attempts.")
    custom_print(file_path=log_file_path, text=f'***************************************************************************')
    return []  # Return empty list after max retries



def load_restricted_stations(object_list: List[ObjchanObject], resticted_stations_path: str = None) -> List[Tuple[ObjchanObject, List[int]]]:
    """
    # TODO Modify the explanation, especially the format of the restricted stations.
    Loads restricted stations from a JSON file and ensures that each object in the provided list has an entry.
    Args:
        object_list (List[ObjchanObject]): A list of ObjchanObject instances.
        resticted_stations_path (str, optional): The path to the JSON file containing restricted stations. 
                                                 Defaults to "test_case/restricted_stations.json".
    Returns:
        List[Tuple[ObjchanObject, List[int]]]: A list of tuples, where each tuple contains an ObjchanObject instance and a list of restricted station numbers.
    Raises:
        FileNotFoundError: If the restricted_stations.json file is not found at the specified path.
    """
    if resticted_stations_path is None:
        resticted_stations_path = "test_case/restricted_stations.json"
    # if the path is dir, automatically add the file name, "restricted_stations.json"
    if os.path.isdir(resticted_stations_path):
        resticted_stations_path = os.path.join(resticted_stations_path, "restricted_stations.json")
    if not os.path.exists(resticted_stations_path):
        raise FileNotFoundError(f"restricted_stations.json not found in {resticted_stations_path}")
    # Restricted stations should be like
    """
    [
        {
            "object": {
                "name": "name1",
                "init_content": "DMEM",
                "labware": {
                    "id": 3,
                    "name": "15_ml_tube"
                }
            },
            "places": [
                1,
                2,
                3
            ]
        },
        {
            "object": {
                "init_content": "DMEM"
            },
            "places": [
                4,
                5,
                6
            ]
        }
    ]

    """

    with open(resticted_stations_path) as f:
        loaded_data = json.load(f)

    # If the object name is not in the restricted_stations, add it with an empty list
    print(f"{loaded_data=}")
    restricted_stations = [(ObjchanObject(**entry["object"]),entry["places"]) for entry in loaded_data]
    object_placement_info = []
    for object in object_list:
        restricted_station_info = object.search_constraints(constraints=restricted_stations)
        if restricted_station_info is not None:
            object_placement_info.append((object, restricted_station_info))
        else:
            object_placement_info.append((object, []))
    return object_placement_info


def get_haichi(stations: Chack_chan, restricted_stations: List[Tuple[ObjchanObject, List[int]]], id: str, log_file_path: str = '') -> dict:
    stations = [i+1 for i in range(stations.get_station_num())]
    objects = sort_objects_by_constraints(restricted_stations)
    all_results = []
    results = []  # 最終結果を保存するリスト
    
    generator = permutations(stations=stations, objects=objects, selected_objects=[], selected_indices=set(), results=results, batch_size=32)

    # ジェネレーターから結果のバッチを取得し、表示（先頭だけ）
    all_num = 0
    for batch in generator:
        # print(batch[0])
        all_num += len(batch)
        all_results += batch
        # 遅すぎるので全通りの出力は後回しにした
        break
    
    custom_print(file_path=log_file_path, text=f"all_num: {all_num}")

    custom_print(file_path=log_file_path, text=f"************ haichi-kun result ************")
    custom_print(file_path=log_file_path, text=f"{all_results[:10]=}")
    write_file(
        BASE_DIR,
        id,
        'haichi_chan',
        "haichi.json",
        "json",
        all_results
    )
    return all_results

def get_骨子_script(prompt: str, process_flow: str, model: str, id: str, log_file_path: str = '', results_dir: str = None) -> str:
    custom_print(file_path=log_file_path, text=f"************ Code-chan for 骨子スクリプト result ************")
    code_chan_obj = CodeChan(mode='骨子スクリプト')
    replace_word = "___processflow___"
    if replace_word not in prompt:
        custom_print(file_path=log_file_path, text = f"replace_word: {replace_word} is not in the prompt.\n")
    prompt_template_script = copy.deepcopy(prompt).replace(replace_word, process_flow)
    custom_print(file_path=log_file_path, text=f"prompt_template_script: {prompt_template_script}")
    python_script_path = code_chan_obj.call_llm(
        prompt=prompt_template_script,
        model=model,
        id=id,
        results_dir=results_dir,
    )
    custom_print(file_path=log_file_path, text=f"python_script_path: {python_script_path}")
    return code_chan_obj.python_code

def get_OT2_script(prompt: str, 骨子_script: Optional[str], process_flow: str, model: str, id: str) -> str:
    print(f"************ Code-chan result ************")
    print(f"prompt: {prompt}")
    replace_word = "___processflow___"
    if replace_word not in prompt:
        raise ValueError(f"replace_word: {replace_word} is not in the prompt.")
    prompt = prompt.replace(replace_word, process_flow)
    code_chan_obj = CodeChan(mode='Codechan_for_OT2')
    python_script_path = code_chan_obj.call_llm(
        prompt=prompt,
        model=model,
        id=id,
    )
    code_chan_obj.evaluate(python_script_path, id)
    print(f"python_script_path: {python_script_path}")
    return code_chan_obj.python_code

def get_OT2_with_haichi_script(prompt: str, haichi: str, process_flow: str, model: str, id: str) -> str:
    print(f"************ Code-chan result ************")
    replace_word = "___processflow___"
    if replace_word not in prompt:
        raise ValueError(f"replace_word: {replace_word} is not in the prompt.")
    prompt = prompt.replace(replace_word, process_flow)
    replace_word = "__placement__"
    if replace_word not in prompt:
        raise ValueError(f"replace_word: {replace_word} is not in the prompt.")
    prompt = prompt.replace(replace_word, haichi)
    print(f"prompt: {prompt}")
    code_chan_obj = CodeChan(mode='Codechan_for_OT2_with_haichi')
    python_script_path = code_chan_obj.call_llm(
        prompt=prompt,
        model=model,
        id=id,
    )
    code_chan_obj.evaluate(python_script_path, id)
    print(f"python_script_path: {python_script_path}")
    return code_chan_obj.python_code

def get_OT2_with_haichi_based_on_骨子_script(prompt: str, process_flow: str, 骨子script: str, haichi: dict, model: str, id: str, log_file_path: str = '', results_dir: str = None) -> Tuple[str, str, str, str]:
    custom_print(file_path=log_file_path, text=f"************ Code-chan result ************")
    replace_word = "___processflow___"
    if replace_word not in prompt:
        custom_print(file_path=log_file_path, text = f"replace_word: {replace_word} is not in the prompt.")
    prompt = prompt.replace(replace_word, process_flow)
    replace_word = "___skeleton_script___"
    if replace_word not in prompt:
        custom_print(file_path=log_file_path, text = f"replace_word: {replace_word} is not in the prompt.")
    prompt = prompt.replace(replace_word, 骨子script)
    replace_word = "__placement__"
    if replace_word not in prompt:
        raise ValueError(f"replace_word: {replace_word} is not in the prompt.")
    prompt = prompt.replace(replace_word, json.dumps(haichi, cls=DataclassEncoder))
    print(f"prompt: {prompt}")
    custom_print(file_path=log_file_path, text=f"get_OT2_with_haichi_based_on_骨子_script prompt: {prompt}")
    code_chan_obj = CodeChan(mode='最終スクリプト')
    python_script_path = code_chan_obj.call_llm(
        prompt=prompt,
        model=model,
        id=id,
        results_dir=results_dir,
    )
    output_path, output_text, result_type = code_chan_obj.evaluate(python_script_path, id, results_dir=results_dir)
    custom_print(file_path=log_file_path, text=f"python_script_path: {python_script_path}")
    return code_chan_obj.python_code, output_path, output_text, result_type

def run_check_chan(haichi: dict, id: str, base_path: str = '', save_path: str = '', log_file_path: str = '', relative_restriction_path: str = config.relative_restriction_path) -> Tuple[List[bool], str]:
    try:
        station = Chack_chan()
        # Object -> dict
        object_list = [obj[0] for obj in haichi]
        custom_print(file_path=log_file_path, text=f"************ Check-chan result ************")
        custom_print(file_path=log_file_path, text=f"object_list: {object_list}")
        custom_print(file_path=log_file_path, text=f"haichi: {haichi}")

        # haichi like
        # {"PBS": "Station11", "15% paraformaldehyde": "Station10",...}
        # object_list like
        # [{"name": "PBS", "quantity": 2, "init_content": "", "labware": {"id": "", "name": "PBS"}}, {
        
        for object_place_info in haichi:
            custom_print(file_path=log_file_path, text=f"object: {object_place_info}")
            place = object_place_info[1]
            object = object_place_info[0][0]
            # place like Station1
            # Replace with the actual station number
            custom_print(file_path=log_file_path, text=f"place: {place}")
            station.add_object(Object(type_=object.name,
                                    holes=10,
                                    holes_r=5,
                                    top_left_coordinate=(1, 9),
                                    bottom_right_coordinate=(9, 1),
                                    name=object.name,
                                    other_info = object), place)
            
        custom_print(file_path=log_file_path, text="***Station info*** from")
        custom_print(file_path=log_file_path, text=station.show_property())
        custom_print(file_path=log_file_path, text="***Station info*** to")
        relative_restriction = Path(relative_restriction_path)
        custom_print(file_path=log_file_path, text=f"relative_restriction: {relative_restriction}")
        custom_print(file_path=log_file_path, text=station.check_conditions(relative_restriction))

        # save check_chan result
        if not base_path == "":
            write_file(
                BASE_DIR,
                id,
                'check_chan',
                "check_chan_result.json",
                "json",
                station.check_conditions(relative_restriction)
            )

        # Store the station visualization result
        visualization = station.show_property()
        # TODO change the path to the correct path
        return station.check_conditions(relative_restriction), visualization
    except Exception as e:
        import traceback
        custom_print(file_path=log_file_path, text=f'Error: {e}')
        custom_print(file_path=log_file_path, text=f'Traceback: {traceback.format_exc()}')
        return [False], ""

