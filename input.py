import os
from typing import List, Tuple

OT2_STATIONS = [f"{i+1}" for i in range(12)]  # ステーションのリストを作成

PROCESS_FLOW_NAME = ["example_process_flow_for_obj_chan", "qPCR", "IHC"]
PROCESS_FLOW_DICT: dict = {
    "example_process_flow_for_obj_chan": """
1) Transfer 100 µL of {XXX} cell suspension from a 1.5 mL tube to each well in a 96 well plate.
2) Transfer 200 µL {YYY} medium from a 15 mL tube to each well in the 96 well plate.
3) Gently mix the contents of each well.
""",
    "qPCR_en": """
QPCR
Sample prep for measurement using the QuantStudio 6 Pro.
There are 11 samples, and the plan is to test each with 4 primers, each in duplicate.

Input:

Containers for reagents: tubes or plates
11 sample DNAs: 50 μL each
Water: 50 μL
10 μM primer_F: 50 μL
10 μM primer_R: 50 μL
PCR MIX: 1000 μL
96-well PCR plate: 1 plate
Other necessary tubes or plates for liquid mixing
Output:
A 96-well PCR plate containing a mixture of sample DNA, primer, and PCR MIX.

Procedure:

Dispense 221 μL of PCR MIX into 4 separate tubes.
Add 19.5 μL of 10 μM primer_F1-4 to the tubes with PCR MIX.
Add 19.5 μL of 10 μM primer_R1-4 to the tubes with PCR MIX.
Mix the PCR MIX and primers by pipetting.
Apply 5 μL of sample DNA or water to the reaction plate, filling the columns as shown in the plate map below.
Apply 10 μL of the PCR MIX and primer mixture to the reaction plate, filling the rows as shown in the plate map below.
Plate Map: All 96 wells will be used.

S_n = sample_n (There are 11 types of samples this time, from 1 to 11).
NTC = no template control: water = negative control.
P_m = primer set_m: a set of forward and reverse primers. This time, there are 4 sets.
    """,
    "qPCR": """
QPCR
QuantStudio 6 Proで測定するサンプルprepを行う
11サンプルあって、それぞれ4プライマー x duplicateで試験するイメージ
Input：試薬類の容器はチューブまたはプレート
11 sample DNAs			各50 μL
water					50 μL
10 μM primer_F			50 μL
10 μM primer_R			50 μL
PCR MIX				1000 μL
96 well PCR  plate			1 plate
その他液体混合に必要なチューブまたはプレートなど
output
sample DNA, primer, PCR MIXの混合溶液が入った96 well PCR plate x 1
procedure
1. PCR MIXを221 μLずつ4つに分注する
2. PCR MIXが入ったチューブに10 μM primer_F1-4を19.5 μL添加する
3. PCR MIXが入ったチューブに10 μM primer_R1-4を19.5 μL添加する
4. PCR MIXとprimerをピペッティングで混合する
5. サンプル DNAまたはwater をreaction plateに5 μLずつアプライする
下記plate mapの列を埋めていくイメージ
6. PCR MIXとprimerの混合溶液を10 μLずつreaction plateにアプライする
下記plate mapの行を埋めていくイメージ
plate map
96 well全て使用する
S_n = sample_n
今回は1〜11までの11種類のサンプル
NTC = no template control：水＝ネガティブコントロール
P_m = primer set_m：forward primerとreverse primerのセット
今回は4種類のセット
      """
      ,
      "IHC": """
IHC
Wash cells with xx mL of PBS (-).
Fix cells in xx mL of 15% paraformaldehyde for 1 hr at RT (approximately 25 °C).
Remove PFA and add xx mL of PBS (-), then store at 4 °C.
After removing the solutions, treat cells with 50 µL/well of 0.2% Triton X-100/PBS (-).
Incubate for 30 min at RT.
Wash with xx mL of PBS (-).
Block with 50 µL of Blocking One (03953–95, Nacalai Tesque Inc, Japan) for 1 hr at RT.
After removal of the solutions, stain cells at 4 °C overnight in 50 µL of the 1st antibody diluent (rabbit anti-ZO-1, 61–7300, Thermo Fisher Scientific Inc, MA, USA; anti-MITF, mouse anti-MiTF, ab80651, Abcam plc., Britain; antibody diluent, S2022, Agilent Technologies Inc, USA).
Remove solutions, wash cells with xx mL of PBS (-).
Stain at RT for 1 hr in 50 µL of the 2nd antibody diluent (Alexa Fluor 546 Goat Anti-mouse IgG, A-11030, Thermo Fisher Scientific Inc, MA, USA; Alexa Fluor 488 Goat Anti-rabbit IgG, A-11034, Thermo Fisher Scientific Inc, MA, USA; antibody diluent, S2022, Agilent Technologies Inc, USA) with DAPI (1 µg/mL, D1206, Thermo Fisher Scientific Inc, MA, USA).
Remove solutions, wash with xx mL of PBS (-).
Add 50 µL of PBS (-).
Acquire images of immunohistochemistry samples using an IX73 inverted microscope (Olympus, Japan).
      """

,
      "Colour water mix experiment full": """
# Constraints for prompt.
P300_SINGLE_GEN2 is on the LEFT in OT-2.

# Process flow
Preparation: Prepare each of two types of colored water (Color A, 'Color A water' and Color B, 'Color A water'). The colored water is diluted with water using food coloring.
Note: The A color water and B color water have been prepared in advance and is stored in different 6-well plates.
Preparation of the 96 well plate: Set an empty 96 well plate on the experimental bench.
Mixing of the colored water:
Using a micropipette, add 96 µl of Color A water and 0 µl of Color B water to the first well.
Then, by decreasing the amount of Color A water by 1 µl and increasing the amount of Color B water by 1 µl for each well, add 95 µl of Color A water and 1 µl of Color B water for the next well and so on.
Finally, add 0 µl of Color A water and 96 µl of Color B water to the last well.
      """
,
"Colour water mix experiment": """
# Constraints for prompt.
P300_SINGLE_GEN2 is on the LEFT in OT-2.

# Process flow
Preparation: Prepare each of two types of colored water (Color A, 'Color A water' and Color B, 'Color A water'). The colored water is diluted with water using food coloring.
Note: The A color water and B color water have been prepared in advance and is stored in different 6-well plates.
Preparation of the 96 well plate: Set an empty 96 well plate on the experimental bench.
Mixing of the colored water:
Using a micropipette, add 10 µl of Color A water and 0 µl of Color B water to the first well.
Then, by decreasing the amount of Color A water by 1 µl and increasing the amount of Color B water by 1 µl for each well, add 9 µl of Color A water and 1 µl of Color B water for the next well and so on.
Continue...
Finally, add 0 µl of Color A water and 10 µl of Color B water to the last wel (10-th well).
      """
    # "constraints": Constraints(allowed_objects=[]),
}

CELL_MEDIUM_PAIRS: List[Tuple] = [
    ("hMSC", "DMEM"),
    ("iPS", "RPMI"),
    ("HeLa", "MEMα"),
]
CELL_MEDIUM_PAIR_IDX = 0
CELL = CELL_MEDIUM_PAIRS[CELL_MEDIUM_PAIR_IDX][0]
MEDIUM = CELL_MEDIUM_PAIRS[CELL_MEDIUM_PAIR_IDX][1]



"""
Code-chan for OT2用プロンプト
"""
PROMPT = """
I want to write a Python script that runs Opentrons OT2 machine. This robot can be used to automate laboratory experiment, and is used by many researchers in biology.

Can you write down a Python script that does the following experiment?

___processflow___
"""

"""
骨子スクリプト生成用プロンプト
"""


PROMPT_TEMPLATE_SCRIPT = """
I want to write a Python script that runs the Opentrons OT2 machine. This robot can be used to automate laboratory experiments and is widely used by many researchers in biology.

Can you write a Python script for the following experiment?
However, please replace the position of the objects with __place_{i}__ and store the object and position pair like this: {{"__place_{i}__": "{obj}"}}.

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
"""


PROMPT_HAICHI = """
I want to write a Python script that runs Opentrons OT2 machine. This robot can be used to automate laboratory experiment, and is used by many researchers in biology.

Can you write down a Python script that does the following experiment?

___processflow___

Please keep in mind that when you set the place of objects on OT2, use this information:

__haichi__
"""



PROMPT_骨子_HAICHI_REPLACE = """
We have the following Opentrons OT2 script. This script describes the position of the labware (Station) as __place_{i}__.

Skeleton script:

python
___skeleton_script___
Please generate a script where __place_{i}__ is replaced with the correct position based on the following labware placement information.

Placement information:

markdown
__placement__
Please reply with the Python script where __place_{i}__ has been replaced with the correct locations. If there is missing information in the placement details required to fill in __place_{i}__ in the skeleton script, you may supplement it as necessary. However, do not modify the placement information.
"""


if __name__ == "__main__":
    # Save each process flow into a separate text file

    save_dir = "test_case"

    hard_coded_variables = {
        "OT2_STATIONS": OT2_STATIONS,
        "PROCESS_FLOW_DICT": PROCESS_FLOW_DICT,
        "PROMPT": PROMPT,
        "PROMPT_TEMPLATE_SCRIPT": PROMPT_TEMPLATE_SCRIPT,
        "PROMPT_HAICHI": PROMPT_HAICHI,
        "PROMPT_骨子_HAICHI_REPLACE": PROMPT_骨子_HAICHI_REPLACE,
    }

    output_dir = f"{save_dir}/process_flows"
    os.makedirs(output_dir, exist_ok=True)

    for name, content in PROCESS_FLOW_DICT.items():
        file_path = os.path.join(output_dir, f"{name}.txt")
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)

    # Save hard-coded variables
    output_dir = f"{save_dir}/hard_coded_variables"
    os.makedirs(output_dir, exist_ok=True)

    for name, content in hard_coded_variables.items():
        file_path = os.path.join(output_dir, f"{name}.txt")
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(str(content))



    output_dir