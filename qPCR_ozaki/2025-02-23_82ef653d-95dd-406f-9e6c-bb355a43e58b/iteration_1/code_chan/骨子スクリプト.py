from opentrons import protocol_api

metadata = {
    'protocolName': 'QPCR Sample Preparation for QuantStudio 6 Pro',
    'author': 'Your Name',
    'description': 'Automated preparation of qPCR samples including sample DNA, primers, and PCR mix.',
    'apiLevel': '2.9'  # Adjust to your Opentrons API level
}

def run(protocol: protocol_api.ProtocolContext):

    # Labware Setup
    # Tip racks
    tiprack_300 = protocol.load_labware('opentrons_96_tiprack_300ul', '__place_1__')
    tiprack_20 = protocol.load_labware('opentrons_96_tiprack_20ul', '__place_2__')

    # PCR plate for reactions
    pcr_plate = protocol.load_labware('biorad_96_wellplate_200ul_pcr', '__place_3__')

    # Reagent tube racks
    reagent_tuberack = protocol.load_labware('opentrons_24_tuberack_generic_2ml_screwcap', '__place_4__')
    mixture_tuberack = protocol.load_labware('opentrons_24_tuberack_generic_2ml_screwcap', '__place_5__')

    # Pipettes
    p300 = protocol.load_instrument('p300_single', mount='right', tip_racks=[tiprack_300])
    p20 = protocol.load_instrument('p20_single', mount='left', tip_racks=[tiprack_20])

    # Reagents
    sample_dna = reagent_tuberack.wells_by_name()['A1']
    water = reagent_tuberack.wells_by_name()['A2']
    pcr_mix = reagent_tuberack.wells_by_name()['A3']

    # Primers F1-F13 in wells B1-B13
    primers_F = [reagent_tuberack.wells_by_name()['B' + str(i+1)] for i in range(13)]
    # Primers R1-R13 in wells C1-C13
    primers_R = [reagent_tuberack.wells_by_name()['C' + str(i+1)] for i in range(13)]

    # Mixture tubes: D1-D13 for PCR MIX + Primers, D14 for template-only mixture
    mixture_tubes = [mixture_tuberack.wells_by_name()['D' + str(i+1)] for i in range(13)]
    template_only_mixture = mixture_tuberack.wells_by_name()['D14']

    # Protocol steps

    # Step 1: Dispense 137.6 μL of PCR MIX into 13 tubes
    p300.pick_up_tip()
    for tube in mixture_tubes:
        p300.transfer(137.6, pcr_mix, tube, new_tip='never')
    p300.drop_tip()

    # Step 2 and 3: Add 3.2 μL of primer_F and primer_R to each tube
    for i in range(13):
        p20.pick_up_tip()
        p20.transfer(3.2, primers_F[i], mixture_tubes[i], new_tip='never')
        p20.transfer(3.2, primers_R[i], mixture_tubes[i], new_tip='never')
        p20.mix(5, 20, mixture_tubes[i])
        p20.drop_tip()

    # Step 5: Dispense 86 μL of PCR MIX into 'template-only' mixture tube
    p300.pick_up_tip()
    p300.transfer(86, pcr_mix, template_only_mixture, new_tip='never')
    p300.drop_tip()

    # Step 6: Add 4 μL of water to 'template-only' mixture
    p20.pick_up_tip()
    p20.transfer(4, water, template_only_mixture, mix_after=(5, 20), new_tip='never')
    p20.drop_tip()

    # Step 8: Apply 5 μL of sample DNA or water to reaction plate wells
    # Prepare plate map
    sample_wells = []
    ntc_wells = []
    template_only_wells = []

    # Generate well lists
    # Sample wells: A1-A39 (13 primers x 3 replicates)
    sample_well_names = ['A' + str(i+1) for i in range(39)]
    sample_wells = [pcr_plate.wells_by_name()[well_name] for well_name in sample_well_names]

    # NTC wells: B1-B39
    ntc_well_names = ['B' + str(i+1) for i in range(39)]
    ntc_wells = [pcr_plate.wells_by_name()[well_name] for well_name in ntc_well_names]

    # Template only wells: C1-C3
    template_only_well_names = ['C' + str(i+1) for i in range(3)]
    template_only_wells = [pcr_plate.wells_by_name()[well_name] for well_name in template_only_well_names]

    # Dispense 5 μL of sample DNA into sample wells
    for well in sample_wells:
        p20.pick_up_tip()
        p20.transfer(5, sample_dna, well, new_tip='never')
        p20.drop_tip()

    # Dispense 5 μL of water into NTC wells
    for well in ntc_wells:
        p20.pick_up_tip()
        p20.transfer(5, water, well, new_tip='never')
        p20.drop_tip()

    # Dispense 5 μL of sample DNA into template only wells
    for well in template_only_wells:
        p20.pick_up_tip()
        p20.transfer(5, sample_dna, well, new_tip='never')
        p20.drop_tip()

    # Step 9: Apply 10 μL of PCR MIX and primer mixture to reaction plate wells
    # For sample wells
    for i in range(13):  # For each primer mixture
        mixture = mixture_tubes[i]
        for j in range(3):  # Triplicates
            index = i * 3 + j
            sample_well = sample_wells[index]
            p20.pick_up_tip()
            p20.transfer(10, mixture, sample_well, new_tip='never')
            p20.drop_tip()
    # For NTC wells
    for i in range(13):
        mixture = mixture_tubes[i]
        for j in range(3):
            index = i * 3 + j
            ntc_well = ntc_wells[index]
            p20.pick_up_tip()
            p20.transfer(10, mixture, ntc_well, new_tip='never')
            p20.drop_tip()
    # For template only wells
    for well in template_only_wells:
        p20.pick_up_tip()
        p20.transfer(10, template_only_mixture, well, new_tip='never')
        p20.drop_tip()
