#The following is used to format the output file and provide the output of the cgi GUI
from abc import ABC, abstractmethod
from pathlib import Path
import matplotlib.pyplot as plt
from matplotlib.ticker import LogLocator, LogFormatterMathtext
import sys
import numpy as np
import math

from bums2.core.config import Bums2Config
from bums2.core.detectors import DetectorResponses

#The first class will essentially be the template for both output files, since the CLI and CGI give the same output format
class OutputFormatter(ABC):
    #This function will define the template
    def render(self, cfg: Bums2Config, out_path: Path):
        self.start()
        print()
        print(f"rnorm = {cfg.rnorm}")
        print()
        for line in getattr(cfg, "iter_log", []):
            print(line)
        if getattr(cfg, "iter_log", []):
            print()
        self._print_static_header()
        self._summary_line(cfg)
        self._print_static_detector_header()
        for det in cfg.detectors:
            self._detector_line(det)
        self._print_starting_spectrum(cfg)
        self._print_totals(cfg)
        self._print_static_spectrum_header()
        for i in range(cfg.num_groups):
            self._spectrum_line(cfg, i)
        self.write_plot(cfg, out_path)
        self.finish()

        self._dose_section(cfg)
        self._detector_response_section(cfg)

    #All the static headers and printings
    def _print_static_header(self):
        print("-" * 80)
        print("Response    Unfold   Maxwell      Calib.  Smooth   Per Cent    No. of")
        print("Matrix       Code   Temp,Shape    Factor  Factor    Error      Iterations")
        print("________    ______  ____,_____    ______  ______   ________    __________")

    def _print_static_detector_header(self):
        print("Detectors     Measured       Calculated    Percent")
        print("              Counts         Counts        Difference")
        print("_________     ___________    ____________  __________")

    def _print_static_spectrum_header(self):
        print()
        print("BIN  ENERGY      FLUENCE     FLUENCE     DOSE EQV.   DOSE EQV.")
        print("No.  Max (MeV)   NEUT/CM2    N/CM2/LETH  (REM)       (% of Total)")

    #Abstract variables, which will be dependent on the mode of input
    @abstractmethod
    def start(self):
        """CGI will emit the HTTP preamble; CLI will do nothing"""

    @abstractmethod
    def _summary_line(self, cfg: Bums2Config):
        """Print the one-line summary"""
    
    @abstractmethod
    def _detector_line(self, det):
        """Print one detector's row"""
    @abstractmethod
    def _print_starting_spectrum(self, cfg: Bums2Config):
        """Print "Starting Spectrum = ..."""

    @abstractmethod
    def _print_totals(self, cfg: Bums2Config):
        """Prints the totals and averages"""

    @abstractmethod
    def _spectrum_line(self, cfg: Bums2Config, idx: int):
        """Print one spectrum bin row"""
    
    @abstractmethod
    def write_plot(self, cfg: Bums2Config, out_path: Path):
        """Generate and save the plot"""
    
    @abstractmethod
    def finish(self):
        """CGI closes HTML"""
    
    @abstractmethod
    def _dose_section(self, cfg: Bums2Config):
        """Dose-response curves"""
    
    @abstractmethod
    def _detector_response_section(self, cfg: Bums2Config):
        """Detector-response curves"""

#The second class will focus on the structuring of the cli output file
class CLIFormatter(OutputFormatter):
    def start(self):
        pass

    def render(self, cfg: Bums2Config, out_path: Path):
        out_path = Path(out_path)
        # Open the file and temporarily redirect stdout into it
        with out_path.open("a") as fh:
            old_stdout = sys.stdout
            sys.stdout = fh
            try:
                # Call the parent class’s render (all of your print(...)s live there)
                OutputFormatter.render(self, cfg, out_path)
            finally:
                sys.stdout = old_stdout

    def _summary_line(self, cfg):
        s = cfg.summary
        name     = cfg.matrix_name or ""
        alg      = cfg.alg or ""
        tempm    = cfg.tempm or 0.0
        shape    = cfg.shape or 0.0
        cal      = cfg.cal_factor or 0.0
        smooth   = cfg.smoothing or 0.0
        perror   = s.perror or 0.0
        iters    = cfg.iter_count or 0
        print(
            f"{name:<5}"          #Response Matrix
            f"{alg:>13}"       #Unfolding Method
            f"{tempm:6.2f},"     #Temperature    
            f"{shape:<4.2f}"     #Shape Factor
            f"{cal:10.4f}"       #Calibration Factor
            f"{smooth:8.4f}"        #Smooth Factor
            f"{perror:9.4f}"     #Percent Error
            f"{iters:12d}\n") #Number of Iterations
    
    def _detector_line(self, det):
        print(
            f"{det.ball or '':<9}   "           #Detector Name
            f"{det.bce or 0.0:>12.3f}   "       #Measured Counts  
            f"{det.bcc or 0.0:>12.3f}   "       #Calculated Counts  
            f"{det.pcterr or 0.0:>10.3f}")     #Percent Difference    
    
    def _print_starting_spectrum(self, cfg):
        if cfg.start_spec.upper() == "MAXIET":
            print()
            print("Starting Spectrum      = MAXIET Algorithm")
        elif cfg.start_spec.upper() == "USER INPUT":
            print()
            print("Starting Spectrum = User Input Spectrum")   
        else:
            spec = cfg.best_file
            if spec.is_file():
                header = spec.read_text().splitlines()[0].rstrip()
                print()
                print(f"Starting Spectrum      = {header}")
        print()
                
    
    def _spectrum_line(self, cfg, idx):
        s = cfg.summary
        print(
            f"{(idx):<4d} "
            f"{(cfg.e_end[idx+1]):>11.3e} "
            f"{(s.spc[idx]):>11.3e} "
            f"{(cfg.spl[idx]):>11.3e} "
            f"{(s.rem[idx]):>11.3e} "
            f"{(s.prem[idx]):>11.3e}")
    
    def _print_totals(self, cfg):
        s = cfg.summary
        print(f"Total Fluence          = {s.sumspc:>11.3e} Neutrons/cm2\n")
        print(f"Ave. Energy (Less Th.) = {s.aveen:>11.3e} MeV\n")
        print(f"Dose Equivalent        = {s.sumrem:>11.3e} REM\n")
        print()
        
    def write_plot(self, cfg, out_path):
        import os
        from pathlib import Path

        # Detect CGI mode and adjust output path for image accordingly
        if "GATEWAY_INTERFACE" in os.environ:
            # CGI mode — serve image from public /images folder
            img_filename = "spectrum_output.png"
            img_path = Path("/var/www/html/images") / img_filename
            web_img_src = f"/images/{img_filename}"
        else:
            # CLI mode — save alongside the output file
            img_path = out_path.with_suffix(".png")
            web_img_src = None  # Not used in CLI mode

        # === Plotting logic (unchanged) ===
        plt.figure(figsize=(8,5))
        n = cfg.num_groups

        edges = np.array(cfg.e_end[:n+1], dtype=float)
        unfolded = np.empty(n+1, dtype=float)
        starting  = np.empty(n+1, dtype=float)
        unfolded[0]  = cfg.spl[0]
        unfolded[1:] = cfg.spl[:n]
        starting[0]  = cfg.splstart[0]
        starting[1:] = cfg.splstart[:n]

        emin, emax = edges[0], edges[-1]
        min_exp = math.floor(math.log10(emin))
        max_exp = math.ceil (math.log10(emax))
        x_decades = [10**i for i in range(min_exp, max_exp+1)]

        all_vals = np.hstack([unfolded, starting])
        ymax = all_vals.max()
        positive_vals = all_vals[all_vals > 0]
        if len(positive_vals) == 0:
            min_ye = -10  # fallback for all-zero case
        else:
            min_ye = math.floor(math.log10(positive_vals.min()))
        max_ye = math.ceil (math.log10(ymax))
        y_decades = [10**i for i in range(min_ye, max_ye+1)]

        ax = plt.gca()
        ax.set_xscale("log")
        ax.set_yscale("log")

        ax.set_title("Bonner Sphere Unfolding", fontsize=12, fontweight="bold")
        ax.grid(True, which="both", linestyle=":", linewidth=0.5)
        ax.set_xlabel("Neutron Energy (MeV)")
        ax.set_ylabel("Neutron Flux per Unit Lethargy")

        ax.set_xticks(x_decades)
        ax.xaxis.set_major_locator(LogLocator(base=10.0, subs=(1.0,), numticks=len(x_decades)))
        ax.xaxis.set_minor_locator(LogLocator(base=10.0, subs=range(2,10), numticks=100))
        ax.xaxis.set_major_formatter(LogFormatterMathtext(base=10, labelOnlyBase=True))

        ax.set_yticks(y_decades)
        ax.yaxis.set_major_locator(LogLocator(base=10.0, subs=(1.0,), numticks=len(y_decades)))
        ax.yaxis.set_minor_locator(LogLocator(base=10.0, subs=range(2,10), numticks=100))
        ax.yaxis.set_major_formatter(LogFormatterMathtext(base=10, labelOnlyBase=True))

        ax.step(edges, unfolded, where="pre", label="Unfolded Spectrum")
        ax.step(edges, starting,  where="pre", label="Starting Spectrum")

        ax.set_xlim(10**min_exp, 10**max_exp)
        ax.set_ylim(10**min_ye,  10**max_ye)

        ax.legend(loc="upper right", frameon=False)
        plt.tight_layout()
        plt.savefig(img_path, dpi=150)

        # === Output rendering ===
        print(f"\nPlot saved to {img_path}")
        if web_img_src:
            print(f"<div style='text-align:center'><img src='{web_img_src}' alt='Spectrum Plot' style='max-width:100%; height:auto;'></div>")



    def _dose_section(self, cfg):
        print("Dose Response Functions:")
        print(f"{'Name':30s} {'Response':>15s} Units")
        print("-"*60)
        dr = DetectorResponses(cfg.ce, cfg.spc, dose_dir=Path("dose"), response_dir=("response"))
        for name, resp, units in dr.dose_functions():
            print(f"{name:30s} {resp:15.5e} {units}")
        print()

        print("Standard Equivalent Dose Calculations:")
        print(f"{'Name':45s} {'Value (pSv):>15s'}")
        print("-"*60)
        for label, val, _ in dr.standard_equivalent():
            print(f"{label:45s} {val:15.5e} pSv")
        print()
    
    def _detector_response_section(self, cfg):
        print("Detector Responses:")
        print(f"{'Name':30s} {'Response':>15s} Units")
        print("-"*60)
        dr = DetectorResponses(cfg.ce, cfg.spc)
        for name, resp, units in dr.detector_response():
            print(f"{name:30s} {resp:15.5e} {units}")
        print()
        
        
    
    def finish(self): pass

#The third class will focus on the structuring of the CGI output page
class CGIFormatter(OutputFormatter):
    from pathlib import Path

    # Automatically resolve the base BUMS2 directory regardless of where this file lives
    # This finds the outermost /BUMS2 directory by moving up until 'SPECTRA' is found
    def find_project_root():
        current = Path(__file__).resolve()
        for parent in current.parents:
            if (parent / "SPECTRA").exists():
                return parent
        raise FileNotFoundError("Could not locate project root with SPECTRA directory.")

    # Set the canonical project root path
    PROJECT_ROOT = find_project_root()

    # Define paths based on that root
    SPECTRA_DIR = PROJECT_ROOT / "SPECTRA"
    MATRIX_DIR = PROJECT_ROOT / "MATRIX"
    HELP_DIR = PROJECT_ROOT / "HELP"

    def start(self):
        print("Content-Type: text/html\n")
        print("<html><head><title>BUMS2 Results</title></head><body>")
        print("<hr>")
        print("<font face='courier'><pre>")

    def _summary_line(self, cfg):
        temp = cfg.tempm if cfg.start_spec.upper() == "MAXIET" else cfg.tempij
        s = cfg.summary
        print(
            f"{cfg.matrix_name or '':<5}"          # Response Matrix
            f"{cfg.alg or '':>13}"                 # Unfolding Method
            f"{temp or 0.0:6.2f},"                 # Temperature    
            f"{cfg.shape or 0.0:<4.2f}"           # Shape Factor
            f"{cfg.cal_factor or 0.0:10.4f}"      # Calibration Factor
            f"{cfg.smoothing or 0.0:8.4f}"        # Smooth Factor
            f"{s.perror or 0.0:9.4f}"             # Percent Error
            f"{cfg.iter_count or 0:12d}<br>"      # Number of Iterations
        )

    def _detector_line(self, det):
        print(
            f"{det.ball or '':<9} "            # Detector Name
            f"{det.bce or 0.0:>12.3f} "       # Measured Counts  
            f"{det.bcc or 0.0:>12.3f} "       # Calculated Counts  
            f"{det.pcterr or 0.0:>10.3f}<br>" # Percent Difference
        )

    def _print_starting_spectrum(self, cfg):
        if cfg.start_spec.upper() == "MAXIET":
            print("Starting Spectrum = MAXIET Algorithm<br>")
        else:
            spec = Path("spectra") / cfg.best_file
            if spec.is_file():
                header = spec.read_text().splitlines()[0].rstrip()
                print(f"Starting Spectrum = {header}<br>")
            else:
                print("Starting Spectrum = (none)<br>")
        print()

    def _spectrum_line(self, cfg, idx):
        s = cfg.summary
        #print("BIN  ENERGY      FLUENCE     FLUENCE     DOSE EQV.   DOSE EQV.<br>")
        #print("No.  Max (MeV)   NEUT/CM2    N/CM2/LETH  (REM)       (% of Total)<br>")
        print(
            f"{(idx):<4d} "
            f"{(cfg.e_end[idx+1]):>11.3e} "
            f"{(s.spc[idx]):>11.3e} "
            f"{(s.spl[idx]):>11.3e} "
            f"{(s.rem[idx]):>11.3e} "
            f"{(s.prem[idx]):>11.3e}"
        )

    def _print_totals(self, cfg):
        s = cfg.summary
        print(f"Total Fluence          = {s.sumspc:>11.3e} Neutrons/cm2<br>")
        print(f"Ave. Energy (Less Th.) = {s.aveen:>11.3e} MeV<br>")
        print(f"Dose Equivalent        = {s.sumrem:>11.3e} REM<br>")
    #LiDebug
    #def write_plot(self, cfg, out_path):
    #    print("</pre></font>")
    #    gif = out_path / "spectrum.gif"
    #    print(f"<div style='text-align:center'><img src='{gif}' alt='Spectrum'></div>")
    #    print("<font face='courier'><pre>")
    #LiDebug
    #def _dose_section(self, cfg):
    #    dr = DetectorResponses(
    #        ce      = cfg.e_end.tolist(),
    #        values  = cfg.spl.tolist(),
    #        dose_dir     = Path("dose"),
    #        response_dir = Path("response"),
    #    )
    #    def _dose_fn():
    #        print("<h2>Dose Response Functions</h2>")
    #        print("Name                           Response         Units<br>")
    #        print("-" * 60 + "<br>")
    #        for name, resp, units in dr.dose_functions():
    #            print(f"{name:30s} {resp:15.5e}  {units}<br>")
    #        print("<br>")
    #        print("<h2>Standard Equivalent Dose Calculations</h2>")
    #        print("Name                                        Value (pSv)<br>")
    #        print("-" * 60 + "<br>")
    #        for label, val, _ in dr.standard_equivalent():
    #            print(f"{label:45s} {val:15.5e} pSv<br>")
    #        print("<br>")
    #    self._wrap_pre(_dose_fn)
    #def _detector_response_section(self, cfg):
    #    dr = DetectorResponses(
    #        ce      = cfg.e_end.tolist(),
    #        values  = cfg.spl.tolist(),
    #        response_dir = Path("response"),
    #    )
    #    def _resp_fn():
    #        print("<h2>Detector Responses</h2>")
    #        print("Name                           Response         Units<br>")
    #        print("-" * 60 + "<br>")
    #        for name, resp, units in dr.detector_responses():
    #            print(f"{name:30s} {resp:15.5e}  {units}<br>")
    #        print("<br>")
    #    self._wrap_pre(_resp_fn)
    #LiDebug replaced with what's below:
        # Helper to temporarily close the <pre> block, emit HTML, then reopen <pre>
    def _wrap_pre(self, fn):
        # close pre/font
        print("</pre></font>")
        try:
            fn()
        finally:
            # reopen pre/font for subsequent fixed-width output
            print("<font face='courier'><pre>")

    def write_plot(self, cfg, out_path: Path):
        """
        Generate the spectrum plot (same as CLI) and save to output_path.
        Then emit an <img> tag pointing at a web-accessible path if possible.
        """
        # Ensure out_path is a Path and exists
        out_path = Path(out_path)
        out_path.mkdir(parents=True, exist_ok=True)

        # Build image path in output folder (web server should serve this folder)
        img_filename = "spectrum.png"
        img_path = out_path / img_filename

        # === Plotting logic (copied from CLI version) ===
        import matplotlib.pyplot as plt
        from matplotlib.ticker import LogLocator, LogFormatterMathtext
        import numpy as np
        import math

        plt.figure(figsize=(8,5))
        n = cfg.num_groups

        edges = np.array(cfg.e_end[:n+1], dtype=float)
        unfolded = np.empty(n+1, dtype=float)
        starting  = np.empty(n+1, dtype=float)

        unfolded[0]  = cfg.spl[0]
        unfolded[1:] = cfg.spl[:n]

        starting[0]  = cfg.splstart[0]
        starting[1:] = cfg.splstart[:n]

        emin, emax = edges[0], edges[-1]
        min_exp = math.floor(math.log10(emin))
        max_exp = math.ceil (math.log10(emax))
        x_decades = [10**i for i in range(min_exp, max_exp+1)]

        #all_vals = np.hstack([unfolded, starting])
        #ymin, ymax = all_vals.min(), all_vals.max()
        #min_ye = math.floor(math.log10(ymin))
        #max_ye = math.ceil (math.log10(ymax))
        #y_decades = [10**i for i in range(min_ye, max_ye+1)]
        all_vals = np.hstack([unfolded, starting])
        ymax = all_vals.max()
        
        # Handle zeros safely (same as CLI version)
        positive_vals = all_vals[all_vals > 0]
        if len(positive_vals) == 0:
            min_ye = -10  # fallback for all-zero case
        else:
            min_ye = math.floor(math.log10(positive_vals.min()))
        
        max_ye = math.ceil(math.log10(ymax))
        y_decades = [10**i for i in range(min_ye, max_ye+1)]

        ax = plt.gca()
        ax.set_xscale("log")
        ax.set_yscale("log")

        ax.set_title("Bonner Sphere Unfolding", fontsize=12, fontweight="bold")
        ax.grid(True, which="both", linestyle=":", linewidth=0.5)
        ax.set_xlabel("Neutron Energy (MeV)")
        ax.set_ylabel("Neutron Flux per Unit Lethargy")

        ax.set_xticks(x_decades)
        ax.xaxis.set_major_locator(LogLocator(base=10.0, subs=(1.0,), numticks=len(x_decades)))
        ax.xaxis.set_minor_locator(LogLocator(base=10.0, subs=range(2,10), numticks=100))
        ax.xaxis.set_major_formatter(LogFormatterMathtext(base=10, labelOnlyBase=True))

        ax.set_yticks(y_decades)
        ax.yaxis.set_major_locator(LogLocator(base=10.0, subs=(1.0,), numticks=len(y_decades)))
        ax.yaxis.set_minor_locator(LogLocator(base=10.0, subs=range(2,10), numticks=100))
        ax.yaxis.set_major_formatter(LogFormatterMathtext(base=10, labelOnlyBase=True))

        ax.step(edges, unfolded, where="pre", label="Unfolded Spectrum")
        ax.step(edges, starting,  where="pre", label="Starting Spectrum")

        ax.set_xlim(10**min_exp, 10**max_exp)
        ax.set_ylim(10**min_ye,  10**max_ye)

        ax.legend(loc="upper right", frameon=False)
        plt.tight_layout()
        plt.savefig(img_path, dpi=150)
        plt.close()

        # === Emit HTML img tag ===
        # Try to compute a web-accessible src by seeing if img_path is under /var/www/html
        try:
            web_root = Path("/var/www/html").resolve()
            img_resolved = img_path.resolve()
            if str(img_resolved).startswith(str(web_root)):
                web_img_src = "/" + str(img_resolved.relative_to(web_root)).replace("\\", "/")
            else:
                # If not under web root, emit an absolute file path (may or may not be accessible),
                # but the most common deployment will put the CGI's output_path under web root.
                web_img_src = f"file://{img_resolved}"
        except Exception:
            web_img_src = f"file://{img_path}"

        # Close pre, emit image HTML, reopen pre
        def _emit_img():
            print(f"<div style='text-align:center'><img src='{web_img_src}' alt='Spectrum Plot' style='max-width:100%; height:auto;'></div>")
            print(f"<p style='text-align:center; font-family:monospace;'>Plot saved to {img_path}</p>")
        self._wrap_pre(_emit_img)

    def _dose_section(self, cfg):
        """
        Emit dose HTML inside the page. Use _wrap_pre to ensure we are outside the <pre> block.
        This mirrors the CLI dose printing but as formatted HTML.
        """
        from bums2.core.summary import Summary  # if you need types
        dr = DetectorResponses(cfg.ce, cfg.spc, dose_dir=Path("dose"), response_dir=Path("response"))

        def _dose_fn():
            print("<h2>Dose Response Functions</h2>")
            print("<table>")
            print("<tr><th style='text-align:left'>Name</th><th style='text-align:right'>Response</th><th>Units</th></tr>")
            for name, resp, units in dr.dose_functions():
                print(f"<tr><td>{name}</td><td style='text-align:right'>{resp:15.5e}</td><td>{units}</td></tr>")
            print("</table>")
            print("<br>")
            print("<h2>Standard Equivalent Dose Calculations</h2>")
            print("<table>")
            print("<tr><th style='text-align:left'>Name</th><th style='text-align:right'>Value (pSv)</th></tr>")
            for label, val, _ in dr.standard_equivalent():
                print(f"<tr><td>{label}</td><td style='text-align:right'>{val:15.5e} pSv</td></tr>")
            print("</table><br>")
        self._wrap_pre(_dose_fn)

    def _detector_response_section(self, cfg):
        """
        Emit detector response table. Use same API as CLI (detector_response()).
        """
        dr = DetectorResponses(cfg.ce, cfg.spc, response_dir=Path("response"))

        def _resp_fn():
            print("<h2>Detector Responses</h2>")
            print("<table>")
            print("<tr><th style='text-align:left'>Name</th><th style='text-align:right'>Response</th><th>Units</th></tr>")
            # Use the same method name as the CLI version
            for name, resp, units in dr.detector_response():
                print(f"<tr><td>{name}</td><td style='text-align:right'>{resp:15.5e}</td><td>{units}</td></tr>")
            print("</table><br>")
        self._wrap_pre(_resp_fn)

    @staticmethod
    def run_cgi(form_dict, output_path):
        from bums2.io import input as input_module
        from bums2.io.matrix import ResponseMatrix
        from bums2.io.user_spectrum import UserSpectrumLoader
        from bums2.core.standardize import Standardize
        from bums2.core.summary import SummaryCalculator
        from bums2.algorithms.guess import SpectrumGuesser
        from bums2.algorithms.maxiet import maxiet
        from bums2.algorithms.maxed import maxed
        from bums2.algorithms.sand2 import sand2
        from bums2.algorithms.bon import bon
        from bums2.algorithms.spunit import spunit
        from bums2.utils.dose import DoseConverter
        import numpy as np
        from pathlib import Path

        cfg = input_module.run(form_dict)

        project_root = Path(__file__).resolve().parent.parent.parent
        matrix_dir = project_root / "MATRIX"

        resp = ResponseMatrix.from_file(
            matrix_name=cfg.matrix_name,
            detector_mask=cfg.detector_mask,
            max_energy=cfg.max_energy,
            matrix_dir=matrix_dir,
        )

        cfg.e_end = list(resp.e_end)
        cfg.iter_log = []
        cfg.num_det = resp.mat.shape[1]
        cfg.num_groups = resp.num_bins

        e_end = np.array(cfg.e_end, dtype=float)
        ce = np.zeros(cfg.num_groups, dtype=float)
        wdleth = np.zeros(cfg.num_groups, dtype=float)
        aleth = np.zeros((cfg.num_det, cfg.num_groups), dtype=float)

        for i in range(cfg.num_groups):
            ce[i] = (e_end[i] * e_end[i+1])**0.5
            wdleth[i] = np.log(e_end[i+1]) - np.log(e_end[i])
        for j in range(cfg.num_det):
            for i in range(cfg.num_groups):
                aleth[j, i] = resp.mat[i+1, j] * wdleth[i]

        cfg.ce = ce
        cfg.aleth = aleth

        bce = np.array(cfg.measured_counts, dtype=float)
        errbce = np.array(cfg.measured_errors, dtype=float)

        mask = np.array(cfg.detector_mask, dtype=bool)
        bce = bce[mask]
        errbce = errbce[mask]

        dead = cfg.dead
        bce = bce / (1.0 - dead * bce)

        sum_err = errbce.sum()
        n = len(errbce)
        whtbce = np.array([
            (sum_err / (n * e)) if e != 0.0 else 0.0
            for e in errbce
        ], dtype=float)

        cfg.bce = bce
        cfg.errbce = errbce
        cfg.whtbce = whtbce

        if cfg.start_spec.upper().startswith("MAXIET"):
            spli, tempm = maxiet(cfg).maxiet_spectrum(
                ce=ce,
                bce=bce,
                aleth=aleth,
                errbce=errbce,
                whtbce=whtbce,
                out=None
            )
            cfg.tempm = tempm
        elif cfg.start_spec.upper().startswith("USER INPUT"):
            loader = UserSpectrumLoader(cfg, ce)
            spli = loader.load()
        else:
            from pathlib import Path

            # Use project root to build absolute spectra path
            project_root = Path(__file__).resolve().parent.parent
            spectra_dir = project_root / "SPECTRA"

            sg = SpectrumGuesser(cfg, spectra_dir=spectra_dir, standardize=True)
#LiDebug first, previous below
            best_file, spli = sg.guess(form_dict.get("input_spectrum"))
            #best_file, spli = sg.guess(None)
            cfg.best_file = best_file
            spli = np.array(spli, dtype=float)

        alethnew, spl_unit = Standardize.trans_mat(aleth, spli)
        spl = Standardize.normalize(bce, errbce, alethnew, cfg.num_det, cfg.num_groups, spl_unit)
        sf = Standardize.scale_factor(bce, errbce, aleth, cfg.num_det, cfg.num_groups, spli) * cfg.cal_factor
        cfg.rnorm = sf
        bcc = Standardize.cal_response(alethnew, spl)

        error = Standardize.fit_error(bce, bcc, whtbce)
        chi = Standardize.chi_squared(cfg.num_det, bce, bcc, errbce)

        splstart = np.zeros_like(spli)
        for i in range(cfg.num_groups):
            splstart[i] = spli[i] * sf

        iter_count = 0
        starterror = np.sqrt(error / cfg.num_det) * 100
        alg = cfg.alg.upper()

        if "MAXED" in alg:
            spl, splstart = maxed(cfg).maxed_unfold(
                resp.mat, bce, errbce, spl, cfg.num_groups, cfg.num_det)
        elif "SANDII" in alg:
            spl, splstart = sand2(cfg).sand2_unfold(
                resp.mat, bce, errbce, spl, cfg.num_groups, cfg.num_det)
        else:
            runner = bon(cfg) if "BON" in alg else spunit(cfg)
            unfold = lambda it: runner.bon_unfolding(alethnew, bce, spl, cfg.num_groups, cfg.num_det, it) if "BON" in alg else runner.spunit_unfold(alethnew, bce, bcc, spl, cfg.num_groups, cfg.num_det, it)

            cfg.iter_log.append(
                f"Iteration = {iter_count:<4d}  Error = {starterror:>7.3f}  Chi-Squared = {chi:>11.3E}"
            )

            if cfg.iter > 0:
                old_chi = float("inf")
                while True:
                    spl, bcc, iter_count = unfold(iter_count)
                    error = Standardize.fit_error(bce, bcc, whtbce)
                    chi = Standardize.chi_squared(cfg.num_det, bce, bcc, errbce)
                    up_error = np.sqrt(error / cfg.num_det) * 100

                    cfg.iter_log.append(
                        f"Iteration = {iter_count:<4d}  Error = {up_error:>7.3f}  Chi-Squared = {chi:>11.3E}"
                    )

                    if not (
                        chi / old_chi < cfg.tstrat
                        and iter_count + cfg.itertesterror <= cfg.iter
                        and error > cfg.tstper
                    ):
                        break
                    old_chi = chi

        from bums2.core.summary import SummaryCalculator
        from bums2.utils.dose import DoseConverter
        from bums2.core.summary import Summary

        calc = SummaryCalculator(
            ce=ce,
            wdleth=wdleth,
            spli=spli,
            spl=spl,
            alethnew=alethnew,
            bce=bce,
            bcc=bcc,
            errbce=errbce,
            cal=cfg.cal_factor,
            df=DoseConverter(),
            cfg=cfg,
        )
        summary: Summary = calc.compute(
            alg=cfg.alg,
            start_spec=cfg.start_spec,
            iter_count=iter_count,
            tempij=cfg.tempij,
        )

        cfg.summary = summary
        cfg.spc = summary.spc.tolist()
        cfg.spl = spl.tolist()
        cfg.rem = summary.rem.tolist()
        cfg.prem = summary.prem.tolist()
        cfg.splstart = splstart.tolist()
        cfg.pcterr = summary.pcterr.tolist()
        cfg.iter_count = iter_count
        cfg.ce = ce

        for det, bcc_val, pct in zip(cfg.detectors, bcc, summary.pcterr):
            det.bcc = bcc_val
            det.pcterr = pct

        # Finally: render
        CGIFormatter().render(cfg, output_path)

    def finish(self):
        print("</pre></font>")
        print("</body></html>")
    