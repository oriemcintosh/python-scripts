import os
import csv
from bs4 import BeautifulSoup


def format_owner_names(owner_names):
    """
    Function to clean up owner names to be used within new CSV file.
    """

    formatted_names = []
    for name in owner_names:
        if name == "":
            pass
        else:
            # Split the name on the space
            parts = name.split()
            
            # Add a comma after the first part
            formatted_name = parts[0] + ', ' + ' '.join(parts[1:])
            
            # Remove any ampersands
            formatted_name = formatted_name.replace('&', '')
            
            formatted_names.append(formatted_name.strip())
    
    return formatted_names


def papa_updater(html_output_path):
    """
    This function will go through html files previously created from
    the `papa_loader` function and gather the details from the html
    and create a new csv file put into a path of your choosing.
    """
    
    # Header Row List
    header_row = ['Owner(s)', 'Property Address', 'Municipality', 'Parcel Control Number', 'Subdivision', 'Sale Date', 'Legal Description']
    
    # Gather file path for updated CSV
    ("Please enter the file path where you want to place the updated CSV file.")
    csv_output_path = input("Output file syntax, for linx, /home/user/papa_udater/csv/updated_owners.csv: \n")
    
    # Check to see if directory for CSV output exists, if not, create it.
    if not os.path.exists(csv_output_path):
        directory, filename = os.path.split(csv_output_path)
        os.makedirs(directory)
    
    # Create Header for CSV File
    with open(csv_output_path, 'w') as f:
          writer = csv.writer(f)
          # Write first row with Headers
          writer.writerow(header_row)
          header_written = True
    
    
    # Loop through files in the directory
    for filename in os.listdir(html_output_path):
    
      # Check if file is HTML
      if filename.endswith('.html'):
    
        # Open and read the file
        with open(os.path.join(html_output_path, filename)) as html_page_data:
          soup = BeautifulSoup(html_page_data, 'html.parser')

          # Find the header row
          header_row = soup.find('tr', class_='table_header')

          # Find the owners from the Table with heading "Owner(s)"
          owners_index = None
          for i, th in enumerate(header_row.find_all('th')):
              if th.text.strip() == 'Owner(s)':
                  owners_index = i
                  break

          # If owners_index is None, print an error message and exit the script    
          data_rows = header_row.find_next_siblings('tr')
          for row in data_rows:
              owner_cell = row.find_all('td')[owners_index]
              try:
                  # Break down the owners / split the lines
                  owner_names = owner_cell.text.splitlines()
                  owner = format_owner_names(owner_names)
              except:
                  print("Failed to format owner names.")
          
          try:
            # Property Address Span
            property_address = soup.find('span', id='MainContent_lblLocation').string
          except AttributeError:
            property_address = 'N/A'
          
          try:
              # Municipality Span
              municipality = soup.find('span', id='MainContent_lblMunicipality').string
          except AttributeError:
              municipality = 'N/A'
          
          try:
              # Parcel Control Number Span
              parcel_control_number = soup.find('span', id='MainContent_lblPCN').string
          except AttributeError:
              parcel_control_number = 'N/A'
          
          try:
              # Subdivision
              subdivision = soup.find('span', id='MainContent_lblSubdiv').string
          except AttributeError:
              subdivision = 'N/A'
          
          try:
              # Sale Date
              sale_date = soup.find('span', id='MainContent_lblSaleDate').string
          except AttributeError:
              sale_date = 'N/A'
          
          try:
              # Legal Description
              legal_description = soup.find('span', id='MainContent_lblLegalDesc').string
          except AttributeError:
              legal_description = 'N/A'
          
        
          with open(csv_output_path, 'a') as csv_output:
              if header_written:
                try:
                    writer = csv.writer(csv_output)
                    writer.writerow([owner, property_address, municipality, parcel_control_number, subdivision, sale_date, legal_description])
                except:
                    print("Error Writing Row")