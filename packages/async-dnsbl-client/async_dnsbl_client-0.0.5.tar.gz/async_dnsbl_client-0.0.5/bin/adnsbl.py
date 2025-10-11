#!/usr/bin/python3

import argparse
import sys

import asyncio

import async_dnsbl_client

def get_args():

    me = sys.argv[0]
    epilog = f'''\nExamples:
    {me} 1.1.1.1
    {me} -a dnsbl.example.com dnsbl.example.org -r dnsbl.example.net 1.1.1.1'''

    parser = argparse.ArgumentParser(description='Sleep which can awake', epilog=epilog,  formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('host', metavar='HOST', help='host to check (IP or hostname)')
    parser.add_argument('--append', '-a', nargs='+', default=list(), metavar='DNSBL', help='add this DNSBL to check')
    parser.add_argument('--remove', '-r', nargs='+', default=list(), metavar='DNSBL', help='remove this DNSBL')
    parser.add_argument('--nameserver', '-n', default=None, metavar='NS server', help='DNS server')

    return parser.parse_args()

def main():
    args = get_args()
    zones = async_dnsbl_client.dnsbl_zones

    for r in args.remove:
        zones.remove(r)

    zones.extend(args.append)

    result = asyncio.run(async_dnsbl_client.dnsbl(args.host, zones, nameserver=args.nameserver))
    print('\n'.join(result))
    return int(bool(len(result)))

if __name__ == '__main__':
    sys.exit(main())