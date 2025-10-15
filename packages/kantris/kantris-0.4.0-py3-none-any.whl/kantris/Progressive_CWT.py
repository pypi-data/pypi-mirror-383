"""
progressive_cwt.py
Progressive CWT renderer - compute coarse-to-fine in chunks and update plot.
Requires: numpy, pywt, matplotlib
"""

import numpy as np
import pywt
import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm, Normalize
import concurrent.futures
import time
from typing import Sequence, Tuple, List

def chunk_scales_indices(n_scales: int, passes: int = 4) -> List[List[int]]:
    """
    Create a sequence of lists of scale indices to compute in progressive passes.
    Strategy: in pass 0 take every 2^(passes-1) index -> coarse;
    pass 1 fills in the midpoints (binary subdivision).
    Example: n_scales=16, passes=4 -> indexes computed in order that fills gaps.
    """
    indices = []
    # We will generate per-pass step = 2**(passes-1-pass)
    used = np.zeros(n_scales, dtype=bool)
    for p in range(passes):
        step = 2 ** (passes - 1 - p)
        idx = np.arange(0, n_scales, step)
        # include only not-yet-used indices
        idx = [int(i) for i in idx if (0 <= i < n_scales) and not used[int(i)]]
        indices.append(idx)
        used[idx] = True
    # final pass for any remaining indices
    remaining = [i for i in range(n_scales) if not used[i]]
    if remaining:
        indices.append(remaining)
    return indices

def progressive_cwt_plot(
    data: np.ndarray,
    wavelet: str = "cmor1-1",
    n_scales: int = 400,
    passes: int = 5,
    cmap: str = "viridis",
    yscale: str = "log",
    zscale: str = "log",
    dt: float = None,
    figsize=(12,6),
    dpi=150,
    max_workers: int = 4,
):
    """
    Compute CWT progressively and update a matplotlib plot.
    - timestamps, values: 1D arrays (seconds, amplitude)
    - n_scales: total number of scales for final image
    - passes: number of progressive passes (higher -> more smooth refinement)
    """
        # --- input checks ---
    if data.ndim != 2 or data.shape[1] < 2:
        raise ValueError("data must be Nx2: data[:,0]=time, data[:,1]=signal")

    timestamps = data[:, 0].astype(float)
    values = data[:, 1].astype(float)

    if dt is None:
        dt = np.diff(timestamps).mean()
    # full target scales (logspace)
    cw = pywt.ContinuousWavelet(wavelet)
    central = pywt.central_frequency(wavelet) if hasattr(pywt, "central_frequency") else cw.center_frequency
    # choose freq range: from f_min_coi..Nyquist
    T_in_seconds = timestamps[-1] - timestamps[0]
    f_max = 1.0 / dt / 2.0
    f_min_coi = (1.4 * np.sqrt(2 * 1.0) * cw.center_frequency) / (T_in_seconds)  # approximate from your class
    freqs = np.logspace(np.log10(f_min_coi), np.log10(f_max), n_scales)
    scales = central / (freqs * dt)

    # build chunking schedule
    schedule = chunk_scales_indices(n_scales, passes=passes)
    print("Progressive passes:", len(schedule), "chunks sizes:", [len(s) for s in schedule])

    # image buffer (n_scales x n_times)
    n_times = values.size
    image = np.full((n_scales, n_times), np.nan, dtype=float)

    # prepare figure
    fig, ax = plt.subplots(figsize=figsize, dpi=dpi)
    # use compute_edges if available; here we'll plot with imshow for simplicity (fast updates)
    # We'll show freq increasing from bottom to top
    extent = [timestamps[0], timestamps[-1], freqs[0], freqs[-1]]
    # initial dummy image (all NaN => blank)
    im = ax.imshow(np.zeros_like(image), aspect='auto', origin='lower', extent=extent, cmap=cmap)
    ax.set_yscale(yscale)
    ax.set_xlabel("Time (s)")
    ax.set_ylabel("Frequency (Hz)")
    ax.set_title("Progressive CWT (coarse->fine)")
    cb = fig.colorbar(im, ax=ax)

    # maintain global vmin/vmax from already-computed cells (robust percentiles)
    def current_vmin_vmax(img):
        flat = img[~np.isnan(img)]
        if flat.size == 0:
            return (1e-12, 1.0)
        vmin = np.percentile(flat, 2)
        vmax = np.percentile(flat, 98)
        if vmin <= 0:
            vmin = np.min(flat[flat>0]) if np.any(flat>0) else 1e-12
        return vmin, vmax

    # executor for background computing
    executor = concurrent.futures.ThreadPoolExecutor(max_workers=max_workers)

    def compute_scales(indices: Sequence[int]):
        """Compute CWT only for a subset of scales (indices). Returns (indices, abs_cwt_rows)"""
        # Build scales array for requested indices in original order
        s = scales[list(indices)]
        # Do cwt on full signal but with only s -> pywt.cwt accepts arbitrary scales
        coeffs, freqs_out = pywt.cwt(values, s, wavelet, sampling_period=dt)
        return np.abs(coeffs), np.array(indices), freqs_out

    # progressive loop: submit tasks per chunk; when finished, update image and plot
    futures = []
    for chunk in schedule:
        if len(chunk) == 0:
            continue
        # submit a worker
        fut = executor.submit(compute_scales, chunk)
        futures.append(fut)

    # as tasks complete, update image
    completed = 0
    total_tasks = len(futures)
    for fut in concurrent.futures.as_completed(futures):
        try:
            abscoeffs, idxs, freqs_out = fut.result()
        except Exception as e:
            print("Task error:", e)
            continue
        # abscoeffs shape: (len(idxs), n_times)
        # fill into image at corresponding rows
        for i_local, i_global in enumerate(idxs):
            image[i_global, :] = abscoeffs[i_local, :]

        # recompute vmin/vmax from computed values
        vmin, vmax = current_vmin_vmax(image)
        # update imshow - need to set extent & data shaped for imshow (freqs->y)
        # we need final image scaled by freq order. imshow expects shape (ny, nx) where ny corresponds to freq axis.
        im.set_data(image)
        im.set_clim(vmin, vmax)
        # optionally update colorbar label or limits
        cb.on_mappable_changed(im)

        # redraw
        fig.canvas.draw_idle()
        plt.pause(0.001)   # yield to GUI and show update

        completed += 1
        print(f"Completed chunk {completed}/{total_tasks} (filled {len(idxs)} scales)")

    executor.shutdown(wait=False)
    print("Progressive CWT finished.")
    return fig, image, freqs