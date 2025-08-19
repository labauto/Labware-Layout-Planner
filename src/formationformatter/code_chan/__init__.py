from pathlib import Path
import pandas as pd
import datetime
import glob
import os
import shutil
import subprocess
import traceback
import uuid
import warnings
from typing import (Any, Callable, Dict, Generic, List, Optional, Set, Tuple,
                    Type, TypeVar, Union, cast, overload)

import openai
from blobfile import exists

warnings.filterwarnings("ignore", category=FutureWarning)
import sys
import os
print('File', os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from src.formationformatter.config import config
OPENAI_KEY = config.openai_key
from .utils import (check_filename_extract_model_info, write_file,
                    extract_markdown_code_blocks, init_df_eval,
                    prepare_python_script, run_opentrons_simulate,
                    save_prompt_and_answer_with_modelname)

openai.api_key = OPENAI_KEY





# import os
# full_path = os.path.dirname(os.path.realpath(__file__))
# path, filename = os.path.split(full_path)
# BASE_DIR = os.path.dirname(full_path)
BASE_DIR = config.base_dir
print(BASE_DIR)


# パッケージ読み込み時に仮想環境の用意と opentrons のインストールを行う
def ensure_venv_and_install() -> str:
    """
    プロジェクトルートに .venv が存在しなければ作成し、仮想環境内に opentrons をインストールする。
    仮想環境内の Python のパスを返す。
    """
    file_path = __file__
    project_dir = Path(os.path.dirname(file_path))
    venv_dir = project_dir / ".venv"
    python_path = venv_dir / "bin" / "python"

    if not venv_dir.exists():
        # 仮想環境を作成する
        subprocess.check_call([sys.executable, "-m", "venv", str(venv_dir)])
        # 仮想環境内で opentrons をインストールする
        subprocess.check_call([str(python_path), "-m", "pip", "install", "opentrons"])

    return str(python_path)

# パッケージの読み込み時に初期処理を実行
_PYTHON_PATH = ensure_venv_and_install()

class CodeChan:

    def __init__(self, mode: str = 'OT2') -> None:
        self.mode = mode
        self.python_script_path = ''
        self.python_code = ''
        pass

    @staticmethod
    def extract_markdown_code_blocks(text: List[str], language: str = 'python'):
        """Extracts markdown python code blocks from txt file"""

        code_blocks = []
        in_code_block = False
        for line in text:
            if line.startswith(f"```{language}"):
                in_code_block = True
                code_block = []
            elif line.startswith("```"):
                in_code_block = False
            elif in_code_block:
                code_blocks.append(line)
        return code_blocks


    def prepare_python_script(self, id: str, gpt_answer_file_path: str) -> Union[str, None]:
        """
        prepare python script from generated answer by GPT-3
        """
        # save it as an  python script
        python_script_path = os.path.join(os.path.dirname(gpt_answer_file_path), f"script_{self.mode}.py")

        SEPARATOR = "answer:*************************\n"

        # remove the last line
        text = open(gpt_answer_file_path, "r").readlines()
        # get text after SEPARATOR
        indices = [i for i, x in enumerate(text) if x == SEPARATOR]
        # if separated section is more than two, remove the last one
        # e.g.
        # aaaaa
        # bbbbb
        # answer:*************************
        # ccccc
        # ddddd
        # answer:*************************
        # eeeee
        # fffff
        #
        # then, get the text after the first separator and remove the last one
        try:
            if len(indices) > 1:
                text = text[indices[0] + 1 : indices[-1]]
            else:
                text = text[indices[0] + 1 :]
        except IndexError as e:
            pass
        except Exception as e:
            print(e)
            traceback.print_exc()

        # if there's markdown code notation, extract the code
        # e.g.
        # ```python
        # aaaaa
        # bbbbb
        # ```
        # then, get the text between ```python and ```
        if any("```python" in s for s in text):
            text = extract_markdown_code_blocks(text)

        if len(text) == 0:
            return None

        with open(python_script_path, "w") as f:
            f.writelines(text)
        return python_script_path

    def extension_name_to_language(self, extension: str) -> str:
        extension_dict = {
            'py': 'python',
            'js': 'javascript',
            'json': 'json',
            'txt': 'text',
            'html': 'html',
        }
        return extension_dict[extension]

    def save_code_block_as_file(self, base_path: str, id: str, gpt_answer_file_path: str, extension: str) -> Union[str, None]:
        """
        prepare code block from generated answer by GPT
        """
        # save it as an  code block
        code_block_file_path = os.path.join(os.path.dirname(gpt_answer_file_path), f"{self.mode}.{extension}")

        SEPARATOR = "answer:*************************\n"

        # remove the last line
        text = open(gpt_answer_file_path, "r").readlines()
        # get text after SEPARATOR
        indices = [i for i, x in enumerate(text) if x == SEPARATOR]
        try:
            if len(indices) > 1:
                text = text[indices[0] + 1 : indices[-1]]
            else:
                text = text[indices[0] + 1 :]
        except IndexError as e:
            pass
        except Exception as e:
            print(e)
            traceback.print_exc()

        if any(f"```{self.extension_name_to_language(extension)}" in s for s in text):
            text = self.extract_markdown_code_blocks(text, self.extension_name_to_language(extension))
        else:
            text = ''

        if len(text) == 0:
            return None

        # with open(code_block_file_path, "w") as f:
        #     f.writelines(text)
        write_file(
            base_path,
            id,
            'code_chan',
            f"{self.mode}.{extension}",
            extension,
            text,
            is_multiline=True
        )
        return code_block_file_path

    def save_llm_result_as_file(self, id: str, prompt: str, answer: str, model: str, file_extension: str = '.txt', results_dir = None) -> str:
        """save_llm_result_as_file _summary_

        Save LLMs' answer to a file

        Returns:
            str: saved filepath
        """
        import os
        if results_dir is None:
            results_dir = os.path.join(BASE_DIR)
        print(f'results_dir: {results_dir}')
        # if not exist, make new dir
        if not os.path.exists(results_dir):
            os.mkdir(results_dir)

        write_file(
            results_dir,
            id,
            'code_chan',
            f"prompt_{self.mode}{file_extension}",
            "txt",
            prompt
        )
        answer_file_path = write_file(
            results_dir,
            id,
            'code_chan',
            f"answer_{self.mode}{file_extension}",
            "txt",
            answer
        )
        write_file(
            results_dir,
            id,
            'code_chan',
            f"model_{self.mode}{file_extension}",
            "txt",
            model
        )
        # save_path = os.path.join(results_dir, id)
        # print(f'save_path: {save_path}')
        # from pathlib import Path
        # Path(save_path).mkdir(exist_ok=True, parents=True)

        # with open(os.path.join(save_path, f"prompt_{self.mode}{file_extension}"), "w") as f:
        #     f.write(prompt)
        # with open(os.path.join(save_path, f"answer_{self.mode}{file_extension}"), "w") as f:
        #     f.write(answer)
        # with open(os.path.join(save_path, f"model_{self.mode}{file_extension}"), "w") as f:
        #     f.write(model)

        # python_script_path = self.prepare_python_script(id, os.path.join(save_path, f"answer_{self.mode}{file_extension}"))
        python_script_path = self.save_code_block_as_file(results_dir, id, answer_file_path, 'py')
        json_path = self.save_code_block_as_file(results_dir, id, answer_file_path, 'json')

        return python_script_path


    def call_llm(self, prompt: str, model: str, id: str, results_dir: str = None) -> str:
        """
        Call OpenAI LLM and return the answer as a string.
        Use same UUID for the call and the file name.
        """
        # print(f'{openai.Model.list()}')
        # call LLM
        res = openai.ChatCompletion.create(
            model=model,
            messages=[
                {"role": "user", "content": prompt},
            ],
        )
        # get answer
        answer = res.choices[0]["message"]["content"]
        python_script_path = self.save_llm_result_as_file(id, prompt, answer, model, results_dir=results_dir)

        self.python_script_path = python_script_path
        if python_script_path is None:
            return ''

        self.python_code = open(python_script_path, "r").read()
        return python_script_path
    


    def run_opentrons_simulate(self, id: str, protocol_file: str, output_filename: str, results_dir: str = None) -> Tuple[str, str, str]:
        """
        仮想環境内の opentrons.simulate を実行し、標準出力／標準エラーを取得、ファイルに保存する。
        """
        # _PYTHON_PATH は初回読み込み時に設定されている
        print(f"{protocol_file=}")
        cmd = f'"{_PYTHON_PATH}" -m opentrons.simulate "{protocol_file}"'
        if results_dir is None:
            results_dir = BASE_DIR
        output_dir = os.path.join(results_dir, f"{id}/opentrons_simulate/")

        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        output_path = os.path.join(output_dir, output_filename)

        result_type = ""
        output_text = ""
        # TODO: 想定と違う場所に保存されてしまう
        with open(output_path, "w") as f:
            print(f"Executing command: {cmd}")
            proc = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            if proc.returncode != 0:
                output_text += proc.stderr
                f.write(proc.stderr)
                result_type = "error"
                with open(os.path.join(output_dir, "stderr.txt"), "w") as err_file:
                    err_file.write(proc.stderr)
            else:
                output_text += proc.stdout
                f.write(proc.stdout)
                result_type = "ok"
                with open(os.path.join(output_dir, "stdout.txt"), "w") as out_file:
                    out_file.write(proc.stdout)
        return output_path, output_text, result_type

    def evaluate(self, script_path: str, id: str, results_dir: str = None) -> Tuple[str, str, str]:
        """
        evaluate the script with opentrons_simulate
        :param script_path: str: path to the script
        :param id: str: id for the evaluation
        :return: Tuple[str, str, str]: output_path, output_text, result_type
        """
        print(f"{script_path=}")
        # evaluate the script
        try:
            output_path, output_text, result_type = self.run_opentrons_simulate(id, script_path, f"{self.mode}.txt", results_dir=results_dir)
            return output_path, output_text, result_type
        except Exception as e:
            print(e)
            traceback.print_exc()


    def plot(self, modes: List[str]) -> pd.DataFrame:
        results_dir = os.path.join(BASE_DIR)
        # get all dirs
        dirs = glob.glob(f"{results_dir}/*")
        print(dirs)
        # get all opentrons_simulate result
        results = [] # [{'id': 'xxx', 'mode': 'xxx', 'opentrons_simulate_result': 'xxx'}]
        for d in dirs:
            id = os.path.basename(d)
            for mode in modes:
                if os.path.exists(os.path.join(d, f"opentrons_simulate/{mode}.txt")):
                    with open(os.path.join(d, f"opentrons_simulate/{mode}.txt"), "r") as f:
                        opentrons_simulate_result = f.read()
                        results.append({
                            'id': id,
                            'mode': mode,
                            'model': 'gpt-4',
                            'opentrons_simulate_result': opentrons_simulate_result
                        })
        df = pd.DataFrame(results)
        # save df
        df.to_csv(os.path.join(results_dir, f"df_for_plot.csv"), index=False)
        return df
