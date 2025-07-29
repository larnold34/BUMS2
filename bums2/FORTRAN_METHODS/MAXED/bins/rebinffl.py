import numpy as np

def rebin_ffl(fl_leth, enbf, target_edges, d, s, B, *, fortran_fidelity=True):
    """
    Python translation of the MAXED REBINFFL subroutine.

    Parameters
    ----------
    fl_leth : (NB,) array-like
        Spectrum in lethargy units on the working grid (Fortran FL array).

    enbf : (NB+1,) array-like
        Working-grid energy bin edges.

    target_edges : (Ntgt,) array-like
        Destination bin edges (e.g., ENBZKL for default, ENBR for response).

    d, s : (M,) array-like
        Measured counts and 1σ uncertainties.

    B : (M, NB) array-like
        Response matrix on the working grid (same one used for all forward calcs).

    fortran_fidelity : bool, default True
        When True, reproduces historical MAXED overwrite behavior when assigning FBL.
        When False, assigns FBL only within the target bin interval (more intuitive).

    Returns
    -------
    fb : (NB,) ndarray
        Rebinned spectrum per *bin* (Fortran FB).

    fbl : (NB,) ndarray
        Rebinned spectrum per *unit lethargy* (Fortran FBL).

    chi2 : float
        χ² comparing B @ fb vs D (with uncertainties S).

    Notes
    -----
    Fortran algorithm:
      1. For each target bin L, compute a lethargy-weighted average FDL(L) of the
         working-grid FL(K) whose *lower* edge ENBF(K) is inside that target bin.
      2. Assign FDL(L) into FBL(K) for all K satisfying ENBF(K) >= target_edges[L]
         (overwrites from low to high). This produces a step function.
      3. Convert FBL -> FB by multiplying by working-grid log bin widths.
      4. Compute forward counts: E = B @ FB; χ² = Σ (D-E)^2 / S^2.

    """
    fl_leth = np.asarray(fl_leth, dtype=np.float64)
    enbf = np.asarray(enbf, dtype=np.float64)
    target_edges = np.asarray(target_edges, dtype=np.float64)
    d = np.asarray(d, dtype=np.float64)
    s = np.asarray(s, dtype=np.float64)
    B = np.asarray(B, dtype=np.float64)

    NB = len(enbf) - 1
    Ntgt = len(target_edges)
    Ntgt_m1 = Ntgt - 1

    # 1) Lethargy-weighted averages in target bins
    fdl = np.zeros(Ntgt_m1, dtype=np.float64)
    lower = enbf[:-1]
    upper = enbf[1:]
    widths = np.log(upper) - np.log(lower)
    for L in range(Ntgt_m1):
        mask = (lower >= target_edges[L]) & (lower < target_edges[L+1])
        if not np.any(mask):
            fdl[L] = 0.0
        else:
            w = widths[mask]
            fdl[L] = np.sum(fl_leth[mask] * w) / np.sum(w)

    # 2) Assign to working-grid FBL
    fbl = np.zeros(NB, dtype=np.float64)
    if fortran_fidelity:
        # Historical overwrite: every K whose lower edge >= this target lower gets updated
        for L in range(Ntgt_m1):
            fbl[lower >= target_edges[L]] = fdl[L]
    else:
        # More intuitive: only assign within that target interval
        for L in range(Ntgt_m1):
            mask = (lower >= target_edges[L]) & (lower < target_edges[L+1])
            fbl[mask] = fdl[L]

    # 3) Convert to per-bin spectrum
    fb = fbl * widths

    # 4) Chi-square
    E = B @ fb
    chi2 = np.sum(((d - E) ** 2) / (s ** 2))

    return fb, fbl, chi2
