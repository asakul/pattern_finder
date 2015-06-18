import csv
import datetime

class Candle:
    def __init__(self, date, min_price, max_price, open_price, close_price, volume):
        self.date = date
        self.min_price = min_price
        self.max_price = max_price
        self.open_price = open_price
        self.close_price = close_price
        self.volume = volume

class Quote:
    def __init__(self):
        self.candles = []
        self.times = []

    def load_from_csv(self, filename):
        col_ticker = None
        col_date = None
        col_open = None
        col_high = None
        col_low = None
        col_close = None
        col_volume = None

        code = None

        with open(filename) as f:
            reader = csv.reader(f)
            header = reader.__next__()
            col_ticker = header.index("<TICKER>")
            col_date = header.index("<DATE>")
            col_time = header.index("<TIME>")
            col_open = header.index("<OPEN>")
            col_high = header.index("<HIGH>")
            col_low = header.index("<LOW>")
            col_close = header.index("<CLOSE>")
            col_volume = header.index("<VOL>")
            for row in reader:
                if code == None:
                    code = row[col_ticker]
                else:
                    if row[col_ticker] != code: raise Exception("Mixed tickers in file: not supported")

                date = self.parse_date(row[col_date], row[col_time])
                price_open = float(row[col_open])
                price_high = float(row[col_high])
                price_low = float(row[col_low])
                price_close = float(row[col_close])
                volume = float(row[col_volume])

                candle = Candle(date, price_low, price_high, price_open, price_close, volume)
                self.candles.append(candle)
                self.times.append(date)
        self.code = code

    def parse_date(self, date, time):
        if len(date) != 8:
            raise Exception("Invalid date format: should be YYYYMMDD, have: " + date)
        if len(time) != 6:
            raise Exception("Invalid time format: should be HHMMDD, have: " + date)
        y = int(date[0:4])
        m = int(date[4:6])
        d = int(date[6:8])

        hour = int(time[0:2])
        minutes = int(time[2:4])
        sec = int(time[4:6])

        return datetime.datetime(y, m, d, hour, minutes)

    def get_time(self, index):
        try:
            return self.times[index];
        except KeyError:
            return None

    def get_candle(self, index):
        try:
            return self.candles[index];
        except KeyError:
            return None

    def total_candles(self):
        return len(self.candles)

def load_quotes(filename):
    q = Quote()
    q.load_from_csv(filename)
    return q
