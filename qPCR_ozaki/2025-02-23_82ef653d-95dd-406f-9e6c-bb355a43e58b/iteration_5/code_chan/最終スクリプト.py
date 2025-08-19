from opentrons import protocol_api

metadata = {
    'protocolName': 'PCR Preparation Protocol',
    'author': 'Your Name',
    'description': 'Automated PCR setup using Opentrons OT-2',
    'apiLevel': '2.10'
}

def run(protocol: protocol_api.ProtocolContext):

    # Load labware at specified deck positions
    # Position 1: 1_sample_DNAs in a tube rack
    sample_dna_rack = protocol.load_labware('opentrons_24_tuberack_eppendorf_1.5ml_safelock_snapcap', '1', '1_sample_DNAs')
    
    # Position 2: Water in a tube rack
    water_rack = protocol.load_labware('opentrons_24_tuberack_eppendorf_1.5ml_safelock_snapcap', '2', 'water')
    
    # Position 3: 10 µM Primer F in a tube rack
    primer_f_rack = protocol.load_labware('opentrons_24_tuberack_eppendorf_1.5ml_safelock_snapcap', '3', '10_µM_primer_F')
    
    # Position 4: 10 µM Primer R in a tube rack
    primer_r_rack = protocol.load_labware('opentrons_24_tuberack_eppendorf_1.5ml_safelock_snapcap', '4', '10_µM_primer_R')
    
    # Position 5: PCR MIX in a tube rack
    pcr_mix_rack = protocol.load_labware('opentrons_24_tuberack_eppendorf_1.5ml_safelock_snapcap', '5', 'PCR_MIX')
    
    # Position 7: 96-well PCR plate
    pcr_plate = protocol.load_labware('nest_96_wellplate_100ul_pcr_full_skirt', '7', '96_well_PCR_plate')
    
    # Position 10: Empty tube in a tube rack
    empty_tube_rack = protocol.load_labware('opentrons_24_tuberack_nest_1.5ml_snapcap', '10', 'empty_tube')

    # Load tip racks
    tip_rack_20ul = protocol.load_labware('opentrons_96_tiprack_20ul', '6')
    tip_rack_300ul = protocol.load_labware('opentrons_96_tiprack_300ul', '9')
    
    # Load pipettes
    p20 = protocol.load_instrument('p20_single_gen2', 'left', tip_racks=[tip_rack_20ul])
    p300 = protocol.load_instrument('p300_single_gen2', 'right', tip_racks=[tip_rack_300ul])

    # Reagents locations
    sample_dna = sample_dna_rack.wells_by_name()['A1']
    water = water_rack.wells_by_name()['A1']
    primer_f = primer_f_rack.wells_by_name()['A1']
    primer_r = primer_r_rack.wells_by_name()['A1']
    pcr_mix = pcr_mix_rack.wells_by_name()['A1']
    empty_tube = empty_tube_rack.wells_by_name()['A1']

    # Define the PCR setup
    num_samples = 8  # Adjust the number of samples as needed
    sample_wells = pcr_plate.wells()[:num_samples]

    # Prepare master mix in the empty tube
    master_mix_volume = 15 * num_samples * 1.1  # 10% extra volume
    p300.transfer(master_mix_volume, pcr_mix, empty_tube)

    # Add water to master mix
    water_volume = 5 * num_samples * 1.1
    p300.transfer(water_volume, water, empty_tube, mix_after=(3, 100))

    # Add primers to master mix
    primer_volume = 1 * num_samples * 1.1
    p20.transfer(primer_volume, primer_f, empty_tube, mix_after=(3, 15))
    p20.transfer(primer_volume, primer_r, empty_tube, mix_after=(3, 15))

    # Distribute master mix to PCR plate
    for well in sample_wells:
        p20.transfer(20, empty_tube, well)

    # Add sample DNA to PCR plate
    for well in sample_wells:
        p20.transfer(5, sample_dna, well, mix_after=(3, 15))
