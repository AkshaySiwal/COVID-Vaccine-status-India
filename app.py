import requests
import datetime
from flask import Flask, render_template, request

app = Flask(__name__)

@app.route("/", methods = ["GET", "POST"])
def index():
    all_centers = {}
    if request.method == 'POST':
        days = request.form.get('days')
        if not days:
            days = 1
        else:
            days = int(days)
            rem = days % 7
            div = days // 7
            if rem > 0:
                days = div + 1
            else:
                days = div
        pin = str(request.form['pin'])
        if 'zerovaccine' in request.form:
            include_zero_vaccine = True
        else:
            include_zero_vaccine = False
        for i in range( days):
            date = (datetime.datetime.today() +  datetime.timedelta(days=i * 7 )).strftime('%d-%m-%Y')
            centers = details(date=date, pin=pin, include_zero_vaccine=include_zero_vaccine)
            all_centers.update(centers)
    all_centers = sorted(all_centers.items())
    return render_template('index.html', all_centers=all_centers)

@app.route("/notification")
def notification():
    return "WIlL ADD THIS FEATURE SOON"

def details(date, pin, include_zero_vaccine):
    base_url = 'https://cdn-api.co-vin.in/api/v2/appointment/sessions/public/calendarByPin?pincode=%s&date=%s' % (pin, date)
    response = requests.get(base_url)
    centers = {}
    for i in response.json().get('centers', []):
        for s in i.get('sessions', []):
            date = s['date']
            key = int(''.join(date.split('-')[::-1]))
            available = s.get('available_capacity', 0)
            if not include_zero_vaccine:
                if available > 0:
                    record = {'date' : date, 'center_id': i['center_id'], 'name': i['name'], 'address' : i['address'] + ', ' + i['block_name'] + ', ' + i['district_name'] + ', ' + i['state_name'] + ', ' + str(i['pincode']), 'vaccine': s['vaccine'], 'min_age_limit' : s['min_age_limit'], 'available_capacity': s['available_capacity'], 'fee_type' : i['fee_type']}
            else:
                record = {'date' : date, 'center_id': i['center_id'], 'name': i['name'], 'address' : i['address'] + ', ' + i['block_name'] + ', ' + i['district_name'] + ', ' + i['state_name'] + ', ' + str(i['pincode']), 'vaccine': s['vaccine'], 'min_age_limit' : s['min_age_limit'], 'available_capacity': s['available_capacity'], 'fee_type' : i['fee_type']}
            if record:
                if key in centers:
                    centers[key].append(record)
                else:
                    centers[key] = [record]
    return centers


if __name__ == '__main__':
    app.run()
