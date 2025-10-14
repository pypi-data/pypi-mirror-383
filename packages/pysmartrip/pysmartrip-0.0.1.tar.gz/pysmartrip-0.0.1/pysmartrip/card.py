from .trip import Trip

import calendar
import datetime as dt
import csv
import json

USAGE_HISTORY_URL = "https://smartrip.wmata.com/Card/UsageReport/Index"
GET_EXCEL_URL = "https://smartrip.wmata.com/Card/UsageReport/GetExcel"


class SmarTripCard:
    def __init__(self, ctx, card_id: str):
        self.ctx = ctx
        self.card_id = card_id

    def __repr__(self):
        return f"SmarTripCard({self.card_id})"

    def __str__(self):
        return f"SmarTripCard({self.card_id})"

    def _get_results(self, params):
        const = {
            "TransactionStatus": "Successful",
            "cardId": self.card_id,
        }
        r = self.ctx.session.get(GET_EXCEL_URL, params=params | const)
        if r.ok:
            return [Trip.from_csv(line) for line in r.text.split("\n")[1:][::-1]]
        return None

    def _get_month_results(self, month: int, year: int):
        date_fmt = "%m/%d/%Y %H:%M:%S"
        last_day = calendar._monthlen(year, month)
        start = dt.datetime(year, month, 1, 0, 0)
        end = dt.datetime(year, month, last_day, 23, 59)
        params = {
            "Month": f"{year:4}{month:02}",
            "StartDate": start.strftime(date_fmt),
            "EndDate": end.strftime(date_fmt),
            "Period": "M",
        }
        return self._get_results(params)

    def _get_between_results(self, start, end):
        date_fmt = "%m/%d/%Y %H:%M:%S"
        params = {
            "StartDate": start.strftime(date_fmt),
            "EndDate": end.strftime(date_fmt),
            "Period": "R",
        }
        return self._get_results(params)

    def get_trips_by_month(self, month: int, year: int):
        data = {
            "IsByMonth": "true",
            "SelectedMonth": f"{year:4}{month:02}",
            "CardId": int(self.card_id),
            "BackUrl": f"~/CardSummary/Index/{self.card_id}",
            # does this matter?
            "MinStartDate": "1/1/1970+12:00:00AM",
            "SubmitButton": "True",
        }
        r = self.ctx._post_with_rvt(f"{USAGE_HISTORY_URL}/{self.card_id}", data)
        if r.ok:
            return self._get_month_results(month, year)
        return None

    def get_trips_between(self, start_date: str, end_date: str):
        start = None
        end = None
        date_fmt = "%m/%d/%Y"
        try:
            start = dt.datetime.strptime(start_date, date_fmt)
            end = dt.datetime.strptime(end_date, date_fmt)
            end += dt.timedelta(hours=23, minutes=59)
        except:
            raise Exception("improperly formatted date (mm/dd/yyyy)")
        data = {
            "IsByMonth": "false",
            "CardId": int(self.card_id),
            "BackUrl": f"~/CardSummary/Index/{self.card_id}",
            "StartDate": start_date,
            "EndDate": end_date,
            # does this matter?
            "MinStartDate": "1/1/1970+12:00:00AM",
            "SubmitButton": "True",
        }
        r = self.ctx._post_with_rvt(f"{USAGE_HISTORY_URL}/{self.card_id}", data)
        if r.ok:
            return self._get_between_results(start, end)
        return None
