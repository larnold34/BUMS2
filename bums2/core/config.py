# bums2/core/config.py
from dataclasses import dataclass, field, fields, MISSING
from pathlib import Path
from typing import Any, Dict, List, Optional, Union, get_origin, get_args

@dataclass
class Bums2Config:
    # ——— User input parameters ———
    max_energy:    float
    iter:          int
    itertesterror: int
    endtesterror:  float
    tempij:        float
    smoothing:     float
    shape:         float
    perturbation:   float
    cal_factor:    float

    matrix_name:   str
    start_spec:    str
    alg:           str

    input_file:      Optional[Path] = None
    output_file:     Optional[Path] = None
    detector_mask:   List[bool]    = field(default_factory=list)
    measured_counts: List[float]   = field(default_factory=list)
    measured_errors: List[float]   = field(default_factory=list)

    # ——— Response matrix parameter ———
    e_end: Optional[List[float]] = None

    # ——— Initialized parameters ———
    slopej: float = 0.0
    slpmin: float = 0.0
    slpmax: float = 0.51
    perslp: float = 0.01
    thermj: float = 1.0
    themmin: float = 0.1
    themmax: float = 100.0
    dead: float = 0.0
    shp: float = 0.01
    tstrat: float = 0.999
    jx: int = 1
    kx: int = 1
    ls: int = 1
    jjj: int = 0
    spmx: float = 1.0

    tstper: float = field(init=False)
    perthm: float = field(init=False)
    pere: float = field(init=False)

    tempi: float = field(init=False)
    slopei: float = field(init=False)
    thermi: float = field(init=False)

    detectors:      List[Any]   = field(default_factory=list)
    spc:            Optional[List[float]] = None
    spl:            Optional[List[float]] = None
    rem:            Optional[List[float]] = None
    prem:           Optional[List[float]] = None
    splstart:       Optional[List[float]] = None

    num_groups:     int = field(init=False, default=0)
    num_det:        int = field(init=False, default=0)

    tempm:       float = field(init=False)
    iter_count:  float = field(init=False)

    iter_log: List[str] = field(default_factory=list)
    rnorm: float = field(init=False, default=0.0)

    ce:    Optional[List[float]] = None
    bce: Optional[List[float]] = None
    aleth: Optional[List[float]] = None
    errbce: Optional[List[float]] = None
    whtbce: Optional[List[float]] = None


    @classmethod
    def from_dict(cls, raw: Dict[str, Any]) -> "Bums2Config":
        kwargs: Dict[str, Any] = {}
        missing = []

        # 1) check required presence
        for f in fields(cls):
            if not f.init:
                continue
            if f.default is MISSING and f.default_factory is MISSING:
                #This field is required
                if f.name not in raw:
                    missing.append(f.name)
        if missing:
            raise ValueError(f"Missing required config fields: {', '.join(missing)}")

        # 2) convert each present field
        for f in fields(cls):
            name, typ = f.name, f.type
            if name not in raw:
                # leave fields absent if they’re optional or have defaults
                # also skip any derived variables
                if not f.init:
                    continue
                continue
            val = raw[name]

            # int
            if typ is int:
                try:
                    kwargs[name] = int(val)
                except Exception:
                    raise ValueError(f"Field {name} expects int, got {val!r}")

            # float
            elif typ is float:
                try:
                    kwargs[name] = float(val)
                except Exception:
                    raise ValueError(f"Field {name} expects float, got {val!r}")

            # Path or Optional[Path]
            elif typ is Path or (
                 get_origin(typ) is Union and Path in get_args(typ)
            ):
                kwargs[name] = Path(val) if val else None

            # List[...] 
            elif get_origin(typ) is list:
                subtype, = get_args(typ)
                # split only if it’s a string; if it’s already a list, use it directly
                parts = val.split(",") if isinstance(val, str) else list(val)
                if subtype is bool:
                    kwargs[name] = [
                        p.strip().lower() in ("1", "true", "t", "yes")
                        for p in parts
                    ]
                elif subtype is float:
                    try:
                        kwargs[name] = [float(p) for p in parts]
                    except Exception:
                        raise ValueError(
                            f"Field {name} expects comma-separated floats, got {val!r}"
                        )
                else:
                    # fallback: leave as list of raw strings
                    kwargs[name] = parts

            # all other types (e.g. str) – pass through
            else:
                kwargs[name] = val

       
        cfg = cls(**kwargs)

        cfg.tstper = (cfg.num_det * cfg.endtesterror**2) / 10000
        cfg.perthm = 1.0 + 20.0 * cfg.perslp
        cfg.pere = 1.0 + 10.0 * cfg.perslp

        cfg.tempi = cfg.tempij
        cfg.tempm = cfg.tempij
        cfg.slopei = cfg.slopej
        cfg.thermi = cfg.thermj

        cfg.iter_count = cfg.iter

        return cfg