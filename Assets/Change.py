import os

# Set the directory where your files are located
directory = 'J:/Pygame Project/Assets/Level1-2'

# Get a list of files in the directory
files = os.listdir(directory)

# Sort the files in ascending order based on their filenames
files.sort()

# Define a base name for your files
base_name = 'tiles'  # Change this to your desired base name

# Initialize a counter
counter = 0

# Iterate through the files and rename them
for file in files:
    if os.path.isfile(os.path.join(directory, file)):
        # Get the file extension

        # Generate the new filename
        new_name = f'{base_name}_{counter}.png'
        new_path = os.path.join(directory, new_name)

        # Rename the file
        os.rename(os.path.join(directory, file), new_path)

        # Increment the counter
        counter += 1
