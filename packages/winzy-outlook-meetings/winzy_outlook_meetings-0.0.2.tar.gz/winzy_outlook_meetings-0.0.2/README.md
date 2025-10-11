# winzy-outlook-meetings

[![PyPI](https://img.shields.io/pypi/v/winzy-outlook-meetings.svg)](https://pypi.org/project/winzy-outlook-meetings/)
[![Changelog](https://img.shields.io/github/v/release/sukhbinder/winzy-outlook-meetings?include_prereleases&label=changelog)](https://github.com/sukhbinder/winzy-outlook-meetings/releases)
[![Tests](https://github.com/sukhbinder/winzy-outlook-meetings/workflows/Test/badge.svg)](https://github.com/sukhbinder/winzy-outlook-meetings/actions?query=workflow%3ATest)
[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](https://github.com/sukhbinder/winzy-outlook-meetings/blob/main/LICENSE)

Get outlook calendar entries in commandline.

## Introduction

`winzy_outlook_meetings` is a plugin of `winzy`, which allows users to retrieve outlook calendar entries in a command-line interface.

## Features

*   Retrieves outlook calendar entries based on start date and number of days.
*   Supports both text-based output and opening the generated schedule in its default application.

## Prerequisites

Before you begin using `winzy_outlook_meetings`, ensure that:

*   You have Python installed on your system.
*   You are familiar with basic command-line interface operations.
*   Your Outlook calendar account has been configured properly.


## Installation

First configure your Winzy project [to use Winzy](https://github.com/sukhbinder/winzy).

Then install this plugin in the same environment as your Winzy application.
```bash
pip install winzy-outlook-meetings
```

## Usage


To retrieve and display your Outlook calendar entries, use the following command:

```bash
winzy outcal --start <date> --days <number>
```
Replace `<date>` with the desired start date in `YYYY-MM-DD` format and `<number>` with the number of days for which you want to retrieve calendar entries.

For example, to retrieve the next 14 days' worth of Outlook calendar entries, use:

```bash
winzy outcal --start 2023-03-01 --days 14
```

## Output

`winzy_outlook_meetings` will display the retrieved calendar entries in a human-readable format. The output include information such as event titles, start, duration, locations, and descriptions.


## Development

To set up this plugin locally, first checkout the code. Then create a new virtual environment:
```bash
cd winzy-outlook-meetings
python -m venv venv
source venv/bin/activate
```
Now install the dependencies and test dependencies:
```bash
pip install -e '.[test]'
```
To run the tests:
```bash
python -m pytest
```
