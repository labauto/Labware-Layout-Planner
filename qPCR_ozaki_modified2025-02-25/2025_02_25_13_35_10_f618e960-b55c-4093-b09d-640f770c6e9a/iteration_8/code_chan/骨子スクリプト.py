from opentrons import protocol_api

metadata = {
    'protocolName': 'QPCR Preparation with Opentrons OT-2',
    'author': 'Your Name',
    'description': 'Automated qPCR setup involving sample DNA, primers, and PCR mix',
    'apiLevel': '2.9'  # Specify the API level for this code
}

def run(protocol: protocol_api.ProtocolContext):
    # Labware setup
    # Tip racks
    tip_rack_20ul_1 = protocol.load_labware('opentrons_96_tiprack_20ul', '__place_1__')
    tip_rack_20ul_2 = protocol.load_labware('opentrons_96_tiprack_20ul', '__place_2__')
    tip_rack_300ul = protocol.load_labware('opentrons_96_tiprack_300ul', '__place_3__')

    # Pipettes
    p20 = protocol.load_instrument('p20_single_gen2', 'left', tip_racks=[tip_rack_20ul_1, tip_rack_20ul_2])
    p300 = protocol.load_instrument('p300_single_gen2', 'right', tip_racks=[tip_rack_300ul])

    # Reagents and samples
    primer_plate = protocol.load_labware('corning_96_wellplate_360ul_flat', '__place_4__')  # Contains primers F and R
    sample_plate = protocol.load_labware('nest_12_reservoir_15ml', '__place_5__')  # Contains DNA sample, water, and PCR mix
    mixing_tubes = protocol.load_labware('opentrons_24_aluminumblock_nest_1.5ml_snapcap', '__place_6__')  # For mixing PCR mix and primers
    pcr_plate = protocol.load_labware('biorad_96_wellplate_200ul_pcr', '__place_7__')  # 96 well PCR plate for reactions

    # Reagent setup in sample_plate
    sample_dna = sample_plate.wells_by_name()['A1']
    water = sample_plate.wells_by_name()['A2']
    pcr_mix = sample_plate.wells_by_name()['A3']

    # Prepare PCR mix with primers for each of the 13 primers
    for i in range(13):
        # Calculate the source wells for primers
        primer_f_well = primer_plate.wells()[i]  # Primer_F
        primer_r_well = primer_plate.wells()[i + 13]  # Primer_R (Assuming primers F are in columns 1-13 and R in 14-26)
        mixing_tube = mixing_tubes.wells()[i]

        # Transfer 137.6 μL of PCR mix to mixing tube
        p300.pick_up_tip()
        p300.transfer(137.6, pcr_mix, mixing_tube, new_tip='never')
        p300.drop_tip()

        # Add 3.2 μL of Primer_F to mixing tube
        p20.pick_up_tip()
        p20.transfer(3.2, primer_f_well, mixing_tube, new_tip='never')
        # Add 3.2 μL of Primer_R to mixing tube
        p20.transfer(3.2, primer_r_well, mixing_tube, new_tip='never')
        # Mix the contents
        p20.mix(5, 20, mixing_tube)
        p20.drop_tip()

    # Prepare PCR mix without primers for template-only control
    mixing_tube_template_only = mixing_tubes.wells()[13]
    p300.pick_up_tip()
    p300.transfer(86, pcr_mix, mixing_tube_template_only, new_tip='never')
    p300.drop_tip()

    # Add 4 μL of water to the mixing tube for template-only control
    p20.pick_up_tip()
    p20.transfer(4, water, mixing_tube_template_only, new_tip='never')
    # Mix the contents
    p20.mix(5, 20, mixing_tube_template_only)
    p20.drop_tip()

    # Dispense 5 μL of sample DNA or water into the PCR plate wells
    samples = ['sample_dna'] * 39 + ['water'] * 39 + ['sample_dna'] * 3  # 39 wells for sample, 39 for NTC, 3 for template only
    destinations = pcr_plate.wells()[:81]  # First 81 wells
    for dest, sample in zip(destinations, samples):
        source = sample_dna if sample == 'sample_dna' else water
        p20.pick_up_tip()
        p20.transfer(5, source, dest, new_tip='never')
        p20.drop_tip()

    # Dispense 10 μL of PCR mix with primers into the PCR plate wells
    # For the 13 primer sets in triplicate
    mix_sources = [mixing_tubes.wells()[i] for i in range(13)] * 6  # Each primer mix used 6 times (triplicate for sample and NTC)
    # For template-only control
    mix_sources += [mixing_tube_template_only] * 3

    for dest, mix in zip(destinations, mix_sources):
        p20.pick_up_tip()
        p20.transfer(10, mix, dest, new_tip='never')
        p20.mix(5, 15, dest)  # Mix after dispensing
        p20.drop_tip()
