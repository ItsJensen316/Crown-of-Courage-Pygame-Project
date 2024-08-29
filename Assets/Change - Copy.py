import os

# Define your dictionary
rename_dict = {
    '211': '101',
    '212': '102',
    '213': '103',   #Ladder
    '204':'131',
    '205':'132',
    '206':'133',
    '207':'134',    #Door
    '224': '141',
    '225': '142',
    '226': '143',
    '227': '144',
    '228': '145',
    '229': '146',
    '230': '147',
    '231': '148',
    '232': '149',
    '233': '150',
    '234': '151',
    '235': '152',
    '236': '153',
    '237': '154',
    '238': '155',
    '239': '156',
    '240': '157',
    '241': '158',
    '242': '159',
    '243': '160',
    '244': '161',
    '245': '162',
    '246': '163',
    '247': '164',
    '248': '165',   #Lift
    '198':'171',
    '199':'172',
    '202':'173',
    '203':'174',
    '267':'175',    #Box
    '250':'181',
    '254':'182',
    '255':'183',
    '268':'184',    #Inventory
    '200':'300',
    '201':'301',
    '208': '302',
    '209': '303',
    '210': '304',
##    '211': '305',
##    '212': '306',
##    '213': '307',
    '214': '308',
    '215': '309',
    '216': '310',
    '217': '311',
    '218': '312',
    '219': '313',
    '220': '314',
    '221': '315',
    '222': '316',
    '223': '317',
    '249': '318',
    '251': '319',
    '252': '320',
    '253': '321',
    '256': '322',
    '257': '323',
    '258': '324',
    '259': '325',
    '260': '326',
    '261': '327',
    '262': '328',
    '263': '329',
    '264': '330',
    '265': '331',
    '266': '332',
}

# Directory where your files are located
directory = 'J:/Pygame Project/Assets/1-2/Extras'

# Iterate over files in the directory
for filename in os.listdir(directory):
    if filename.startswith('tile'):
        # Extract the numeric part of the filename (e.g., '20' or '90')
        numeric_part = filename.split('e')[1].split('.')[0]
        
        # Check if the numeric part is in the dictionary
        if numeric_part in rename_dict:
            # Rename the file by replacing the numeric part with the dictionary value
            new_filename = filename.replace(numeric_part,'_'+rename_dict[numeric_part])
            os.rename(os.path.join(directory, filename), os.path.join(directory, new_filename))
