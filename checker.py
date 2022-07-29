import requests
import datetime
import calendar
import json
from fake_useragent import UserAgent
from dateutil import rrule
import re
import argparse


def lambda_handler(event, context=None):
    def date_maker(date, start_of_month=False):
        date = date.split('-')
        counter = 0
        for i in date:
            i = re.sub('^0', '', i)
            date[counter] = i
            counter += 1
        if start_of_month == True:
            date = datetime.date(int(date[0]), int(date[1]), 1)
        else:
            date = datetime.date(int(date[0]), int(date[1]), int(date[2]))
        return date

    def format_months(months):
        counter = 0
        for i in months:
            months[counter] = datetime.date(i.year, i.month, i.day)
            counter += 1

    def get_permit_entrance_id():
        entrance_url = 'https://ridb.recreation.gov/api/v1/facilities/233262/permitentrances'
        payload = {'query': permit_entrance}
        headers = {'apikey': api_key}
        results = requests.get(entrance_url, headers=headers, params=payload)
        results = json.loads(results.text)
        permit_entrance_id = (results['RECDATA'][0]['PermitEntranceID'])
        return permit_entrance_id

    def get_availability():
        ua = UserAgent()
        availability_list = []
        for i in url_list:
            availability_url = i
            headers = {'apikey': api_key, "user-agent": ua.random}
            availability = requests.get(availability_url, headers=headers)
            availability = json.loads(availability.text)
            availability_list.append(availability)
        return availability_list

    def check_availability(availability_list, permit_entrance_id, start_date, end_date):
        count = 0
        for month in availability_list:
            for key1, value1 in month.items():
                for key2, value2 in value1.items():
                    temp_date = date_maker((key2))
                    if start_date <= temp_date <= end_date:
                        for key3, value3 in value2.items():
                            if key3 == permit_entrance_id:
                                if month[key1][key2][key3]['remaining'] > 0 and month[key1][key2][key3][
                                    'remaining'] < 100:
                                    print('this permit is available on', key2)
                                    count += 1
                                if month[key1][key2][key3]['remaining'] > 105:
                                    print(
                                        'This is a non quota permit. Reservations will sometimes release a week before, but there will always be an unlimited amount.')
                                    quit()
        if count == 0:
            print("sorry this permit is not available in your selected range")

    api_key = 'ab3f1f1a-9cc2-4c20-bff6-dbf3a2d9fa96'
    starting_date_input = event['start_date']
    ending_date_input = event['end_date']
    permit_entrance = event['permit_entrance']
    url_list = []

    if permit_entrance == 'HH01':
        permit_entrance = "HH11"

    start_date = date_maker(starting_date_input)
    start_of_month = date_maker(starting_date_input, True)
    end_date = date_maker(ending_date_input)
    months = list(rrule.rrule(rrule.MONTHLY, dtstart=start_of_month, until=end_date))
    format_months(months)

    for i in months:
        end_of_month = datetime.date(i.year, i.month, calendar._monthlen(i.year, i.month))
        temp_url = ("https://www.recreation.gov/api/permitinyo/233262/availability?start_date=" + str(
            i) + "&end_date=" + str(end_of_month) + "&commercial_acct=false")
        url_list.append(temp_url)

    permit_entrance_id = get_permit_entrance_id()
    availability_list = get_availability()
    check_availability(availability_list, permit_entrance_id, start_date, end_date)

    return ('placeholder')