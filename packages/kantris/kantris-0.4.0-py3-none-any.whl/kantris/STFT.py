"""
STFT utility class inspired by the provided CWT class.
Ziel: schnelle, robuste Short-Time Fourier Transform (STFT) Implementierung
mit einer normalen Generate(...) Methode und einer GenerateFast(...)-Methode,
welche Auflösung gegen Geschwindigkeit tauscht.

Rückgabewerte der Generate-Methoden:
    stft_matrix: complex ndarray (n_freqs, n_times)
    freqs: ndarray (n_freqs,) in Hz
    times: ndarray (n_times,) in seconds (relative to data[:,0].min())
    meta: dict mit nützlichen Metainformationen (dt, n_fft, hop_length, window)

Benötigte Pakete: numpy, matplotlib (optional für PlotSTFT). Scipy wird NICHT benötigt.
"""
from __future__ import annotations

import numpy as np
from typing import Optional, Tuple, Dict, Any
import math
import time
import concurrent.futures
try:
    import matplotlib.pyplot as plt
    from matplotlib.colors import LogNorm, Normalize
except Exception:
    plt = None
try:
    from scipy.ndimage import gaussian_filter1d
    _HAS_SCIPY = True
except Exception:
    _HAS_SCIPY = False

class STFT:
    @staticmethod
    def _next_pow2(x: int) -> int:
        return 1 << ((x - 1).bit_length())

    @staticmethod
    def _uniform_resample_if_needed(t: np.ndarray, y: np.ndarray, tol: float = 1e-6):
        """Stellt sicher, dass Zeitstempel gleichmäßig sind. Falls nicht: Interpoliert auf gleichmäßiges Gitter.
        Returns (t_uniform, y_uniform, dt, interpolated_flag)
        """
        dt_vec = np.diff(t)
        if len(dt_vec) == 0:
            return t, y, 1.0, False
        if not np.allclose(dt_vec, dt_vec[0], atol=tol):
            N = len(t)
            t_uniform = np.linspace(t.min(), t.max(), N)
            y_uniform = np.interp(t_uniform, t, y)
            dt = t_uniform[1] - t_uniform[0]
            return t_uniform, y_uniform, dt, True
        else:
            return t, y, dt_vec[0], False

    @staticmethod
    def _frame_signal(y: np.ndarray, frame_len: int, hop: int) -> np.ndarray:
        """Erzeuge eine (n_frames, frame_len) Ansicht (falls möglich) mit Stride-Tricks.
        Falls das Signal nicht vollständig in Frames passt, wird am Ende mit Null aufgefüllt.
        """
        N = y.shape[0]
        n_frames = 1 + (N - frame_len + hop) // hop if N >= frame_len else 1
        pad_len = max(0, (n_frames - 1) * hop + frame_len - N)
        if pad_len > 0:
            y = np.concatenate([y, np.zeros(pad_len, dtype=y.dtype)])
        shape = (n_frames, frame_len)
        strides = (y.strides[0] * hop, y.strides[0])
        try:
            frames = np.lib.stride_tricks.as_strided(y, shape=shape, strides=strides)
            return frames.copy()  # copy so further ops don't break if underlying changes
        except Exception:
            # Fallback: slower framing
            frames = np.zeros((n_frames, frame_len), dtype=y.dtype)
            for i in range(n_frames):
                start = i * hop
                frames[i, :] = y[start:start + frame_len]
            return frames

    @staticmethod
    def _window_function(win_name: str, L: int) -> np.ndarray:
        win = win_name.lower()
        if win == 'hann' or win == 'hanning':
            return np.hanning(L)
        if win == 'hamming':
            return np.hamming(L)
        if win == 'blackman':
            return np.blackman(L)
        if win == 'rect' or win == 'rectangular' or win == 'ones':
            return np.ones(L)
        # default
        return np.hanning(L)

    @staticmethod
    def Generate(
        data: np.ndarray,
        window: str = 'hann',
        n_fft: Optional[int] = None,
        hop_length: Optional[int] = None,
        win_length: Optional[int] = None,
        center: bool = True,
        pad_mode: str = 'reflect',
        return_roc: bool = False,
        tol: float = 1e-6,
        use_threads: bool = True,
        max_workers: int = 4,
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray, Dict[str, Any]]:
        """
        Vollständige STFT-Berechnung (optimiert, vektorisiert).

        Parameters
        ----------
        data: Nx2 numpy array, data[:,0]=time (s), data[:,1]=signal (float)
        window: Fenstertyp (hann, hamming, blackman, rect)
        n_fft: FFT-Größe. Falls None -> nächsthöhere Potenz von 2 >= win_length
        win_length: Fensterlänge in Samples. Default: n_fft (falls n_fft gegeben) oder 256
        hop_length: Schrittweite in Samples. Default: win_length//4
        center: If True, frames are centered (pads signal symmetrically)
        pad_mode: padding mode if center is True
        return_roc: return also real/imag or magnitude? (unused, placeholder)
        use_threads/max_workers: optionally parallelize FFT on frame chunks

        Returns (stft_matrix (freqs x times), freqs(Hz), times(s), meta dict)
        """
        if data.ndim != 2 or data.shape[1] < 2:
            raise ValueError('data must be Nx2')
        t = data[:, 0].astype(float)
        y = data[:, 1].astype(float)

        # uniformize timestamps
        t_u, y_u, dt, was_interp = STFT._uniform_resample_if_needed(t, y, tol=tol)
        fs = 1.0 / dt

        # defaults
        if win_length is None and n_fft is None:
            win_length = 256
        if n_fft is None:
            n_fft = STFT._next_pow2(win_length if win_length is not None else 256)
        if win_length is None:
            win_length = n_fft
        if hop_length is None:
            hop_length = max(1, win_length // 4)

        # choose window
        win = STFT._window_function(window, win_length)
        # center -> pad
        y_proc = y_u
        if center:
            left = win_length // 2
            right = left
            y_proc = np.pad(y_proc, (left, right), mode=pad_mode)
            t0 = t_u[0] - left * dt
        else:
            t0 = t_u[0]

        # framing
        frames = STFT._frame_signal(y_proc, win_length, hop_length)
        n_frames = frames.shape[0]
        # apply window
        frames *= win[None, :]

        # zero-pad to n_fft if needed
        if n_fft > win_length:
            frames = np.pad(frames, ((0, 0), (0, n_fft - win_length)), mode='constant')

        # compute rfft across axis=-1 -> shape (n_frames, n_freqs)
        start_time = time.time()
        if use_threads and n_frames >= 512:
            # chunk frames to avoid too-large memory and parallelize
            def _fft_chunk(chunk):
                return np.fft.rfft(chunk, n=n_fft, axis=1)
            chunk_size = max(64, n_frames // (max_workers))
            chunks = [frames[i:i + chunk_size] for i in range(0, n_frames, chunk_size)]
            results = []
            with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as ex:
                futures = [ex.submit(_fft_chunk, ch) for ch in chunks]
                for f in concurrent.futures.as_completed(futures):
                    results.append(f.result())
            # results are out-of-order; reorder by chunk index
            # Instead do synchronous map to preserve order
            results = []
            with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as ex:
                for ch in chunks:
                    results.append(ex.submit(_fft_chunk, ch).result())
            X = np.vstack(results)
        else:
            X = np.fft.rfft(frames, n=n_fft, axis=1)

        # transpose to (n_freqs, n_times)
        X = X.T
        end_time = time.time()

        n_freqs = X.shape[0]
        freqs = np.fft.rfftfreq(n_fft, dt)

        # times: center of each frame in seconds
        times = (np.arange(n_frames) * hop_length) * dt + (win_length / 2.0) * dt
        if center:
            # adjust because we padded
            times = times + t_u[0]
        else:
            times = times + t_u[0]

        meta = {
            'dt': dt,
            'fs': fs,
            'n_fft': n_fft,
            'win_length': win_length,
            'hop_length': hop_length,
            'window': window,
            'compute_seconds': end_time - start_time,
            'was_interpolated': was_interp,
        }

        return X, freqs, times, meta

    @staticmethod
    def GenerateFast(
        data: np.ndarray,
        target_max_time: float = 0.8,
        quality: float = 0.5,
        **kwargs,
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray, Dict[str, Any]]:
        """
        Schnellere STFT-Variante. Ziel: in den meisten Fällen < target_max_time Sekunden rechnen.
        quality in (0..1] steuert die Auflösung/Genauigkeit:
            1.0 -> volle Qualität (delegiert an Generate)
            0.75 -> moderate Reduktion (kleineres n_fft, etwas größere hop)
            0.5 -> deutliche Beschleunigung (dezimierung, kleiner n_fft)
            0.25 -> maximal schnell (starker Decimate und sehr kleiner n_fft)

        Intern trifft die Methode heuristische Entscheidungen:
            - decimation (zeitliche Reduktion via Resample/Interp)
            - verkleinertes n_fft
            - grössere hop_length

        Zusätzliche kwargs werden an Generate weitergereicht.
        """
        if not (0 < quality <= 1.0):
            raise ValueError('quality must be in (0,1]')

        t = data[:, 0].astype(float)
        y = data[:, 1].astype(float)

        # quick time estimate heuristics: number of samples -> determine decimation
        N = len(t)
        # baseline config from Generate defaults
        base_win = kwargs.get('win_length', 256)
        base_nfft = kwargs.get('n_fft', STFT._next_pow2(base_win))
        base_hop = kwargs.get('hop_length', max(1, base_win // 4))

        # choose aggressiveness based on quality
        # compute target reduction factor (time reduction ~ samples * log(nfft))
        # heuristic: reduction_factor ~ 1/quality
        red_factor = max(1.0, 1.0 / quality)

        # Cap decimation so we don't alias high frequencies: compute Nyquist and desired max freq
        # We'll conservatively allow decimation by integer factors only
        # Compute current sampling rate
        _, _, dt, _ = STFT._uniform_resample_if_needed(t, y)
        fs = 1.0 / dt

        # choose decimation factor such that new_fs >= 2*max_freq_of_interest.
        # If user passed 'max_freq' in kwargs, respect it.
        max_freq_user = kwargs.get('max_freq', None)
        if max_freq_user is None:
            max_freq_user = fs / 2.0
        # desired new_fs to keep at least 2.5x max_freq_user
        desired_new_fs = min(fs, max(2.5 * max_freq_user, fs / red_factor))
        decim = max(1, int(np.floor(fs / desired_new_fs)))

        # ensure decim not too large
        decim = min(decim, max(1, int(red_factor)))

        # apply decimation via interpolation to avoid aliasing issues for non-integer factors
        if decim > 1:
            new_N = max(2, int(np.ceil(N / decim)))
            t_new = np.linspace(t[0], t[-1], new_N)
            y_new = np.interp(t_new, t, y)
            data2 = np.column_stack([t_new, y_new])
            decimated = True
        else:
            data2 = data
            decimated = False

        # choose smaller n_fft based on quality
        if quality >= 0.9:
            q_nfft = 1.0
        elif quality >= 0.7:
            q_nfft = 0.8
        elif quality >= 0.5:
            q_nfft = 0.5
        else:
            q_nfft = 0.25

        win_length = kwargs.get('win_length', 256)
        n_fft = kwargs.get('n_fft', STFT._next_pow2(win_length))
        n_fft = max(8, int(STFT._next_pow2(int(n_fft * q_nfft))))
        hop_length = kwargs.get('hop_length', max(1, int(win_length * max(0.2, 1.0 - quality))))

        # pass modified kwargs to Generate
        gen_kwargs = dict(kwargs)
        gen_kwargs.update({'n_fft': n_fft, 'win_length': win_length, 'hop_length': hop_length})

        start = time.time()
        X, freqs, times, meta = STFT.Generate(data2, **gen_kwargs)
        elapsed = time.time() - start

        meta['generate_fast'] = True
        meta['decimated'] = decimated
        meta['decimation_factor_est'] = decim
        meta['requested_quality'] = quality
        meta['compute_seconds'] = elapsed

        return X, freqs, times, meta

    @staticmethod
    def PlotSTFT(
        X: np.ndarray,
        freqs: np.ndarray,
        times: np.ndarray,
        vmin: Optional[float] = None,
        vmax: Optional[float] = None,
        yscale: str = 'linear',
        cmap: str = 'viridis',
        figsize: Tuple[float, float] = (12, 6),
        dpi: int = 200,
        log_z: bool = False,
    ) -> plt.Figure:
        """Erstellt ein STFT-Spektrogramm aus der komplexen STFT-Matrix X.
        X shape: (n_freqs, n_times)
        """
        if plt is None:
            raise RuntimeError('matplotlib not available')

        # Ensure numpy arrays
        freqs = np.asarray(freqs, dtype=float)
        times = np.asarray(times, dtype=float)
        Z = np.abs(X)

        # Sort freqs ascending (and reorder Z accordingly) — pcolormesh expects monotonic coords
        if freqs[0] > freqs[-1]:
            order = np.argsort(freqs)
            freqs = freqs[order]
            Z = Z[order, :]

        # For log yscale: remove or shift zero frequency (cannot plot <=0 on log scale)
        if yscale == 'log':
            if np.any(freqs <= 0):
                # remove zero-frequency row(s)
                positive_mask = freqs > 0
                if not positive_mask.any():
                    raise ValueError("All frequencies <= 0; cannot use log yscale.")
                freqs = freqs[positive_mask]
                Z = Z[positive_mask, :]

        # Mask invalid values so NaNs don't break color scaling
        Z = np.ma.masked_invalid(Z)

        # compute default vmin/vmax robustly from unmasked values
        if vmin is None:
            try:
                vmin = np.percentile(Z.compressed(), 1)
            except Exception:
                vmin = 1e-12
        if vmax is None:
            try:
                vmax = np.percentile(Z.compressed(), 99)
            except Exception:
                vmax = float(Z.max()) if Z.size else 1.0
        if vmin <= 0:
            vmin = max(vmin, 1e-12)

        norm = LogNorm(vmin=vmin, vmax=vmax) if log_z else Normalize(vmin=vmin, vmax=vmax)

        # build edges for pcolormesh (length = centers+1)
        # requires compute_edges(center_array) function available in module
        x_edges = compute_edges(times)
        y_edges = compute_edges(freqs)

        # avoid any non-positive edges when using log yscale
        if yscale == 'log':
            # replace any zero/negative edges with a tiny positive epsilon
            eps = 1e-12
            y_edges[y_edges <= 0] = eps

        fig, ax = plt.subplots(figsize=figsize, dpi=dpi)

        # pcolormesh with edges is robust for log yscale (the axis will transform the coordinates)
        pcm = ax.pcolormesh(x_edges, y_edges, Z, shading='auto', norm=norm, cmap=cmap)

        if yscale == 'log':
            ax.set_yscale('log')
            # optional: set reasonable y-limits from smallest positive freq to max
            ax.set_ylim(y_edges[1], y_edges[-1])
        else:
            ax.set_yscale('linear')

        ax.set_xlabel('Time (s)')
        ax.set_ylabel('Frequency (Hz)')
        ax.set_title('STFT Spectrogram')
        fig.colorbar(pcm, ax=ax)
        fig.tight_layout()
        return fig


    @staticmethod
    # ---------- Plot-Funktion: PlotSTFT2 ----------
    def PlotSTFT2(
        data: np.ndarray,
        X: np.ndarray,
        freqs: np.ndarray,
        times: np.ndarray,
        meta: dict,
        vmin: float = None,
        vmax: float = None,
        yscale: str = 'log',
        cmap: str = 'viridis',
        figsize: tuple = (12,6),
        dpi: int = 200,
        smooth_sigma: float = 1.0,
        per_freq_percentile: float = 99.0
    ):
        eps = 1e-12
        y = data[:,1].astype(float)
        t = data[:,0].astype(float)

        # mask edges (Frames die vom Padding betroffen sind)
        half_win_secs = meta['win_length'] * meta['dt'] / 2.0
        valid = (times >= t[0] + half_win_secs) & (times <= t[-1] - half_win_secs)
        X_plot = X[:, valid]
        times_plot = times[valid]
        freqs_plot = freqs.copy()

        # remove zero/neg freq rows for log yscale
        if yscale == 'log':
            pos = freqs_plot > 0
            if not np.any(pos):
                raise ValueError("No positive frequencies available for log yscale.")
            freqs_plot = freqs_plot[pos]
            X_plot = X_plot[pos, :]

        # magnitude
        Z = np.abs(X_plot) + eps   # (n_freqs, n_times)

        # Per-frequency normalization (divide by per_freq_percentile-th percentile)
        p = per_freq_percentile
        pvals = np.percentile(Z, p, axis=1, keepdims=True)
        pvals[pvals <= eps] = eps
        Z_norm = Z / pvals

        # smoothing along frequency axis (to reduce speckle)
        if smooth_sigma is not None and smooth_sigma > 0:
            if _HAS_SCIPY:
                Z_smooth = gaussian_filter1d(Z_norm, sigma=smooth_sigma, axis=0, mode='nearest')
            else:
                # simple fallback: 1D uniform smoothing kernel along freq axis
                from numpy import convolve
                kernel = np.ones(3) / 3.0
                Z_smooth = np.vstack([np.convolve(row, kernel, mode='same') for row in Z_norm])
        else:
            Z_smooth = Z_norm

        # convert to dB for nicer contrast
        Z_db = 20.0 * np.log10(Z_smooth + eps)

        # robust vmin/vmax wenn nicht gegeben
        if vmin is None:
            vmin = np.percentile(Z_db, 5.0)
        if vmax is None:
            vmax = np.percentile(Z_db, 99.5)

        # build edges for pcolormesh
        x_edges = compute_edges(times_plot)
        y_edges = compute_edges(freqs_plot)
        # avoid non-positive edges for log scale
        if yscale == 'log':
            y_edges[y_edges <= 0] = eps

        fig, ax = plt.subplots(figsize=figsize, dpi=dpi)

        pcm = ax.pcolormesh(x_edges, y_edges, Z_db, shading='auto',
                            cmap=cmap, norm=plt.Normalize(vmin=vmin, vmax=vmax))

        if yscale == 'log':
            ax.set_yscale('log')
            ax.set_ylim(y_edges[1], y_edges[-1])
        else:
            ax.set_yscale('linear')

        ax.set_xlabel('Time (s)')
        ax.set_ylabel('Frequency (Hz)')
        ax.set_title('STFT Spectrogram (per-freq normalized, smoothed, dB)')
        cbar = fig.colorbar(pcm, ax=ax, label='dB (per-freq normalized)')
        fig.tight_layout()
        return fig

# End of file

def compute_edges(a: np.ndarray) -> np.ndarray:
    """Compute edge array from centers (length -> length+1)."""
    a = np.asarray(a, dtype=float)
    if a.size < 2:
        return np.array([a[0] - 0.5, a[0] + 0.5])
    mid = 0.5 * (a[:-1] + a[1:])
    first = a[0] - 0.5 * (a[1] - a[0])
    last  = a[-1] + 0.5 * (a[-1] - a[-2])
    edges = np.empty(a.size + 1, dtype=float)
    edges[0] = first
    edges[-1] = last
    edges[1:-1] = mid
    return edges