from opentrons import protocol_api

metadata = {
    'protocolName': 'qPCR Preparation for QuantStudio 6 Pro',
    'author': 'Your Name',
    'description': 'Prepare qPCR reactions with sample DNA, primers, PCR mix, and controls.',
    'apiLevel': '2.9'
}

def run(protocol: protocol_api.ProtocolContext):

    # Labware setup

    # Tip racks
    tiprack_p20 = protocol.load_labware('opentrons_96_tiprack_20ul', '9')  # __place_1__ replaced with '9'
    tiprack_p300 = protocol.load_labware('opentrons_96_tiprack_300ul', '10')  # __place_2__ replaced with '10'

    # Sample DNA tube in slot 1
    sample_dna_labware = protocol.load_labware('opentrons_24_aluminumblock_generic_2ml_screwcap', '1')  # __place_3__ replaced with '1'
    sample_dna_tube = sample_dna_labware.wells_by_name()['A1']

    # Water tube in slot 2
    water_labware = protocol.load_labware('opentrons_24_aluminumblock_generic_2ml_screwcap', '2')
    water_tube = water_labware.wells_by_name()['A1']

    # Primer_F tube in slot 3
    primer_f_labware = protocol.load_labware('opentrons_24_aluminumblock_generic_2ml_screwcap', '3')
    primer_f_tube = primer_f_labware.wells_by_name()['A1']

    # Primer_R tube in slot 4
    primer_r_labware = protocol.load_labware('opentrons_24_aluminumblock_generic_2ml_screwcap', '4')
    primer_r_tube = primer_r_labware.wells_by_name()['A1']

    # PCR MIX source tube in slot 6
    pcr_mix_labware = protocol.load_labware('opentrons_24_aluminumblock_generic_2ml_screwcap', '6')
    pcr_mix_tube = pcr_mix_labware.wells_by_name()['A1']

    # Template-only PCR MIX tube in slot 5 (supplemented as necessary)
    template_only_mix_labware = protocol.load_labware('opentrons_24_aluminumblock_generic_2ml_screwcap', '5')
    template_only_mix_tube = template_only_mix_labware.wells_by_name()['A1']

    # Mix plate (supplemented as necessary)
    mix_plate = protocol.load_labware('opentrons_96_aluminumblock_generic_pcr_strip_200ul', '11')  # __place_5__ replaced with '11'

    # Reaction plate
    reaction_plate = protocol.load_labware('biorad_96_wellplate_200ul_pcr', '8')  # __place_6__ replaced with '8'

    # Pipettes
    p20 = protocol.load_instrument('p20_single_gen2', 'left', tip_racks=[tiprack_p20])
    p300 = protocol.load_instrument('p300_single_gen2', 'right', tip_racks=[tiprack_p300])

    # Step 1: Dispense 137.6 μL of PCR MIX into one tube (since only one primer set)
    dest_well = mix_plate.wells()[0]  # A1
    p300.pick_up_tip()
    p300.transfer(137.6, pcr_mix_tube, dest_well, new_tip='never')
    p300.drop_tip()

    # Step 2 and 3: Add 3.2 μL of primer_F and primer_R to PCR MIX tube
    p20.pick_up_tip()
    p20.transfer(3.2, primer_f_tube, dest_well, new_tip='never')
    p20.transfer(3.2, primer_r_tube, dest_well, mix_after=(3, 10), new_tip='never')
    p20.drop_tip()

    # Step 5 and 6: Prepare template-only PCR MIX
    p300.pick_up_tip()
    p300.transfer(86, pcr_mix_tube, template_only_mix_tube, new_tip='never')
    p300.drop_tip()
    p20.pick_up_tip()
    p20.transfer(4, water_tube, template_only_mix_tube, mix_after=(3, 10), new_tip='never')
    p20.drop_tip()

    # Step 8: Add 5 μL of sample DNA or water into the reaction plate
    sample_wells = []
    ntc_wells = []
    for rep in range(3):  # Replicates
        sample_well = reaction_plate.rows()[rep][0]  # Column 1
        ntc_well = reaction_plate.rows()[rep + 3][0]
        sample_wells.append(sample_well)
        ntc_wells.append(ntc_well)

    # Template-only wells
    template_only_wells = [reaction_plate.wells_by_name()['G1'], reaction_plate.wells_by_name()['G2'], reaction_plate.wells_by_name()['G3']]

    # Add sample DNA to sample wells
    for well in sample_wells:
        p20.pick_up_tip()
        p20.transfer(5, sample_dna_tube, well, new_tip='never')
        p20.drop_tip()

    # Add water to NTC wells
    for well in ntc_wells:
        p20.pick_up_tip()
        p20.transfer(5, water_tube, well, new_tip='never')
        p20.drop_tip()

    # Add sample DNA to template-only wells
    for well in template_only_wells:
        p20.pick_up_tip()
        p20.transfer(5, sample_dna_tube, well, new_tip='never')
        p20.drop_tip()

    # Step 9: Add 10 μL of PCR MIX and primer mixture into reaction plate
    for well in sample_wells:
        p20.pick_up_tip()
        p20.transfer(10, dest_well, well, new_tip='never')
        p20.drop_tip()

    for well in ntc_wells:
        p20.pick_up_tip()
        p20.transfer(10, dest_well, well, new_tip='never')
        p20.drop_tip()

    # Add template-only PCR MIX to template-only wells
    for well in template_only_wells:
        p20.pick_up_tip()
        p20.transfer(10, template_only_mix_tube, well, new_tip='never')
        p20.drop_tip()
