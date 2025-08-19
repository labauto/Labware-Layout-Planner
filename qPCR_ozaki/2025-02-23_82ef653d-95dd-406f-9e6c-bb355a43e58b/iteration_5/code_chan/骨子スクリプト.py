from opentrons import protocol_api

metadata = {
    'protocolName': 'QPCR Preparation',
    'author': 'Your Name',
    'description': 'Automated QPCR preparation on Opentrons OT-2',
    'apiLevel': '2.9'
}

def run(protocol: protocol_api.ProtocolContext):

    # Load labware with placeholders for positions
    tiprack_p20 = protocol.load_labware('opentrons_96_tiprack_20ul', '__place_1__')
    tiprack_p300 = protocol.load_labware('opentrons_96_tiprack_300ul', '__place_2__')
    reagent_rack = protocol.load_labware('opentrons_24_aluminumblock_generic_2ml_screwcap', '__place_3__')
    primer_rack = protocol.load_labware('opentrons_24_aluminumblock_generic_2ml_screwcap', '__place_4__')
    mixing_rack = protocol.load_labware('opentrons_24_aluminumblock_generic_2ml_screwcap', '__place_5__')
    reaction_plate = protocol.load_labware('biorad_96_wellplate_200ul_pcr', '__place_6__')

    # Load pipettes
    p20 = protocol.load_instrument('p20_single_gen2', 'right', tip_racks=[tiprack_p20])
    p300 = protocol.load_instrument('p300_single_gen2', 'left', tip_racks=[tiprack_p300])

    # Define reagent locations
    PCR_MIX_source = reagent_rack.wells_by_name()['A1']
    sample_DNA = reagent_rack.wells_by_name()['A2']
    water = reagent_rack.wells_by_name()['A3']

    # Define primer wells
    primers_F_wells = primer_rack.wells()[:13]  # Forward primers in first 13 wells
    primers_R_wells = primer_rack.wells()[13:26]  # Reverse primers in next 13 wells

    # Define mixing tubes for PCR MIX and primers
    mixing_tubes = mixing_rack.wells()[:13]  # 13 tubes for mixes with primers
    template_only_tube = mixing_rack.wells_by_name()['A4']  # Tube for template-only control

    # Step 1: Dispense 137.6 μL PCR MIX into 13 mixing tubes
    for dest in mixing_tubes:
        p300.pick_up_tip()
        p300.transfer(137.6, PCR_MIX_source, dest, new_tip='never')
        p300.drop_tip()

    # Step 5: Dispense 86 μL PCR MIX for template-only control
    p300.pick_up_tip()
    p300.transfer(86, PCR_MIX_source, template_only_tube, new_tip='never')
    p300.drop_tip()

    # Step 2 & 3: Add 3.2 μL of primers F and R to each mixing tube
    for f_primer, r_primer, dest in zip(primers_F_wells, primers_R_wells, mixing_tubes):
        p20.pick_up_tip()
        p20.transfer(3.2, f_primer, dest, new_tip='never')
        p20.transfer(3.2, r_primer, dest, new_tip='never')
        p20.mix(3, 20, dest)
        p20.blow_out(dest.top())
        p20.drop_tip()

    # Step 6: Add 4 μL of water into template-only control tube
    p20.pick_up_tip()
    p20.transfer(4, water, template_only_tube, mix_after=(3, 20), new_tip='never')
    p20.drop_tip()

    # Step 8: Apply 5 μL of sample DNA or water to reaction plate
    # Sample wells
    sample_wells = []
    for col in range(1, 14):  # Columns 1-13
        for row in ['A', 'B', 'C']:  # Rows A-C
            well_name = f'{row}{col}'
            sample_wells.append(reaction_plate.wells_by_name()[well_name])
    # NTC wells
    ntc_wells = []
    for col in range(1, 14):
        for row in ['D', 'E', 'F']:  # Rows D-F
            well_name = f'{row}{col}'
            ntc_wells.append(reaction_plate.wells_by_name()[well_name])
    # Template-only wells
    template_only_wells = []
    for row in ['A', 'B', 'C']:
        well_name = f'{row}14'  # Column 14
        template_only_wells.append(reaction_plate.wells_by_name()[well_name])

    # Dispense sample DNA to sample wells
    for well in sample_wells:
        p20.pick_up_tip()
        p20.transfer(5, sample_DNA, well, new_tip='never')
        p20.drop_tip()

    # Dispense water to NTC wells
    for well in ntc_wells:
        p20.pick_up_tip()
        p20.transfer(5, water, well, new_tip='never')
        p20.drop_tip()

    # Dispense sample DNA to template-only wells
    for well in template_only_wells:
        p20.pick_up_tip()
        p20.transfer(5, sample_DNA, well, new_tip='never')
        p20.drop_tip()

    # Step 9: Apply 10 μL of PCR MIX + primers to reaction plate
    for i, mix_tube in enumerate(mixing_tubes):
        col = i + 1
        dest_wells = []
        for row in ['A', 'B', 'C', 'D', 'E', 'F']:
            well_name = f'{row}{col}'
            dest_wells.append(reaction_plate.wells_by_name()[well_name])
        for well in dest_wells:
            p20.pick_up_tip()
            p20.transfer(10, mix_tube, well, new_tip='never')
            p20.drop_tip()

    # Dispense PCR MIX (template-only) to template-only wells
    for well in template_only_wells:
        p20.pick_up_tip()
        p20.transfer(10, template_only_tube, well, new_tip='never')
        p20.drop_tip()
