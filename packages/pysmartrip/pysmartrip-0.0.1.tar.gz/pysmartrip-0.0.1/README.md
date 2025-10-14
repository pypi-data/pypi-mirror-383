# pysmartrip 

pysmartrip is a Python library that provides a simple API for fetching your WMATA SmarTrip data.

## Usage
```python
from pysmartrip import SmarTrip

st = SmarTrip("username", "password")
card = st.cards[0]
for trip in card.get_trips_between("09/29/2025", "10/03/2025"):
    if trip.bus_route:
        print(f"{trip.time} -- {trip.balance}")

for trip in card.get_trips_by_month(8, 2025):
    if trip.operator == "Metrorail":
        if trip.exit_location:
            print(f"{trip.time} -- {trip.exit_location}")
```
---
Used in [this blogpost](https://mmae.kr/scraping-the-smartrip-website-to-automate-my-timesheets/)
