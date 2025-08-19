"""
   {
      "name":"1.5 mL tube",
      "labware": {
        "id": 1,
        "name": "1.5_ml_tube"
      },
      "quantity":1,
      "init_content":"hMSC cell suspension"
   },
"""
# ここにobjects.jsonもプロンプトに入れる必要がある？
# 覚えさせる必要あり？
PROMPT = {
    "v1": """
Extract the following information from the given process flow text.
Please make sure that you only answer JSON format without any other text so that we can extract the results correctly.

1. Labware name
2. Labware quantity
3. Initial content if the labware is a tube, plate, or dish. Otherwise, leave it blank.

Example 1:

Process flow text:
```
1) Add 100 uL of sample from 1.5 ml tube to 96 well plate.
2) Transfer 10 ml medium to 15 ml tube.
3) Add 300 µl of the medium from 15 ml tube to 96 well plate.
```

```json
[
    {"name": "1.5 ml tube", "quantity": 1, "init_content": "sample", "labware": {"id": 1, "name": "1.5_ml_tube"}},
    {"name": "96 well plate", "quantity": 1, "init_content": "medium", "labware": {"id": 2, "name": "96_well_plate"}},
    {"name": "15 ml tube", "quantity": 1, "init_content": "", "labware": {"id": 3, "name": "15_ml_tube"}}
]
```

Example 2:

Process flow text:
```
Add 5 ml DMEM from 15 ml tube to 90 mm dish.
And then add 5 ml MEMa from 15 ml tube to the same dish.
Finally, add 10 µl sample from 1.5 ml tube to the same dish.
```

```json
[
    {"name": "15 ml tube", "quantity": 2, "init_content": "DMEM", "labware": {"id": 3, "name": "15_ml_tube"}},
    {"name": "90 mm dish", "quantity": 1, "init_content": "", "labware": {"id": 4, "name": "90_mm_dish"}},
    {"name": "1.5 ml tube", "quantity": 1, "init_content": "sample", "labware": {"id": 1, "name": "1.5_ml_tube"}}
]
```

Example 3:

Process flow text:
```
1) Harvest cells from culture dish using trypsin in 15 ml tube and transfer to another 15 ml tube.
2) Centrifuge the 15 ml tube at 1000 rpm for 5 minutes to pellet the cells.
3) Discard the supernatant and resuspend the cell pellet in 1 ml of PBS.
4) Transfer 100 µl of the cell suspension to a counting chamber and count the number of cells under a microscope.
5) Calculate the dilution factor required to obtain a desired cell concentration.
6) Prepare a dilution of cells by adding the appropriate volume of cell suspension and PBS to a 15 ml tube.
7) Mix the cells and PBS thoroughly by gently pipetting up and down.
8) Add 100 µl of the diluted cell suspension to each well of a 96-well plate.
```

```json
[
    {"name": "culture dish", "quantity": 1, "init_content": "cells", "labware": {"id": None, "name": "culture_dish"}},
    {"name": "15 ml tube", "quantity": 1, "init_content": "", "labware": {"id": 3, "name": "15_ml_tube"}},
    {"name": "15 ml tube", "quantity": 1, "init_content": "trypsin", "labware": {"id": 3, "name": "15_ml_tube"}},
    {"name": "15 ml tube", "quantity": 1, "init_content": "PBS", "labware": {"id": 3, "name": "15_ml_tube"}},
    {"name": "96-well plate", "quantity": 1, "init_content": "", "labware": {"id": 2, "name": "96_well_plate"}},
]
```

For this example, do not include these things in your answer:
```json
[
    {"name": "counting chamber", "quantity": 1, "init_content": ""}, # counting chamber is not a labware
    {"name": "microscope", "quantity": 1, "init_content": ""}, # microscope is not a labware
    {"name": "pipette", "quantity": 1, "init_content": ""}, # pipette is not a labware
    {"name": "pipette tip", "quantity": 1, "init_content": ""} # pipette tip is not a labware
]
```

Now, it's your turn to try it out! Please make sure to avoid this kind of error `json.decoder.JSONDecodeError: Expecting value: line 2 column 86 (char 87)` by only answering JSON format without any other text. For example, do not add None or null to your answer, instead, leave it blank string.
Process flow text:
```
{__process_flow_text__}
```
""",
    #
    #
    #
    #
    #
    #
    #
    #
    #
    #
    #
    #
    #
    #
    #
    #
    #
    #
    #
    #
    "v2": """

Example 3:

Process flow text:
```
1) Pipette 200 µL of PBS buffer into a 1.5 mL microcentrifuge tube.
2) Add 10 µL of a 1 mg/mL protein solution to the microcentrifuge tube.
3) Vortex the tube gently to mix the solution.
4) Centrifuge at 13,000 rpm for 1 minute to remove any air bubbles.
5) Load 20 µL of the mixture onto a SDS-PAGE gel.
6) Run the gel at 120 V for 1 hour.
7) Stain the gel with Coomassie Blue for 30 minutes.
8) Destain the gel with a destaining solution until bands are visible.

```

```json
[
    {"labware_name": "1.5 mL microcentrifuge tube", "labware_quantity": 1, "init_content": "PBS buffer"},
    {"labware_name": "SDS-PAGE gel", "labware_quantity": 1}
]
```

Example 4:

Process Flow Text:
```
1) Add 2 mL of LB broth to a 15 mL culture tube.
2) Inoculate the broth with a single colony of E. coli from an agar plate.
3) Incubate the culture tube at 37 °C with shaking at 200 rpm for 16 hours.
4) Transfer 1 mL of the overnight culture to a fresh 15 mL tube containing 9 mL of LB broth.
5) Grow the culture at 37 °C with shaking at 200 rpm until the OD600 reaches 0.6-0.8.
6) Induce protein expression by adding 1 mM IPTG.
7) Continue incubation at 37 °C for 4 hours.
8) Harvest the cells by centrifugation at 4,000 rpm for 10 minutes.
```

```json
[
    {"labware_name": "15 mL culture tube", "labware_quantity": 2},
    {"labware_name": "LB broth", "labware_quantity": 2},
    {"labware_name": "agar plate", "labware_quantity": 1},
    {"labware_name": "IPTG", "labware_quantity": 1}
]
```

Example 5:

Process Flow Text:
```
Copy code
1) Prepare a 1.5 mL microcentrifuge tube with 500 µL of lysis buffer.
2) Add 10 µL of protease inhibitor to the tube.
3) Harvest cells from a culture dish and resuspend them in the lysis buffer.
4) Incubate the tube on ice for 30 minutes.
5) Centrifuge the tube at 14,000 rpm for 10 minutes at 4 °C.
6) Transfer the supernatant to a new microcentrifuge tube.
7) Add 50 µL of Ni-NTA resin to the tube and incubate for 1 hour at 4 °C.
8) Centrifuge the tube at 2,000 rpm for 2 minutes to pellet the resin.
9) Wash the resin three times with wash buffer.
10) Elute the protein with elution buffer.
```

```json
[
    {"labware_name": "1.5 mL microcentrifuge tube", "labware_quantity": 2},
    {"labware_name": "lysis buffer", "labware_quantity": 1},
    {"labware_name": "protease inhibitor", "labware_quantity": 1},
    {"labware_name": "culture dish", "labware_quantity": 1},
    {"labware_name": "Ni-NTA resin", "labware_quantity": 1},
    {"labware_name": "wash buffer", "labware_quantity": 1},
    {"labware_name": "elution buffer", "labware_quantity": 1}
]
```

Example 6:

Process Flow Text:
```
1) Add 10 mL of DMEM medium to a T-75 flask.
2) Add 1 mL of fetal bovine serum (FBS) to the flask.
3) Seed the flask with 1x10^6 HeLa cells.
4) Incubate the flask at 37 °C with 5% CO2 for 24 hours.
5) Add 100 µL of a 10 mM stock solution of drug A to the flask.
6) Incubate the flask at 37 °C with 5% CO2 for 48 hours.
7) Harvest the cells by trypsinization and transfer to a 15 mL conical tube.
8) Centrifuge the tube at 1,200 rpm for 5 minutes.
9) Resuspend the cell pellet in 1 mL of PBS buffer.
10) Analyze the cells by flow cytometry.
```

```json
[
    {"labware_name": "T-75 flask", "labware_quantity": 1},
    {"labware_name": "DMEM medium", "labware_quantity": 1},
    {"labware_name": "fetal bovine serum (FBS)", "labware_quantity": 1},
    {"labware_name": "HeLa cells", "labware_quantity": 1},
    {"labware_name": "drug A", "labware_quantity": 1},
    {"labware_name": "15 mL conical tube", "labware_quantity": 1},
    {"labware_name": "PBS buffer", "labware_quantity": 1}
]
```

Example 7:

Process Flow Text:
```
1) Prepare a 1.5 mL microcentrifuge tube with 300 µL of binding buffer.
2) Add 20 µL of streptavidin magnetic beads to the tube.
3) Incubate the tube at room temperature for 10 minutes with gentle shaking.
4) Place the tube on a magnetic rack for 2 minutes to pellet the beads.
5) Remove the supernatant and add 300 µL of wash buffer to the tube.
6) Resuspend the beads by vortexing.
7) Repeat steps 4-6 two more times.
8) Add 100 µL of biotinylated protein to the tube.
9) Incubate the tube at room temperature for 30 minutes with gentle shaking.
10) Place the tube on a magnetic rack for 2 minutes to pellet the beads.
11) Remove the supernatant and resuspend the beads in 100 µL of elution buffer.
12) Analyze the eluate by Western blotting.
```

```json
[
    {"labware_name": "1.5 mL microcentrifuge tube", "labware_quantity": 1},
    {"labware_name": "binding buffer", "labware_quantity": 1},
    {"labware_name": "streptavidin magnetic beads", "labware_quantity": 1},
    {"labware_name": "magnetic rack", "labware_quantity": 1},
    {"labware_name": "wash buffer", "labware_quantity": 1},
    {"labware_name": "biotinylated protein", "labware_quantity": 1},
    {"labware_name": "elution buffer", "labware_quantity": 1}
]
```
    """,

#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
    "v3": """

# Setting
You are a helpful assistant who is an expert in biology, computer science, and engineering.

# Order
Extract the following information from the given process flow text.
Please make sure that you only answer JSON format without any other text so that we can extract the results correctly.

1. Labware name
2. Labware quantity
3. Initial content if the labware is a tube, plate, or dish. Otherwise, leave it blank.

# Note
1. If the labware contains a specific content, please provide the content. Otherwise, leave it blank like  "init_content": "".
2. Focus on the labware; don't name the content like {"name":"sample", ...}
3. No sample is born out of nothing. Even if the container is not specified, interpolate the output as far as possible.
4. Initial content that cannot be assumed to be homogeneous should be clearly marked as a separate container to distinguish it.
5. Objects initially at the experimental desk should be clearly indicated. In other words, do not include things in the INITIAL CONTENT that may come out due to the experiment.

# Example 1

Process flow text:
```
1) Add 100 uL of sample from 1.5 ml tube to 96 well plate.
2) Transfer 10 ml medium to 15 ml tube.
3) Add 300 µl of the medium from 15 ml tube to 96 well plate.
```

```json
[
    {"name": "1.5 ml tube", "quantity": 1.5, "unit": "ml", "init_content": "sample", "labware": {"id": 1, "name": "1.5_ml_tube"}},
    {"name": "96 well plate", "quantity": 1, "unit": "ml",  "init_content": "medium", "labware": {"id": 2, "name": "96_well_plate"}},
    {"name": "15 ml tube", "quantity":0, "unit":"",  "init_content": "", "labware": {"id": 3, "name": "15_ml_tube"}}
]
```
# Bad Example 1
```json
[
    {"name": "sample", "quantity": 100, "unit": "uL", "init_content": "", "labware": {"id": 1, "name": "1.5_ml_tube"}},
    {"name": "medium", "quantity": 10, "unit": "ml", "init_content": "", "labware": {"id": 1, "name": "15_ml_tube"}},
]
```

In this bad example, the labware is not specified, and the content is specified. This is not the correct format.
Again Focus on the labware; DO NOT name the content like {"name":"sample", ...}

# Process flow
```
{__process_flow_text__}
```
""",

#
#
#
#
#
#
#
#
#
"v4": """
## Overview
You are tasked with extracting specific details from a text describing a scientific experiment. Focus solely on the labware used in the experiment.

## Your Task
Read the given experiment description and extract the following information in JSON format:

1. **Labware Name:** Identify each piece of **labware**, mentioned, identical name. If there are identical laboratory instruments, name them so that they can be distinguished from each other.
2. **Labware Quantity:** Note how much of the labware is used, if mentioned.
3. **Initial Content:** If the labware is a tube, plate, or dish and contains something at the start, describe the content. If it's empty or the content is not specified, leave this field blank.
4. **Labware ID and Name:** Provide an ID and a standardized name for each labware item.


## Guidelines
- For labware with specific contents, list the content name in the "init_content" field. Leave it blank ("init_content": "") if no content is specified.
- Focus on identifying the labware, not the substances it contains. The labware's name should not be confused with the content it holds.
- Assume no sample is created spontaneously; try to infer the origin of all substances as best as you can.
- If a labware's initial content is mixed or not uniform, list it as separate entries to clarify the distinction.
- Clearly indicate which items are present on the experimental bench at the beginning. Do not include substances that appear as a result of the experiment in the "INITIAL CONTENT".

## Example
### Given Text
Add 100 uL of sample from 1.5 ml tube to 96 well plate.
Transfer 10 ml medium to 15 ml tube.
Add 300 µl of the medium from 15 ml tube to 96 well plate.


### Correct Output Format
```json
[
    {"name": "1.5 ml tube sample", "quantity": 1.5, "unit": "ml", "init_content": "sample", "labware": {"id": 1, "name": "1.5_ml_tube"}},
    {"name": "96 well plate medium", "quantity": 1, "unit": "ml", "init_content": "medium", "labware": {"id": 2, "name": "corning_96_wellplate_360ul_flat"}},
    {"name": "15 ml tube", "quantity": 0, "unit": "", "init_content": "", "labware": {"id": 3, "name": "15_ml_tube"}}
]


### Incorrect Output Format (NG)
[
    {"name": "sample", "quantity": 100, "unit": "uL", "init_content": ""},
    {"name": "medium", "quantity": 10, "unit": "ml", "init_content": ""}
]

Note: In the incorrect example, the focus is wrongly placed on the contents rather than the labware itself, which is not what is asked for.
Do not directly name the content like {"name":"sample", ...}


# Process flow
```
{__process_flow_text__}
```
""",
"v4.labwarelist": """
## Overview
You are tasked with extracting specific details from a text describing a scientific experiment. Focus solely on the labware used in the experiment. Use labwares from the available labware list below.

## Your Task
Read the given experiment description and extract the following information in JSON format:

1. **Labware Name:** Identify each piece of **labware**, mentioned, identical name. If there are identical laboratory instruments, name them so that they can be distinguished from each other.
2. **Labware Quantity:** Note how much of the labware is used, if mentioned.
3. **Initial Content:** If the labware is a tube, plate, or dish and contains something at the start, describe the content. If it's empty or the content is not specified, leave this field blank.
4. **Labware ID and Name:** Provide an ID and a standardized name for each labware item. Use the available labware list below to match the labware with the correct ID and name. If the labware is not on the list, leave the ID field blank.

## Available Labware List (ID and Name)
1. 1.5_ml_tube
2. 2.0_ml_tube
3. 15_ml_tube
4. corning_96_wellplate_360ul_flat
5. corning_24_wellplate_3.4ml_flat
6. corning_6_wellplate_16.8ml_flat
7. opentrons_96_tiprack_1000ul
8. opentrons_96_tiprack_300ul
9. opentrons_96_tiprack_20ul
10. opentrons_96_tiprack_10ul
11. nest_12_reservoir_15ml
12. opentrons_10_tuberack_falcon_4x50ml_6x15ml_conical
13. opentrons_24_tuberack_eppendorf_1.5ml_safelock_snapcap
14. opentrons_24_tuberack_eppendorf_2ml_safelock_snapcap


## Guidelines
- For labware with specific contents, list the content name in the "init_content" field.
- Focus on identifying the labware, not the substances it contains. The labware's name should not be confused with the content it holds.
- Assume no sample is created spontaneously; try to infer the origin of all substances as best as you can.
- If a labware's initial content is mixed or not uniform, list it as separate entries to clarify the distinction.
- Clearly indicate which items are present on the experimental bench at the beginning. Do not include substances that appear as a result of the experiment in the "INITIAL CONTENT".

## Example
### Given Text
Add 100 uL of sample from 1.5 ml tube to 96 well plate.
Transfer 10 ml medium to 15 ml tube.
Add 300 µl of the medium from 15 ml tube to 96 well plate.


### Correct Output Format
```json
{   "labware":
        [
            {"name": "sample", "quantity": 1.5, "unit": "ml", "init_content": "sample", "labware": {"id": 1, "name": "1.5_ml_tube"}},
            {"name": "medium", "quantity": 1, "unit": "ml", "init_content": "medium", "labware": {"id": 2, "name": "corning_96_wellplate_360ul_flat"}},
            {"name": "empty_15_ml_tube", "quantity": 0, "unit": "", "init_content": "", "labware": {"id": 3, "name": "15_ml_tube"}}
        ]
}


### Incorrect Output Format (NG)
[
    {"name": "sample", "quantity": 100, "unit": "uL", "init_content": ""},
    {"name": "medium", "quantity": 10, "unit": "ml", "init_content": ""}
]

Note: In the incorrect example, the focus is wrongly placed on the contents rather than the labware itself, which is not what is asked for.
Do not directly name the content like {"name":"sample", ...}


# Process flow
```
{__process_flow_text__}
```
""",

"v5.labwarelist": """
## Overview
You are tasked with extracting specific details from a text describing a scientific experiment. Focus solely on the labware used in the experiment. Use labwares from the available labware list below.

## Your Task
Read the given experiment description and extract the following information in JSON format:

1. **Labware Name:** Identify each piece of **labware**, mentioned, identical name. If there are identical laboratory instruments, name them so that they can be distinguished from each other.
2. **Labware Quantity:** Note how much of the labware is used, if mentioned.
3. **Initial Content:** If the labware is a tube, plate, or dish and contains something at the start, describe the content. If it's empty or the content is not specified, leave this field blank.
4. **Labware ID and Name:** Provide an ID and a standardized name for each labware item. Use the available labware list below to match the labware with the correct ID and name. If the labware is not on the list, leave the ID field blank.

## Available Labware List (ID and Name)
{__available_labware_list__}


## Guidelines
- For labware with specific contents, list the content name in the "init_content" field.
- Focus on identifying the labware, not the substances it contains. The labware's name should not be confused with the content it holds.
- Assume no sample is created spontaneously; try to infer the origin of all substances as best as you can.
- If a labware's initial content is mixed or not uniform, list it as separate entries to clarify the distinction.
- Clearly indicate which items are present on the experimental bench at the beginning. Do not include substances that appear as a result of the experiment in the "INITIAL CONTENT".

## Example
### Given Text
Add 100 uL of sample from 1.5 ml tube to 96 well plate.
Transfer 10 ml medium to 15 ml tube.
Add 300 µl of the medium from 15 ml tube to 96 well plate.


### Correct Output Format
```json
{   "labware":
        [
            {"name": "sample", "quantity": 1.5, "unit": "ml", "init_content": "sample", "labware": {"id": 1, "name": "1.5_ml_tube"}},
            {"name": "medium", "quantity": 1, "unit": "ml", "init_content": "medium", "labware": {"id": 2, "name": "corning_96_wellplate_360ul_flat"}},
            {"name": "empty_15_ml_tube", "quantity": 0, "unit": "", "init_content": "", "labware": {"id": 3, "name": "15_ml_tube"}}
        ]
}


### Incorrect Output Format (NG)
[
    {"name": "sample", "quantity": 100, "unit": "uL", "init_content": ""},
    {"name": "medium", "quantity": 10, "unit": "ml", "init_content": ""}
]

Note: In the incorrect example, the focus is wrongly placed on the contents rather than the labware itself, which is not what is asked for.
Do not directly name the content like {"name":"sample", ...}


# Process flow
```
{__process_flow_text__}
```
""",

"v6.labwarelist": """
## Overview
You need to read a text describing a scientific experiment and extract information **only** about the labware used (e.g., tubes, plates, dishes). Match each item of labware with the corresponding entry from the **available labware list** shown below.

## Task
1. **Identify Each Labware Item**  
   - Extract the exact name of each piece of labware from the experiment description.  
   - If multiple items share the same labware type (e.g., two 1.5 ml tubes), label them so it is clear they are distinct objects.

2. **Quantity and Unit**  
   - Record the amount of each labware item, along with its **unit** (e.g., "ml," "µL").  
   - Even if the quantity is zero or is not explicitly given, include a `"unit"` field in the output (it can be left empty if truly unknown).

3. **Initial Content**  
   - If the labware starts with a particular substance (e.g., "media," "buffer"), put that in the `"init_content"` field.  
   - If there is no initial content, leave this field blank (`""`).

4. **Labware ID and Name**  
   - For each piece of labware, provide an ID and a standardized name by matching it to the **available labware list**.  
   - If no match exists, leave the ID blank and only provide the name you have identified.

## Available Labware List (ID and Name)
```
{Replace this entire section with the actual list, for example:
1. 1.5_ml_tube  
2. 15_ml_tube  
3. corning_96_wellplate_360ul_flat
}
```

## Formatting the Output
Your final answer must be in **JSON** format, using the following structure for each labware item:
```json
{
  "labware": [
    {
      "name": "string",
      "quantity": number,
      "unit": "string",
      "init_content": "string",
      "labware": {
         "id": 0,
         "name": "string"
      }
    },
    ...
  ]
}
```
- The `"name"` field should describe the labware as it appears in the text (e.g., `"1.5 ml tube"`).
- The `"quantity"` field should reflect how many labware items exist or how much volume it holds if the text specifies.
- Always include the `"unit"` field, even if it is empty.
- Use `"init_content"` for contents only if specified at the experiment's start.
- For the `"labware"` object, fill in the correct ID and name based on the **available labware list**.

## Example

### Input Text
```
Add 100 µL of a sample from a 1.5 ml tube to a 96 well plate.  
Transfer 10 ml of medium to a 15 ml tube.  
Add 300 µL of the medium from the 15 ml tube to the 96 well plate.
```

### Correct Output
```json
{
  "labware": [
    {
      "name": "1.5 ml tube",
      "quantity": 1,
      "unit": "piece",
      "init_content": "sample",
      "labware": {
        "id": 1,
        "name": "1.5_ml_tube"
      }
    },
    {
      "name": "96 well plate",
      "quantity": 1,
      "unit": "piece",
      "init_content": "",
      "labware": {
        "id": 3,
        "name": "corning_96_wellplate_360ul_flat"
      }
    },
    {
      "name": "15 ml tube",
      "quantity": 1,
      "unit": "piece",
      "init_content": "medium",
      "labware": {
        "id": 2,
        "name": "15_ml_tube"
      }
    }
  ]
}
```

> **Note**: Focus on the labware itself (e.g., tubes, plates), not the **volume transferred**. The `"quantity"` here indicates one piece of each labware. `"unit"` is `"piece"` to indicate that.

### Incorrect Output
```json
[
  {
    "name": "sample",
    "quantity": 100,
    "unit": "µL",
    "init_content": ""
  },
  {
    "name": "medium",
    "quantity": 10,
    "unit": "ml",
    "init_content": ""
  }
]
```
> **Problem**: This output focuses on the substances and volumes rather than the labware itself. It also omits the required `"labware": {"id": "...", "name": "..."}` field.

## Process Flow
```
{__process_flow_text__}
```

Use these instructions to ensure each labware item is clearly listed with name, quantity, unit, initial content, and matched labware ID/name from the labware list.
```
}
"""
}