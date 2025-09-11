#!/usr/bin/env python3

import cgi
import cgitb
from urllib.parse import unquote_plus
from pathlib import Path
import traceback
import os

os.environ['MPLCONFIGDIR'] = '/tmp/matplotlib'

# Enable detailed error output to the browser
cgitb.enable()

print("Content-Type: text/html\n")

try:
    from bums2.io import output as output_module

    # Parse the form input into a dict
    form = cgi.FieldStorage()
    form_dict = {
        k: unquote_plus(form.getfirst(k, "").decode("utf-8") if isinstance(form.getfirst(k, ""), bytes) else form.getfirst(k, ""))
        for k in form.keys()
    }

    output_path = Path("/var/www/html/images/spectrum_output.txt")

    # Run CGIFormatter, which handles everything internally (no driver.py required)
    output_module.CGIFormatter.run_cgi(form_dict, output_path)

except Exception:
    print("<html><body><h2>An error occurred</h2>")
    print("<pre>")
    traceback.print_exc()
    print("</pre></body></html>")
