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
        img_path = out_path.with_suffix(".png")
        plt.figure(figsize=(8,5))

        n = cfg.num_groups

        # build the EXACT same (eend[i], spl[i-1]) arrays:
        edges = np.array(cfg.e_end[:n+1], dtype=float)   # length = n+1
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

        # title, grid, labels
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

        # step plots
        ax.step(edges, unfolded, where="pre", label="Unfolded Spectrum")
        ax.step(edges, starting,  where="pre", label="Starting Spectrum")        

        # tighten to the data
        ax.set_xlim(10**min_exp,   10**(max_exp))
        ax.set_ylim(10**min_ye,    10**(max_ye))

        ax.legend(loc="upper right", frameon=False)
        plt.tight_layout()
        plt.savefig(img_path, dpi=150)
        print(f"\nPlot saved to {img_path}")


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
# class CGIFormatter(OutputFormatter):
#     def start(self):
#         print("Content-Typea: text/html\n")
#         print("<html><head><title>BUMS2 Results</title></head><body>")
#         print("<hr>")
#         print("<font face='courier'><pre>")
    
#     def _summary_line(self, cfg):
#         temp = cfg.tempm if cfg.start_spec.upper()=="MAXIET" else cfg.tempij
#         s = cfg.summary
#         print(
#             f"{cfg.matrix_name or '':<5}"          #Response Matrix
#             f"{cfg.alg or '':>13}"       #Unfolding Method
#             f"{temp or 0.0:6.2f},"          #Temperature    
#             f"{cfg.shape or 0.0:<4.2f}"     #Shape Factor
#             f"{cfg.cal_factor or 0.0:10.4f}"       #Calibration Factor
#             f"{cfg.smoothing or 0.0:8.4f}"        #Smooth Factor
#             f"{s.perror or 0.0:9.4f}"     #Percent Error
#             f"{cfg.iter_count or 0:12d}<br>") #Number of Iterations
    
#     def _detector_line(self, det):
#         print(
#             f"{det.ball or '':<9} "           #Detector Name
#             f"{det.bce or 0.0:>12.3f} "       #Measured Counts  
#             f"{det.bcc or 0.0:>12.3f} "       #Calculated Counts  
#             f"{det.pcterr or 0.0:>10.3f}<br>")    #Percent Difference
    
#     def _print_starting_spectrum(self, cfg):
#         if cfg.start_spec.upper() == "MAXIET":
#             print("Starting Spectrum = MAXIET Algorithm<br>")
#         else:
#             spec = Path("spectra") / cfg.best_file
#             if spec.is_file():
#                 header = spec.read_text().splitlines()[0].rstrip()
#                 print(f"Starting Spectrum = {header}<br>")
#             else:
#                 print("Starting Spectrum = (none)<br>")
#         print()
        
#     def _spectrum_line(self, cfg, idx):
#         s = cfg.summary
#         print("BIN  ENERGY      FLUENCE     FLUENCE     DOSE EQV.   DOSE EQV.<br>")
#         print("No.  Max (MeV)   NEUT/CM2    N/CM2/LETH  (REM)       (% of Total)<br>")
#         print(
#             f"{(idx):<4d} "
#             f"{(cfg.e_end[idx+1]):>11.3e} "
#             f"{(s.spc[idx]):>11.3e} "
#             f"{(s.spl[idx]):>11.3e} "
#             f"{(s.rem[idx]):>11.3e} "
#             f"{(s.prem[idx]):>11.3e}")
        
#     def _print_totals(self, cfg):
#         s = cfg.summary
#         print(f"Total Fluence          = {s.sumspc:>11.3e} Neutrons/cm2<br>")
#         print(f"Ave. Energy (Less Th.) = {s.aveen:>11.3e} MeV<br>")
#         print(f"Dose Equivalent        = {s.sumrem:>11.3e} REM<br>")
 
#     def write_plot(self, cfg, out_path):
#         print("</pre></font>")
#         gif = out_path / f"spectrum.gif"
#         print(f"<div style='text-align:center'><img src='{gif}' alt='Spectrum'></div>")
#         print("font face ='courier'><pre>")
    
#     def _dose_section(self, cfg):
#         dr = DetectorResponses(
#             ce      = cfg.e_end.tolist(),
#             values  = cfg.spl.tolist(),
#             dose_dir     = Path("dose"),
#             response_dir = Path("response"),
#         )

#         def _dose_fn():
#             print("<h2>Dose Response Functions</h2>")
#             print("Name                           Response         Units<br>")
#             print("-" * 60 + "<br>")
#             for name, resp, units in dr.dose_functions():
#                 print(f"{name:30s} {resp:15.5e}  {units}<br>")
#             print("<br>")

#             print("<h2>Standard Equivalent Dose Calculations</h2>")
#             print("Name                                        Value (pSv)<br>")
#             print("-" * 60 + "<br>")
#             for label, val, _ in dr.standard_equivalent():
#                 print(f"{label:45s} {val:15.5e} pSv<br>")
#             print("<br>")

#         self._wrap_pre(_dose_fn)

#     def _detector_response_section(self, cfg):
#         dr = DetectorResponses(
#             ce      = cfg.e_end.tolist(),
#             values  = cfg.spl.tolist(),
#             response_dir = Path("response"),
#         )

#         def _resp_fn():
#             print("<h2>Detector Responses</h2>")
#             print("Name                           Response         Units<br>")
#             print("-" * 60 + "<br>")
#             for name, resp, units in dr.detector_responses():
#                 print(f"{name:30s} {resp:15.5e}  {units}<br>")
#             print("<br>")

#         self._wrap_pre(_resp_fn)

        
#     def finish(self):
#         print("</pre></font>")
#         print("</body></html>")