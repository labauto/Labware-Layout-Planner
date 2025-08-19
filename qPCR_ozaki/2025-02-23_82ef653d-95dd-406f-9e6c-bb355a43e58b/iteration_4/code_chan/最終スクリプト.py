# Import necessary modules
from opentrons import protocol_api

# Metadata
metadata = {
    'protocolName': 'Automated PCR Setup',
    'author': 'Your Name',
    'description': 'An automated protocol for setting up PCR reactions.',
    'apiLevel': '2.11'
}

def run(protocol: protocol_api.ProtocolContext):

    # Labware Definitions
    # Position 1: 1.5 ml tube (reagent)
    reagent_tube_rack = protocol.load_labware(
        'opentrons_24_tuberack_eppendorf_1.5ml_safelock_snapcap',
        location='1',
        label='1.5 ml Tube Rack'
    )

    # Position 2: Water
    water_reservoir = protocol.load_labware(
        'nest_12_reservoir_15ml',
        location='2',
        label='Water Reservoir'
    )

    # Position 3: 10 µM Primer_F
    primer_F_tube_rack = protocol.load_labware(
        'opentrons_24_tuberack_nest_1.5ml_snapcap',
        location='3',
        label='Primer_F Tube Rack'
    )

    # Position 4: 10 µM Primer_R
    primer_R_tube_rack = protocol.load_labware(
        'opentrons_24_tuberack_nest_1.5ml_snapcap',
        location='4',
        label='Primer_R Tube Rack'
    )

    # Position 6: PCR MIX
    pcr_mix_reservoir = protocol.load_labware(
        'nest_12_reservoir_15ml',
        location='6',
        label='PCR MIX Reservoir'
    )

    # Position 8: 96 Well PCR Plate
    pcr_plate = protocol.load_labware(
        'nest_96_wellplate_100ul_pcr_full_skirt',
        location='8',
        label='96 Well PCR Plate'
    )

    # Pipettes
    left_pipette = protocol.load_instrument(
        'p20_single_gen2', mount='left', tip_racks=[
            protocol.load_labware(
                'opentrons_96_tiprack_20ul', location='5')
        ])

    right_pipette = protocol.load_instrument(
        'p300_single_gen2', mount='right', tip_racks=[
            protocol.load_labware(
                'opentrons_96_tiprack_300ul', location='7')
        ])

    # Reagents and Samples
    reagent_tube = reagent_tube_rack.wells_by_name()['A1']
    water = water_reservoir.wells_by_name()['A1']
    primer_F = primer_F_tube_rack.wells_by_name()['A1']
    primer_R = primer_R_tube_rack.wells_by_name()['A1']
    pcr_mix = pcr_mix_reservoir.wells_by_name()['A1']

    # Protocol Steps
    # Step 1: Transfer PCR MIX to PCR Plate
    right_pipette.pick_up_tip()
    right_pipette.distribute(
        25,  # volume in µL
        pcr_mix,
        [well.bottom() for well in pcr_plate.wells()],
        new_tip='never'
    )
    right_pipette.drop_tip()

    # Step 2: Add Water to PCR Plate
    right_pipette.pick_up_tip()
    right_pipette.distribute(
        5,  # volume in µL
        water,
        [well.bottom() for well in pcr_plate.wells()],
        new_tip='never'
    )
    right_pipette.drop_tip()

    # Step 3: Add Primer_F to PCR Plate
    left_pipette.pick_up_tip()
    left_pipette.distribute(
        10,  # volume in µL
        primer_F,
        [well.bottom() for well in pcr_plate.wells()],
        new_tip='never'
    )
    left_pipette.drop_tip()

    # Step 4: Add Primer_R to PCR Plate
    left_pipette.pick_up_tip()
    left_pipette.distribute(
        10,  # volume in µL
        primer_R,
        [well.bottom() for well in pcr_plate.wells()],
        new_tip='never'
    )
    left_pipette.drop_tip()

    # Additional steps can be added as required
