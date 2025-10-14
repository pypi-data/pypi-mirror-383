from datetime import datetime


class Trip:
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

    def __str__(self):
        return f"Trip({self.seq_no})"

    def __repr__(self):
        return f"Trip({self.seq_no})"

    """
    Seq. #,Time,Description,Operator,Entry Location/ Bus Route,Exit Location,Product,Rem. Rides,Change (+/-),Balance
    """

    @classmethod
    def from_csv(cls, line):
        seq_no = None
        time = None
        description = None
        operator = None
        entry_location = None
        bus_route = None
        exit_location = None
        product = None
        rem_rides = None
        change = None
        balance = None

        for i, v in enumerate(line.split(",")):
            match i:
                case 0:
                    seq_no = int(v)
                case 1:
                    time = datetime.strptime(v, "%m/%d/%y %I:%M %p")
                case 2:
                    description = v
                case 3:
                    operator = v
                case 4:
                    if v:
                        if v[0].isdigit():
                            bus_route = v
                        else:
                            entry_location = v
                case 5:
                    exit_location = v
                case 6:
                    product = v
                case 7:
                    rem_rides = v
                case 8:
                    change = v
                case 9:
                    balance = v

        return cls(
            seq_no=seq_no,
            time=time,
            description=description,
            operator=operator,
            entry_location=entry_location,
            bus_route=bus_route,
            exit_location=exit_location,
            product=product,
            rem_rides=rem_rides,
            change=change,
            balance=balance,
        )
