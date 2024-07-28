from print_tricks import pt

import requests
import json

def convert_spreadsheet_to_json(url, sheet_name):

    sheet_id = url.split('/d/')[1].split('/')[0]

    export_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet={sheet_name}"

    response = requests.get(export_url)

    if response.status_code != 200:

        raise Exception(f"Error fetching data: {response.status_code} - {response.text}")

    data = response.text.splitlines()

    pt(data, response)

    categories = {}

    for row in data[1:]:

        row = row.split(',')

        category, space, cell_group, cell = row[0], row[1], row[2], row[3]

        if category not in categories:

            categories[category] = {}

        if space not in categories[category]:

            categories[category][space] = {}

        if cell_group not in categories[category][space]:

            categories[category][space][cell_group] = []

        if cell:

            categories[category][space][cell_group].append(json.loads(cell))

    return json.dumps(categories, indent=4)



# Example usage


url = "https://docs.google.com/spreadsheets/d/1BIcuDhuk46e-CAy4yxcHxNVSZ3YkRYSAeznutxZ3eyc/edit?gid=19839303#gid=19839303"

sheet_name = "Cleaning Calc"

json_data = convert_spreadsheet_to_json(url, sheet_name)

print(json_data)