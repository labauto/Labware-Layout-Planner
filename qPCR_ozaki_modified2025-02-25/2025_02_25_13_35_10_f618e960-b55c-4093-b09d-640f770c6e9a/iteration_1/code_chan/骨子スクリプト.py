from opentrons import protocol_api

metadata = {
    'protocolName': 'QPCR Preparation Protocol',
    'author': 'Your Name',
    'description': 'Automated preparation of QPCR reactions including sample DNA, primers, and PCR MIX',
    'apiLevel': '2.9'  # Specify the API level for this code
}

def run(protocol: protocol_api.ProtocolContext):
    # Set up labware
    # Tip racks
    tiprack_300 = protocol.load_labware('opentrons_96_tiprack_300ul', '__place_1__')
    tiprack_20 = protocol.load_labware('opentrons_96_tiprack_20ul', '__place_2__')

    # PCR MIX tubes in a 15 mL tube rack
    pcr_mix_tuberack = protocol.load_labware('opentrons_10_tuberack_falcon_4x50ml_6x15ml_conical', '__place_3__')
    # PCR MIX is in tube A1, PCR MIX for template only is in tube A2

    # Primer plate
    primer_plate = protocol.load_labware('corning_96_wellplate_360ul_flat', '__place_4__')
    # Primers F1-13 in wells A1-A13, Primers R1-13 in wells B1-B13

    # Sample DNA and water in tube rack
    sample_tuberack = protocol.load_labware('opentrons_24_tuberack_nest_1.5ml_snapcap', '__place_5__')
    # Sample DNA in tube A1, water in tube B1

    # Output 96-well PCR plate
    pcr_plate = protocol.load_labware('biorad_96_wellplate_200ul_pcr', '__place_6__')

    # Plate for mixing PCR MIX and primers
    mix_plate = protocol.load_labware('nest_96_wellplate_2ml_deep', '__place_7__')

    # Set up pipettes
    p300 = protocol.load_instrument('p300_single', 'left', tip_racks=[tiprack_300])
    p20 = protocol.load_instrument('p20_single_gen2', 'right', tip_racks=[tiprack_20])

    # Reagents and samples
    pcr_mix = pcr_mix_tuberack.wells_by_name()['A1']
    pcr_mix_template_only = pcr_mix_tuberack.wells_by_name()['A2']

    sample_dna = sample_tuberack.wells_by_name()['A1']
    water = sample_tuberack.wells_by_name()['B1']

    # Step 1: Dispense 137.6 μL of PCR MIX into 13 wells in mix_plate
    for i in range(13):
        dest = mix_plate.wells()[i]
        p300.pick_up_tip()
        p300.aspirate(137.6, pcr_mix)
        p300.dispense(137.6, dest)
        p300.drop_tip()

    # Steps 2 & 3: Add 3.2 μL of primer_F and primer_R to each PCR MIX well
    for i in range(13):
        dest = mix_plate.wells()[i]
        primer_f = primer_plate.wells_by_name()[f'A{i+1}']
        primer_r = primer_plate.wells_by_name()[f'B{i+1}']
        p20.pick_up_tip()
        p20.transfer(3.2, primer_f, dest, new_tip='never')
        p20.transfer(3.2, primer_r, dest, mix_after=(3, 10), new_tip='never')
        p20.drop_tip()

    # Step 4: Mix PCR MIX and primers (already mixed during transfer)

    # Step 5: Dispense 86 μL of PCR MIX into a separate well for template only
    p300.pick_up_tip()
    p300.aspirate(86, pcr_mix)
    p300.dispense(86, mix_plate.wells()[13])
    p300.drop_tip()

    # Step 6: Add 4 μL of water to the PCR MIX for template only
    p20.pick_up_tip()
    p20.transfer(4, water, mix_plate.wells()[13], mix_after=(3, 10), new_tip='never')
    p20.drop_tip()

    # Step 7: Mix PCR MIX and water (already mixed during transfer)

    # Step 8: Apply 5 μL each of sample DNA or water to the reaction plate
    well_counter = 0
    for replicate in range(3):  # Duplicate 3 times
        for primer_num in range(13):
            # Apply sample DNA
            dest_well = pcr_plate.wells()[well_counter]
            p20.pick_up_tip()
            p20.aspirate(5, sample_dna)
            p20.dispense(5, dest_well)
            p20.drop_tip()
            well_counter += 1

        for primer_num in range(13):
            # Apply water for NTC
            dest_well = pcr_plate.wells()[well_counter]
            p20.pick_up_tip()
            p20.aspirate(5, water)
            p20.dispense(5, dest_well)
            p20.drop_tip()
            well_counter += 1

        # Template-only control
        dest_well = pcr_plate.wells()[well_counter]
        p20.pick_up_tip()
        p20.aspirate(5, sample_dna)
        p20.dispense(5, dest_well)
        p20.drop_tip()
        well_counter += 1

    # Step 9: Apply 10 μL of PCR MIX and primer mixtures to the reaction plate
    well_counter = 0
    for replicate in range(3):
        for primer_num in range(13):
            # Apply PCR MIX with primers to sample wells
            source = mix_plate.wells()[primer_num]
            dest_well = pcr_plate.wells()[well_counter]
            p20.pick_up_tip()
            p20.transfer(10, source, dest_well, mix_after=(3, 10), new_tip='never')
            p20.drop_tip()
            well_counter += 1

        for primer_num in range(13):
            # Apply PCR MIX with primers to NTC wells
            source = mix_plate.wells()[primer_num]
            dest_well = pcr_plate.wells()[well_counter]
            p20.pick_up_tip()
            p20.transfer(10, source, dest_well, mix_after=(3, 10), new_tip='never')
            p20.drop_tip()
            well_counter += 1

        # Apply PCR MIX with water to template-only control
        source = mix_plate.wells()[13]
        dest_well = pcr_plate.wells()[well_counter]
        p20.pick_up_tip()
        p20.transfer(10, source, dest_well, mix_after=(3, 10), new_tip='never')
        p20.drop_tip()
        well_counter += 1
