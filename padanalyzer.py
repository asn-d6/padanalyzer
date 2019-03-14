#!/usr/bin/python3

import sys
import datetime

import log_line
import hs_log

def analyze_logfile(f):
    hslog = hs_log.HSLog()

    for line_str in f:
        log_line.parse_log_line(line_str, hslog)
    hslog.finalize_global_log()

    #hslog.finalize_hs_log()

def main():
    if (len(sys.argv) != 2):
        print("Usage:\n\t$ padanalyzer.py <logfile>")
        return

    logfile = sys.argv[1]

    try:
        with open(logfile, 'r') as logfile_f:
            analyze_logfile(logfile_f)
    except IOError:
        print("No log file provided", file=sys.stderr)

if __name__ == '__main__':
    main()
