from opentrons import protocol_api

metadata = {
    'protocolName': 'qPCR Preparation for QuantStudio 6 Pro',
    'author': 'Your Name',
    'description': 'Preparation of qPCR reactions using sample DNA and primers',
    'apiLevel': '2.9'  # Specify the API level
}

def run(protocol: protocol_api.ProtocolContext):
    # Load labware
    tiprack_p300 = protocol.load_labware('opentrons_96_tiprack_300ul', '6')
    tiprack_p20 = protocol.load_labware('opentrons_96_tiprack_20ul', '9')
    tiprack_p20_2 = protocol.load_labware('opentrons_96_tiprack_20ul', '11')

    reaction_plate = protocol.load_labware('biorad_96_wellplate_200ul_pcr', '7')

    tuberack_15ml = protocol.load_labware('opentrons_15_tuberack_falcon_15ml_conical', '5')

    primer_plate = protocol.load_labware('corning_96_wellplate_360ul_flat', '8')

    tuberack_samples = protocol.load_labware('opentrons_24_tuberack_nest_1.5ml_snapcap', '1')

    mix_plate = protocol.load_labware('nest_96_wellplate_2ml_deep', '10')

    # Load pipettes
    p300 = protocol.load_instrument('p300_single', mount='left', tip_racks=[tiprack_p300])
    p20 = protocol.load_instrument('p20_single_gen2', mount='right', tip_racks=[tiprack_p20, tiprack_p20_2])

    # Reagents
    pcr_mix = tuberack_15ml.wells_by_name()['A1']
    sample_dna = tuberack_samples.wells_by_name()['A1']
    water = tuberack_samples.wells_by_name()['B1']

    # Assign primer wells
    primer_F_wells = primer_plate.wells()[0:13]  # Primer_F1 to Primer_F13
    primer_R_wells = primer_plate.wells()[13:26]  # Primer_R1 to Primer_R13

    # Assign wells for PCR Mix + primers
    pcr_mix_primer_wells = mix_plate.wells()[0:13]  # For mixes with primers

    # Template control well
    template_control_well = mix_plate.wells()[13]

    # Step 1: Dispense 137.6 μL of PCR MIX into 13 wells
    p300.pick_up_tip()
    for dest_well in pcr_mix_primer_wells:
        p300.transfer(137.6, pcr_mix, dest_well, new_tip='never')
    p300.drop_tip()

    # Step 2-4: Add primers and mix
    for i in range(13):
        p20.pick_up_tip()
        # Add primer_F
        p20.transfer(3.2, primer_F_wells[i], pcr_mix_primer_wells[i], new_tip='never')
        # Add primer_R
        p20.transfer(3.2, primer_R_wells[i], pcr_mix_primer_wells[i], new_tip='never')
        # Mix
        p20.mix(5, 20, pcr_mix_primer_wells[i])
        p20.blow_out(pcr_mix_primer_wells[i].top())
        p20.drop_tip()

    # Steps 5-7: Prepare template only control mix
    p300.pick_up_tip()
    p300.transfer(86, pcr_mix, template_control_well, new_tip='never')
    p300.drop_tip()

    p20.pick_up_tip()
    p20.transfer(4, water, template_control_well, new_tip='never')
    p20.mix(5, 20, template_control_well)
    p20.blow_out(template_control_well.top())
    p20.drop_tip()

    # Step 8: Apply 5 μL of sample DNA or water to reaction plate wells
    # Prepare lists of destination wells
    sample_dna_primer_wells = reaction_plate.wells()[0:39]  # 13 primers x 3 replicates
    ntc_primer_wells = reaction_plate.wells()[39:78]  # NTC wells
    template_only_wells = reaction_plate.wells()[78:81]  # Template only control wells

    # Distribute sample DNA
    dna_wells = sample_dna_primer_wells + template_only_wells
    p20.pick_up_tip()
    p20.distribute(5, sample_dna, dna_wells, new_tip='never')
    p20.drop_tip()

    # Distribute water (NTC)
    p20.pick_up_tip()
    p20.distribute(5, water, ntc_primer_wells, new_tip='never')
    p20.drop_tip()

    # Step 9: Apply 10 μL of PCR MIX + primer mix into reaction plate wells
    # For sample DNA + primer reactions
    for i in range(13):
        dest_wells = sample_dna_primer_wells[i*3 : (i+1)*3]
        p20.pick_up_tip()
        p20.distribute(10, pcr_mix_primer_wells[i], dest_wells, new_tip='never')
        p20.drop_tip()

    # For NTC + primer reactions
    for i in range(13):
        dest_wells = ntc_primer_wells[i*3 : (i+1)*3]
        p20.pick_up_tip()
        p20.distribute(10, pcr_mix_primer_wells[i], dest_wells, new_tip='never')
        p20.drop_tip()

    # For template only wells
    p20.pick_up_tip()
    p20.distribute(10, template_control_well, template_only_wells, new_tip='never')
    p20.drop_tip()
