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
def main_loop():
    is_error = True
    loop_count = 0
    for _ in range(5):
        """
        設定
        """
        process_flow = """QPCR
        QuantStudio 6 Proで測定するサンプルprepを行う
        1サンプルあってそれぞれ13プライマー x duplicate(3)で試験するイメージ
        NTCは13プライマー x duplicate(3)用意する
        その他、PrimerなしのTemplateのみを1 x duplicate(3)用意する


        Input：試薬類の容器はチューブまたはプレート
        1 sample DNAs			100 μL
        water					100 μL
        10 μM primer_F			各20 μL
        10 μM primer_R			各20 μL
        PCR MIX				2064 μL
        96 well PCR  plate (empty)		1 plate
        その他液体混合に必要なチューブまたはプレートなど
        output
        sample DNA, primer, PCR MIXの混合溶液が入った96 well PCR plate x 1
        procedure
        1. PCR MIXを137.6 μLずつ13個に分注する
        2. PCR MIXが入ったチューブに10 μM primer_F1-13を3.2 μL添加する
        3. PCR MIXが入ったチューブに10 μM primer_R1-13を3.2 μL添加する
        4. PCR MIXとprimerをピペッティングで混合する
        5. templateのみ用のPCR MIXを86 μL分注する
        6. templateのみ用のPCR MIXにwaterを4 μL添加する
        7. templateのみ用のPCR MIXとwaterをピペッティングで混合する
        8. サンプル DNAまたはwater をreaction plateに2 μLずつアプライする
        下記plate mapの列を埋めていくイメージ
        9. PCR MIXとprimerの混合溶液を10 μLずつreaction plateにアプライする
        下記plate mapの行を埋めていくイメージ
        plate map
        81 well使用する
        S_n = sample_n
        今回はヒト標準cDNA1つ
        NTC = no template control：水＝ネガティブコントロール（全primerについて置く）
        P_m = primer set_m：forward primerとreverse primerのセット
        今回は13種類
        Templateのみ：primerなしのMastermix + template（ヒト標準cDNA）
        OT-2のピペット
        20 μLと300 μL 
        """
        replace_word = "___processflow___"
        prompt = """
        I want to write a Python script that runs Opentrons OT2 machine. This robot can be used to automate laboratory experiment, and is used by many researchers in biology.

        Can you write down a Python script that does the following experiment?

        Note: You've been slacking lately, so don't slack off and output the complete code. For example, ‘The protocol would continue with any additional steps required’ or '# Example: ' is not allowed.

        ___processflow___
        """
        prompt = prompt.replace(replace_word, process_flow)
        replace_word = "___processflow___"
        if replace_word not in config.prompt_template:
            raise ValueError(f"replace_word: {replace_word} is not in the prompt_template.")
        prompt_template_script = """
        I want to write a Python script that runs the Opentrons OT2 machine. This robot can be used to automate laboratory experiments and is widely used by many researchers in biology.

        Can you write a Python script for the following experiment?
        However, please replace the position of the objects with __place_{i}__ and store the object and position pair like this: {{"__place_{i}__": "{obj}"}}.

        Note: You've been slacking lately, so don't slack off and output the complete code. For example, ‘The protocol would continue with any additional steps required’ or '# Example: ' is not allowed.

        For example, for this script:

        ```python
        from opentrons import protocol_api

        metadata = {
            'protocolName': 'Liquid transfer across multiple labware',
            'author': 'Your Name',
            'description': 'Transfer liquid from one 96-well plate to another 96-well plate and a 12-well plate',
            'apiLevel': '2.9'  # Specify the API level for this code
        }

        def run(protocol: protocol_api.ProtocolContext):
            # Set up labware
            tip_rack1 = protocol.load_labware('opentrons_96_tiprack_300ul', 1)
            tip_rack2 = protocol.load_labware('opentrons_96_tiprack_300ul',  2)  # Second tip rack
            plate_source_96 = protocol.load_labware('corning_96_wellplate_360ul_flat', 3)
            plate_destination_96 = protocol.load_labware('corning_96_wellplate_360ul_flat',  4)
            plate_destination_12 = protocol.load_labware('corning_12_wellplate_6.9ml_flat',  5)

            # Set up pipette
            pipette = protocol.load_instrument('p300_single', 'right', tip_racks=[tip_rack1, tip_rack2])  # Specify two tip racks
            pass
        You should replace the positions of the objects with __place_1__, __place_2__, __place_3__, __place_4__, and __place_5__ like this:

        ```python
        from opentrons import protocol_api

        metadata = {
            'protocolName': 'Liquid transfer across multiple labware',
            'author': 'Your Name',
            'description': 'Transfer liquid from one 96-well plate to another 96-well plate and a 12-well plate',
            'apiLevel': '2.9'  # Specify the API level for this code
        }

        def run(protocol: protocol_api.ProtocolContext):
            # Set up labware
            tip_rack1 = protocol.load_labware('opentrons_96_tiprack_300ul', '__place_1__')
            tip_rack2 = protocol.load_labware('opentrons_96_tiprack_300ul', '__place_2__')  # Second tip rack
            plate_source_96 = protocol.load_labware('corning_96_wellplate_360ul_flat', '__place_3__')
            plate_destination_96 = protocol.load_labware('corning_96_wellplate_360ul_flat', '__place_4__')
            plate_destination_12 = protocol.load_labware('corning_12_wellplate_6.9ml_flat', '__place_5__')

            # Set up pipette
            pipette = protocol.load_instrument('p300_single', 'right', tip_racks=[tip_rack1, tip_rack2])  # Specify two tip racks
            pass
        ```


        And please provide the object and position pairs like this:

        ```json
        {"__place_1__": "{obj1}", "__place_2__": "{obj2}", "__place_3__": "{obj3}", "__place_4__": "{obj4}", "__place_5__": "{obj5}"}
        So, your output should include:
        ```

        The template Python script
        The object and position pairs
        Here is the process flow of the experiment: ___processflow___

        Here is the object_list, assign a separate location to each object:
        ___object_list___
        """
        # prompt_template_script = prompt_template_script.replace(replace_word, process_flow)
        replace_word = "___processflow___"
        if replace_word not in config.prompt_haichi:
            raise ValueError(f"replace_word: {replace_word} is not in the prompt_haichi.")
        prompt_haichi = config.prompt_haichi.replace(replace_word, process_flow)
        prompt_骨子_haichi_replace = """
        We have the following Opentrons OT2 script. This script describes the position of the labware (Station) as __place_{i}__.

        Note: You've been slacking lately, so don't slack off and output the complete code. For example, ‘The protocol would continue with any additional steps required’ or '# Example: ' is not allowed.

        Skeleton script:

        python
        ___skeleton_script___
        Please generate a script where __place_{i}__ is replaced with the correct position based on the following labware placement information.

        Placement information:

        markdown
        __placement__
        Please reply with the Python script where __place_{i}__ has been replaced with the correct locations. If there is missing information in the placement details required to fill in __place_{i}__ in the skeleton script, you may supplement it as necessary. However, do not modify the placement information.
        """
        prompt_骨子_haichi_replace = prompt_骨子_haichi_replace.replace("___processflow___", process_flow)
        model = config.model
        base_id = datetime.now().strftime('%Y_%m_%d_%H_%M_%S_') + str(uuid.uuid4()) + '/iteration_'


        BASE_DIR = "/home/cab314/qnaphdd/FF_results/qPCR_ozaki/FF_results/regenerate_OT2_code_for_28_23_38_27_iter2"
        os.makedirs(BASE_DIR, exist_ok=True)

        id = 0
        while os.path.exists(os.path.join(BASE_DIR, str(id))):
            id = id + 1
        id = str(id)
        log_file_path = os.path.join(BASE_DIR, id, f"{base_id}_log.txt")
        os.makedirs(os.path.dirname(log_file_path), exist_ok=True)

        # ObjchanObject のインスタンスを作成
        obj1 = ObjchanObject(
            name="1 sample DNAs",
            quantity=100,
            init_content="sample DNAs",
            labware={"id": 1, "name": "tube_1.5ml"},
            unit="\u03bcL"
        )

        obj2 = ObjchanObject(
            name="water",
            quantity=100,
            init_content="water",
            labware={"id": 1, "name": "tube_1.5ml"},
            unit="\u03bcL"
        )

        obj3 = ObjchanObject(
            name="10 \u03bcM primer_F",
            quantity=20,
            init_content="",
            labware={"id": 2, "name": "corning_96_wellplate_360ul_flat"},
            unit="\u03bcL"
        )

        obj4 = ObjchanObject(
            name="10 \u03bcM primer_R",
            quantity=20,
            init_content="",
            labware={"id": 2, "name": "corning_96_wellplate_360ul_flat"},
            unit="\u03bcL"
        )

        obj5 = ObjchanObject(
            name="PCR MIX",
            quantity=2064,
            init_content="",
            labware={"id": 3, "name": "tube_15ml"},
            unit="\u03bcL"
        )

        obj6 = ObjchanObject(
            name="96 well PCR plate",
            quantity=1,
            init_content="empty",
            labware={"id": 4, "name": "96well_pcr_plate"},
            unit="plate"
        )

        # (ObjchanObject, 禁止ステーションリスト) とステーション番号のタプルのリストを作成
        haichi_i: List[Tuple[Tuple[Object, List[int]], int]] = [
            ((obj1, []), 1),
            ((obj2, []), 2),
            ((obj3, []), 3),
            ((obj4, []), 4),
            ((obj5, []), 6),
            ((obj6, []), 8),
        ]

        get_object_list = [obj1, obj2, obj3, obj4, obj5, obj6]
        prompt_template_script = prompt_template_script.replace("___object_list___", str(get_object_list))
        custom_print(file_path=log_file_path, text=f"OK: {haichi_i}")
        """ 5. OT2スクリプト with 配置 replaced from 骨子_script"""

        err_msg = ""
        骨子_script = ""
        for iteratation in range(10):
            custom_print(file_path=log_file_path, text=f"{loop_count=}, {iteratation=}")
            """ 3. code-chan """
            """ 3.1 骨子スクリプト """
            flow = f"\n# Process flow:\n```{process_flow}\n```" + "" if err_msg == "" else f"\n# This is the error message: \n ```{err_msg}\n```\n# original protocol: \n ```{骨子_script}\n```\n"
            custom_print(file_path=log_file_path, text=f"Generate 骨子スクリプト from \n~~~~~~~~~~\n{flow}\n~~~~~~~~~~")
            骨子_script = get_骨子_script(prompt_template_script, flow, model, id, log_file_path, results_dir=BASE_DIR)
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
                is_error = False
                custom_print(file_path=log_file_path, text=f"OK: {haichi_i}")
                break
            else:
                err_msg = output_text
                custom_print(file_path=log_file_path, text=f"Errorがでたので骨子スクリプトを再生成します: {err_msg}")
                continue
        loop_count += 1

        if is_error == False:
            custom_print(file_path=log_file_path, text=f"OK: {haichi_i}")
            break


if __name__ == "__main__":
    main_loop()

