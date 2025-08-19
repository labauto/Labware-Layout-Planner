from opentrons import protocol_api

metadata = {
    'protocolName': 'QPCR Sample Preparation',
    'author': 'Your Name',
    'description': 'Prepare qPCR reactions for measurement with QuantStudio 6 Pro',
    'apiLevel': '2.9'
}

def run(protocol: protocol_api.ProtocolContext):
    # Labware setup
    # Tip racks
    tiprack_p20 = protocol.load_labware('opentrons_96_tiprack_20ul', '5')
    tiprack_p300 = protocol.load_labware('opentrons_96_tiprack_300ul', '7')

    # Pipettes
    p20 = protocol.load_instrument('p20_single_gen2', 'left', tip_racks=[tiprack_p20])
    p300 = protocol.load_instrument('p300_single_gen2', 'right', tip_racks=[tiprack_p300])

    # PCR MIX stock in 15 mL tube in tube rack at position 6
    pcr_mix_tube_rack = protocol.load_labware('opentrons_15_tuberack_falcon_15ml_conical', '6')
    pcr_mix_tube = pcr_mix_tube_rack.wells_by_name()['A1']  # PCR MIX in A1

    # Primer_F in 96 well plate at position 3
    primer_F_plate = protocol.load_labware('corning_96_wellplate_360ul_flat', '3')
    primers_F_wells = primer_F_plate.wells()[:13]  # Primer_F1-13 in wells A1 to A13

    # Primer_R in 96 well plate at position 4
    primer_R_plate = protocol.load_labware('corning_96_wellplate_360ul_flat', '4')
    primers_R_wells = primer_R_plate.wells()[:13]  # Primer_R1-13 in wells A1 to A13

    # PCR MIX aliquots with primers in 96 well plate at position 9
    pcr_mix_aliquots_plate = protocol.load_labware('nest_96_wellplate_100ul_pcr_full_skirt', '9')
    pcr_mix_wells = pcr_mix_aliquots_plate.wells()[:13]  # PCR MIX aliquots in wells A1 to A13
    template_mix_well = pcr_mix_aliquots_plate.wells()[13]  # Template-only PCR MIX in well A14

    # Sample DNA in tube rack at position 1
    sample_dna_tube_rack = protocol.load_labware('opentrons_24_tuberack_nest_1.5ml_snapcap', '1')
    sample_dna_tube = sample_dna_tube_rack.wells_by_name()['A1']  # Sample DNA in A1

    # Water in tube rack at position 2
    water_tube_rack = protocol.load_labware('opentrons_24_tuberack_nest_1.5ml_snapcap', '2')
    water_tube = water_tube_rack.wells_by_name()['A1']  # Water in A1

    # Reaction plate (destination plate) at position 8
    reaction_plate = protocol.load_labware('biorad_96_wellplate_200ul_pcr', '8')

    # Step 1: Dispense 137.6μL PCR MIX into 13 wells
    for well in pcr_mix_wells:
        p300.pick_up_tip()
        p300.transfer(137.6, pcr_mix_tube.bottom(2), well.bottom(2), new_tip='never')
        p300.drop_tip()

    # Step 2: Add 3.2μL primer_F1-13 to PCR MIX wells
    for primer_well, mix_well in zip(primers_F_wells, pcr_mix_wells):
        p20.pick_up_tip()
        p20.transfer(3.2, primer_well.bottom(1), mix_well.top(-2), mix_after=(3, 10), new_tip='never')
        p20.drop_tip()

    # Step 3: Add 3.2μL primer_R1-13 to PCR MIX wells
    for primer_well, mix_well in zip(primers_R_wells, pcr_mix_wells):
        p20.pick_up_tip()
        p20.transfer(3.2, primer_well.bottom(1), mix_well.top(-2), mix_after=(3, 10), new_tip='never')
        p20.drop_tip()

    # Step 4: Mix PCR MIX and primers by pipetting
    for mix_well in pcr_mix_wells:
        p300.pick_up_tip()
        p300.mix(5, 50, mix_well.bottom(2))
        p300.drop_tip()

    # Step 5: For template only, dispense 86μL PCR MIX
    p300.pick_up_tip()
    p300.transfer(86, pcr_mix_tube.bottom(2), template_mix_well.bottom(2), new_tip='never')
    p300.drop_tip()

    # Step 6: Add 4μL water to template-only PCR MIX
    p20.pick_up_tip()
    p20.transfer(4, water_tube.bottom(1), template_mix_well.top(-2), mix_after=(3, 10), new_tip='never')
    p20.drop_tip()

    # Step 7: Mix PCR MIX and water
    p300.pick_up_tip()
    p300.mix(5, 50, template_mix_well.bottom(2))
    p300.drop_tip()

    # Prepare reaction wells
    reaction_wells = reaction_plate.wells()[:81]
    reaction_wells_sample = reaction_wells[:39]  # First 39 wells for sample DNA + primers
    reaction_wells_ntc = reaction_wells[39:78]  # Next 39 wells for NTC + primers
    reaction_wells_template_only = reaction_wells[78:81]  # Last 3 wells for template only

    # Step 8: Add 5μL of sample DNA to sample wells and template-only wells
    for well in reaction_wells_sample + reaction_wells_template_only:
        p20.pick_up_tip()
        p20.transfer(5, sample_dna_tube.bottom(1), well.bottom(1), new_tip='never')
        p20.drop_tip()

    # Step 8: Add 5μL of water to NTC wells
    for well in reaction_wells_ntc:
        p20.pick_up_tip()
        p20.transfer(5, water_tube.bottom(1), well.bottom(1), new_tip='never')
        p20.drop_tip()

    # Step 9: Add 10μL of PCR MIX with primers to sample wells
    for i in range(13):
        mix_well = pcr_mix_wells[i]
        for j in range(3):
            dest_well = reaction_wells_sample[3 * i + j]
            p20.pick_up_tip()
            p20.transfer(10, mix_well.bottom(1), dest_well.bottom(1), new_tip='never')
            p20.drop_tip()

    # Step 9: Add 10μL of PCR MIX with primers to NTC wells
    for i in range(13):
        mix_well = pcr_mix_wells[i]
        for j in range(3):
            dest_well = reaction_wells_ntc[3 * i + j]
            p20.pick_up_tip()
            p20.transfer(10, mix_well.bottom(1), dest_well.bottom(1), new_tip='never')
            p20.drop_tip()

    # Step 9: Add 10μL of template-only PCR MIX to template-only wells
    for well in reaction_wells_template_only:
        p20.pick_up_tip()
        p20.transfer(10, template_mix_well.bottom(1), well.bottom(1), new_tip='never')
        p20.drop_tip()
