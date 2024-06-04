# This Python application will take the location of an existing CSV
# file with owner information gatherd previously from https://pbcpao.gov
# An advanced search can be done based on subdivision, which could be
# the name of your community / area based on the county using their
# advanced search query https://pbcpao.gov/AdvSearch/AdvanceSearch#

from papa_csv_loader import papa_loader
from papa_csv_updater import papa_updater

# Run loader function and then updater function

try:
    html_output_path = papa_loader()
    print("HTML files have been created.\n")
except:
    print("Error running loader function.\n")
    
try:
    papa_updater(html_output_path)
    print("Updated CSV file has been created.\n")
except:
    print("Error running updater function.\n")