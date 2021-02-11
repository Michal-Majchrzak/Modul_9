import requests
import csv
import os
from flask import Flask, render_template, request


def save_csv_from_nbp():
    nbp_response = requests.get("http://api.nbp.pl/api/exchangerates/tables/C?format=json")
    nbp_data = nbp_response.json()

    data_dict = nbp_data.pop(0)
    rates = data_dict.get('rates')

    with open(os.path.join(DIR_PATH, 'rates.csv'), 'w', newline='') as csvfile:
        file_writer = csv.writer(csvfile, delimiter=";")
        file_writer.writerow(["currency", "code", "bid", "ask"])  # column names
        for rate in rates:
            file_writer.writerow(rate.values())


def get_rates_from_csv() -> dict:
    csv_file = os.path.join(DIR_PATH, 'rates.csv')
    key_names = ['name', 'bid', 'ask']
    currencies = dict()

    if not os.path.exists(csv_file):
        save_csv_from_nbp()

    with open(csv_file, newline='') as file:
        reader = csv.reader(file, delimiter=';')
        for row in reader:
            currency_name = row.pop(1)
            currencies[currency_name] = dict(zip(key_names, row))

    del currencies['code']
    return currencies


def calculate_rate_to_pln(currency: str, amount: float) -> tuple:
    rates = get_rates_from_csv()
    bid = float(rates[currency].get('bid'))
    return tuple([f'{amount} {currency} = {round(amount * bid, 2)} PLN', f'{bid:.4f}'])


def correct_entered_amount(text: str) -> float:
    accepted_chars = {'.', ','}
    # Separate from user's answer only digits and acceptable chars defined in set:accepted_chars.
    # Then replace commas to dots to help with casting to float
    semi_acceptable_answer = ''.join(char for char in text if char.isdigit() or char in accepted_chars)
    semi_acceptable_answer = semi_acceptable_answer.replace(',', '.')

    if semi_acceptable_answer != '':

        number_elements = semi_acceptable_answer.rsplit('.', maxsplit=1)
        acceptable_answer = ''

        if len(number_elements) == 1:
            acceptable_answer = ''.join(char for char in number_elements[0] if char.isdigit())
        else:
            acceptable_answer = ''.join(char for char in number_elements[0] if char.isdigit())
            acceptable_answer += '.' + number_elements[1]

        return float(acceptable_answer)
    else:
        return float(0.0)


DIR_PATH = os.path.dirname(os.path.abspath(__file__))
app = Flask(__name__)


@app.route('/', methods=['GET', 'POST'])
def exchange_calculator():
    rates = get_rates_from_csv()

    if request.method == 'POST':
        data = request.form
        currency = data.get('currency')
        amount = correct_entered_amount(data.get('amount'))

        result, used_rate = calculate_rate_to_pln(currency, amount)

        return render_template('exchange.html',
                               currencies=rates.keys(),
                               result=result,
                               used_rate=used_rate,
                               last_currency=currency,
                               last_amount=amount)

    return render_template("exchange.html", currencies=rates.keys())


if __name__ == "__main__":
    app.run(debug=True)
