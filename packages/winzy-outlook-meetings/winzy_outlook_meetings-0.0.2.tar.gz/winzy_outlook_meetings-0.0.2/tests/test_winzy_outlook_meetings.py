import pytest
import winzy_outlook_meetings as w
from datetime import datetime

from argparse import Namespace, ArgumentParser


def test_create_parser():
    subparser = ArgumentParser().add_subparsers()
    parser = w.create_parser(subparser)

    assert parser is not None

    dateval = datetime.today().strftime("%Y-%m-%d")
    result = parser.parse_args(["-s", dateval])
    assert result.start == dateval
    assert result.days == 1


def test_plugin(capsys):
    w.outcal_plugin.hello(None)
    captured = capsys.readouterr()
    assert "Hello! This is an example ``winzy`` plugin." in captured.out


def test_run_without_minimal(tmpdir, capsys):
    # Create a temporary file with example lines
    temp_file = tmpdir.join("test_outcal.txt")
    temp_file.write("2025-10-1 10:00,test,30,teams\n2025-10-2,allday,,teams")

    # Call the run method
    w.HelloWorld().run_inner(str(temp_file), False)

    # Capture the output
    captured = capsys.readouterr()
    expected = "2025-10-1 10:00,test,30,teams\n2025-10-2,allday,,teams\n"
    assert captured.out == expected


def test_run_with_minimal(tmpdir, capsys):
    # Create a temporary file with example lines
    temp_file = tmpdir.join("test_outcal.txt")
    temp_file.write(
        "2025-10-1 10:00,test,30,teams\n2025-10-1 11:00,test2,60,teams\n2025-10-2,allday,,teams"
    )

    # Call the run_inner method
    w.HelloWorld().run_inner(str(temp_file), True)

    # Capture the output
    captured = capsys.readouterr()
    expected = (
        "2025-10-1\n\t 10:00 TEST\n\t 11:00 TEST2\n2025-10-2\n\t All-day ALLDAY\n"
    )
    assert captured.out == expected
