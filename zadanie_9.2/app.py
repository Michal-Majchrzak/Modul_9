import requests
import csv

nbp_response = requests.get("http://api.nbp.pl/api/exchangerates/tables/C?format=json")
nbp_data = nbp_response.json()

data_dict = nbp_data.pop(0)
rates = data_dict.get('rates')

with open('rates.csv', 'w', newline='') as csvfile:
    file_writer = csv.writer(csvfile, delimiter=";")
    file_writer.writerow(["currency", "code", "bid", "ask"])
    for rate in rates:
        file_writer.writerow(rate.values())
