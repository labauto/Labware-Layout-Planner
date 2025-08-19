from opentrons import protocol_api

metadata = {
    'protocolName': 'qPCR Sample Preparation',
    'author': 'Your Name',
    'description': 'Automated preparation of qPCR samples with 13 primer sets and controls',
    'apiLevel': '2.9'
}

def run(protocol: protocol_api.ProtocolContext):

    # Labware setup

    # Tip racks
    tiprack_20 = protocol.load_labware('opentrons_96_tiprack_20ul', '7')
    tiprack_20_2 = protocol.load_labware('opentrons_96_tiprack_20ul', '9')
    tiprack_300 = protocol.load_labware('opentrons_96_tiprack_300ul', '5')

    # Sample DNA tube at position 1
    sample_dna_rack = protocol.load_labware('opentrons_24_tuberack_generic_2ml_screwcap', '1')
    sample_dna_tube = sample_dna_rack.wells_by_name()['A1']

    # Water tube at position 2
    water_rack = protocol.load_labware('opentrons_24_tuberack_generic_2ml_screwcap', '2')
    water_tube = water_rack.wells_by_name()['A1']

    # Primer tubes at positions 3 and 4
    primer_f_rack = protocol.load_labware('opentrons_24_tuberack_generic_2ml_screwcap', '3')
    primer_f_tube = primer_f_rack.wells_by_name()['A1']

    primer_r_rack = protocol.load_labware('opentrons_24_tuberack_generic_2ml_screwcap', '4')
    primer_r_tube = primer_r_rack.wells_by_name()['A1']

    # PCR MIX tube at position 6
    pcr_mix_rack = protocol.load_labware('opentrons_24_tuberack_generic_2ml_screwcap', '6')
    pcr_mix_tube = pcr_mix_rack.wells_by_name()['A1']

    # Reaction plate (96-well PCR plate) at position 8
    reaction_plate = protocol.load_labware('biorad_96_wellplate_200ul_pcr', '8')

    # Pipettes
    p20 = protocol.load_instrument('p20_single_gen2', 'left', tip_racks=[tiprack_20, tiprack_20_2])
    p300 = protocol.load_instrument('p300_single_gen2', 'right', tip_racks=[tiprack_300])

    # Mix tubes for PCR MIX + primers at position 10
    mix_tube_rack = protocol.load_labware('opentrons_24_tuberack_generic_2ml_screwcap', '10')

    # PCR MIX + primers tubes in mix_tube_rack positions A1-A13
    pcr_primer_mixes = mix_tube_rack.wells()[:13]

    # Template-only PCR MIX tube in mix_tube_rack position B1
    template_only_mix = mix_tube_rack.wells_by_name()['B1']

    # Step 1: Aliquot 137.6 μL PCR MIX into 13 tubes
    for i in range(13):
        dest_tube = pcr_primer_mixes[i]
        p300.pick_up_tip()
        p300.transfer(137.6, pcr_mix_tube, dest_tube, new_tip='never')
        p300.mix(3, 100, dest_tube)
        p300.drop_tip()

    # Step 5: Prepare template-only PCR MIX, 86 μL PCR MIX + 4 μL water
    p300.pick_up_tip()
    p300.transfer(86, pcr_mix_tube, template_only_mix, new_tip='never')
    p300.mix(3, 80, template_only_mix)
    p300.drop_tip()

    p20.pick_up_tip()
    p20.transfer(4, water_tube, template_only_mix, new_tip='never')
    p20.mix(3, 10, template_only_mix)
    p20.drop_tip()

    # Since primers are in single tubes, add primers directly to PCR MIX tubes
    for i in range(13):
        dest_tube = pcr_primer_mixes[i]
        # Add forward primer
        p20.pick_up_tip()
        p20.transfer(3.2, primer_f_tube, dest_tube, new_tip='never')
        p20.mix(3, 10, dest_tube)
        p20.drop_tip()
        # Add reverse primer
        p20.pick_up_tip()
        p20.transfer(3.2, primer_r_tube, dest_tube, new_tip='never')
        p20.mix(3, 10, dest_tube)
        p20.drop_tip()

    # Define wells for sample DNA, NTC, and template-only controls
    sample_wells = []
    ntc_wells = []
    for i in range(13):
        # For each PCR primer mix
        for rep in range(3):
            # Sample wells
            well_sample = reaction_plate.wells()[i * 6 + rep]
            sample_wells.append((well_sample, i))
            # NTC wells
            well_ntc = reaction_plate.wells()[i * 6 + 3 + rep]
            ntc_wells.append((well_ntc, i))

    # Template-only wells (last 3 wells)
    template_only_wells = reaction_plate.wells()[78:81]

    # Step 8: Add 5 μL sample DNA to sample wells
    for well, _ in sample_wells:
        p20.pick_up_tip()
        p20.transfer(5, sample_dna_tube, well, new_tip='never')
        p20.drop_tip()

    # Add 5 μL water to NTC wells
    for well, _ in ntc_wells:
        p20.pick_up_tip()
        p20.transfer(5, water_tube, well, new_tip='never')
        p20.drop_tip()

    # Add 5 μL sample DNA to template-only wells
    for well in template_only_wells:
        p20.pick_up_tip()
        p20.transfer(5, sample_dna_tube, well, new_tip='never')
        p20.drop_tip()

    # Step 9: Add 10 μL of PCR MIX + primers to sample wells and NTC wells
    for well, primer_index in sample_wells:
        mix_tube = pcr_primer_mixes[primer_index]
        p20.pick_up_tip()
        p20.transfer(10, mix_tube, well, new_tip='never')
        p20.drop_tip()

    for well, primer_index in ntc_wells:
        mix_tube = pcr_primer_mixes[primer_index]
        p20.pick_up_tip()
        p20.transfer(10, mix_tube, well, new_tip='never')
        p20.drop_tip()

    # Add 10 μL of template-only PCR MIX to template-only wells
    for well in template_only_wells:
        p20.pick_up_tip()
        p20.transfer(10, template_only_mix, well, new_tip='never')
        p20.drop_tip()

    # Protocol complete
