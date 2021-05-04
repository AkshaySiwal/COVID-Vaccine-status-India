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
        group = request.form.get('group')
        if group.lower() == 'age 18-44':
            age = 18
        elif group.lower() == 'age 45+':
            age = 45
        else:
            age = 0
        for i in range( days):
            date = (datetime.datetime.today() +  datetime.timedelta(days=i * 7 )).strftime('%d-%m-%Y')
            centers = details(date=date, pin=pin, include_zero_vaccine=include_zero_vaccine, age=age)
            all_centers.update(centers)
    all_centers = sorted(all_centers.items())
    return render_template('index.html', all_centers=all_centers)

@app.route("/notification")
def notification():
    return "WIlL ADD THIS FEATURE SOON"

def details(date, pin, include_zero_vaccine, age):
    base_url = 'https://cdn-api.co-vin.in/api/v2/appointment/sessions/public/calendarByPin?pincode=%s&date=%s' % (pin, date)
    response = requests.get(base_url)
    print(response.url)
    print(response.status_code)
    print(response.json())
    centers = {}
    for i in response.json().get('centers', []):
        for s in i.get('sessions', []):
            date = s['date']
            key = int(''.join(date.split('-')[::-1]))
            available = s.get('available_capacity', 0)
            age_limit = s.get('min_age_limit', 0)
            age_keep = False
            zero_keep = False
            if age == 18:
                if 18 <= age_limit < 45:
                    age_keep = True
                else:
                    age_keep = False
            elif age == 45:
                if age_limit >= 45:
                    age_keep = True
                else:
                    age_keep = False
            else:
                age_keep = True

            if not include_zero_vaccine:
                if available > 0:
                    zero_keep = True
                else:
                    zero_keep = False
            else:
                zero_keep = True

            if age_keep and zero_keep:
                record = {'date' : date, 'center_id': i['center_id'], 'name': i['name'], 'address' : i['address'] + ', ' + i['block_name'] + ', ' + i['district_name'] + ', ' + i['state_name'] + ', ' + str(i['pincode']), 'vaccine': s['vaccine'], 'min_age_limit' : s['min_age_limit'], 'available_capacity': s['available_capacity'], 'fee_type' : i['fee_type']}
                if key in centers:
                    centers[key].append(record)
                else:
                    centers[key] = [record]
    return centers


if __name__ == '__main__':
    app.run()
