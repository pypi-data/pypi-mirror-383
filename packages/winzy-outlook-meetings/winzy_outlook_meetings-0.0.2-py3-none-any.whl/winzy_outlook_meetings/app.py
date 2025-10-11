import os
import shlex
import subprocess
import tempfile
from datetime import datetime, timedelta
from pathlib import Path


from dateutil import parser

VBSCRIPT = """
Const olFolderCalendar = 9
Dim fso
Set fso = WScript.CreateObject("Scripting.Filesystemobject")
Set f = fso.OpenTextFile("{fname}", 2)

Set objOutlook = CreateObject("Outlook.Application")
Set objNamespace = objOutlook.GetNamespace("MAPI")
Set objFolder = objNamespace.GetDefaultFolder(olFolderCalendar)
Set colItems = objFolder.Items
colItems.Sort("[Start]")
colItems.IncludeRecurrences = "True"
strFilter = "[Start] >= '{stdate}' AND [Start] <= '{enddate}'"
Set colFilteredItems = colItems.Restrict(strFilter)

For Each objItem In colFilteredItems
    f.WriteLine  objItem.Start   & "," & objItem.Subject  & ","  & objItem.Duration & ","  & objItem.Location
Next

f.Close
"""

APPCMD = "cscript //Nologo '{fname}'"


def write_script(begin=datetime.today(), days=1):
    td = tempfile.gettempdir()
    file1 = Path(td) / "app.txt"
    file2 = Path(td) / "_appq.vbs"

    file1.touch()
    if days > 0:
        endday = begin + timedelta(days=days)
    else:
        endday = begin
        begin = begin + timedelta(days=days)

    endday = endday.strftime("%m/%d/%Y")
    begin = begin.strftime("%m/%d/%Y")
    with open(file2, "w") as fout:
        fout.write(VBSCRIPT.format(fname=file1, stdate=begin, enddate=endday))
    return file2, file1


def run_script(scriptfile):
    startupinfo = subprocess.STARTUPINFO()
    startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
    apptxt = APPCMD.format(fname=scriptfile)
    cmds = shlex.split(apptxt)
    iret = subprocess.call(
        cmds,
        startupinfo=startupinfo,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

    return iret


def get_outlook_schedule(begin=datetime.today(), days=1, show=False):
    if isinstance(begin, str):
        begin_d = parser.parse(begin)
    else:
        begin_d = begin

    script, output = write_script(begin=begin_d, days=days)
    iret = run_script(script)

    if show:
        os.startfile(output)
    return output


def subprocess_say(msg):
    startinfo = subprocess.STARTUPINFO()
    startinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
    iret = subprocess.run(
        ["say", msg],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        startupinfo=startinfo,
    )
    return iret
