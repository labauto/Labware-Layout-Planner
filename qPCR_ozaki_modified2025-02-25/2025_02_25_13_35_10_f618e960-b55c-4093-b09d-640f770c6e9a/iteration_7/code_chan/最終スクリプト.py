from opentrons import protocol_api

metadata = {
    'protocolName': 'qPCR Preparation for QuantStudio 6 Pro',
    'author': 'Your Name',
    'description': 'Prepare qPCR samples with multiple primers and duplicates',
    'apiLevel': '2.9'  # Specify the API level
}

def run(protocol: protocol_api.ProtocolContext):
    # Labware setup

    # Tip racks
    tiprack_20 = protocol.load_labware('opentrons_96_tiprack_20ul', '9')
    tiprack_300 = protocol.load_labware('opentrons_96_tiprack_300ul', '10')

    # Pipettes
    p20 = protocol.load_instrument('p20_single_gen2', 'left', tip_racks=[tiprack_20])
    p300 = protocol.load_instrument('p300_single_gen2', 'right', tip_racks=[tiprack_300])

    # Primers plate (10 μM primer_F and primer_R)
    primers_plate = protocol.load_labware('corning_96_wellplate_360ul_flat', '2')

    # PCR MIX tube rack (15 mL tube)
    pcr_mix_tuberack = protocol.load_labware('opentrons_10_tuberack_falcon_4x50ml_6x15ml_conical', '5')

    # Sample DNA reservoir
    sample_reservoir = protocol.load_labware('usascientific_12_reservoir_22ml', '6')

    # Water tube rack
    water_tuberack = protocol.load_labware('opentrons_24_tuberack_generic_2ml_screwcap', '8')

    # PCR plate for the reaction
    pcr_plate = protocol.load_labware('biorad_96_wellplate_200ul_pcr', '12')

    # PCR MIX + primers plate
    pcr_mix_plate = protocol.load_labware('corning_96_wellplate_360ul_flat', '7')

    # Reagents
    pcr_mix = pcr_mix_tuberack.wells_by_name()['A1']  # PCR MIX in 15 mL tube
    sample_dna = sample_reservoir.wells_by_name()['A1']  # Sample DNA
    water = water_tuberack.wells_by_name()['A1']  # Water for NTC and template-only control

    # Constants
    num_primers = 13
    num_replicates = 3

    # Step 1: Distribute PCR MIX into 13 wells, 137.6 μL each
    pcr_mix_wells = pcr_mix_plate.wells()[:num_primers]  # First 13 wells
    p300.distribute(137.6, pcr_mix, pcr_mix_wells, new_tip='always')

    # Step 2 & 3: Add 3.2 μL of primer_F and primer_R to each PCR MIX well
    for i in range(num_primers):
        primer_f_well = primers_plate.wells()[i]  # Primer_F1-13
        primer_r_well = primers_plate.wells()[i + num_primers]  # Primer_R1-13
        p20.transfer(3.2, primer_f_well, pcr_mix_wells[i], new_tip='always')
        p20.transfer(3.2, primer_r_well, pcr_mix_wells[i], mix_after=(3, 10), new_tip='always')

    # Step 5 & 6: Prepare template-only control PCR MIX
    template_control_well = pcr_mix_plate.wells()[num_primers]
    p300.transfer(86, pcr_mix, template_control_well, new_tip='always')
    p20.transfer(4, water, template_control_well, mix_after=(3, 10), new_tip='always')

    # Step 8: Add sample DNA or water to the reaction plate, 5 μL per well
    total_samples = num_primers * num_replicates  # 39 wells for sample DNA
    total_ntc = num_primers * num_replicates  # 39 wells for NTC
    total_toc = num_replicates  # 3 wells for template-only control
    total_wells = total_samples + total_ntc + total_toc  # 81 wells

    all_wells = pcr_plate.wells()[:total_wells]

    # Add sample DNA to sample wells
    sample_wells = all_wells[:total_samples]
    p20.distribute(5, sample_dna, sample_wells, new_tip='always')

    # Add water to NTC wells
    ntc_wells = all_wells[total_samples:total_samples + total_ntc]
    p20.distribute(5, water, ntc_wells, new_tip='always')

    # Add sample DNA to template-only control wells
    toc_wells = all_wells[total_samples + total_ntc:]
    p20.distribute(5, sample_dna, toc_wells, new_tip='always')

    # Step 9: Add PCR MIX + primer mixtures to the reaction wells, 10 μL per well

    # Add PCR MIX + primers to sample wells
    for i in range(num_primers):
        source_well = pcr_mix_wells[i]
        dest_wells = sample_wells[i * num_replicates:(i + 1) * num_replicates]
        p20.distribute(10, source_well, dest_wells, new_tip='always')

    # Add PCR MIX + primers to NTC wells
    for i in range(num_primers):
        source_well = pcr_mix_wells[i]
        dest_wells = ntc_wells[i * num_replicates:(i + 1) * num_replicates]
        p20.distribute(10, source_well, dest_wells, new_tip='always')

    # Add template-only PCR MIX to template-only control wells
    p20.distribute(10, template_control_well, toc_wells, new_tip='always')
