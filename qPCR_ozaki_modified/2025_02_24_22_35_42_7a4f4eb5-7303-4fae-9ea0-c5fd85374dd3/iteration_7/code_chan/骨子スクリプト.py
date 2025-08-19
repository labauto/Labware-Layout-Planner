from opentrons import protocol_api

metadata = {
    'protocolName': 'QPCR Preparation on OT-2',
    'author': 'Assistant',
    'description': 'Prepare QPCR reactions with sample DNA, primers, and PCR Mix',
    'apiLevel': '2.9'
}

def run(protocol: protocol_api.ProtocolContext):
    # Set up labware
    tip_rack_300 = protocol.load_labware('opentrons_96_tiprack_300ul', '__place_1__')
    tip_rack_20 = protocol.load_labware('opentrons_96_tiprack_20ul', '__place_2__')
    
    # Load pipettes
    p300 = protocol.load_instrument('p300_single_gen2', 'left', tip_racks=[tip_rack_300])
    p20 = protocol.load_instrument('p20_single_gen2', 'right', tip_racks=[tip_rack_20])
    
    # Load PCR MIX reservoir
    pcr_mix_reservoir = protocol.load_labware('nest_12_reservoir_15ml', '__place_3__')
    
    # Load primers plate (96-well plate)
    primers_plate = protocol.load_labware('corning_96_wellplate_360ul_flat', '__place_4__')
    
    # Load mixing plate for PCR MIX + primers
    mixing_plate = protocol.load_labware('nest_96_wellplate_200ul_flat', '__place_5__')
    
    # Load reaction PCR plate
    reaction_plate = protocol.load_labware('biorad_96_wellplate_200ul_pcr', '__place_6__')
    
    # Load sample DNA and water tuberack
    sample_tuberack = protocol.load_labware('opentrons_24_tuberack_generic_2ml_screwcap', '__place_7__')
    
    # Define reagents
    PCR_MIX = pcr_mix_reservoir.wells_by_name()['A1']
    sample_DNA = sample_tuberack.wells_by_name()['A1']
    water = sample_tuberack.wells_by_name()['A2']
    
    # Define primers
    primers_F = [well for well in primers_plate.rows_by_name()['A'][:13]]
    primers_R = [well for well in primers_plate.rows_by_name()['B'][:13]]
    
    # Define mixing wells for PCR MIX + primers
    mixing_wells = mixing_plate.wells()[:13]  # First 13 wells for PCR MIX + primers
    template_only_well = mixing_plate.wells()[13]  # Next well for template-only control
    
    # Step 1: Distribute PCR MIX to mixing wells
    for well in mixing_wells:
        p300.pick_up_tip()
        p300.transfer(137.6, PCR_MIX, well, new_tip='never')
        p300.drop_tip()
    
    # Step 5: Dispense PCR MIX for template-only control
    p300.pick_up_tip()
    p300.transfer(86, PCR_MIX, template_only_well, new_tip='never')
    p300.drop_tip()
    
    # Step 2 and 3: Add primers to PCR MIX
    for i in range(13):
        p20.pick_up_tip()
        p20.transfer(3.2, primers_F[i], mixing_wells[i], new_tip='never')
        p20.transfer(3.2, primers_R[i], mixing_wells[i], new_tip='never', mix_after=(3, 10))
        p20.drop_tip()
    
    # Step 6: Add water to template-only PCR MIX
    p20.pick_up_tip()
    p20.transfer(4, water, template_only_well, new_tip='never', mix_after=(3, 10))
    p20.drop_tip()
    
    # Define reaction plate wells
    reaction_wells = reaction_plate.wells()[:81]  # First 81 wells
    
    # Step 8: Apply 5 μL of sample DNA or water to reaction plate
    for i in range(13):
        # Sample DNA wells
        sample_dna_wells = reaction_wells[i*6 : i*6 + 3]
        p20.pick_up_tip()
        for well in sample_dna_wells:
            p20.aspirate(5, sample_DNA)
            p20.dispense(5, well)
        p20.drop_tip()
        
        # NTC wells (use water)
        ntc_wells = reaction_wells[i*6 + 3 : i*6 + 6]
        p20.pick_up_tip()
        for well in ntc_wells:
            p20.aspirate(5, water)
            p20.dispense(5, well)
        p20.drop_tip()
    
    # Template-only control wells
    template_only_wells = reaction_wells[78:81]
    p20.pick_up_tip()
    for well in template_only_wells:
        p20.aspirate(5, sample_DNA)
        p20.dispense(5, well)
    p20.drop_tip()
    
    # Step 9: Apply 10 μL of PCR MIX + primers mix to reaction plate
    for i in range(13):
        # PCR MIX + primers mixture
        primer_mix = mixing_wells[i]
        # Sample DNA wells
        sample_dna_wells = reaction_wells[i*6 : i*6 + 3]
        # NTC wells
        ntc_wells = reaction_wells[i*6 + 3 : i*6 +6]
        
        # Apply to sample DNA wells
        p20.pick_up_tip()
        for well in sample_dna_wells:
            p20.aspirate(10, primer_mix)
            p20.dispense(10, well)
        p20.drop_tip()
        
        # Apply to NTC wells
        p20.pick_up_tip()
        for well in ntc_wells:
            p20.aspirate(10, primer_mix)
            p20.dispense(10, well)
        p20.drop_tip()
    
    # For template-only control wells
    # The PCR MIX is in template_only_well
    p20.pick_up_tip()
    for well in template_only_wells:
        p20.aspirate(10, template_only_well)
        p20.dispense(10, well)
    p20.drop_tip()
