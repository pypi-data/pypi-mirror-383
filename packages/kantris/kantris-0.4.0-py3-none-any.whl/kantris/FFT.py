import numpy as np
import pywt
import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm, Normalize
from concurrent.futures import ThreadPoolExecutor
from scipy.interpolate import interp1d

import time
from typing import Tuple, Optional, Any, List

from .DataManipulation import DataManipulation, Array
from .plotter import Plotter

import logging
logger = logging.getLogger(__name__)



class FFT:
    VERSION = 'Kantris.FFT: 0.2.1'
    def FFT(data: np.ndarray|tuple[list, list], tol: float = 1e-6, format: str = 'f', scale: float = 1) -> tuple[list, list]:
        if isinstance(data, tuple):
            x = data[0]
            y = data[1]
        elif isinstance(data, np.ndarray):
            x = data[:, 0]
            y = data[:, 1]
        else:
            logging.error(f'invalid data type "{type(data)}", must be tuple[list] or ndarray')
            return

        # Prüfen auf gleichmäßige Abstände
        dx = np.diff(x)
        if not np.allclose(dx, dx[0], atol=tol):
            logger.info("Input x-values are not evenly spaced: interpolating to uniform grid")
            N = len(x)
            x_uniform = np.linspace(x.min(), x.max(), N)
            # Verwende die angegebene LinearInterpol-Funktion
            y_uniform = DataManipulation.LinearInterpol(x_uniform, x, y)
            sampling_interval = x_uniform[1] - x_uniform[0]
        else:
            y_uniform = y
            sampling_interval = dx[0]

        # FFT auf reellem Signal
        N = len(y_uniform)
        fft_vals = np.fft.rfft(y_uniform)
        freqs = np.fft.rfftfreq(N, d=sampling_interval)
        amplitudes = np.abs(fft_vals)
        if format == 'T':
            freqs = 1/freqs

        if scale != 1:
            freqs = freqs/scale

        # Ergebnis: Spaltenweise Frequenz und Amplitude
        return freqs, amplitudes

    @staticmethod
    def PlotFFT(freqs, amplitudes, plotconf):
        CONFIG = {
            "plot": {
                "title": Plotter.Label(f"Fourier Plot [{len(freqs)} Points]").Color("black").Fontsize(20),
                "plotsize": (14,6),
                "dpi": 400,
                "legend": Plotter.Legend(False).Position("upper right"),
                "plot": False,
                "legend": None,
            },
            "x-axis": {
                #Label and Unit (Unit supports Latex)
                "label": Plotter.Label("Frequency").Unit(r"Hz").Color("black").Fontsize(20),
                #Range and Scale
                "scale": "log",
                #Ticks | Int: # of Ticks, Float: Steps, Array/Tuple: Fixed
                #"major-ticks": 2.0,
                #"minor-ticks": 0.5,
                #Tick-Label:
                "major-label": Plotter.Label().Color("black").Fontsize(18),
                #Tick-Ticker
                "major-ticker": Plotter.TickTicker().Length(8).Width(1).Direction("inout"),
                "minor-ticker": Plotter.TickTicker().Length(4).Width(1).Direction("inout"),
                #Tick-Grid
                "major-grid": Plotter.TickGrid().Color("gray").Alpha(0.25).Width(1).Style("-"),
                "minor-grid": Plotter.TickGrid().Color("gray").Alpha(0.2).Width(0.6).Style("--"),
            },
            "y-axis": {
                #Label and Unit (Supports Latex)
                "label": Plotter.Label("Amplitude").Color("black").Fontsize(20),
                #Range and Scale
                "scale": "log",
                #Ticks | Int: # of Ticks, Float: Steps, Array/Tuple: Fixed
                #"major-ticks": 1.0,
                #"minor-ticks": 0.5,
                #Tick-Label:
                "major-label": Plotter.Label().Color("black").Fontsize(18),
                #Tick-Ticker
                "major-ticker": Plotter.TickTicker().Length(8).Width(1).Direction("inout"),
                "minor-ticker": Plotter.TickTicker().Length(4).Width(1).Direction("inout"),
                #Tick-Grid
                "major-grid": Plotter.TickGrid().Color("gray").Alpha(0.25).Width(1).Style("-"),
                "minor-grid": Plotter.TickGrid().Color("gray").Alpha(0.2).Width(0.6).Style("--"),
            },
        }
        GRAPHS = [{
        "label": None,
        #Data
        "data": Plotter.Graph().X(freqs).Y(amplitudes),
        #Style
        "line-styling": Plotter.Line(),
        "marker-styling": Plotter.Marker().Style(""),
    }]
        fig = Plotter.Plot(CONFIG)
        return fig

class CWT:
    VERSION = 'Kantris.CWT: 0.3.0'
    COI_SCALE = 1.4
    @staticmethod
    def CWT(data,
            wavelet='cmor1-1',
            scales=None,
            tol: float = 1e-6,
            cmap:str = 'viridis',
            figsize: tuple = (3440, 1440),
            dpi: float = 100,
            max_workers: int = 1, 
            yscale = "linear",
            znorm = "linear",
            plot: bool = True,
            period_mode: bool = False,
            limit_by_coi: bool = True,
            save_fig: str = False,
            printlogs: bool = True,
            ):
        """
        Optimierte Continuous Wavelet Transform (CWT) mit Fortschrittsanzeigen:
        - NumPy-Interpolation
        - logarithmische Skalen
        - einmaliges Wavelet-Objekt
        - optional Parallelisierung
        """
        Logger = BoolLogger(printlogs)
        Logger.print("[CWT] Start der CWT")
        # Extrahiere Zeit und Signal
        x = data[:, 0]
        y = data[:, 1]

        # Gleichmäßigkeit prüfen
        dx = np.diff(x)
        if not np.allclose(dx, dx[0], atol=tol):
            Logger.print(f"[CWT] Ungleichmäßige Abstände erkannt. Interpolation auf gleichmäßiges Gitter...")
            N = len(x)
            x_uniform = np.linspace(x.min(), x.max(), N)
            y_uniform = np.interp(x_uniform, x, y)
            dt = x_uniform[1] - x_uniform[0]
            Logger.print(f"[CWT] Interpolation abgeschlossen. Δt={dt:.5f} - {60/dt:.5f}hz, Punkte={N}")
        else:
            x_uniform = x
            y_uniform = y
            dt = dx[0]
            Logger.print(f"[CWT] Gleichmäßige Abstände: Δt={dt:.5f} - {60/dt:.5f}hz, Punkte={len(x)}, T={TtoTime(dt*len(x))}")

        # Skalen festlegen
        if scales is None:
            f_c = pywt.ContinuousWavelet(wavelet).center_frequency
            s_min = 2 * f_c
            s_max = f_c * len(data)
            scales = np.logspace(np.log10(s_min), np.log10(s_max), num=300)
            Logger.print(f"[CWT] Generierte {len(scales)} Skalen")
        else:
            Logger.print(f"[CWT] Nutze {len(scales)} übergebene Skalen")

        # Wavelet-Objekt
        Logger.print(f"[CWT] Wavelet: {wavelet}")

        cwt_start_time = time.time()
        cwtmatr, freqs = pywt.cwt(y, scales, wavelet, sampling_period=dt)
        Logger.print(f"Min: {freqs.min():.6f} Hz  |  Max: {freqs.max():.6f} Hz")
        Logger.print(f"Perioden: {1/freqs.max():.2f} s  bis  {1/freqs.min():.2f} s")
        # --- nach CWT-Berechnung ---
        # --- nach CWT-Berechnung ---
        cwtmatr = np.abs(cwtmatr)
        cwt_end_time = time.time()
        Logger.print(f"[CWT] CWT-Berechnung abgeschlossen in {cwt_end_time-cwt_start_time:.2f}s")
        Logger.print(f"[CWT] Berechnet Frequenzen für {len(freqs)} Bins")

        if not plot:
            return cwtmatr, freqs, {"cwt_timer": cwt_end_time-cwt_start_time}
        # slice inner 100% (oder passe auf 90% falls notwendig)
        n_times = cwtmatr.shape[1]
        t0 = int(np.floor(0.0 * n_times))
        t1 = int(np.ceil(1.0 * n_times))
        t0 = max(0, t0)
        t1 = min(n_times, t1)

        Z = cwtmatr[:, t0:t1]               # shape (n_freqs, t1-t0)
        # prefer x_uniform if you interpolated earlier; otherwise fallback to x
        try:
            x_plot = x_uniform[t0:t1]
        except NameError:
            x_plot = x[t0:t1]
        y_plot = freqs                        # length n_freqs

        # --- COI mask: mask out values outside cone (i.e. near edges) ---
        # center frequency of the wavelet
        cw = pywt.ContinuousWavelet(wavelet)
        center_freq = cw.center_frequency
        # distance to edge (seconds) for each plotted time
        dist_to_edge = np.minimum(x_plot - x_plot[0], x_plot[-1] - x_plot)
        # avoid division by zero
        eps = 1e-12
        # coi frequency threshold per time (Hz): frequencies >= coi_freq are considered safe
        coi_freq = (np.sqrt(2.0) * center_freq) / (dist_to_edge + eps)   # shape (n_times,)
        Logger.print(f"[CWT] COI Min frequency: {min(coi_freq):.2f}hz, Max Period: {1/min(coi_freq):.2f}s")



        # mask: valid if freq >= coi_freq(time)
        # build boolean array shape (n_freqs, n_times)
        # freqs is shape (n_freqs,), coi_freq is (n_times,)
        valid = (y_plot[:, None] >= coi_freq[None, :])

        # Mask out values outside COI (i.e., where valid == False)
        Z_masked = np.ma.array(Z, mask=~valid)

        # For plotting the COI line: only plot where coi_freq is inside the computed freq-range
        fmin, fmax = freqs.min(), freqs.max()
        coi_freq_plot = np.where((coi_freq >= fmin) & (coi_freq <= fmax), coi_freq, np.nan)

        # 1) Z-Scale-Norm mit festen Grenzen (z.B. obere Grenze aus Daten, untere Grenze sinnvoll setzen)
        vals = Z_masked.compressed()   # nur die unmaskierten Werte als 1D-Array
        if vals.size == 0:
            raise ValueError("Alle Werte sind maskiert oder es gibt keine gültigen Werte.")
        
        #Set reasonable Z-limits. Primarly required for the huge amount of near 0 Amplitudes and Strong Ultra-Low-Frequency Amplitudes ruining the log scale
        k1 = 1
        while True:
            vmin = np.percentile(vals, k1)
            #Special Conditions
            if vmin < 1e-2:
                vmin = 1e-2
                break
            #Normal Conditions
            if vmin == 0.0:
                k1 += 1
            else:
                break
        k2 = 1
        while True:
            vmax = np.percentile(vals, 100-k2)
            #Normal Conditions
            if vmax == 0.0:
                k2 += 1
            else:
                break
        
        Logger.print("DEBUG", vmin, k1, vmax, k2)
        if not limit_by_coi:
            Z_masked = Z

        # --- Plot ---
        Logger.print("[CWT] Erstelle Plot...")
        plot_start_time = time.time()

        if figsize[0] > 100 or figsize[1] > 100:
            px = 1/dpi
            figsize = (figsize[0]*px, figsize[1]*px)
        fig, axs = plt.subplots(figsize=figsize, dpi=dpi)
        fig.canvas.draw()


        if znorm.lower() in ("log",):
            znorm = LogNorm(vmin=vmin, vmax=vmax)
        else:
            znorm = Normalize(vmin=vmin, vmax=vmax)
        if period_mode:
            y_plot = 1/y_plot
        # choose shading mode robustly
        if (len(x_plot) == Z_masked.shape[1]) and (len(y_plot) == Z_masked.shape[0]):
            pcm = axs.pcolormesh(x_plot, y_plot, Z_masked, norm=znorm, shading='nearest', cmap=cmap)
        else:
            x_edges = compute_edges(x_plot)
            y_edges = compute_edges(y_plot)
            pcm = axs.pcolormesh(x_edges, y_edges, Z_masked, norm=znorm, shading='auto', cmap=cmap)

        # draw COI line only where inside freq range
        axs.plot(x_plot, coi_freq_plot, color='white', linestyle='--', linewidth=1, label='COI')

        # optionally shade the region outside COI (low frequencies near edges) for clarity:
        # we shade only where coi_freq_plot is finite (i.e. inside f-range).
        # fill between ymin and coi (mask NaNs automatically)
        ymin = fmin if fmin > 0 else (np.min(freqs[freqs > 0]) if np.any(freqs > 0) else 1e-12)
        # use where to avoid drawing fill under NaNs
        finite_mask = ~np.isnan(coi_freq_plot)
        if finite_mask.any():
            axs.fill_between(x_plot[finite_mask], ymin, coi_freq_plot[finite_mask],
                             color='white', alpha=0.4, linewidth=0)

        # finalize axes
        fig.colorbar(pcm, ax=axs)
        axs.set_yscale(yscale)

        Logger.print("freqs:")
        Logger.print(freqs[0])
        Logger.print(freqs[-1])
        

        f_freqs_min, f_freqs_max = min(freqs), max(freqs)

        f_coi_min, f_coi_max = min(coi_freq), max(coi_freq)
        if limit_by_coi:
            f_min, f_max = max(f_coi_min, f_freqs_min), min(f_coi_max, f_freqs_max)
        else:
            f_min, f_max = f_freqs_min, f_freqs_max

        if period_mode:
            axs.set_ylim(1/f_min, 1/f_max)
        else:
            axs.set_ylim(f_min, f_max)

        axs.set_xlabel("Time (s)")
        if period_mode:
            axs.set_ylabel("Period (s)")
        else:
            axs.set_ylabel("Frequency (Hz)")
        axs.set_title(f"Continuous Wavelet Transform (Scaleogram) with {wavelet}")
        axs.legend(loc='upper right', fontsize='small')
        plt.tight_layout()
        plt.show()
        if isinstance(save_fig, str) and save_fig != "":
            fig.savefig(save_fig, dpi=dpi)
        plot_end_time = time.time()
        Logger.print(f"[CWT] Plot abgeschlossen in {plot_end_time - plot_start_time:.2f}s")

        return cwtmatr, freqs, {"cwt_timer": cwt_end_time-cwt_start_time}
    
    @staticmethod
    def DWT(
        data: np.ndarray,
        wavelet: str = 'db4',
        level: Optional[int] = None,
        target_period: Optional[float] = None,   # in seconds, z.B. 24*3600
        tol: float = 1e-6,
        cmap: str = 'viridis',
        figsize: Tuple[float, float] = (10, 6),
        yscale: str = "linear",
        pad: bool = True,
        pad_mode: str = 'reflect',
        normalize: Optional[str] = None,         # default None: show raw first
        to_db: bool = False,
        show_approx: bool = True,                # show approx row by default (useful for long periods)
        return_plot: bool = True,
        max_plot_cols: int = 2000,               # for large N decimate columns for plotting
        clip_percentiles: Optional[Tuple[float,float]] = (1.0,99.0), # optional clipping before normalize
        return_extra: bool = True                # return powers and swt_coeffs for analysis
    ) -> Tuple[np.ndarray, np.ndarray, Optional[Any], Optional[Any], Optional[dict]]:
        """
        Optimized SWT-based DWT helper.
        Returns: dwtmatr (levels x time), freqs (levels), fig, ax, extras(dict)
        extras includes 'powers' (RMS per level) and 'swt_coeffs' if requested.
        """

        # --- input checks ---
        if data.ndim != 2 or data.shape[1] < 2:
            raise ValueError("data must be Nx2: data[:,0]=time, data[:,1]=signal")

        x = data[:, 0].astype(float)
        y = data[:, 1].astype(float)

        # --- uniform grid / dt ---
        dx = np.diff(x)
        if not np.allclose(dx, dx[0], atol=tol):
            Norig = len(x)
            x_uniform = np.linspace(x.min(), x.max(), Norig)
            y_uniform = np.interp(x_uniform, x, y)
            dt = x_uniform[1] - x_uniform[0]
        else:
            x_uniform = x
            y_uniform = y
            dt = dx[0] if len(dx) > 0 else 1.0

        # simple unit check: if dt very small or large, warn user (ms vs s)
        if dt < 1e-3:
            # dt in ms or smaller — warn but continue
            print("[DWT] Warning: dt very small ({}). Are your timestamps in seconds?".format(dt))
        if dt > 1e5:
            print("[DWT] Warning: dt very large ({}). Check time units.".format(dt))

        N = len(y_uniform)
        if N < 2:
            raise ValueError("Signal too short (N < 2).")

        max_possible = int(np.floor(np.log2(N)))
        if max_possible < 1:
            raise ValueError("Signal too short for wavelet decomposition (max level < 1).")

        # --- auto-level from target_period (if provided) ---
        if target_period is not None:
            fs = 1.0 / dt
            f_target = 1.0 / float(target_period)
            est_level = int(round(np.log2(fs / f_target) - 1))
            # clamp to sensible range
            est_level = max(1, min(est_level, max_possible))
            if level is None:
                level = est_level
            else:
                level = min(level, max_possible)
            print(f"[DWT] target_period={target_period}s -> est_level={est_level}, using level={level}")
        else:
            if level is None:
                # pragmatic default: prefer deeper analysis for longer signals but not too deep
                level = min(6, max_possible)
            else:
                level = min(level, max_possible)

        # --- ensure divisibility and pad if needed ---
        block = 2 ** level
        rem = N % block
        if rem != 0:
            if pad:
                pad_len = block - rem
                left = pad_len // 2
                right = pad_len - left
                y_uniform = np.pad(y_uniform, (left, right), mode=pad_mode)
                x_left = x_uniform[0] - np.arange(left, 0, -1) * dt
                x_right = x_uniform[-1] + np.arange(1, right + 1) * dt
                x_uniform = np.concatenate([x_left, x_uniform, x_right])
                N = len(y_uniform)
                print(f"[DWT] Padded by {pad_len} samples ({left}/{right}), new N={N}")
            else:
                # reduce level until divisible
                while level > 0 and (N % (2 ** level) != 0):
                    level -= 1
                if level < 1:
                    raise ValueError("No valid level found. Set pad=True or increase signal length.")
                block = 2 ** level

        # --- compute SWT ---
        try:
            swt_coeffs = pywt.swt(y_uniform, wavelet, level=level)
        except Exception as e:
            raise RuntimeError(f"SWT failed: {e}")

        levels = len(swt_coeffs)
        # allocate float32 matrix for memory savings if large
        dwtmatr = np.zeros((levels, N), dtype=np.float32)
        for i, (cA, cD) in enumerate(swt_coeffs):
            dwtmatr[i, :] = np.abs(cD).astype(np.float32)

        # include approximation optionally
        approx_row = None
        if show_approx:
            approx_row = np.abs(swt_coeffs[-1][0]).astype(np.float32)

        # --- frequency mapping (dyadic approx) ---
        fs = 1.0 / dt if dt != 0 else 1.0
        freqs = np.array([fs / (2 ** (i + 1)) for i in range(levels)], dtype=float)

        # --- energy / RMS per level (useful for debugging) ---
        powers = np.array([np.sqrt(np.mean(dwtmatr[i, :] ** 2)) for i in range(levels)], dtype=float)
        approx_rms = None
        if show_approx:
            approx_rms = float(np.sqrt(np.mean(approx_row ** 2)))

        # --- optional percentil-clipping to avoid single outliers dominating ---
        if clip_percentiles is not None:
            lo_p, hi_p = clip_percentiles
            vmin = np.percentile(dwtmatr, lo_p)
            vmax = np.percentile(dwtmatr, hi_p)
            # clip in-place (but keep dtype)
            dwtmatr = np.clip(dwtmatr, vmin, vmax)

        # --- normalization ---
        eps = 1e-12
        if normalize == 'per_level':
            for i in range(dwtmatr.shape[0]):
                row = dwtmatr[i, :]
                mn, mx = row.min(), row.max()
                if mx - mn > 0:
                    dwtmatr[i, :] = (row - mn) / (mx - mn)
        elif normalize == 'global':
            mn, mx = dwtmatr.min(), dwtmatr.max()
            if mx - mn > 0:
                dwtmatr = (dwtmatr - mn) / (mx - mn)

        if to_db:
            dwtmatr = 20.0 * np.log10(dwtmatr + eps)

        # --- prepare for plotting: low freq bottom ---
        dwtmatr_plot = dwtmatr[::-1, :]
        freqs_plot = freqs[::-1]

        if show_approx and approx_row is not None:
            dwtmatr_plot = np.vstack([dwtmatr_plot, approx_row])
            freqs_plot = np.concatenate([freqs_plot, [fs / (2 ** levels)]])

        # --- decimate columns for plotting if large ---
        x_rel = x_uniform - x_uniform[0]   # relative time (s) -> nicer axis
        if return_plot:
            plot_N = dwtmatr_plot.shape[1]
            if plot_N > max_plot_cols:
                # choose indices uniformly
                idx = np.linspace(0, plot_N - 1, max_plot_cols).astype(int)
                x_plot = x_rel[idx]
                Z_plot = dwtmatr_plot[:, idx]
            else:
                x_plot = x_rel
                Z_plot = dwtmatr_plot

            fig, ax = plt.subplots(figsize=figsize)
            # imshow is usually faster; use extent so x axis corresponds to time and y to freqs
            extent = [x_plot[0], x_plot[-1], freqs_plot[0], freqs_plot[-1]]
            im = ax.imshow(
                Z_plot,
                aspect='auto',
                origin='lower',
                extent=extent,
                cmap=cmap,
                interpolation='nearest'
            )
            cbar = fig.colorbar(im, ax=ax)
            cbar.set_label("Amplitude (abs or normalized)" if not to_db else "Amplitude (dB)")
            if yscale == "log":
                ax.set_yscale("log")   # might raise for imshow; you can set yticks manually instead
            ax.set_xlabel("Time (s) (relative)")
            ax.set_ylabel("Frequency (Hz)")
            ax.set_title(f"Discrete Wavelet (SWT) — wavelet={wavelet}, levels={levels}")
            plt.tight_layout()
            plt.show()
        else:
            fig, ax = None, None

        extras = None
        if return_extra:
            extras = {
                "powers": powers,
                "approx_rms": approx_rms,
                "swt_coeffs": swt_coeffs
            }

        return dwtmatr, freqs, fig, ax, extras
    
    @staticmethod
    def splitCWT(
        data: np.ndarray,
        frequency_range: tuple = "auto",
        n_scales: int = 400,
        wavelet: str = "cmor1-1",
        y_scale: str = "log",
        z_scale: str= "log",
        do_plot: bool = True,
        split_plots: bool = False,
        print_logs: bool = True,
        tol: float = 1e-6,
        plot_config: dict = {},
    ) -> dict:
        """
        Performs a Multi-Range CWT. If the minimal Cone if Influence (COI) frequency of the data (depends on dt) is lower than the critcal frequency ()
        """
        #

        Logger = BoolLogger(print_logs)
        Logger.print("[splitCWT] Start der splitCWT")
        plot = None

        timer = Timer()
        EndResult = {
            'data': {},
            'timers': {},
            'plot': None,
        }
        #
        Timestamps = Array.Col(data, 0)
        Values = Array.Col(data, 1)
        #

        timer.Start("interpolation")
        # Gleichmäßigkeit prüfen
        dx = np.diff(Timestamps)
        if not np.allclose(dx, dx[0], atol=tol):
            Logger.print(f"[splitCWT] Ungleichmäßige Abstände erkannt. Interpolation auf gleichmäßiges Gitter...")
            N = len(Timestamps)
            x_uniform = np.linspace(Timestamps.min(), Timestamps.max(), N)
            y_uniform = np.interp(x_uniform, Timestamps, Values)
            dt = x_uniform[1] - x_uniform[0]
            t_operation = timer.Stop("interpolation")
            Logger.print(f"[splitCWT] Interpolation abgeschlossen. Δt={dt:.5g} - {60/dt:.5g}hz, Punkte={N}, T={TtoTime(dt*len(x_uniform))} in {TtoTime(t_operation)}")
        else:
            x_uniform = Timestamps
            y_uniform = Values
            dt = dx[0]
            t_operation = timer.Stop("interpolation")
            Logger.print(f"[splitCWT] Gleichmäßige Abstände: Δt={dt:.5g} - {60/dt:.5g}hz, Punkte={len(x_uniform)}, T={TtoTime(dt*len(x_uniform))} in {TtoTime(t_operation)}")
        
        Timestamps = x_uniform
        Values = y_uniform
        N_data = len(Timestamps)
        T_in_seconds = Timestamps[-1] - Timestamps[0]
        T_in_days = T_in_seconds/(3600*24)
        # Possible Frequency Ranges
        f_max = 1/dt/2
        f_min_coi = (CWT.COI_SCALE*np.sqrt(2*CWT.getBfromWavelet(wavelet))*pywt.ContinuousWavelet(wavelet).center_frequency)/(T_in_seconds)
        f_min = f_min_coi
        if frequency_range == "auto":
            pass
        else:
            if f_max > max(frequency_range):
                f_max =  max(frequency_range)
            else:
                print(f"[splitCWT] Maximum given Frequency of {max(frequency_range):.4g}hz is higher than maximum possible Frequency for data {f_max:.4g}hz (Nisq Limit). Limiting Range.")
            if f_min_coi < min(frequency_range):
                f_min =  min(frequency_range)
            else:
                print(f"[splitCWT] Minium given Frequency of {min(frequency_range):.4g}hz is lower than minimum possible Frequency for data {f_min:.4g}hz (COI Limit). Limiting Range.")


        Logger.print(f'[splitCWT] Maximum Frequency: {f_max:.4g}hz, Minimum Period: {TtoTime(1/f_max)}')
        Logger.print(f'[splitCWT] Minimum Frequency: {f_min:.4g}hz, Maximum Period: {TtoTime(1/f_min)}')

        if dt/T_in_days < 10:
            hasSplit = True
            dt_2 = T_in_days*20
            Logger.print(f'[splitCWT] Δt of {dt:.5g}s is too low for minimum COI Frequency ({TtoTime(T_in_seconds)} would require Δt of {T_in_days*10:.4g}s). Splitting into Ranges [{f_max:.4g}hz to {1/dt_2/2:.4g}hz, Δt={TtoTime(dt)}] and [{1/dt_2/2:.4g}hz to {f_min:.4g}hz, Δt={TtoTime(dt_2)}] to prevent long calculation time.')
            Timestamps_2 = np.linspace(Timestamps[0], Timestamps[-1], int(T_in_seconds/dt_2))
            Values_2 = np.interp(Timestamps_2, Timestamps, Values)
        else:
            hasSplit = False

        if hasSplit:
            #Notes: freqs1[0] ~ freqs2[-1]
            #
            #
            ## CWT1


            timer.Start("CWT1")
            Logger.print(f'[splitCWT] starting CWT-1 calculation with {wavelet}-Wavelet and {int(n_scales)}-Scales')
            
            freqs_1 = np.logspace(np.log10(1/dt_2/2), np.log10(f_max), int(n_scales))
            central = pywt.central_frequency(wavelet)
            scales = central / (freqs_1 * dt)
            cwtmatr_1, freqs_1 = pywt.cwt(Values, scales, wavelet, sampling_period=dt)
            cwtmatr_abs_1 = np.abs(cwtmatr_1)

            t_operation = timer.Stop("CWT1")
            Logger.print(f"[splitCWT] CWT-1 calculation done in {TtoTime(t_operation)}")

            ## CWT2
            timer.Start("CWT2")
            Logger.print(f'[splitCWT] starting CWT-2 calculation with {wavelet}-Wavelet and {int(n_scales)}-Scales')
            
            freqs_2 = np.logspace(np.log10(f_min), np.log10(1/dt_2/2), n_scales)
            central = pywt.central_frequency(wavelet)
            scales = central / (freqs_2 * dt_2)
            cwtmatr_2, freqs_2 = pywt.cwt(Values_2, scales, wavelet, sampling_period=dt_2)
            cwtmatr_abs_2 = np.abs(cwtmatr_2)

            t_operation = timer.Stop("CWT2")
            Logger.print(f"[splitCWT] CWT-2 calculation done in {TtoTime(t_operation)}")

            if do_plot:
                if not split_plots:
                    timer.Start("plot")
                    plot = CWT.PlotMultiCWT([cwtmatr_abs_1, cwtmatr_abs_2], [freqs_1, freqs_2], [Timestamps, Timestamps_2], y_scale=y_scale, z_scale=z_scale, wavelet=wavelet, inter=plot_config.get('inter', 5))
                    t_operation = timer.Stop("plot")
                    Logger.print(f"[splitCWT] Generating Plot done in {TtoTime(t_operation)}")
                    plot.show()
                else:
                    timer.Start("plot")
                    plot_1 = CWT.PlotCWT(cwtmatr_abs_1, freqs_1, Timestamps, y_scale=y_scale, z_scale=z_scale, wavelet=wavelet, inter=plot_config.get('inter', 5))
                    plot_2 = CWT.PlotCWT(cwtmatr_abs_2, freqs_2, Timestamps_2, y_scale=y_scale, z_scale=z_scale, wavelet=wavelet, inter=plot_config.get('inter', 5))
                    t_operation = timer.Stop("plot")
                    Logger.print(f"[splitCWT] Generating Plot done in {TtoTime(t_operation)}")

        elif not hasSplit:
            timer.Start("CWT")
            Logger.print(f'[splitCWT] starting CWT calculation with {wavelet}-Wavelet and {n_scales}-Scales')
            freqs = np.logspace(np.log10(f_min), np.log10(f_max), n_scales)
            central = pywt.central_frequency(wavelet)
            scales = central / (freqs * dt)
            cwtmatr, freqs = pywt.cwt(Values, scales, wavelet, sampling_period=dt)
            cwtmatr_abs = np.abs(cwtmatr)
            t_operation = timer.Stop("CWT")
            Logger.print(f"[splitCWT] CWT-calculation done in {TtoTime(t_operation)}")
            if do_plot:
                timer.Start("plot")
                plot = CWT.PlotCWT(cwtmatr_abs, freqs, Timestamps, y_scale=y_scale, z_scale=z_scale, wavelet=wavelet, inter=plot_config.get('inter', 5))
                t_operation = timer.Stop("plot")
                Logger.print(f"[splitCWT] Generating Plot done in {TtoTime(t_operation)}")
        
        EndResult['plot'] = plot
        return EndResult



    @staticmethod
    def PlotCWT(
        cwtmatr: np.ndarray, freqs: np.ndarray, timestamps: np.ndarray, limit_by_coi: bool=True, wavelet: str = None, y_scale="log", z_scale="linear",
        cmap="viridis", figsize=(12,6), dpi=400, inter=5, cwtmatr_absolute: bool = True) -> plt.Figure:
        if not cwtmatr_absolute:
            cwtmatr = np.abs(cwtmatr)
        Z_values = cwtmatr[:, 0:cwtmatr.shape[1]]

        if limit_by_coi and wavelet is None:
            print("NO WAVELET GIVEN")
            raise Exception
            return

        if limit_by_coi:
            x_plot = timestamps
            y_plot = freqs
            # distance to edge (seconds) for each plotted time
            dist_to_edge = np.minimum(x_plot - x_plot[0], x_plot[-1] - x_plot)
            # avoid division by zero
            eps = 1e-12
            # coi frequency threshold per time (Hz): frequencies >= coi_freq are considered safe
            coi_freq = (CWT.COI_SCALE*np.sqrt(2.0*CWT.getBfromWavelet(wavelet)) * pywt.ContinuousWavelet(wavelet).center_frequency) / (dist_to_edge + eps)   # shape (n_times,)
            # mask: valid if freq >= coi_freq(time)
            # build boolean array shape (n_freqs, n_times)
            # freqs is shape (n_freqs,), coi_freq is (n_times,)
            valid = (y_plot[:, None] >= coi_freq[None, :])
            # Mask out values outside COI (i.e., where valid == False)
            Z_masked = np.ma.array(Z_values, mask=~valid)
            # For plotting the COI line: only plot where coi_freq is inside the computed freq-range
            fmin, fmax = freqs.min(), freqs.max()
            coi_freq_plot = np.where((coi_freq >= fmin) & (coi_freq <= fmax), coi_freq, np.nan)

            vmin = np.percentile(Z_values[valid], 2)
            if vmin < 1e-3:
                vmin = 1e-3
            vmax = np.percentile(Z_values[valid], 98)
        else:
            vmin = np.percentile(Z_values, 2)
            if vmin < 1e-3:
                vmin = 1e-3
            vmax = np.percentile(Z_values, 98)

        if z_scale.lower() in ("log",):
            znorm = LogNorm(vmin=vmin, vmax=vmax)
        else:
            znorm = Normalize(vmin=vmin, vmax=vmax)


        #Create Plot Instance
        fig, axs = plt.subplots(figsize=figsize, dpi=dpi)
        fig.canvas.draw()
        if limit_by_coi:
            if (len(timestamps) == Z_masked.shape[1]) and (len(y_plot) == Z_masked.shape[0]):
                x,y,z = CWT.downsample_x(x_plot, y_plot, Z_masked, inter=inter)
                pcm = axs.pcolormesh(x,y,z, norm=znorm, shading='nearest', cmap=cmap)
            else:
                x_edges = compute_edges(x_plot)
                y_edges = compute_edges(y_plot)
                x,y,z = CWT.downsample_x(x_edges, y_edges, Z_masked, inter=inter)
                pcm = axs.pcolormesh(x,y,z, norm=znorm, shading='auto', cmap=cmap)
            # draw COI line only where inside freq range
            axs.plot(x_plot, coi_freq_plot, color='white', linestyle='--', linewidth=1, label='COI')
            # optionally shade the region outside COI (low frequencies near edges) for clarity:
            # we shade only where coi_freq_plot is finite (i.e. inside f-range).
            # fill between ymin and coi (mask NaNs automatically)
            ymin = fmin if fmin > 0 else (np.min(freqs[freqs > 0]) if np.any(freqs > 0) else 1e-12)
            # use where to avoid drawing fill under NaNs
            finite_mask = ~np.isnan(coi_freq_plot)
            if finite_mask.any():
                axs.fill_between(x_plot[finite_mask], ymin, coi_freq_plot[finite_mask],
                                color='white', alpha=0.4, linewidth=0)
        else:
            pcm = axs.pcolormesh(timestamps, freqs, Z_values, norm=znorm, shading='nearest', cmap=cmap)

        if y_scale in ("linear", ):
            axs.set_yscale("linear")
        else:
            axs.set_yscale("log")
        axs.set_xlabel("Time (s)")
        if limit_by_coi:
            axs.set_ylim(np.min(coi_freq), np.max(y_plot))
        axs.set_ylabel("Frequency (Hz)")
        axs.set_title(f"Continuous Wavelet Transform (Scaleogram) | {wavelet} | x{inter}")
        fig.colorbar(pcm, ax=axs)
        fig.tight_layout()
        return fig

    @staticmethod
    def PlotMultiCWT(
        cwtmatr: List[np.ndarray], freqs: List[np.ndarray], timestamps: List[np.ndarray], limit_by_coi: bool=True, wavelet: str = None, y_scale="log", z_scale="linear",
        cmap="viridis", figsize=(12,6), dpi=200, cwtmatr_absolute: bool = True, inter: int = 5,
        ) -> plt.Figure:
        if (len(cwtmatr) != len(freqs)) or (len(freqs) != len(timestamps)):
            raise Exception("Inputs for CwtMatrix, Freqs and Timestmaps are not of equal length")
        else:
            PlotDim= len(cwtmatr)
            if PlotDim > 2:
                print(f"[splitCWT] PlotDim is {PlotDim}>2. Limited to 2.")
        if not cwtmatr_absolute:
            cwtmatr = [np.abs(matrix) for matrix in cwtmatr]
        for i in range(0, PlotDim):
            freqs[i], cwtmatr[i] = CWT.__ensure_sorted(freqs[i], cwtmatr[i])

        dt1 = np.median(np.diff(timestamps[0]))
        dt2 = np.median(np.diff(timestamps[1]))
        dt_min = min(dt1, dt2)
        t_start = max(min(timestamps[0]), min(timestamps[1]))  # oder min() wenn beide gleichbereich
        t_end   = min(max(timestamps[0]), max(timestamps[1]))  # sicherstellen Überlappung

        time_common = np.arange(t_start, t_end + dt_min/2, dt_min)
        def interp_to_common(time_orig, A):
            # A shape (nfreq, ntime_orig)
            return np.array([np.interp(time_common, time_orig, row) for row in A])
        
        Ai = [None, None]
        Ai[0] = interp_to_common(timestamps[0], cwtmatr[0])
        Ai[1] = interp_to_common(timestamps[1], cwtmatr[1])
        freqs_all = np.concatenate([freqs[0], freqs[1]])
        A_all     = np.vstack([Ai[0], Ai[1]])
        
        order = np.argsort(freqs_all)
        freqs_sorted = freqs_all[order]
        A_sorted     = A_all[order, :]

        p99 = np.percentile(A_sorted, 99, axis=1, keepdims=True)
        p99[p99 == 0] = 1e-12
        A_norm = A_sorted / p99

        return CWT.PlotCWT(A_norm, freqs_sorted, time_common, limit_by_coi=limit_by_coi, wavelet=wavelet, y_scale=y_scale, z_scale=z_scale, cmap=cmap, figsize=figsize, dpi=dpi, cwtmatr_absolute=cwtmatr_absolute, inter=inter)

    @staticmethod
    def __ensure_sorted(freqs, mat):
        # sort nach freq aufsteigend
        idx = np.argsort(freqs)
        freqs_s = freqs[idx]
        mat_s = mat[idx, :]
        return freqs_s, mat_s
    
    @staticmethod
    def getBfromWavelet(wavelet: str):
        if wavelet[0:4] == "cmor":
            k = wavelet.strip("cmor").split('-')[0]
            return float(k)
        else:
            return 1.0

    @staticmethod
    def downsample_x_old(x, y, Z, inter=5):
        """
        Downsample Z only along the x-axis by grouping 'inter' columns together.
        Returns (x_ds, y, Z_ds).
        
        Parameters
        ----------
        x : 1D array-like, length nx (columns of Z)
        y : 1D array-like, length ny (rows of Z)
        Z : 2D array-like or numpy.ma.MaskedArray with shape (ny, nx)
        inter : int, downsampling factor (e.g. 10 => each group of 10 x points -> 1)
        
        Returns
        -------
        x_ds : 1D numpy array length m = ceil(nx / inter)
        y     : same as input y (unchanged)
        Z_ds  : 2D array (ny, m) or MaskedArray if input was masked
        """
        x = np.asarray(x)
        y = np.asarray(y)

        # Accept masked arrays, preserve mask behavior
        is_masked = np.ma.is_masked(Z) or isinstance(Z, np.ma.MaskedArray)
        if is_masked:
            Z = np.ma.asarray(Z)
        else:
            Z = np.asarray(Z)

        if Z.ndim != 2:
            raise ValueError("Z must be 2D (ny, nx).")
        ny, nx = Z.shape
        if x.shape[0] != nx:
            raise ValueError(f"len(x) ({x.shape[0]}) != Z.shape[1] ({nx})")
        if y.shape[0] != ny:
            raise ValueError(f"len(y) ({y.shape[0]}) != Z.shape[0] ({ny})")

        m = (nx + inter - 1) // inter  # number of output x bins
        # compute downsampled x as block mean
        x_ds = np.empty(m, dtype=x.dtype)
        if is_masked:
            col_means = []
            for j in range(m):
                start = j * inter
                end = min(start + inter, nx)
                x_ds[j] = x[start:end].mean()
                # mean across the sliced columns for each row (preserves mask semantics)
                col_mean = Z[:, start:end].mean(axis=1)
                col_means.append(col_mean)
            Z_ds = np.ma.column_stack(col_means)   # shape (ny, m)
        else:
            # vectorized building via list comprehension (fast enough)
            cols = []
            for j in range(m):
                start = j * inter
                end = min(start + inter, nx)
                x_ds[j] = x[start:end].mean()
                cols.append(Z[:, start:end].mean(axis=1))
            Z_ds = np.column_stack(cols)  # shape (ny, m)

        return x_ds, y, Z_ds
    @staticmethod
    def downsample_x(x, y, Z, inter=5, method='linear'):
        """
        Downsample Z only along the x-axis using interpolation.
        Masked arrays are supported and mask is preserved.
        
        Parameters
        ----------
        x : 1D array-like, length nx (columns of Z)
        y : 1D array-like, length ny (rows of Z)
        Z : 2D array-like or numpy.ma.MaskedArray with shape (ny, nx)
        inter : int, downsampling factor (e.g. 10 => each group of 10 x points -> 1)
        method : str, interpolation method ('linear', 'cubic', etc.)

        Returns
        -------
        x_ds : 1D numpy array length ceil(nx / inter)
        y     : same as input y (unchanged)
        Z_ds  : 2D array (ny, ceil(nx / inter)) or MaskedArray if input was masked
        """
        x = np.asarray(x)
        y = np.asarray(y)

        # Maske erkennen und Array konvertieren
        is_masked = np.ma.is_masked(Z) or isinstance(Z, np.ma.MaskedArray)
        if is_masked:
            Z = np.ma.asarray(Z)
        else:
            Z = np.asarray(Z)

        if Z.ndim != 2:
            raise ValueError("Z must be 2D (ny, nx).")
        ny, nx = Z.shape
        if x.shape[0] != nx:
            raise ValueError(f"len(x) ({x.shape[0]}) != Z.shape[1] ({nx})")
        if y.shape[0] != ny:
            raise ValueError(f"len(y) ({y.shape[0]}) != Z.shape[0] ({ny})")

        # Neue Länge entlang x
        new_nx = int(np.ceil(nx / inter))
        x_ds = np.linspace(x[0], x[-1], new_nx)

        if is_masked:
            # Z als MaskedArray behandeln
            Z_ds = np.ma.empty((ny, new_nx))
            for i in range(ny):
                row = Z[i, :]
                mask = row.mask if hasattr(row, "mask") else np.zeros_like(row, dtype=bool)
                if mask.all():
                    # ganze Reihe ist maskiert → auch im Ergebnis maskiert
                    Z_ds[i, :] = np.ma.masked
                else:
                    f = interp1d(x[~mask], row.data[~mask], kind=method,
                                bounds_error=False, fill_value=np.nan)
                    Z_interp = f(x_ds)
                    # rekonstruierte Maske → wo nicht interpolierbar
                    Z_interp = np.ma.masked_invalid(Z_interp)
                    Z_ds[i, :] = Z_interp
        else:
            # Normales ndarray
            Z_ds = np.empty((ny, new_nx))
            for i in range(ny):
                f = interp1d(x, Z[i, :], kind=method)
                Z_ds[i, :] = f(x_ds)

        return x_ds, y, Z_ds

    @staticmethod
    def splitCWT_Fast(
        data: np.ndarray,
        frequency_range: tuple = "auto",
        n_scales: int = 400,
        wavelet: str = "cmor1-1",
        y_scale: str = "log",
        z_scale: str = "log",
        do_plot: bool = True,
        split_plots: bool = False,
        print_logs: bool = True,
        tol: float = 1e-6,
        plot_config: dict = {},
        quality: float = 0.5,           # 0..1, 1 = volle Qualität, 0.25 = sehr schnell / grob
        max_decimation: int = 32,       # max. erlaubte Dezimationsfaktor (safety)
        min_scales: int = 32,          # Minimum an Skalen, auch bei sehr kleinem quality
    ) -> dict:
        """
        Fast variant of splitCWT: uses decimation + fewer scales to compute a CWT faster.
        quality: float in (0,1], 1 => same as splitCWT; lower => faster & lower quality.
        Returns EndResult dict similar to splitCWT, and meta info under EndResult['data']['meta'].
        """

        Logger = BoolLogger(print_logs)
        Logger.print("[splitCWT_Fast] Start (quality={:.3f})".format(quality))
        timer = Timer()
        EndResult = {'data': {}, 'timers': {}, 'plot': None}

        # --- Read and uniformize input ---
        Timestamps = Array.Col(data, 0).astype(float)
        Values = Array.Col(data, 1).astype(float)

        # interpolation to uniform grid if needed
        dx = np.diff(Timestamps)
        if dx.size == 0:
            raise ValueError("Not enough data points.")
        if not np.allclose(dx, dx[0], atol=tol):
            Logger.print("[splitCWT_Fast] Ungleichmäßige Abstände erkannt. Interpolating to uniform grid...")
            N = len(Timestamps)
            x_uniform = np.linspace(Timestamps.min(), Timestamps.max(), N)
            y_uniform = np.interp(x_uniform, Timestamps, Values)
            dt = x_uniform[1] - x_uniform[0]
            Logger.print(f"[splitCWT_Fast] Interpolation: N={N}, dt={dt:.5g}s")
        else:
            x_uniform = Timestamps
            y_uniform = Values
            dt = dx[0]
            Logger.print(f"[splitCWT_Fast] Already uniform: N={len(x_uniform)}, dt={dt:.5g}s")

        # metadata
        N_data = len(x_uniform)
        T_in_seconds = x_uniform[-1] - x_uniform[0]
        T_in_days = T_in_seconds / (3600 * 24)
        fs = 1.0 / dt
        f_max_possible = fs / 2.0

        # --- frequency range handling (respect user's frequency_range if given) ---
        f_min_coi = (CWT.COI_SCALE * np.sqrt(2 * CWT.getBfromWavelet(wavelet)) * pywt.ContinuousWavelet(wavelet).center_frequency) / (T_in_seconds)
        f_min = f_min_coi
        if frequency_range != "auto":
            # user-provided tuple or list expected (min, max)
            try:
                f_user_min, f_user_max = float(min(frequency_range)), float(max(frequency_range))
                # clip to physically possible
                f_min = max(f_min_coi, f_user_min)
                if f_user_max < f_max_possible:
                    f_max = f_user_max
                else:
                    f_max = f_max_possible
            except Exception:
                Logger.print("[splitCWT_Fast] Invalid frequency_range provided. Falling back to auto.")
                f_max = f_max_possible
        else:
            f_max = f_max_possible

        Logger.print(f"[splitCWT_Fast] freq-range candidate: {f_min:.4g} .. {f_max:.4g} Hz")

        # --- determine decimation factor based on quality and safety (avoid aliasing) ---
        if not (0 < quality <= 1.0):
            quality = max(0.01, min(1.0, quality))
        # Heuristic: desired reduction factor ~ 1/quality
        desired_reduction = 1.0 / quality
        # Target new sampling frequency: try to keep Nyquist >= 2.5 * f_max (some safety)
        target_fs = min(fs, max(2.5 * f_max, fs / desired_reduction))
        decim_est = int(np.floor(fs / target_fs)) if target_fs > 0 else 1
        decim = max(1, min(decim_est, max_decimation))
        # ensure decim isn't larger than N/64 (avoid ridiculously small signals)
        decim = min(decim, max(1, N_data // 64))

        # apply decimation by interpolating to a coarser uniform grid (safer than naive downsample)
        if decim > 1:
            new_N = max(16, int(np.ceil(N_data / decim)))
            x_ds = np.linspace(x_uniform[0], x_uniform[-1], new_N)
            y_ds = np.interp(x_ds, x_uniform, y_uniform)
            dt_ds = x_ds[1] - x_ds[0]
            Logger.print(f"[splitCWT_Fast] Decimated by factor ~{decim}: {N_data} -> {new_N} samples, dt={dt_ds:.5g}s")
        else:
            x_ds = x_uniform
            y_ds = y_uniform
            dt_ds = dt
            Logger.print(f"[splitCWT_Fast] No decimation (decim=1), dt={dt_ds:.5g}s")

        # --- choose reduced n_scales based on quality (but not below min_scales) ---
        n_scales_fast = max(min_scales, int(np.ceil(n_scales * quality)))
        Logger.print(f"[splitCWT_Fast] Using {n_scales_fast} scales (orig {n_scales}, quality {quality:.3f})")

        # --- Decide whether to split like original splitCWT (for COI reasons) ---
        # Use same heuristic as original: if dt/T_in_days < 10 then split, but compare with decimated dt
        hasSplit = False
        if (dt_ds / (T_in_days if T_in_days > 0 else 1.0)) < 10:
            hasSplit = True
            # choose dt_2 as in original: T_in_days * 20 (seconds)
            dt_2 = T_in_days * 20.0
            # guard dt_2 lower bound
            if dt_2 <= 0:
                dt_2 = dt_ds
            # define a second downsampled grid for long periods
            N2 = max(16, int(np.ceil(T_in_seconds / dt_2)))
            x_ds2 = np.linspace(x_uniform[0], x_uniform[-1], N2)
            y_ds2 = np.interp(x_ds2, x_uniform, y_uniform)
            dt2 = x_ds2[1] - x_ds2[0]
            Logger.print(f"[splitCWT_Fast] Splitting into two ranges (fast mode): dt1={dt_ds:.5g}s dt2={dt2:.5g}s")
        else:
            hasSplit = False

        # --- Now compute CWT(s) on reduced data / reduced scales ---
        results = {}
        timer.Start("cwt_compute")
        central = pywt.central_frequency(wavelet)

        try:
            if hasSplit:
                # Upper freq range on faster-sampled decimated signal (x_ds, y_ds)
                freqs_1 = np.logspace(np.log10(1.0 / dt2 / 2.0), np.log10(f_max), n_scales_fast)
                scales_1 = central / (freqs_1 * dt_ds)   # note: keep dt_ds (higher res) for upper band if desired
                # Do CWT on the *faster* series (x_ds or original?) choose x_ds for speed
                cwtmatr_1, freqs_1 = pywt.cwt(y_ds, scales_1, wavelet, sampling_period=dt_ds)
                cwtmatr_abs_1 = np.abs(cwtmatr_1)

                # Lower freq range on coarser series x_ds2
                freqs_2 = np.logspace(np.log10(f_min), np.log10(1.0 / dt2 / 2.0), n_scales_fast)
                scales_2 = central / (freqs_2 * dt2)
                cwtmatr_2, freqs_2 = pywt.cwt(y_ds2, scales_2, wavelet, sampling_period=dt2)
                cwtmatr_abs_2 = np.abs(cwtmatr_2)

                results['cwt1'] = (cwtmatr_abs_1, freqs_1, x_ds)
                results['cwt2'] = (cwtmatr_abs_2, freqs_2, x_ds2)
            else:
                freqs_f = np.logspace(np.log10(f_min), np.log10(f_max), n_scales_fast)
                scales_f = central / (freqs_f * dt_ds)
                cwtmatr, freqs_f = pywt.cwt(y_ds, scales_f, wavelet, sampling_period=dt_ds)
                cwtmatr_abs = np.abs(cwtmatr)
                results['cwt'] = (cwtmatr_abs, freqs_f, x_ds)
        except Exception as e:
            timer.Stop("cwt_compute")
            Logger.print(f"[splitCWT_Fast] CWT failed: {e}")
            raise

        t_cwt = timer.Stop("cwt_compute")
        Logger.print(f"[splitCWT_Fast] CWT compute done in {TtoTime(t_cwt)}")

        # --- plotting (if requested) using existing PlotCWT / PlotMultiCWT helpers ---
        plot = None
        if do_plot:
            timer.Start("plot")
            if hasSplit:
                if not split_plots:
                    plot = CWT.PlotMultiCWT([results['cwt1'][0], results['cwt2'][0]],
                                            [results['cwt1'][1], results['cwt2'][1]],
                                            [results['cwt1'][2], results['cwt2'][2]],
                                            y_scale=y_scale, z_scale=z_scale, wavelet=wavelet, inter=plot_config.get('inter', 5))
                else:
                    p1 = CWT.PlotCWT(results['cwt1'][0], results['cwt1'][1], results['cwt1'][2], y_scale=y_scale, z_scale=z_scale, wavelet=wavelet, inter=plot_config.get('inter', 5))
                    p2 = CWT.PlotCWT(results['cwt2'][0], results['cwt2'][1], results['cwt2'][2], y_scale=y_scale, z_scale=z_scale, wavelet=wavelet, inter=plot_config.get('inter', 5))
                    plot = (p1, p2)
            else:
                plot = CWT.PlotCWT(results['cwt'][0], results['cwt'][1], results['cwt'][2], y_scale=y_scale, z_scale=z_scale, wavelet=wavelet, inter=plot_config.get('inter', 5))
            t_plot = timer.Stop("plot")
            Logger.print(f"[splitCWT_Fast] Plot done in {TtoTime(t_plot)}")

        # --- build EndResult ---
        EndResult['plot'] = plot
        EndResult['timers']['cwt_compute'] = t_cwt
        EndResult['timers']['total'] = t_cwt + (t_plot if do_plot else 0)
        EndResult['data']['meta'] = {
            'decimation': decim,
            'decimated_samples': x_ds.size,
            'quality': quality,
            'n_scales_requested': n_scales,
            'n_scales_used': n_scales_fast,
            'wavelet': wavelet,
            'f_min': float(f_min),
            'f_max': float(f_max),
            'dt_original': float(dt),
            'dt_used': float(dt_ds),
        }

        return EndResult




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

class BoolLogger():
    def __init__(self, do: bool=True):
        self.do = do
    def print(self, *args):
        if self.do:
            print(*args)
        else:
            pass

class Timer():
    def __init__(self):
        self.timers = {}

    def Start(self, name: str):
        self.timers[name] = [time.time(), None]

    def Stop(self, name: str):
        times = self.timers.get(name, None)
        if times is None:
            return None
        else:
            self.timers[name][1] = time.time()
        return self.timers[name][1] - self.timers[name][0]
    
    def StopAndPrint(self, name: str):
        times = self.timers.get(name, None)
        if times is None:
            return None
        else:
            self.timers[name][1] = time.time()
        print(TtoTime(self.timers[name][1] - self.timers[name][0]))
        return self.timers[name][1] - self.timers[name][0]

    def Get(self, name: str):
        return self.timers.get(name, None)
    def GetAll(self):
        return self.timers

def TtoTime(T) -> str:
    t = np.abs(T)
    if t < 1:
        return f'{t*1000:.4g}ms'
    elif t < 60*2:
        return f'{t:.4g}s'
    elif t < 3600*2:
        return f'{t/60:.4g}m'
    elif t < 3600*24*2:
        return f'{t/3600:.4g}h'
    elif t < 3600*24*365*2:
        return f'{t/3600/24:.4g}d'
    else:
        return f'{t/3600/24/365:.4g}a'
    

