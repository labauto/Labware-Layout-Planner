from opentrons import protocol_api

metadata = {
    'protocolName': 'QPCR Sample Preparation for QuantStudio 6 Pro',
    'author': 'Your Name',
    'description': 'Prepare samples for QPCR with primers and controls',
    'apiLevel': '2.9'  # Specify the API level for this code
}

def run(protocol: protocol_api.ProtocolContext):
    # Set up labware

    # Tip racks
    p20_tip_rack = protocol.load_labware('opentrons_96_tiprack_20ul', '9')
    p300_tip_rack = protocol.load_labware('opentrons_96_tiprack_300ul', '11')

    # Tube rack for samples (sample DNA and water)
    tube_rack_samples = protocol.load_labware('opentrons_24_tuberack_eppendorf_1.5ml_safelock_snapcap', '1')
    sample_dna = tube_rack_samples.wells_by_name()['A1']
    water = tube_rack_samples.wells_by_name()['A2']

    # Tube rack for primers
    tube_rack_primers = protocol.load_labware('opentrons_24_tuberack_eppendorf_1.5ml_safelock_snapcap', '3')
    primer_forward_tube = tube_rack_primers.wells_by_name()['A1']  # Primer_F
    primer_reverse_tube = tube_rack_primers.wells_by_name()['A2']  # Primer_R

    # Tube rack for 15 mL tubes (PCR MIX)
    tube_rack_15ml = protocol.load_labware('opentrons_15_tuberack_falcon_15ml_conical', '6')
    pcr_mix_tube = tube_rack_15ml.wells_by_name()['A1']  # PCR MIX stock

    # Tube rack for 1.5 mL tubes (PCR MIX aliquots)
    tube_rack_1_5ml = protocol.load_labware('opentrons_24_tuberack_eppendorf_1.5ml_safelock_snapcap', '5')
    pcr_mix_aliquot_tube = tube_rack_1_5ml.wells_by_name()['A1']  # Tube for PCR MIX + primers
    pcr_mix_template_only_tube = tube_rack_1_5ml.wells_by_name()['A2']  # Tube for PCR MIX template only (no primers)

    # 96 well PCR plate for reaction setup
    pcr_plate = protocol.load_labware('corning_96_wellplate_360ul_flat', '8')

    # Pipettes
    p20 = protocol.load_instrument('p20_single_gen2', 'left', tip_racks=[p20_tip_rack])
    p300 = protocol.load_instrument('p300_single_gen2', 'right', tip_racks=[p300_tip_rack])

    # Step 1: Aliquot PCR MIX into aliquot tube (137.6 μL)
    p300.pick_up_tip()
    p300.transfer(137.6, pcr_mix_tube, pcr_mix_aliquot_tube, new_tip='never')
    p300.mix(5, 100, pcr_mix_aliquot_tube)
    p300.drop_tip()

    # Step 2 & 3: Add 3.2 μL of primer_F and primer_R to PCR MIX tube
    p20.pick_up_tip()
    p20.transfer(3.2, primer_forward_tube, pcr_mix_aliquot_tube, new_tip='never')
    p20.drop_tip()

    p20.pick_up_tip()
    p20.transfer(3.2, primer_reverse_tube, pcr_mix_aliquot_tube, new_tip='never')
    p20.drop_tip()

    # Step 4: Mix PCR MIX and primers by pipetting
    p300.pick_up_tip()
    p300.mix(5, 100, pcr_mix_aliquot_tube)
    p300.drop_tip()

    # Step 5: Aliquot 86 μL of PCR MIX for template only (no primers)
    p300.pick_up_tip()
    p300.transfer(86, pcr_mix_tube, pcr_mix_template_only_tube, new_tip='never')
    p300.drop_tip()

    # Step 6: Add 4 μL of water to PCR MIX for template only
    p20.pick_up_tip()
    p20.transfer(4, water, pcr_mix_template_only_tube, new_tip='never')
    p20.drop_tip()

    # Step 7: Mix PCR MIX and water by pipetting
    p300.pick_up_tip()
    p300.mix(5, 80, pcr_mix_template_only_tube)
    p300.drop_tip()

    # Prepare lists of destination wells
    sample_wells = [pcr_plate.wells_by_name()[well_name] for well_name in ['A1', 'B1', 'C1']]
    ntc_wells = [pcr_plate.wells_by_name()[well_name] for well_name in ['D1', 'E1', 'F1']]
    template_only_wells = [pcr_plate.wells_by_name()[well_name] for well_name in ['G1', 'H1', 'A2']]

    # Step 8: Apply 5 μL of sample DNA or water to reaction plate
    # Apply sample DNA to sample wells
    for well in sample_wells:
        p20.pick_up_tip()
        p20.transfer(5, sample_dna, well, new_tip='never')
        p20.drop_tip()
    # Apply water to NTC wells
    for well in ntc_wells:
        p20.pick_up_tip()
        p20.transfer(5, water, well, new_tip='never')
        p20.drop_tip()
    # Apply sample DNA to template only wells
    for well in template_only_wells:
        p20.pick_up_tip()
        p20.transfer(5, sample_dna, well, new_tip='never')
        p20.drop_tip()

    # Step 9: Apply PCR MIX with primers to reaction plate (10 μL each)
    p20.pick_up_tip()
    for well in sample_wells + ntc_wells:
        p20.transfer(10, pcr_mix_aliquot_tube, well, new_tip='never')
    p20.drop_tip()
    # Apply PCR MIX (template only) to template only wells
    p20.pick_up_tip()
    for well in template_only_wells:
        p20.transfer(10, pcr_mix_template_only_tube, well, new_tip='never')
    p20.drop_tip()
