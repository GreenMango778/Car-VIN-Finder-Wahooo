# This one does the same as its predecessor but instead utilises an excel sheet with licence plates to bulk load. Same captcha issues as prior.

import pandas as pd
import requests
from bs4 import BeautifulSoup

data = []

user_name = input("Please enter your name: ")

df = pd.read_excel("license_plates.xlsx")

for plate_number in df["Plate Number"]:
    url = f"https://thatcar.nz/c/{plate_number}"
    try:
        response = requests.get(url)
        if response.status_code != 200:
            print("Error: Website returned status code", response.status_code)
            continue
        soup = BeautifulSoup(response.text, "html.parser")
        car_table = soup.find("table", class_="table")
        if car_table is None:
            print("Error: Table not found")
            continue
        car_data = {}
        for row in car_table.find_all("tr"):
            cells = row.find_all("td")
            if len(cells) != 2:
                continue
            property_name = cells[0].get_text(strip=True)
            value = cells[1].get_text(strip=True)
            car_data[property_name] = value

        safety_rating = soup.find("div", {"class": "star-rating safety"})
        if safety_rating is not None:
            rating = safety_rating['title']
            car_data['Safety Rating'] = rating
        else:
            car_data['Safety Rating'] = "N/A"

        print(car_data['VIN'])
        print(car_data['Safety Rating'])
        data.append({'User': user_name, 'Plate Number': plate_number, 'VIN': car_data['VIN'], 'Safety Rating': car_data['Safety Rating']})
        print("Car Loaded")
    except Exception as e:
        print("Error: ", e)

df = pd.DataFrame(data, columns=['User','Plate Number', 'VIN','Safety Rating'])

# create a writer object and use it to create a new workbook
writer = pd.ExcelWriter('vehicle_data.xlsx', engine='xlsxwriter')
df.to_excel(writer, index=False, columns=['User','Plate Number', 'VIN','Safety Rating'])

# get the xlsxwriter workbook and worksheet objects
workbook = writer.book
worksheet = writer.sheets['Sheet1']

# define the format of the column headers
header_format = workbook.add_format({
        'bold': False,
        'align': 'left',
        'valign': 'top'
})

# set the format of the column headers
for col_num, value in enumerate(df.columns.values):
        worksheet.write(0, col_num, value, header_format)

writer.save()
print("Data saved to excel sheet successfully.")
