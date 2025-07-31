#!/usr/bin/env python3

import cgi
import os
from urllib.parse import unquote_plus
from pathlib import Path
import sys

SCRIPT_DIR = Path(__file__).resolve().parent
INPUT_FILE = SCRIPT_DIR / "input.txt"
SPECTRA_DIR = SCRIPT_DIR / "SPECTRA"
MATRIX_DIR = SCRIPT_DIR / "MATRIX"

sys.path.insert(0, str(SCRIPT_DIR))

#from bums2.io import input as input_module
from bums2.io.input import run as run_input
form = cgi.FieldStorage()

ALL_EXPECTED_KEYS = [
    "title", "input_mode", "iter", "itertesterror", "endtesterror", "tempij",
    "smoothing", "shape", "perturbation", "cal_factor", "max_energy",
    "matrix", "matrix_name", "start_spec", "alg", "spectra_form",
    "spectrum_input_mode", "input_spectrum",
    # Detectors
    "bare", "barecd", "2inch", "2inchcd", "3inch", "3inchcd",
    "5inch", "5inchcd", "8inch", "10inch", "12inch", "15inch", "18inch",
    # Detector counts and errors (with underscores)
    "bare_counts", "bare_counts_error",
    "barecd_counts", "barecd_counts_error",
    "2inch_counts", "2inch_counts_error",
    "2inchcd_counts", "2inchcd_counts_error",
    "3inch_counts", "3inch_counts_error",
    "3inchcd_counts", "3inchcd_counts_error",
    "5inch_counts", "5inch_counts_error",
    "5inchcd_counts", "5inchcd_counts_error",
    "8inch_counts", "8inch_counts_error",
    "10inch_counts", "10inch_counts_error",
    "12inch_counts", "12inch_counts_error",
    "15inch_counts", "15inch_counts_error",
    "18inch_counts", "18inch_counts_error",
]

DETECTORS = [
    ("bare", "Bare"), ("barecd", "Bare Cd"), ("2inch", "2 Inch"), ("2inchcd", "2 Inch Cd"),
    ("3inch", "3 Inch"), ("3inchcd", "3 Inch Cd"), ("5inch", "5 Inch"), ("5inchcd", "5 Inch Cd"),
    ("8inch", "8 Inch"), ("10inch", "10 Inch"), ("12inch", "12 Inch"),
    ("15inch", "15 Inch"), ("18inch", "18 Inch")
]

PARAMS = [
    ("iter", "Max. Number of Iterations", 5),
    ("itertesterror", "Iterations before test error", 5),
    ("endtesterror", "Final error %", 3),
    ("tempij", "Maxwellian Temp", 6),
    ("smoothing", "Smoothing Factor", 4),
    ("shape", "Shape", 4),
    ("perturbation", "Perturbation", 4),
    ("cal_factor", "Calibration Factor", 6),
    ("max_energy", "Maximum Energy", 6)
]

def get_field(name, default=""):
    # ONLY prefer form value if present, else default (no cookie fallback)
    if name in form:
        val = form.getvalue(name)
        if isinstance(val, list):
            return ",".join(val)
        return val
    else:
        return default

def text_html(name, size=8, align="right", input_align=None):
    val = get_field(name)
    input_align = input_align or align
    width = "450px" if name == "title" else "100px"
    style = f'style="text-align:{input_align}; width:{width};"'
    return f'<input type="text" name="{name}" size="{size}" value="{val}" {style}>'

def checkbox_html(name):
    checked = "checked" if get_field(name).lower() in ("1", "true", "yes") else ""
    return f'<input type="checkbox" name="{name}" value="true" {checked}>'

def dropdown(name, options):
    selected = get_field(name)
    html = [f'<select name="{name}">']
    for option in options:
        if isinstance(option, tuple):
            val, label = option
        else:
            val = label = option
        sel = 'selected' if val == selected else ''
        html.append(f'<option value="{val}" {sel}>{label}</option>')
    html.append('</select>')
    return "\n".join(html)

def tooltip_html(label, helpfile=None):
    helptext = ""
    if helpfile:
        try:
            with open(SCRIPT_DIR / "HELP" / helpfile, encoding="utf-8") as f:
                helptext = f.read().strip()
        except Exception:
            helptext = "[Help file missing]"
    return f'<span class="tooltip"><b>{label}</b><span class="tooltiptext">{helptext}</span></span>'

def get_file_headers(directory):
    result = []
    try:
        for fname in sorted(f for f in os.listdir(directory) if not f.startswith('.')):
            fpath = os.path.join(directory, fname)
            if os.path.isfile(fpath):
                head = ""
                try:
                    with open(fpath, encoding="utf-8") as f:
                        head = f.readline().strip()
                except Exception:
                    pass
                label = f"{fname} - {head}" if head else fname
                result.append((fname, label))
    except FileNotFoundError:
        pass
    return result

def kv_lines_to_dict(lines):
    d = {}
    for line in lines:
        if "=" in line:
            k,v = line.split("=", 1)
            d[k] = v
    return d

def main():
    kv = {}
    kv_lines = []

    # Process uploaded template file first, if any
    if "upload_file" in form:
      uploaded_template = form['upload_file']
      if hasattr(uploaded_template, "file") and uploaded_template.file:
          for line in uploaded_template.file:
              line = line.decode('utf-8').strip()
              if '=' in line:
                  k, v = line.split('=', 1)
                  v = v.strip()
                  kv_lines.append(f"{k}={v}")

    # Then process other form keys (overwrite or add)
    for key in form.keys():
        if key == "upload_file":
            continue
        val = form.getvalue(key)
        val = ",".join(val) if isinstance(val, list) else str(val)
        kv_lines.append(f"{key}={val}")

    # Build dictionary of key-value pairs
    kv_dict = dict(line.split("=", 1) for line in kv_lines if "=" in line)

    # Ensure all expected keys are present, even if empty
    for key in ALL_EXPECTED_KEYS:
        kv_dict.setdefault(key, "")

    # matrix_name is derived from matrix if not already set
    if "matrix" in kv_dict and not kv_dict.get("matrix_name"):
        kv_dict["matrix_name"] = kv_dict["matrix"]

    # Send to parser
    if "do_submit" in form:
        REQUIRED_KEYS = [
            "iter", "itertesterror", "endtesterror", "tempij",
            "smoothing", "shape", "perturbation", "cal_factor",
            "max_energy", "matrix", "start_spec", "alg"
        ]

        missing_fields = [key for key in REQUIRED_KEYS if not kv_dict.get(key)]
        if missing_fields:
            print("Content-type: text/html\n")
            print("<html><body>")
            print("<h2 style='color:red;'>Error: The following required fields are missing:</h2>")
            print("<ul>")
            for key in missing_fields:
                print(f"<li>{key}</li>")
            print("</ul>")
            print("<p><a href='web.cgi'>Return to form</a></p>")
            print("</body></html>")
            return

        # Run input.py logic
        try:
            # cfg = run_input(kv_dict) #OG line maybe add back
            # Store key=value inputs as POST params or temp file
            print("Content-Type: text/html\n")
            print("""
            <html><body>
            <form id="redirectForm" method="post" action="output.cgi">
            """)
            for key, val in kv_dict.items():
                val = val.replace('"', '&quot;')  # HTML escape
                print(f'<input type="hidden" name="{key}" value="{val}">')
            print("""
            </form>
            <script>document.getElementById('redirectForm').submit();</script>
            </body></html>
            """)

            print("Content-type: text/html\n")
            print("<html><body>")
            print("<h2>Submission Successful</h2>")
            print("<pre>")
            print("CONFIG OBJECT:\n")
            #print(cfg) #with OG line above
            print("</pre>")
            print("</body></html>")

        except Exception as e:
            print("Content-type: text/html\n")
            print("<html><body>")
            print("<h2 style='color:red;'>An error occurred while processing the input:</h2>")
            print(f"<pre>{e}</pre>")
            print("<p><a href='web.cgi'>Return to form</a></p>")
            print("</body></html>")
            print("Status: 303 See Other")
            print("Location: output.cgi")
            print()



    # Then rest of your output printing below...

    print(f"""
    <html>
    <head>
    <title>NOTEZY - BUMS Input</title>
    <style>
    .tooltip {{
      position: relative;
      display: inline-block;
      cursor: help;
      text-decoration: underline;
    }}

    .tooltip .tooltiptext {{
      visibility: hidden;
      width: 500px;
      background-color: #222;
      color: #fff;
      text-align: left;
      border-radius: 4px;
      padding: 12px 16px;
      position: absolute;
      z-index: 1000;
      opacity: 0;
      transition: opacity 0.3s;
      white-space: normal;
      word-wrap: break-word;
      box-sizing: border-box;
      pointer-events: none;
      box-shadow: 0 0 15px rgba(0,0,0,0.6);
    }}

    .tooltip:hover .tooltiptext {{
      visibility: visible;
      opacity: 1;
      pointer-events: auto;
    }}
    </style>
    </head>
    <body bgcolor="white">
    <center><h1>BUMS Input Page!</h1></center>
    <center><h4>There are several quirks about the current version. Do not use spheres that are not part of the response matrix. It can't catch this and will give you a blank output. Also do not use 0. Enter a small number 0.000001 in place of 0.</h4></center>

    <form method="post" action="output.cgi" enctype="multipart/form-data">

    <div id="parse-status" style="margin-top: 10px; font-weight: bold;"></div>
    <table><tr><th align="left">Description:</th><td>{text_html('title', 150, align='left', input_align='left')}</td></tr></table><br>
    """)
#Lidebug above 2 lines
    # Upload section (restored)
    upload_choice = get_field("input_mode", "manual")
    manual_checked = "checked" if upload_choice == "manual" else ""
    file_checked = "checked" if upload_choice == "file" else ""

    print(f"""
    <div style="margin-bottom: 8px;">
      <b>{tooltip_html("Choose Input Mode", "input_mode")}</b><br>
      <label>
        <input type="radio" name="input_mode" value="manual" {manual_checked}>
        Manual Entry
      </label>
      <label>
        <input type="radio" name="input_mode" value="file" {file_checked}>
        Upload File
      </label>
    </div>

    <div style="margin-bottom: 8px;">
      <a href="/downloads/BUMS_Template" download>Download Input Template</a>
    </div>
    <div style="margin-bottom: 8px;">
      <input type="file" name="upload_file" id="upload_file_input">
    </div>

    """)

    print(f"""
    <table border="0" cellspacing="2" cellpadding="2">
    <tr>
        <td valign="top">
          <table border="0" cellspacing="2" cellpadding="2">
            <tr>
                <th>{tooltip_html("Detectors", "detector")}</th>
                <th>{tooltip_html("Detectors Used", "detectors_used")}</th>
                <th>{tooltip_html("Counts", "ball_count")}</th>
                <th></th>
                <th>{tooltip_html("Percent Uncertainty", "ball_error")}</th>
            </tr>
""")

    for i, (key, label) in enumerate(DETECTORS):
        count_name = f"{key.replace('inch', '_inch')}_counts"
        error_name = f"{key.replace('inch', '_inch')}_counts_error"
        print(f"""
            <tr>
                <td align='center'><b>{label}</b></td>
                <td align='center'>{checkbox_html(key)}</td>
                <td align='center'>{text_html(count_name)}</td>
                <td align='center'>&plusmn;</td>
                <td align='center'>{text_html(error_name, 4)}%</td>
            </tr>
        """)

    print(f"""
          </table>
        </td>

        <td valign="top" style="padding-left: 60px;">
          <div style='margin-bottom: 20px;'>
            <b>{tooltip_html("Uncertainty Input", "Uncertainty_input")}</b><br>
            <input type="radio" name="uncertainty_mode" value="manual" {"checked" if get_field("uncertainty_mode", "manual") == "manual" else ""} onclick="setUncertainty('manual')"> Manual Entry<br>
            <input type="radio" name="uncertainty_mode" value="equal" {"checked" if get_field("uncertainty_mode") == "equal" else ""} onclick="setUncertainty('equal')"> Equally Weighted<br>
            <input type="radio" name="uncertainty_mode" value="poisson" {"checked" if get_field("uncertainty_mode") == "poisson" else ""} onclick="setUncertainty('poisson')"> Poisson Distributed
          </div>

          <table>
""")

    for name, label, size in PARAMS:
        helpfile = {
            "iter": "max_iter",
            "itertesterror": "iter_error",
            "endtesterror": "final_error",
            "tempij": "max_temp",
            "smoothing": "smooth",
            "shape": "shape",
            "perturbation": "perturbation",
            "cal_factor": "cal_factor",
            "max_energy": "max_energy"
        }.get(name, None)
        print(f"<tr><td align='left'>{tooltip_html(label, helpfile)}:</td><td align='right'>{text_html(name, size)}</td></tr>")

    print(f"""
          </table>
        </td>
      </tr>
    </table><br><br>
""")

    # Add JS for uncertainty handling
    print("""
    <script>
    function setUncertainty(mode) {
      const rows = document.querySelectorAll('tr');
      rows.forEach(row => {
        const checkbox = row.querySelector('input[type="checkbox"]');
        const countInput = row.querySelector('input[name$="_counts"]');
        const errInput = row.querySelector('input[name$="_counts_error"]');
        if (checkbox && checkbox.checked && countInput && errInput) {
          const count = parseFloat(countInput.value);
          if (mode === 'equal') {
            errInput.value = '5';
          } else if (mode === 'poisson') {
            if (!isNaN(count) && count > 0) {
              errInput.value = (100 / Math.sqrt(count)).toFixed(3);
            } else {
              errInput.value = '';
            }
          }
        }
      });
    }
    </script>
    """)


    spectrum_options = [
        ("Automatic Search", "Automatic Search"),
        ("User Input", "User Input"),
        ("MAXIET", "MAXIET")
    ] + get_file_headers(SPECTRA_DIR)

    matrix_options = get_file_headers(MATRIX_DIR)
    unfolding_methods = ["SPUNIT", "BON", "MAXED", "SANDII"]
    unfolding_dropdown = dropdown("alg", sorted(unfolding_methods[:-1]) + [unfolding_methods[-1]])

    print(f"""
    <table>
    <tr>
    <td>{tooltip_html("Select a starting spectrum", "starting_spectrum")}:</td>
    <td>{dropdown("start_spec", spectrum_options)}</td>
    </tr>
    <tr>
    <td>{tooltip_html("Select a response matrix", "unfolding_matrix")}:</td>
    <td>{dropdown("matrix", matrix_options)}</td>
    </tr>
    <tr>
    <td>{tooltip_html("Select an unfolding method", "unfolding_method")}:</td>
    <td>{unfolding_dropdown}</td>
    </tr>
    </table><br>
    """)

    print('<div id="user-spectrum-section" style="display: none;">')

    print("<hr><h3>User Input Spectrum Entry:</h3>")
    print("Select the form of the neutron spectrum:<br>")
    spectrum_forms = [
        "1: (n fluence rate per bin)/(width of bin in E(MeV))",
        "2: (n fluence rate per bin)/(width of bin in ln(E/MeV))",
        "3: (n fluence rate per bin)"
    ]
    for form_option in spectrum_forms:
        checked = "checked" if get_field("spectra_form") == form_option else ""
        print(f'<input type="radio" name="spectra_form" value="{form_option}" {checked}>{form_option}<br>')
    
    spectrum_input_mode = get_field("spectrum_input_mode", "manual")
    spec_manual = "checked" if spectrum_input_mode == "manual" else ""
    spec_file = "checked" if spectrum_input_mode == "file" else ""
    
    print(f"""
    <br><p>Input your custom spectra with energy bins in the first column and the value in the second bin. The first energy bin is the lower boundary and its value is unused.</p>
    <div style="margin-bottom: 8px;">
      <input type="radio" name="spectrum_input_mode" value="manual" {spec_manual}> Manual Entry
      <input type="radio" name="spectrum_input_mode" value="file" {spec_file}> Upload File
    </div>
    
    <div style="margin-bottom: 8px;">
      <input type="file" name="user_spectrum_file">
    </div>
    <textarea name="input_spectrum" rows="31" cols="80">{get_field("input_spectrum")}</textarea>
    <hr>
    """)
    
    print('</div>')

    print("""
    <input type="submit" name="do_submit" value="Submit">
    <input type="reset" value="Reset">
    </form>

    <script>
    document.querySelectorAll('.tooltip').forEach(function(elem) {
      const tip = elem.querySelector('.tooltiptext');

      function positionTooltip(event) {
        tip.style.display = 'block';
        tip.style.visibility = 'hidden';
        tip.style.opacity = '0';

        const tipRect = tip.getBoundingClientRect();
        const viewportWidth = window.innerWidth;
        const viewportHeight = window.innerHeight;

        let mouseX = event.clientX;
        let mouseY = event.clientY;

        let top = mouseY - tipRect.height - 10;
        if (top < 5) {
          top = mouseY + 20;
        }

        let left = mouseX - tipRect.width / 2;
        left = Math.min(Math.max(5, left), viewportWidth - tipRect.width - 5);

        if (top + tipRect.height > viewportHeight - 5) {
          top = viewportHeight - tipRect.height - 5;
        }

        tip.style.position = 'fixed';
        tip.style.top = top + 'px';
        tip.style.left = left + 'px';
        tip.style.visibility = 'visible';
        tip.style.opacity = '1';
      }

      elem.addEventListener('mouseenter', positionTooltip);
      elem.addEventListener('mouseleave', function() {
        tip.style.visibility = 'hidden';
        tip.style.opacity = '0';
        tip.style.display = 'none';
      });
    });
    </script>
          
    <script>
    document.addEventListener("DOMContentLoaded", function () {
        const fileInput = document.getElementById("upload_file_input");
        const inputModeRadios = document.querySelectorAll('input[name="input_mode"]');
        const uploadRadio = [...inputModeRadios].find(r => r.value === "file");
        const manualRadio = [...inputModeRadios].find(r => r.value === "manual");

        inputModeRadios.forEach(function (radio) {
            radio.addEventListener("change", function () {
                if (this.value === "file") {
                    setTimeout(() => {
                        if (!fileInput.files.length) {
                            if (manualRadio) manualRadio.checked = true;
                        } else {
                            parseFile(fileInput.files[0]);
                        }
                    }, 0);
                }
            });
        });

        fileInput.addEventListener("change", function (e) {
            const file = e.target.files[0];
            if (!file) return;
            if (uploadRadio) uploadRadio.checked = true;
            parseFile(file);
        });

        function parseFile(file) {
            const reader = new FileReader();
            reader.onload = function (event) {
                const newlineRegex = new RegExp('\\r?\\n');
                const lines = event.target.result.split(newlineRegex);
                lines.forEach(line => {
                    if (!line.includes("=")) return;

                    const [rawKey, ...valueParts] = line.split("=");
                    const key = rawKey.trim();
                    const value = decodeURIComponent(valueParts.join("=")).trim();

                    if (!key || key.startsWith(".") || key === "Submit") return;

                    // Checkboxes
                    const checkbox = document.querySelector(`input[type="checkbox"][name="${CSS.escape(key)}"]`);
                    if (checkbox) {
                        checkbox.checked = (value.toLowerCase() === "true" || value === "1");
                        return;
                    }

                    // Radio buttons
                    const radios = document.querySelectorAll(`input[type="radio"][name="${CSS.escape(key)}"]`);
                    if (radios.length) {
                        radios.forEach(r => {
                            if (r.value === value) {
                                r.checked = true;
                            }
                        });
                        return;
                    }

                    // Dropdown/select
                    const select = document.querySelector(`select[name="${CSS.escape(key)}"]`);
                    if (select) {
                        const option = [...select.options].find(opt => opt.value === value);
                        if (option) {
                            select.value = value;
                            select.dispatchEvent(new Event("change"));
                        }
                        return;
                    }

                    // Text inputs
                    const inputs = document.getElementsByName(key);
                    if (inputs.length > 0) {
                        const input = inputs[0];
                        input.value = value;
                    }
                });
            };
            reader.readAsText(file);
        }
    });
    </script>

    <script>
    document.addEventListener("DOMContentLoaded", function () {
        const spectrumFileInput = document.querySelector('input[name="user_spectrum_file"]');
        const spectrumTextarea = document.querySelector('textarea[name="input_spectrum"]');
        const spectrumModeRadios = document.querySelectorAll('input[name="spectrum_input_mode"]');

        if (spectrumFileInput && spectrumTextarea) {
            spectrumFileInput.addEventListener("change", function (e) {
                const file = e.target.files[0];
                if (!file) return;

                const reader = new FileReader();
                reader.onload = function (event) {
                    spectrumTextarea.value = event.target.result.trim();

                    // Auto-select the "file" radio button for spectrum mode
                    spectrumModeRadios.forEach(r => {
                        if (r.value === "file") r.checked = true;
                    });
                };
                reader.readAsText(file);
            });
        }
    });
    </script>

    <script>
    document.addEventListener("DOMContentLoaded", function () {
        const startSpecDropdown = document.querySelector('select[name="start_spec"]');
        const userSpecSection = document.getElementById("user-spectrum-section");
        const inputSpectrumTextarea = document.querySelector('textarea[name="input_spectrum"]');

        function toggleUserSpectrumVisibility() {
            if (startSpecDropdown.value === "User Input") {
                userSpecSection.style.display = "block";
            } else {
                userSpecSection.style.display = "none";
                if (inputSpectrumTextarea) {
                    inputSpectrumTextarea.value = "";
                }
            }
        }

        if (startSpecDropdown && userSpecSection) {
            // Attach change handler
            startSpecDropdown.addEventListener("change", toggleUserSpectrumVisibility);
            // Run once on page load
            toggleUserSpectrumVisibility();
        }
    });
    </script>

          
    </body>
    </html>
    """)

if __name__ == "__main__":
    main()
