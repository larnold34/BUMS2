#The following is used to format the output file and provide the output of the cgi GUI
from abc import ABC, abstractmethod
from pathlib import Path
import matplotlib as plt

from bums2.core.config import Bums2Config
from bums2.core.detectors import DetectorResponses

#The first class will essentially be the template for both output files, since the CLI and CGI give the same output format
class OutputFormatter(ABC):
    #This function will define the template
    def render(self, cfg: Bums2Config, out_path: Path):
        self.start()
        self._print_static_header()
        self._summary_line(cfg)
        self._print_static_detector_header()
        for det in cfg.detectors:
            self._detector_line(det)
        self._print_static_spectrum_header()
        for i in range(cfg.num_groups):
            self._spectrum_line(cfg, i)
        self.write_plot(cfg.eend, cfg.spl, cfg.splstart, out_path)
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
    def _spectrum_line(self, cfg: Bums2Config, idx: int):
        """Print one spectrum bin row"""
    
    @abstractmethod
    def write_plot(self, eend, spl, splstart, out_path: Path):
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
    def start(self): pass

    def _summary_line(self, cfg):
        s = cfg.summary
        print(
            f"{(s.rmtx or ''):<5}"          #Response Matrix
            f"{(s.unfold or ''):>13}"       #Unfolding Method
            f"{(s.tempm or 0.0):6.2f},"     #Temperature    
            f"{(s.shape or 0.0):<4.2f}"     #Shape Factor
            f"{(s.cal or 0.0):10.4f}"       #Calibration Factor
            f"{(s.smo or 0.0):8.4f}"        #Smooth Factor
            f"{(s.perror or 0.0):9.4f}"     #Percent Error
            f"{(s.iter_count or 0):12d}\n") #Number of Iterations
    
    def _detector_line(self, det):
        print(
            f"{(det.ball or ""):<9} "           #Detector Name
            f"{(det.bce or 0.0):>12.3f} "       #Measured Counts  
            f"{(det.bcc or 0.0):>12.3f} "       #Calculated Counts  
            f"{(det.pcterr or 0.0):>10.3f}"     #Percent Difference
            )    
    
    def _print_starting_spectrum(self, cfg):
        if cfg.start_spec.upper() == "MAXIET":
            print("Starting Spectrum = MAXIET Algorithm")
        else:
            spec = Path("spectra") / cfg.best_file
            if spec.is_file():
                header = spec.read_text().splitlines()[0].rstrip()
                print(f"Starting Spectrum = {header}")
            else:
                print("Starting Spectrum = (none)")
        print()
                
    
    def _spectrum_line(self, cfg, idx):
        print(
            f"{(idx):<4d} "
            f"{(self.cfg.eend[idx+1]):>11.3e} "
            f"{(self.cfg.spc[idx]):>11.3e} "
            f"{(self.cfg.spl[idx]):>11.3e} "
            f"{(self.cfg.rem[idx]):>11.3e} "
            f"{(self.cfg.prem[idx]):>11.3e}")
        
    def write_plot(self, eend, spl, splstart, out_path):
        img_path = out_path.with_suffix(".png")
        plt.figure()
        plt.step(eend, splstart, where="pre", label="Starting Spectrum")
        plt.step(eend, spl, where="pre", label="Unfolded Spectrum")
        plt.xscale("log")
        plt.yscale("log")
        plt.xlabel("Neutron Energy(MeV)")
        plt.ylabel("Flux per Unit Lethargy")
        plt.legend()
        plt.savefig(img_path)
        print(f"\nPlot saved to {img_path}")

    def _dose_section(self, cfg):
        print("Dose Response Functions:")
        print(f"{'Name':30s} {'Response':>15s} Units")
        print("-"*60)
        dr = DetectorResponses(cfg.e_end.tolist(), cfg.spl.tolist(), dose_dir=Path("dose"), response_dir=("response"))
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
        dr = DetectorResponses(cfg.e_end.tolist(), cfg.spl.tolist())
        for name, resp, units in dr.detector_response():
            print(f"{name:30s} {resp:15.5e} {units}")
        print()
        
        
    
    def finish(self): pass

#The third class will focus on the structuring of the CGI output page
class CGIFormatter(OutputFormatter):
    def start(self):
        print("Content-Typea: text/html\n")
        print("<html><head><title>BUMS2 Results</title></head><body>")
        print("<hr>")
        print("<font face='courier'><pre>")
    
    def _summary_line(self, cfg):
        temp = cfg.tempm if cfg.start_spec.upper()=="MAXIET" else cfg.tempij
        print(
            f"{(cfg.rmtx or ''):<5}"          #Response Matrix
            f"{(cfg.unfold or ''):>13}"       #Unfolding Method
            f"{(temp or 0.0):6.2f},"          #Temperature    
            f"{(cfg.shape or 0.0):<4.2f}"     #Shape Factor
            f"{(cfg.cal or 0.0):10.4f}"       #Calibration Factor
            f"{(cfg.smo or 0.0):8.4f}"        #Smooth Factor
            f"{(cfg.perror or 0.0):9.4f}"     #Percent Error
            f"{(cfg.iter_count or 0):12d}<br>") #Number of Iterations
    
    def _detector_line(self, det):
        print(
            f"{(det.ball or ""):<9} "           #Detector Name
            f"{(det.bce or 0.0):>12.3f} "       #Measured Counts  
            f"{(det.bcc or 0.0):>12.3f} "       #Calculated Counts  
            f"{(det.pcterr or 0.0):>10.3f}<br>")    #Percent Difference
    
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
        print(
            f"{(idx):<4d} "
            f"{(self.cfg.eend[idx+1]):>11.3e} "
            f"{(self.cfg.spc[idx]):>11.3e} "
            f"{(self.cfg.spl[idx]):>11.3e} "
            f"{(self.cfg.rem[idx]):>11.3e} "
            f"{(self.cfg.prem[idx]):>11.3e}")
    
    def write_plot(self, eend, spl, splstart, out_path):
        print("</pre></font>")
        gif = out_path / f"spectrum.gif"
        print(f"<div style='text-align:center'><img src='{gif}' alt='Spectrum'></div>")
        print("font face ='courier'><pre>")
    
    def _dose_section(self, cfg):
        dr = DetectorResponses(
            ce      = cfg.e_end.tolist(),
            values  = cfg.spl.tolist(),
            dose_dir     = Path("dose"),
            response_dir = Path("response"),
        )

        def _dose_fn():
            print("<h2>Dose Response Functions</h2>")
            print("Name                           Response         Units<br>")
            print("-" * 60 + "<br>")
            for name, resp, units in dr.dose_functions():
                print(f"{name:30s} {resp:15.5e}  {units}<br>")
            print("<br>")

            print("<h2>Standard Equivalent Dose Calculations</h2>")
            print("Name                                        Value (pSv)<br>")
            print("-" * 60 + "<br>")
            for label, val, _ in dr.standard_equivalent():
                print(f"{label:45s} {val:15.5e} pSv<br>")
            print("<br>")

        self._wrap_pre(_dose_fn)

    def _detector_response_section(self, cfg):
        dr = DetectorResponses(
            ce      = cfg.e_end.tolist(),
            values  = cfg.spl.tolist(),
            response_dir = Path("response"),
        )

        def _resp_fn():
            print("<h2>Detector Responses</h2>")
            print("Name                           Response         Units<br>")
            print("-" * 60 + "<br>")
            for name, resp, units in dr.detector_responses():
                print(f"{name:30s} {resp:15.5e}  {units}<br>")
            print("<br>")

        self._wrap_pre(_resp_fn)

        
    def finish(self):
        print("</pre></font>")
        print("</body></html>")