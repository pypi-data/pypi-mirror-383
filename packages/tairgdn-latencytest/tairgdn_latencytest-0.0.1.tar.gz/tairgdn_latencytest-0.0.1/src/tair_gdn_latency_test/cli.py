import argparse
import asyncio
from tair_gdn_latency_test.reader import TairReader
from tair_gdn_latency_test.writer import TairWriter


def parse_args():

    parser = argparse.ArgumentParser(
        description="Tair GDN latency test tool",
        add_help = False
    )

    subparsers = parser.add_subparsers(dest="mode", required=True, help="support mode: 'write' or 'read'")

    parser_write = subparsers.add_parser("write", help="write data to source Tair server", add_help=False)
    parser_write.add_argument("-h", metavar="host", type=str, default="127.0.0.1", help="source server hostname (default 127.0.0.1)")
    parser_write.add_argument("-p", metavar="port", type=int, default=6379, help="source server port (default 6379)")
    parser_write.add_argument("-u", metavar="username", type=str, default="", help="Used to send ACL style \"AUTH username pass\" Needs -a")
    parser_write.add_argument("-a", metavar="password", type=str, default="", help="Password for Tair Auth")
    parser_write.add_argument("-l", metavar="length", type=int, default=0, help="length of command (unit: byte)")
    parser_write.add_argument("-n", metavar="requests", type=int, default=100000, help="Total number of requests (default 100000)")
    parser_write.add_argument("-P", metavar="pipeline", type=int, default=8, help="Pipeline <numreq> requests (default 32)")
    parser_write.add_argument("-c", metavar="connections", type=int, default=8, help="Number of connections (default 1)")
    parser_write.add_argument("--help", action="help", help="Output this help and exit")


    parser_read = subparsers.add_parser("read", help="read from target Tair server and calculate GDN delay time", add_help=False)
    parser_read.add_argument("-h", metavar="host", type=str, default="127.0.0.1", help="target server hostname (default 127.0.0.1)")
    parser_read.add_argument("-p", metavar="port", type=int, default=6379, help="target server port (default 6379)")
    parser_read.add_argument("-u", metavar="username", type=str, default="", help="Used to send ACL style \"AUTH username pass\" Needs -a.")
    parser_read.add_argument("-a", metavar="password", type=str, default="", help="Password for target server Auth")
    parser_read.add_argument("-n", metavar="requests", type=int, default=100000, help="Total number of requests (default 100000)")
    parser_read.add_argument("--help", action="help", help="Output this help and exit.")

    args = parser.parse_args()
    return args

def main():
    args = parse_args()
    if args.mode == "write":
        writer = TairWriter(ip=args.h,
                            port=args.p,
                            username=args.u,
                            password=args.a,
                            requests=args.n,
                            batch_size=args.P,
                            value_length=args.l,
                            connections=args.c)
        try:
            asyncio.run(writer.run())
        except RuntimeError:
            loop = asyncio.get_event_loop()
            loop.run_until_complete(writer.run())
    elif args.mode == "read":
        reader = TairReader(ip=args.h,
                            port=args.p,
                            username=args.u,
                            password=args.a,
                            requests=args.n)
        reader.run()


if __name__ == "__main__":
    main()