#The following script will be used to parse through input files if using CLI or the html input if using the website
import os
import argparse
import cgi
from pathlib import Path
from urllib.parse import unquote
from typing import Dict
from types import SimpleNamespace

from bums2.core.config import Bums2Config

class InputParser:

    #This is to define a class object that will be called upon later
    DET_NAMES = ["bare", "barecd", "2inch", "2inchcd", "3inch", "3inchcd", "5inch", "5inchcd", "8inch", "10inch", "12inch", "15inch", "18inch"]

    #The following will make it so a file input and output path is required when calling from the command line
    def __init__(self):
        self._parser = argparse.ArgumentParser(prog="bums2", description="Run BUMS2 processing pipeline")
        #Take an input file path
        self._parser.add_argument("-i", "--input-file", type=Path, required=True, help="key=Value parameter file")
        #Take an output file path
        self._parser.add_argument("-o", "--output-file", type=Path, required=True, help="Where to write the main output")
    
    #The following will identify if the input is coming from the command line or from the cgi
    def parse(self) -> Bums2Config:
        if "GATEWAY_INTERFACE" in os.environ:
            return self._parse_cgi()
        else:
            return self._parse_cli()
    
    #The following will add underscores to some of the detector_names to make sure the dataclass can assign the inputs properly
    def _key_with_underscore(self, name: str) -> str:
        i=0
        name = name.replace('-', '_')
        while i < len(name) and name[i].isdigit():
            i += 1
        if i > 0:
            name = name[:i] + "_" + name[i:]
        return name
        
    #The following parse the data if using the CLI 
    def _parse_cli(self) -> Bums2Config:
        args = self._parser.parse_args()
        if not args.input_file or not args.output_file:
            self._parser.error("Both --input-file and --output-file paths are required to use the CLI")
        kv = self._read_kv_file(args.input_file)

        #The following will define all the detector information, which will be relevant for the dataclass config.py
        mask = []
        counts = []
        errors = []

        for name in self.DET_NAMES:
            flag = kv.get(name, "").lower() in ("1", "true", "yes")
            mask.append(flag)

            #The counts and errors need the underscores in the names
            base = self._key_with_underscore(name)

            cnt = kv.get(f"{base}_counts", "")
            counts.append(cnt if cnt else "0")

            err = kv.get(f"{base}_counts_error", "")
            errors.append(float(err) if err else 0.0)

        kv["detector_mask"]   = ",".join("true" if f else "false" for f in mask)
        kv["measured_counts"] = ",".join(str(c) for c in counts)
        kv["measured_errors"] = ",".join(str(e) for e in errors)

        kv["input_file"] = str(args.input_file)
        kv["output_file"] = str(args.output_file)

        if "matrix" in kv:
            kv["matrix_name"] = kv["matrix"]

        cfg = Bums2Config.from_dict(kv)

        cfg.detectors.clear()
        for name, used, bce, err in zip(self.DET_NAMES, cfg.detector_mask, cfg.measured_counts, cfg.measured_errors):
            if not used:
                continue
            cfg.detectors.append(SimpleNamespace(ball = name, bce = bce, bcc = 0.0, pcterr = 0.0))
        return cfg
    
    #The following will parse the data if from a cgi input
    def _parse_cgi(self) -> Bums2Config:
        form = cgi.FieldStorage()
        kv: Dict[str, str] = {}
        for key in form.keys():
            val = form.getvalue(key, "")
            kv[key] = unquote(val)

        #The following will define all the detector information, which will be relevant for the dataclass config.py
        mask = []
        counts = []
        errors = []

        for name in self.DET_NAMES:
            flag = kv.get(name, "").lower() in ("1", "true", "yes")
            mask.append(flag)

            #The counts and errors need the underscores in the names
            base = self._key_with_underscore(name)

            cnt = kv.get(f"{base}_counts", "")
            counts.append(cnt if cnt else "0")

            err = kv.get(f"{base}_counts_error", "")
            errors.append(float(err) if err else 0.0)

        kv["detector_mask"]   = ",".join("true" if f else "false" for f in mask)
        kv["measured_counts"] = ",".join(str(c) for c in counts)
        kv["measured_errors"] = ",".join(str(e) for e in errors)

        kv["input_file"] = os.environ.get("SCRIPT_FILENAME", "")
        kv["output_file"] = ""

        if "matrix" in kv:
            kv["matrix_name"] = kv["matrix"]

        cfg = Bums2Config.from_dict(kv)

        cfg.detectors.clear()
        for name, used, bce, err in zip(self.DET_NAMES, cfg.detector_mask, cfg.measured_counts, cfg.measured_errors):
            if not used:
                continue
            cfg.detectors.append(SimpleNamespace(ball = name, bce = bce, bcc = 0.0, pcterr = 0.0))
        return cfg
    
    #The following will read the input and decode it since the inputs are still in URI format
    def _read_kv_file(self, path: Path) -> Dict[str,str]:
        data: Dict[str, str] = {}
        for raw in path.read_text(encoding="utf-8").splitlines():
            line = raw.strip()
            if not line or line.startswith(";"):
                continue
            key, sep, val = line.partition("=")
            key = key.strip()
            val = val if sep else ""
            data[key] = unquote(val)
        return data

if __name__ == "__main__":
    cfg = InputParser().parse()
    print("CONFIGURED AS:\n", cfg)
    

