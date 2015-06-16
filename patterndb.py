
import re

class FitElement:
    def __init__(self, o, h, l, c, v):
        self.open = o
        self.high = h
        self.low = l
        self.close = c
        self.volume = v

class Pattern:
    def __init__(self):
        self.fit_elements = []
        self.exit_after = 0
        self.p_positive = 0
        self.binomial_p = 0
        self.mean = 0
        self.mean_p = 0
        self.sigma = 0

    def add_fit_element(self, element):
        self.fit_elements.append(element)

    def get_fit_element(self, index):
        return self.fit_elements[index]

    def length(self):
        return len(self.fit_elements)


class PatternDb:
    def __init__(self):
        self.patterns = []
        self.pattern_expression = r"Pattern: \d+ occurences ===(.*?)==="
        self.candle_expression = r"C\d+: OHLCV:([.0-9]+):([.0-9]+):([.0-9]+):([.0-9]+):([.0-9]+)"
        self.mean_expression = r"mean = ([-.0-9]+); rejecting H0 at p-value: ([-.0-9]+); sigma = ([-.0-9]+)"
        self.binomial_expression = r"\+ returns: ([-.0-9]+); p-value: ([-.0-9]+)"
        self.price_tolerance = 0.1
        self.volume_tolerance = 0.1
        self.exit_after = 1

    def load_from_txt(self, input_filename):
        text = open(input_filename, "rt").read()

        m = re.search("Price tolerance: ([.0-9]+)", text)
        self.price_tolerance = float(m.group(1))

        m = re.search("Volume tolerance: ([.0-9]+)", text)
        self.volume_tolerance = float(m.group(1))

        m = re.search("Exit after: ([0-9]+)", text)
        self.exit_after = int(m.group(1))
 
        p = re.compile(self.pattern_expression, re.MULTILINE | re.DOTALL)
        rx_candle = re.compile(self.candle_expression)
        rx_mean = re.compile(self.mean_expression)
        rx_bin = re.compile(self.binomial_expression)
        matches = p.findall(text)
        for match in matches:
            pattern = Pattern()
            pos = 0
            m = rx_candle.search(match, pos)
            while m:
                o = float(m.group(1))
                h = float(m.group(2))
                l = float(m.group(3))
                c = float(m.group(4))
                v = float(m.group(5))
                el = FitElement(o, h, l, c, v)
                pattern.add_fit_element(el)
                pos = m.end(0)
                m = rx_candle.search(match, pos)

            m = rx_mean.search(match)
            pattern.mean = float(m.group(1))
            pattern.mean_p = float(m.group(2))
            pattern.sigma = float(m.group(3))

            m = rx_bin.search(match)
            pattern.p_positive = float(m.group(1))
            pattern.binomial_p = float(m.group(2))

            pattern.exit_after = self.exit_after

            self.patterns.append(pattern)
    
    def find_match(self, fit_elements):
        normalized = self.normalize(fit_elements)

        abs_min = normalized[0].low
        abs_max = normalized[0].high
        for el in normalized:
            abs_min = min(abs_min, el.low)
            abs_max = max(abs_max, el.high)
        tolerance = (abs_max - abs_min) * self.price_tolerance

        found = []

        for pattern in self.patterns:
            if pattern.length() != len(fit_elements):
                continue

            found_pattern = pattern
            for i in range(0, pattern.length()):
                if not self.fit(pattern.get_fit_element(i), normalized[i], tolerance):
                    found_pattern = None
                    break

            if found_pattern:
                found.append(pattern)

        return found
                
    def fit(self, el1, el2, candle_tolerance):
        if abs(el1.open - el2.open) > candle_tolerance:
            return False
        if abs(el1.close - el2.close) > candle_tolerance:
            return False
        if abs(el1.high - el2.high) > candle_tolerance:
            return False
        if abs(el1.low - el2.low) > candle_tolerance:
            return False
        if self.volume_tolerance > 0 and abs(el1.volume - el2.volume) > self.volume_tolerance:
            return False

        return True


    def normalize(self, fit_elements):
        result = []
        start_price = fit_elements[0].open
        start_volume = fit_elements[0].volume

        for el in fit_elements:
            el = FitElement(el.open / start_price, el.high / start_price, el.low / start_price, el.close / start_price, el.volume / start_volume)
            result.append(el)
        return result

