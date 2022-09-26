# coding=utf-8

import os
import sys
from datetime import timedelta


def parse_duration(inputs):
    try:
        if inputs.lower().endswith("s"):
            return timedelta(seconds=float(inputs[:-1]))
        elif inputs.lower().endswith("m"):
            return timedelta(seconds=float(inputs[:-1])*60)
        elif inputs.lower().endswith("h"):
            return timedelta(seconds=float(inputs[:-1])*3600)
        elif inputs.lower().endswith("d"):
            return timedelta(days=float(inputs[:-1]))
        else:
            raise ValueError()
    except ValueError:
        print >> sys.stderr, "Unrecongnized DURATION %s.\nProcess exit." % inputs
        sys.exit(1)


def parse_size(inputs):
    try:
        if inputs.lower().endswith("k"):
            return float(inputs[:-1].isdigit())
        elif inputs.lower().endswith("m"):
            return float(inputs[:-1].isdigit())*1024
        elif inputs.lower().endswith("g"):
            return float(inputs[:-1].isdigit())*1024*1024
        else:
            raise ValueError()
    except ValueError:
        print >> sys.stderr, "Unrecongnized SIZE %s.\nProcess exit." % inputs
        sys.exit(1)


EXPIRED_DURATION = parse_duration(os.environ.get("EXPIRED_DURATION", "2d"))
MAX_DUMP_DURATION = parse_duration(os.environ.get("MAX_DUMP_DURATION", "1h"))
MAX_DUMP_SIZE = parse_size(os.environ.get("MAX_DUMP_SIZE", "1g"))
BASE_WORK_DIR = parse_duration(os.environ.get("BASE_WORK_DIR", "/data"))
BUFF_SIZE = 1024