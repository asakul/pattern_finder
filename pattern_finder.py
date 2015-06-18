
import os
import argparse
import sys
import re
from patterndb import PatternDb, FitElement, Pattern
from quotes import Quote, load_quotes

def main():
    parser = argparse.ArgumentParser(description="Searches database, created by pattern-miner")
    parser.add_argument('-d', '--db', action='store', dest='dbfile', help='Input database', required=True)
    parser.add_argument('--interactive', action='store', dest='interactive', help='Interactive mode')
    parser.add_argument('quotes')

    args = parser.parse_args()    
    input_db = args.dbfile

    db = PatternDb()
    db.load_from_txt(input_db)

    if args.interactive:
        while True:
            print("Candles number -> ")
            candles_number = int(sys.stdin.readline())
            elements = []
            for i in range(candles_number):
                print("C{0} O:H:L:C:V-> ".format(i))
                m = re.search("([.0-9]+):([.0-9]+):([.0-9]+):([.0-9]+):([.0-9]+)", sys.stdin.readline())
                if not m:
                    print("Baka! Enter good values.")
                    break
                o = float(m.group(1))
                h = float(m.group(2))
                l = float(m.group(3))
                c = float(m.group(4))
                v = float(m.group(5))
                elements.append(FitElement(o, h, l, c, v))

            patterns = db.find_match(elements)
            if len(patterns) > 0:
                for pattern in patterns:
                    if pattern:
                        print("=== Match")
                        print("Exit after: {0}".format(pattern.exit_after))
                        print("+ return probability: {0}, p-value: {1}".format(pattern.p_positive, pattern.binomial_p))
                        print("Mean return: {0}, p-value: {1}; sigma: {2}".format(pattern.mean, pattern.mean_p, pattern.sigma))

                print("===")
            else:
                print("Match NOT found")
    else:
        q = load_quotes(args.quotes)
        correct = 0
        total = 0
        total_return = 0

        for i in range(0, q.total_candles() - 1):
            c0 = q.get_candle(i)
            c1 = q.get_candle(i + 1)
            t = q.get_time(i + 1)
            elements = []
            for c in [c0, c1]:
                elements.append(FitElement(c.open_price, c.max_price, c.min_price, c.close_price, c.volume))

            patterns = db.find_match(elements)
            if len(patterns) > 0:
                print("At ", t)
                this_pattern = patterns[0]
                for pattern in patterns:
                    print("=== Match")
                    j = 0
                    for el in pattern.fit_elements:
                        print("==== C{0}: {1}:{2}:{3}:{4}:{5}".format(j, el.open, el.high, el.low, el.close, el.volume))
                        j += 1
                    print("Exit after: {0}".format(pattern.exit_after))
                    print("+ return probability: {0}, p-value: {1}".format(pattern.p_positive, pattern.binomial_p))
                    print("Mean return: {0}, p-value: {1}; sigma: {2}".format(pattern.mean, pattern.mean_p, pattern.sigma))
                    if pattern.binomial_p < this_pattern.binomial_p:
                        this_pattern = pattern

                if i + 2 >= q.total_candles() or i + 1 + this_pattern.exit_after >= q.total_candles():
                    continue

                c2 = q.get_candle(i + 2)
                cx = q.get_candle(i + 1 + this_pattern.exit_after)
                ret = (cx.close_price - c2.open_price) / c2.open_price
                true_ret = ret
                high_ret = -10000
                low_ret = 10000
                #stop = False
                #for offset in range(0, this_pattern.exit_after):
                    #c = q.get_candle(i + 2)
                    #high_ret = max(high_ret, (c.max_price - c2.open_price) / c2.open_price)
                    #low_ret = min(low_ret, (c.min_price - c2.open_price) / c2.open_price)
                    #if this_pattern.p_positive > 0.5:
                        #if -0.001 > low_ret:
                            #stop = True
                            #ret = -0.001
                    #else:
                        #if 0.001 < high_ret:
                            #stop = True
                            #ret = 0.001

                if this_pattern.p_positive < 0.5:
                    ret = -ret

                if ret > 0:
                    correct += 1


                total_return += ret
                total += 1
                print("===== Return:", ret)

                print("===")

        print("Total correct guesses:", float(correct) / float(total))
        print("Total:", total)
        print("Total return:", total_return)


if __name__ == "__main__":
    main()
