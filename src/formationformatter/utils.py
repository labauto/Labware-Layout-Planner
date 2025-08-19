import sys
import os
print('File', os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from typing import Optional, Any, List
from pathlib import Path
import dataclasses
import json
import openai
from src.formationformatter.config import config
OPENAI_KEY = config.openai_key
BASE_DIR = config.base_dir
from typing import List, Tuple, Dict

import datetime
    
class DataclassEncoder(json.JSONEncoder):
    def default(self, o):
        if dataclasses.is_dataclass(o):
            return dataclasses.asdict(o)
        return super().default(o)

def write_file(base_path: str, id: str, dir: Optional[str], filename: str, extension: str, content: Any) -> str:
    if dir:
        path = os.path.join(base_path, id, dir)
    else:
        path = os.path.join(base_path, id)

    Path(path).mkdir(exist_ok=True, parents=True)
    save_path = os.path.join(path, filename)

    if extension == "json":
        with open(save_path, "w") as f:
            try:
                json.dump(content, f)
            except Exception as e:
                print(f"Error: {e}")
                try:
                    json.dump(content, cls=DataclassEncoder, fp=f)
                except Exception as e:
                    print(f"Error: {e}")
    elif extension == "txt":
        with open(save_path, "w") as f:
            f.write(content)
    elif extension == "py":
        with open(save_path, "w") as f:
            f.write(content)
    else:
        raise ValueError(f"extension: {extension} is not supported.")
    return save_path


def save_initial_position(initial_position: List[dict], save_path: str):
    """
    save initial position of objects as json file
    """
    with open(save_path, "w") as f:
        json.dump(initial_position, f, indent=4, cls=DataclassEncoder)
    return

def call_llm(
    prompt: str,
    model: str = 'gpt-4',
    system_message: str = "You are a helpful assistant who is an expert in biology, computer science, and engineering.",
) -> str:
    res = openai.ChatCompletion.create(
        model=model,
        messages=[
            {"role": "system", "content": system_message},
            {
                "role": "user",
                "content": prompt,
            },
        ],
    )
    response: str = res['choices'][0]['message']['content']
    return response


def save_object_initial_position_with_text(
    object_list: List[Dict],
    initial_positions: list,
    protocol: str,
    base_path: str,
    id: str,
    filename: str = "initial_position.txt",
    log_file_path: str = '',
    prompt: str = '''
    Please write down step by step instructions of where to place the objects in the protocol given the objects and their initial positions.

    e.g.
    Input text ****
    Protocol:
    {protocol}

    Object list of the protocol:
    {object_list}

    Initial position of the objects:
    {initial_position}
    ***

    Expected output text ****
    Instruction:
    1. Place {XXX} on the deck at {YYY}.
    2. Place {ZZZ} on the deck at {WWW}.
    3. Place {AAA} on the deck at {BBB}.
    ***
    ''',
) -> str:
    """
    save initial position of objects as txt file

    e.g.
    ```
    Protocol:
    {protocol}

    Here is the object list of the protocol.
    {object_list}

    Here is the initial position of the objects.
    {initial_position}

    Here is the natural language instruction from LLMs.
    1. Transfer 100 µL of {XXX} cell suspension from a 1.5 mL tube to each well in a 96 well plate.
    2. Transfer 200 µL {YYY} medium from a 15 mL tube to each well in the 96 well plate.
    ```
    """
    replace_word = "{protocol}"
    if replace_word not in prompt:
        raise ValueError(f"prompt should include {replace_word}.")
    prompt = prompt.replace(replace_word, protocol)
    replace_word = "{object_list}"
    if replace_word not in prompt:
        raise ValueError(f"prompt should include {replace_word}.")
    prompt = prompt.replace(replace_word, str(object_list))
    replace_word = "{initial_position}"
    if replace_word not in prompt:
        raise ValueError(f"prompt should include {replace_word}.")
    prompt = prompt.replace(replace_word, str(initial_positions))

    natural_language_instruction = f"""
Here is the natural language instruction from LLMs.
{call_llm(prompt=prompt, model='gpt-4')}
    """

    result_text = f'''
Protocol:
{protocol}

Here is the object list of the protocol.
{[obj.__dict__ for obj in object_list]}

Here is the initial position of the objects.
{initial_positions}

{natural_language_instruction}
'''
    save_path = write_file(
        base_path=base_path,
        id=id,
        dir=None,
        filename=filename,
        extension="txt",
        content=result_text,
    )
    custom_print(file_path=log_file_path, text=f'******************************************************')
    custom_print(file_path=log_file_path, text=f'save initial position of objects as txt file: {save_path}')
    custom_print(file_path=log_file_path, text=f'******************************************************')
    return natural_language_instruction


def custom_print(file_path: str = BASE_DIR, text: str = '', append: bool = True):
    # if file not exist, create file
    if not os.path.exists(file_path):
        with open(file_path, "w") as f:
            pass
    
    # save text to file
    current_datetime = datetime.datetime.now(datetime.timezone.utc)
    with open(file_path, "a" if append else "w") as f:
        f.write(f'***{current_datetime}***: {str(text)}')
    
    # print text
    print(f'***{current_datetime}***: {text}')
    return
