from opentrons import protocol_api

metadata = {
    'protocolName': 'QPCR Sample Preparation',
    'author': 'Your Name',
    'description': 'Prepare samples for QPCR with multiple primers and controls',
    'apiLevel': '2.9'  # or the latest API level
}

def run(protocol: protocol_api.ProtocolContext):

    # Labware
    # Load tip racks
    tiprack_20ul_1 = protocol.load_labware('opentrons_96_tiprack_20ul', '__place_1__')
    tiprack_20ul_2 = protocol.load_labware('opentrons_96_tiprack_20ul', '__place_8__')
    tiprack_300ul_1 = protocol.load_labware('opentrons_96_tiprack_300ul', '__place_2__')
    tiprack_300ul_2 = protocol.load_labware('opentrons_96_tiprack_300ul', '__place_9__')

    # Load reagents
    # PCR MIX in 15 mL tube in a 15 mL tube rack
    pcr_mix_rack = protocol.load_labware('opentrons_15_tuberack_falcon_15ml_conical', '__place_3__')
    pcr_mix_tube = pcr_mix_rack.wells_by_name()['A1']

    # Sample DNA and water in 1.5 mL tubes in an Eppendorf rack
    sample_rack = protocol.load_labware('opentrons_24_tuberack_eppendorf_1.5ml_safelock_snapcap', '__place_4__')
    sample_dna = sample_rack.wells_by_name()['A1']
    water = sample_rack.wells_by_name()['B1']

    # Primers in a 96 well plate (primers in columns 1 and 2)
    primer_plate = protocol.load_labware('corning_96_wellplate_360ul_flat', '__place_5__')
    # Assign primer_F to column 1 (A1-H1), primer_R to column 2 (A1-H2)

    # PCR MIX + primer mixtures in a 96 well plate
    mix_plate = protocol.load_labware('corning_96_wellplate_360ul_flat', '__place_6__')

    # Reaction plate (96 well PCR plate)
    reaction_plate = protocol.load_labware('biorad_96_wellplate_200ul_pcr', '__place_7__')

    # Pipettes
    p20 = protocol.load_instrument('p20_single_gen2', 'left', tip_racks=[tiprack_20ul_1, tiprack_20ul_2])
    p300 = protocol.load_instrument('p300_single_gen2', 'right', tip_racks=[tiprack_300ul_1, tiprack_300ul_2])

    # Proceed with the steps
    # Step 1: Dispense 137.6 μL of PCR MIX into 13 wells in mix_plate
    for i in range(13):
        dest_well = mix_plate.wells()[i]
        p300.transfer(137.6, pcr_mix_tube, dest_well, new_tip='always')

    # Step 2 and 3: Add 3.2 μL of primer_F and 3.2 μL of primer_R to each PCR MIX well
    for i in range(13):
        mix_well = mix_plate.wells()[i]
        primer_f_well = primer_plate.columns()[0][i]  # primer_F in column 1
        primer_r_well = primer_plate.columns()[1][i]  # primer_R in column 2
        p20.transfer(3.2, primer_f_well, mix_well, new_tip='always')
        p20.transfer(3.2, primer_r_well, mix_well, new_tip='always')
        # Step 4: Mix by pipetting
        p300.pick_up_tip()
        p300.mix(5, 100, mix_well)
        p300.drop_tip()

    # Step 5: Dispense 86 μL of PCR MIX for template only control into a well in mix_plate
    control_mix_well = mix_plate.wells()[13]
    p300.transfer(86, pcr_mix_tube, control_mix_well, new_tip='always')

    # Step 6: Add 4 μL of water to the control mix
    p20.transfer(4, water, control_mix_well, new_tip='always')
    # Step 7: Mix by pipetting
    p300.pick_up_tip()
    p300.mix(5, 80, control_mix_well)
    p300.drop_tip()

    # Step 8: Apply 5 μL of sample DNA or water to reaction plate
    # Define wells for sample DNA, NTC, and template only
    sample_wells = []
    ntc_wells = []
    template_only_wells = []

    # We'll use columns 1-3 for sample with primers (13 primers x 3 replicates = 39 wells)
    # Columns 4-6 for NTC with primers (13 primers x 3 replicates = 39 wells)
    # Columns 7-9 for template only (3 replicates)

    # Sample DNA wells
    for col in range(1, 4):  # columns 1-3
        for row in 'ABCDEFGH':
            well_name = f'{row}{col}'
            sample_wells.append(reaction_plate.wells_by_name()[well_name])

    # NTC wells
    for col in range(4, 7):  # columns 4-6
        for row in 'ABCDEFGH':
            well_name = f'{row}{col}'
            ntc_wells.append(reaction_plate.wells_by_name()[well_name])

    # Template only wells (we need 3 wells)
    template_only_well_names = ['A7', 'B7', 'C7']
    for well_name in template_only_well_names:
        template_only_wells.append(reaction_plate.wells_by_name()[well_name])

    # Apply 5 μL of sample DNA to sample wells
    for well in sample_wells:
        p20.transfer(5, sample_dna, well, new_tip='always')

    # Apply 5 μL of water to NTC wells
    for well in ntc_wells:
        p20.transfer(5, water, well, new_tip='always')

    # Apply 5 μL of sample DNA to template only wells
    for well in template_only_wells:
        p20.transfer(5, sample_dna, well, new_tip='always')

    # Step 9: Apply 10 μL of PCR MIX + primer mixtures to the reaction plate

    # For sample wells
    sample_well_groups = [sample_wells[i:i+3] for i in range(0, len(sample_wells), 3)]
    # For NTC wells
    ntc_well_groups = [ntc_wells[i:i+3] for i in range(0, len(ntc_wells), 3)]

    # Apply PCR MIX + primer mixtures to sample and NTC wells
    for i in range(13):
        mix_well = mix_plate.wells()[i]
        sample_group = sample_well_groups[i]
        ntc_group = ntc_well_groups[i]
        # For sample wells
        for dest_well in sample_group:
            p300.transfer(10, mix_well, dest_well, new_tip='always')
        # For NTC wells
        for dest_well in ntc_group:
            p300.transfer(10, mix_well, dest_well, new_tip='always')

    # Apply control mix to template only wells
    for well in template_only_wells:
        p300.transfer(10, control_mix_well, well, new_tip='always')
