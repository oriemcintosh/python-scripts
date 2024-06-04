import os
import csv
import requests
from bs4 import BeautifulSoup


def papa_loader():
  # Get path to original CSV file with owner information
  owner_csv_path = input("Enter the file path for the source owner CSV: \n")
  
  # Get path to where the html files should be stored
  print("Enter the folder name and location for where the html files are going to be stored.")
  html_output_path = input("File path syntax, for linux, /home/user/papa_loader/html/:\n")
  
  # Open file with Property Control Numbers
  with open(owner_csv_path) as owner_csv:
    csv_reader = csv.reader(owner_csv, delimiter=',')
    next(csv_reader)
    for row in csv_reader:
      # row is a list with each column value
      parcel_number = row[5]
      
      # inside the CSV reader loop
      url = f"https://pbcpao.gov/Property/Details?parcelId={parcel_number}"
      response = requests.get(url)
      page_response = response.text
      
      # Check to see if directory for HTML file output exists, if not, create it
      if not os.path.exists(html_output_path):
          os.makedirs(html_output_path)
      
      # Create Unique Filename based on Parcel Number
      filename = f"{html_output_path}{parcel_number}.html"
      
      # Add page_response to output file
      with open(filename, 'w') as f:
          f.write(page_response)
  
  return html_output_path