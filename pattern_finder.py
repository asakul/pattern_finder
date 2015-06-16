
import os
import argparse
import sys
import re
from patterndb import PatternDb, FitElement, Pattern

def main():
    parser = argparse.ArgumentParser(description="Searches database, created by pattern-miner")
    parser.add_argument('-i', '--input', action='store', dest='input', help='Input filename', required=True)

    args = parser.parse_args()    
    input_db = args.input

    db = PatternDb()
    db.load_from_txt(input_db)

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




if __name__ == "__main__":
    main()
