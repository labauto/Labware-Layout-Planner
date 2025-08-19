from opentrons import protocol_api

metadata = {
    'protocolName': 'QPCR Sample Preparation',
    'author': 'Your Name',
    'description': 'Automated QPCR sample preparation for QuantStudio 6 Pro',
    'apiLevel': '2.9'
}

def run(protocol: protocol_api.ProtocolContext):
    # Labware setup
    # Load tip racks
    tiprack_20 = protocol.load_labware('opentrons_96_tiprack_20ul', '6')
    tiprack_300 = protocol.load_labware('opentrons_96_tiprack_300ul', '9')

    # Load pipettes
    p20 = protocol.load_instrument('p20_single_gen2', 'left', tip_racks=[tiprack_20])
    p300 = protocol.load_instrument('p300_single_gen2', 'right', tip_racks=[tiprack_300])

    # Load other labware

    # PCR MIX source in 15 mL tube on a tube rack
    pcr_mix_tube_rack = protocol.load_labware('opentrons_15_tuberack_falcon_15ml_conical', '5')
    pcr_mix = pcr_mix_tube_rack.wells_by_name()['A1']

    # Sample DNA and water in 1.5 mL tubes
    sample_tube_rack = protocol.load_labware('opentrons_24_tuberack_eppendorf_1.5ml_safelock_snapcap', '1')
    sample_dna = sample_tube_rack.wells_by_name()['A1']
    water = sample_tube_rack.wells_by_name()['A2']

    # Primer tubes in tube racks
    primer_tube_rack_F = protocol.load_labware('opentrons_24_tuberack_generic_2ml_screwcap', '3')
    primer_tube_rack_R = protocol.load_labware('opentrons_24_tuberack_generic_2ml_screwcap', '4')

    # Plate for mixing PCR MIX and primers
    mix_plate = protocol.load_labware('corning_96_wellplate_360ul_flat', '8')

    # 96-well PCR plate for final reactions
    pcr_plate = protocol.load_labware('biorad_96_wellplate_200ul_pcr', '7')

    # Protocol steps

    # Step 1: Dispense 137.6 μL of PCR MIX into 13 wells in mix_plate
    for i in range(13):
        dest_well = mix_plate.wells()[i]
        p300.transfer(137.6, pcr_mix.bottom(z=2), dest_well.bottom(z=2))

    # Steps 2 and 3: Add 3.2 μL of each primer_F and primer_R to the PCR MIX wells
    for i in range(13):
        mix_well = mix_plate.wells()[i]
        primer_f_well = primer_tube_rack_F.wells()[i]
        primer_r_well = primer_tube_rack_R.wells()[i]

        p20.transfer(3.2, primer_f_well.bottom(z=1), mix_well.bottom(z=1), mix_after=(3, 10))
        p20.transfer(3.2, primer_r_well.bottom(z=1), mix_well.bottom(z=1), mix_after=(3, 10))

    # Step 4: Mix PCR MIX and primers by pipetting (mix_after takes care of mixing)

    # Step 5: Dispense 86 μL of PCR MIX for template-only into a separate well
    template_only_mix_well = mix_plate.wells()[13]
    p300.transfer(86, pcr_mix.bottom(z=2), template_only_mix_well.bottom(z=2))

    # Step 6: Add 4 μL water to the template-only PCR MIX
    p20.transfer(4, water.bottom(z=1), template_only_mix_well.bottom(z=1), mix_after=(3, 10))

    # Step 7: Mix PCR MIX and water by pipetting (mix_after takes care of mixing)

    # Step 8: Apply 5 μL of sample DNA or water to the reaction plate
    # Prepare well lists for samples, NTCs, and template-only controls
    sample_wells = []
    ntc_wells = []
    template_only_wells = []
    well_index = 0
    for primer_num in range(13):
        for replicate in range(3):
            sample_wells.append(pcr_plate.wells()[well_index])
            well_index += 1
            ntc_wells.append(pcr_plate.wells()[well_index])
            well_index += 1
    for replicate in range(3):
        template_only_wells.append(pcr_plate.wells()[well_index])
        well_index += 1

    # Dispense 5 μL of sample DNA into sample wells
    p20.distribute(5, sample_dna.bottom(z=1), [well.bottom(z=1) for well in sample_wells], new_tip='always')

    # Dispense 5 μL of water into NTC wells
    p20.distribute(5, water.bottom(z=1), [well.bottom(z=1) for well in ntc_wells], new_tip='always')

    # Dispense 5 μL of sample DNA into template-only wells
    p20.distribute(5, sample_dna.bottom(z=1), [well.bottom(z=1) for well in template_only_wells], new_tip='always')

    # Step 9: Apply 10 μL of PCR MIX + primer mix to the reaction plate
    sample_index = 0
    ntc_index = 0
    for primer_num in range(13):
        mix_well = mix_plate.wells()[primer_num]
        # Dispense into sample wells
        sample_dest_wells = sample_wells[sample_index:sample_index+3]
        p20.distribute(10, mix_well.bottom(z=1), [well.bottom(z=1) for well in sample_dest_wells], new_tip='always')
        sample_index += 3
        # Dispense into NTC wells
        ntc_dest_wells = ntc_wells[ntc_index:ntc_index+3]
        p20.distribute(10, mix_well.bottom(z=1), [well.bottom(z=1) for well in ntc_dest_wells], new_tip='always')
        ntc_index += 3
    # Dispense into template-only wells
    p20.distribute(10, template_only_mix_well.bottom(z=1), [well.bottom(z=1) for well in template_only_wells], new_tip='always')
