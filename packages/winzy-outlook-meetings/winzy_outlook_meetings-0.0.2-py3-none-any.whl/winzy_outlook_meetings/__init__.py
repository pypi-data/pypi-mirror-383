import winzy
from winzy_outlook_meetings.app import get_outlook_schedule
from datetime import datetime


def create_parser(subparser):
    parser = subparser.add_parser(
        "outcal", description="Get outlook calendar entries in commandline "
    )
    parser.add_argument(
        "-s",
        "--start",
        help="Start date (YYYY-MM-DD). Default today",
        default=datetime.today(),
        type=str,
    )
    parser.add_argument(
        "-d", "--days", type=int, default=1, help="No of days, Default 1"
    )
    parser.add_argument(
        "-m",
        "--minimal",
        action="store_true",
        help="If provided, shows minimal information",
    )
    return parser


class HelloWorld:
    """Get outlook calendar entries in commandline"""

    __name__ = "outcal"

    @winzy.hookimpl
    def register_commands(self, subparser):
        parser = create_parser(subparser)
        parser.set_defaults(func=self.run)

    def run(self, args):
        output = get_outlook_schedule(begin=args.start, days=args.days)
        self.run_inner(output, args.minimal)

    def run_inner(self, output, minimal):
        with open(output, "r") as fin:
            lines = fin.readlines()
        if not minimal:
            for line in lines:
                print(line.strip())
        else:
            olddate = ""
            for line in lines:
                try:
                    datetimestr, subject, duration, where = line.strip().split(",")
                except ValueError:
                    continue
                try:
                    date, time = datetimestr.split()
                except ValueError:
                    date = datetimestr.strip()
                    time = "All-day"
                if olddate == "" or olddate != date:
                    print(date)
                print("\t", time, subject.strip().upper()[:15])
                olddate = date

    def hello(self, args):
        # this routine will be called when "winzy outcal is called."
        print("Hello! This is an example ``winzy`` plugin.")


outcal_plugin = HelloWorld()
