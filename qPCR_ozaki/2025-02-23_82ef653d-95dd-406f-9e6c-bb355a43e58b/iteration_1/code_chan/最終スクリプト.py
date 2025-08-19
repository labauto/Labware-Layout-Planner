# Import necessary modules
from opentrons import protocol_api

# Metadata
metadata = {
    'protocolName': 'PCR Setup',
    'author': 'Assistant',
    'description': 'Automated PCR setup using Opentrons OT2',
    'apiLevel': '2.13'  # Use the latest API level supported by your robot
}

def run(protocol: protocol_api.ProtocolContext):
    # Labware setup based on placement information
    # Tip racks
    tiprack_20ul = protocol.load_labware('opentrons_96_tiprack_20ul', '10')
    tiprack_200ul = protocol.load_labware('opentrons_96_tiprack_300ul', '11')

    # Pipettes
    p20 = protocol.load_instrument('p20_single_gen2', 'right', tip_racks=[tiprack_20ul])
    p300 = protocol.load_instrument('p300_single_gen2', 'left', tip_racks=[tiprack_200ul])

    # Position 1: "1 sample DNAs", tube
    sample_dna_tubes = protocol.load_labware('opentrons_24_tuberack_generic_2ml_screwcap', '1')

    # Position 2: "water", tube
    water_tube = protocol.load_labware('opentrons_24_tuberack_generic_2ml_screwcap', '2')

    # Position 3: "10 μM primer_F", tube
    primer_f_tube = protocol.load_labware('opentrons_24_tuberack_generic_2ml_screwcap', '3')

    # Position 4: "10 μM primer_R", tube
    primer_r_tube = protocol.load_labware('opentrons_24_tuberack_generic_2ml_screwcap', '4')

    # Position 5: "PCR MIX", tube
    pcr_mix_tube = protocol.load_labware('opentrons_24_tuberack_generic_2ml_screwcap', '5')

    # Position 6: "96 well PCR plate", plate
    pcr_plate = protocol.load_labware('biorad_96_wellplate_200ul_pcr', '6')

    # Position 7: "template only PCR MIX", tube
    template_only_mix_tube = protocol.load_labware('opentrons_24_tuberack_generic_2ml_screwcap', '7')

    # Position 8: "water for template-only PCR MIX", tube
    water_template_only_tube = protocol.load_labware('opentrons_24_tuberack_generic_2ml_screwcap', '8')

    # Position 9: "Reaction plate (PCR MIX and primer mix)", plate
    reaction_plate_mix = protocol.load_labware('biorad_96_wellplate_200ul_pcr', '9')

    # Position 12: "Reaction plate (sample DNA/water)", plate
    reaction_plate_sample = protocol.load_labware('biorad_96_wellplate_200ul_pcr', '12')

    # Assign tubes and wells
    sample_dna_wells = sample_dna_tubes.wells()
    water_source = water_tube.wells_by_name()['A1']
    primer_f_source = primer_f_tube.wells_by_name()['A1']
    primer_r_source = primer_r_tube.wells_by_name()['A1']
    pcr_mix_source = pcr_mix_tube.wells_by_name()['A1']
    template_only_mix_source = template_only_mix_tube.wells_by_name()['A1']
    water_template_only_source = water_template_only_tube.wells_by_name()['A1']

    # Step 1: Prepare master mix in reaction_plate_mix
    master_mix_well = reaction_plate_mix.wells_by_name()['A1']
    # Transfer PCR MIX
    p300.transfer(2000, pcr_mix_source, master_mix_well)
    # Transfer primer F
    p20.transfer(10, primer_f_source, master_mix_well)
    # Transfer primer R
    p20.transfer(10, primer_r_source, master_mix_well)
    # Mix the master mix
    p300.pick_up_tip()
    p300.mix(10, 200, master_mix_well)
    p300.drop_tip()

    # Step 2: Distribute master mix to reaction_plate_mix
    destination_wells_mix = reaction_plate_mix.rows_by_name()['A'][:8]  # Assuming 8 samples
    p20.distribute(
        10,
        master_mix_well,
        [well for well in destination_wells_mix],
        new_tip='once'
    )

    # Step 3: Distribute sample DNA and water to reaction_plate_sample
    # Sample DNA to wells A1-A5
    for i in range(5):
        p20.pick_up_tip()
        p20.transfer(
            5,
            sample_dna_wells[i],
            reaction_plate_sample.wells_by_name()[f'A{i+1}'],
            new_tip='never'
        )
        p20.drop_tip()
    # Water to well A6 (negative control)
    p20.transfer(
        5,
        water_source,
        reaction_plate_sample.wells_by_name()['A6'],
        new_tip='always'
    )

    # Step 4: Combine reaction components in pcr_plate
    for i in range(6):  # Adjust number based on samples
        p20.pick_up_tip()
        # Transfer sample from reaction_plate_sample to pcr_plate
        p20.transfer(
            5,
            reaction_plate_sample.wells_by_name()[f'A{i+1}'],
            pcr_plate.wells_by_name()[f'A{i+1}'],
            new_tip='never'
        )
        # Transfer master mix from reaction_plate_mix to pcr_plate
        p20.transfer(
            10,
            reaction_plate_mix.wells_by_name()[f'A{i+1}'],
            pcr_plate.wells_by_name()[f'A{i+1}'],
            mix_after=(3, 15),
            new_tip='never'
        )
        p20.drop_tip()

    # Step 5: Add template-only mix to pcr_plate (positive control)
    # Assuming well A7 for positive control
    p20.transfer(
        15,
        template_only_mix_source,
        pcr_plate.wells_by_name()['A7'],
        mix_after=(3, 15),
        new_tip='always'
    )

    # Step 6: Add water for template-only control to pcr_plate (negative control)
    # Assuming well A8 for negative control
    p20.transfer(
        15,
        water_template_only_source,
        pcr_plate.wells_by_name()['A8'],
        mix_after=(3, 15),
        new_tip='always'
    )

    # End of protocol
