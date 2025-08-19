from opentrons import protocol_api

metadata = {
    'protocolName': 'PCR Preparation',
    'author': 'Your Name',
    'description': 'Prepare PCR reactions using PCR MIX, primers, and samples',
    'apiLevel': '2.13'  # Use the appropriate API level
}

def run(protocol: protocol_api.ProtocolContext):

    # Load tip racks
    tip_rack_10ul = protocol.load_labware('opentrons_96_filtertiprack_10ul', '11')
    tip_rack_200ul = protocol.load_labware('opentrons_96_filtertiprack_200ul', '10')

    # Load labware at specified positions
    pcr_mix_tube_rack = protocol.load_labware('opentrons_24_aluminumblock_generic_2ml_screwcap', '1')  # __place_1__ replaced with '1'
    primer_F_tube_rack = protocol.load_labware('opentrons_24_aluminumblock_generic_2ml_screwcap', '2')  # __place_2__ replaced with '2'
    primer_R_tube_rack = protocol.load_labware('opentrons_24_aluminumblock_generic_2ml_screwcap', '3')  # __place_3__ replaced with '3'
    sample_plate = protocol.load_labware('biorad_96_wellplate_200ul_pcr', '5')  # __place_5__ replaced with '5'
    pcr_plate = protocol.load_labware('biorad_96_wellplate_200ul_pcr', '6')     # __place_6__ replaced with '6'

    # Load pipettes
    p10_single = protocol.load_instrument('p10_single', 'left', tip_racks=[tip_rack_10ul])
    p300_single = protocol.load_instrument('p300_single', 'right', tip_racks=[tip_rack_200ul])

    # Define reagents and samples
    pcr_mix = pcr_mix_tube_rack.wells_by_name()['A1']      # PCR MIX tube located in A1 of tube rack at position 1
    primer_F = primer_F_tube_rack.wells_by_name()['A1']    # Primer_F tube located in A1 of tube rack at position 2
    primer_R = primer_R_tube_rack.wells_by_name()['A1']    # Primer_R tube located in A1 of tube rack at position 3

    # Assuming samples are in row A of sample plate at position 5
    samples = sample_plate.rows_by_name()['A'][:8]         # Modify indices as per actual sample locations

    # Destination wells in PCR plate at position 6
    destination_wells = pcr_plate.rows_by_name()['A'][:8]  # Modify indices as per required destinations

    # Prepare master mix tube (assuming an empty tube in B1 of the PCR MIX tube rack)
    master_mix_tube = pcr_mix_tube_rack.wells_by_name()['B1']

    # Calculate total volume needed for master mix including excess
    num_reactions = len(destination_wells)
    master_mix_volume_per_reaction = 10  # μL of PCR MIX and primer mixture per reaction
    total_master_mix_volume = master_mix_volume_per_reaction * num_reactions * 1.1  # Include 10% excess

    # Transfer PCR MIX to master mix tube
    p300_single.pick_up_tip()
    p300_single.transfer(
        221,  # μL of PCR MIX
        pcr_mix,
        master_mix_tube,
        new_tip='never'
    )

    # Transfer Primer_F to master mix tube
    p300_single.transfer(
        19.5,  # μL of Primer_F
        primer_F,
        master_mix_tube,
        new_tip='never'
    )

    # Transfer Primer_R to master mix tube
    p300_single.transfer(
        19.5,  # μL of Primer_R
        primer_R,
        master_mix_tube,
        new_tip='never'
    )

    # Mix the master mix
    p300_single.mix(10, 200, master_mix_tube)
    p300_single.blow_out(master_mix_tube.top())
    p300_single.drop_tip()

    # Distribute master mix to PCR plate wells
    p10_single.distribute(
        master_mix_volume_per_reaction,
        master_mix_tube,
        [well for well in destination_wells],
        new_tip='always',
        blow_out=True
    )

    # Add samples or water to PCR plate wells
    for sample, dest in zip(samples, destination_wells):
        p10_single.pick_up_tip()
        p10_single.transfer(
            5,        # μL of sample DNA or water
            sample,
            dest,
            new_tip='never',
            mix_after=(3, 10)
        )
        p10_single.blow_out(dest.top())
        p10_single.drop_tip()
