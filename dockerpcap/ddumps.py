# coding=utf-8

import os
import netns
import argparse

parser = argparse.ArgumentParser(description="Dump tool to capture all network traffic in specified namespace.")
parser.add_argument("-f", dest="filter", help="the filter shall be used to tshark")
parser.add_argument("--max-duration", help="the max duration shall be limited with tshark")
parser.add_argument("--max-filesize", help="the max filesize shall be limited with tshark")
parser.add_argument("work_dir")
parser.add_argument("ns_path")


def ddump():
    args = parser.parse_args()
    with netns.NetNS(nspath=args.ns_file):
        if args.filter:
            os.execvp("tshark", ("tshark",
                                 "-a", "duration:%d" % args.max_duration,
                                 "-a", "filesize:%d" % args.max_filesize,
                                 "-f", args.filter,
                                 "-w", os.path.join(args.work_dir, "data.pcap")))
        else:
            os.execvp("tshark", ("tshark",
                                 "-a", "duration:%d" % args.max_duration,
                                 "-a", "filesize:%d" % args.max_filesize,
                                 "-w", os.path.join(args.work_dir, "data.pcap")))
