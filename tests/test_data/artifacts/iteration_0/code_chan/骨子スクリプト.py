from opentrons import protocol_api

metadata = {
    'protocolName': 'qPCR Preparation',
    'author': 'Your Name',
    'description': 'Prepare qPCR reactions with multiple samples and primers',
    'apiLevel': '2.9'
}

def run(protocol: protocol_api.ProtocolContext):
    # Labware setup with placeholders
    tip_rack_200 = protocol.load_labware('opentrons_96_tiprack_300ul', '__place_1__')
    tip_rack_20 = protocol.load_labware('opentrons_96_tiprack_20ul', '__place_2__')

    # Reagent tubes and plates
    sample_tubes = protocol.load_labware('opentrons_24_tuberack_generic_2ml_screwcap', '__place_3__') # For sample DNAs and NTC
    primer_plate = protocol.load_labware('nest_96_wellplate_100ul_pcr_full_skirt', '__place_4__')
    pcr_mix_tube = protocol.load_labware('opentrons_24_aluminumblock_generic_2ml_screwcap', '__place_5__')  # PCR MIX in A1
    pcr_mix_primer_tubes = protocol.load_labware('opentrons_24_aluminumblock_generic_2ml_screwcap', '__place_6__')  # Mixtures in A1-A4
    reaction_plate = protocol.load_labware('biorad_96_wellplate_200ul_pcr', '__place_7__')

    # Pipettes
    p300 = protocol.load_instrument('p300_single', 'left', tip_racks=[tip_rack_200])
    p20 = protocol.load_instrument('p20_single_gen2', 'right', tip_racks=[tip_rack_20])

    # Reagent setup
    # PCR Mix in pcr_mix_tube.wells_by_name()['A1']
    pcr_mix = pcr_mix_tube.wells_by_name()['A1']

    # Primer F1-F4 in primer_plate wells A1-D1
    primer_F_wells = [primer_plate.wells_by_name()[well] for well in ['A1', 'B1', 'C1', 'D1']]

    # Primer R1-R4 in primer_plate wells A2-D2
    primer_R_wells = [primer_plate.wells_by_name()[well] for well in ['A2', 'B2', 'C2', 'D2']]

    # Mixes will be prepared in pcr_mix_primer_tubes.wells_by_name()['A1'] to ['A4']
    pcr_mix_primer_wells = [pcr_mix_primer_tubes.wells_by_name()[well] for well in ['A1', 'A2', 'A3', 'A4']]

    # Samples 1-11 in sample_tubes.wells_by_name()['A1'] to ['A11'], NTC (water) in 'A12'
    sample_wells = [sample_tubes.wells_by_name()[f'A{i}'] for i in range(1,13)]  # A1 to A12

    # Prepare PCR mix + primer mixtures
    for i in range(4):
        # Transfer 221 μL of PCR MIX into each of the 4 tubes
        p300.pick_up_tip()
        p300.transfer(221, pcr_mix, pcr_mix_primer_wells[i], new_tip='never')
        p300.drop_tip()

        # Add 19.5 μL of primer_F to the PCR mix
        p20.pick_up_tip()
        p20.transfer(19.5, primer_F_wells[i], pcr_mix_primer_wells[i], new_tip='never')
        p20.drop_tip()

        # Add 19.5 μL of primer_R to the PCR mix
        p20.pick_up_tip()
        p20.transfer(19.5, primer_R_wells[i], pcr_mix_primer_wells[i], new_tip='never')
        p20.drop_tip()

        # Mix PCR mix and primers
        p300.pick_up_tip()
        p300.mix(5, 200, pcr_mix_primer_wells[i])
        p300.drop_tip()

    # Distribute 5 μL of sample DNA or water (NTC) into the reaction plate
    sample_names = ['S' + str(i) for i in range(1,12)] + ['NTC']  # S1 to S11 and NTC
    sample_index = 0
    for sample_name, sample_well in zip(sample_names, sample_wells):
        wells_to_dispense = []
        for primer in range(4):
            for replicate in range(2):
                # Calculate the well position
                row = primer  # rows 0-3 correspond to the 4 primers
                col = sample_index*2 + replicate  # each sample occupies 2 columns (due to duplicates)
                well = reaction_plate.rows()[row][col]
                wells_to_dispense.append(well)
        # Distribute 5 μL sample to wells_to_dispense
        p20.pick_up_tip()
        for dest_well in wells_to_dispense:
            p20.aspirate(5, sample_well)
            p20.dispense(5, dest_well)
        p20.drop_tip()
        sample_index += 1

    # Distribute 10 μL of PCR mix + primer mixtures into the reaction plate
    for primer_index, mix_well in enumerate(pcr_mix_primer_wells):
        wells_to_dispense = []
        for sample_idx in range(12):
            for replicate in range(2):
                row = primer_index
                col = sample_idx*2 + replicate
                well = reaction_plate.rows()[row][col]
                wells_to_dispense.append(well)
        # Distribute 10 μL PCR mix + primer mixture to wells_to_dispense
        p20.pick_up_tip()
        for dest_well in wells_to_dispense:
            p20.aspirate(10, mix_well)
            p20.dispense(10, dest_well)
        p20.drop_tip()
