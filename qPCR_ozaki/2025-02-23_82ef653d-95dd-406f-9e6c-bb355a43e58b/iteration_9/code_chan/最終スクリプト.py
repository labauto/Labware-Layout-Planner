from opentrons import protocol_api

metadata = {
    'protocolName': 'PCR Preparation',
    'author': 'Your Name',
    'description': 'Prepare PCR reaction mix and dispense into PCR plate',
    'apiLevel': '2.11'
}

def run(protocol: protocol_api.ProtocolContext):

    # Load labware
    # Assuming all tubes are placed in a single tube rack at position 1
    # and the PCR plate is at position 7 as specified.

    # Load a tube rack for the tubes at position 1
    tube_rack = protocol.load_labware('opentrons_24_tuberack_eppendorf_1.5ml_safelock_snapcap', '1')

    # Load the 96-well PCR plate at position 7
    pcr_plate = protocol.load_labware('biorad_96_wellplate_200ul_pcr', '7')

    # Load pipettes
    # Assuming we're using a P20 single-channel pipette on the right mount
    pipette = protocol.load_instrument('p20_single_gen2', 'right')

    # Define reagents in the tube rack
    sample_dna = tube_rack.wells_by_name()['A1']   # __place_1__
    water = tube_rack.wells_by_name()['A2']        # __place_2__
    primer_F = tube_rack.wells_by_name()['A3']     # __place_3__
    primer_R = tube_rack.wells_by_name()['A4']     # __place_4__
    pcr_mix = tube_rack.wells_by_name()['A5']      # __place_5__
    empty_tube = tube_rack.wells_by_name()['B1']   # __place_10__

    # Replacing __place_{i}__ with the well positions in the tube rack at position 1

    # Protocol steps
    # Step 1: Prepare the PCR reaction mix in the empty tube
    pipette.pick_up_tip()
    pipette.transfer(10, sample_dna, empty_tube, new_tip='never')  # Transfer 10 µL sample DNA
    pipette.transfer(10, primer_F, empty_tube, new_tip='never')    # Transfer 10 µL primer_F
    pipette.transfer(10, primer_R, empty_tube, new_tip='never')    # Transfer 10 µL primer_R
    pipette.transfer(20, pcr_mix, empty_tube, new_tip='never')     # Transfer 20 µL PCR MIX
    pipette.transfer(50, water, empty_tube, new_tip='never')       # Transfer 50 µL water
    pipette.mix(5, 50, empty_tube)                                 # Mix the reaction
    pipette.blow_out(empty_tube.top())
    pipette.drop_tip()

    # Step 2: Distribute the PCR reaction mix to the PCR plate
    pipette.pick_up_tip()
    pipette.transfer(10, empty_tube, pcr_plate.wells(), new_tip='never', blow_out=True)  # Dispense into PCR plate wells
    pipette.drop_tip()
