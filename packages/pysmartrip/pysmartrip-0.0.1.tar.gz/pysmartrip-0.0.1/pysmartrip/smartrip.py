from .card import SmarTripCard

import csv
import datetime as dt
import re
import requests

ST_USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:143.0) Gecko/20100101 Firefox/143.0"
BAD_LOGIN_STRINGS = ("Invalid user name or password.", "Your account has been locked.")
LOGIN_URL = "https://smartrip.wmata.com/Account/Login"
ACCOUNT_SUMMARY_URL = "https://smartrip.wmata.com/Account/Summary"
CARD_REGEX = "/Card/Summary/Index/([0-9]+)"


class SmarTrip:
    def __init__(self, username: str, password: str):
        self.username = username
        self.password = password
        self.session = requests.Session()
        # mimic a browser, site rejects default user agent string
        self.session.headers.update({"User-Agent": ST_USER_AGENT})
        self._login()
        self.cards = self._get_available_cards()

    def _get_rvt(self, url: str):
        r = self.session.get(url)
        if r.ok:
            tmp = re.search("[a-zA-Z0-9-_]{92}", r.text)
            if tmp:
                return tmp.group(0)
        return None

    def _post_with_rvt(self, url: str, data: dict):
        rvt = self._get_rvt(url)
        if not rvt:
            raise Exception(f"failed to get request verification token for: {url}")
        data["__RequestVerificationToken"] = rvt
        return self.session.post(url, data=data)

    def _login(self):
        data = {
            "UserName": self.username,
            "Password": self.password,
            "OnCancel": "",
            "log_in": "",
        }
        r = self._post_with_rvt(LOGIN_URL, data=data)
        if r.ok:
            for bls in BAD_LOGIN_STRINGS:
                if bls in r.text:
                    raise Exception("login failed! username or password invalid")
        else:
            raise Exception("login failed! bad response for login")
        return True

    def _get_available_cards(self):
        r = self.session.get(ACCOUNT_SUMMARY_URL)
        if r.ok:
            return [
                SmarTripCard(self, card_id)
                for card_id in re.findall(CARD_REGEX, r.text)
            ]
        return None
