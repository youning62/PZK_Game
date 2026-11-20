"""Tiny procedural synth toolkit used to generate all of the game's music / SFX.

Everything is pure numpy/scipy; nothing is sampled.  Output is written with
`soundfile` (OGG Vorbis).  See generate_all.py for how to run.
"""
import numpy as np
from numpy.fft import rfft, irfft
from scipy import signal
from scipy.ndimage import maximum_filter1d, minimum_filter1d, uniform_filter1d

SR = 44100


# ----------------------------------------------------------------------------
# pitch helpers
# ----------------------------------------------------------------------------
_NOTE = {'C': 0, 'D': 2, 'E': 4, 'F': 5, 'G': 7, 'A': 9, 'B': 11}


def midi(name):
    if isinstance(name, (int, float, np.integer, np.floating)):
        return float(name)
    letter = name[0].upper()
    i, acc = 1, 0
    while i < len(name) and name[i] in '#b':
        acc += 1 if name[i] == '#' else -1
        i += 1
    return 12 * (int(name[i:]) + 1) + _NOTE[letter] + acc


def hz(name):
    return 440.0 * 2 ** ((midi(name) - 69) / 12)


def chord(s):
    """'A2 E3 G3' -> [midi...]"""
    return [midi(x) for x in s.split()]


def parse(s, start=0.0, vel=0.8):
    """Parse a melody string into events.

    Tokens: NOTE:beats  (e.g. 'C#5:0.5'), chords with '+' ('C4+E4:1'),
    rests 'r:1', optional velocity suffix '@0.6'.  '|' is ignored (bar marker).
    Returns (events, end_beat) with events = [(beat, dur_beats, [midis], vel)].
    """
    ev, t = [], start
    for tok in s.split():
        if tok == '|':
            continue
        v = vel
        if '@' in tok:
            tok, vs = tok.split('@')
            v = float(vs)
        name, d = tok.split(':')
        d = float(d)
        if name != 'r':
            ev.append((t, d, [midi(x) for x in name.split('+')], v))
        t += d
    return ev, t


# ----------------------------------------------------------------------------
# envelopes / basic oscillators
# ----------------------------------------------------------------------------
def tt(n):
    return np.arange(n) / SR


def gate_env(n, gate, rel, att=0.003):
    """1 during gate (with linear attack), raised-cosine release to 0."""
    t = tt(n)
    e = np.clip(t / max(att, 1e-5), 0, 1)
    r = np.clip((t - gate) / max(rel, 1e-5), 0, 1)
    return e * 0.5 * (1 + np.cos(np.pi * r))


def adsr(n, gate, a=0.01, d=0.2, s=0.7, r=0.2):
    t = tt(n)
    e = np.where(t < a, t / max(a, 1e-5), s + (1 - s) * np.exp(-(t - a) / max(d, 1e-5)))
    rr = np.clip((t - gate) / max(r, 1e-5), 0, 1)
    return e * 0.5 * (1 + np.cos(np.pi * rr))


def tail_fade(x, frac=0.15):
    n = len(x)
    k = max(1, int(n * frac))
    w = 0.5 * (1 + np.cos(np.linspace(0, np.pi, k)))
    x = x.copy()
    x[-k:] *= w if x.ndim == 1 else w[:, None]
    return x


def edge_fade(x, fin=0.002, fout=0.01):
    x = x.copy()
    a, b = max(1, int(fin * SR)), max(1, int(fout * SR))
    wi = np.linspace(0, 1, a) ** 2
    wo = np.linspace(1, 0, b) ** 2
    if x.ndim == 1:
        x[:a] *= wi
        x[-b:] *= wo
    else:
        x[:a] *= wi[:, None]
        x[-b:] *= wo[:, None]
    return x


def phase_of(f, n):
    f = np.broadcast_to(np.asarray(f, float), (n,))
    return 2 * np.pi * np.cumsum(f) / SR


def vibrato(f0, n, rate=5.0, cents=10.0, delay=0.2, ramp=0.3):
    t = tt(n)
    r = np.clip((t - delay) / ramp, 0, 1)
    return f0 * 2 ** (cents * r * np.sin(2 * np.pi * rate * t) / 1200)


def harmonic(f, n, weights, cutoff=None, slope=2.0, phase0=0.0, rand_phase=None):
    """Additive band-limited oscillator.  `weights[k-1]` = amplitude of harmonic k.
    `cutoff` (scalar or array Hz) applies a smooth low-pass of order `slope`."""
    f = np.broadcast_to(np.asarray(f, float), (n,))
    fmax = float(np.max(f))
    ph = phase_of(f, n) + phase0
    out = np.zeros(n)
    for k, w in enumerate(weights, start=1):
        if k * fmax > SR * 0.45:
            break
        if cutoff is not None and np.ndim(cutoff) == 0 and k * float(np.min(f)) > cutoff * 10 ** (45 / (20 * slope)):
            break
        if w == 0:
            continue
        g = w
        if cutoff is not None:
            g = w / np.sqrt(1 + (k * f / cutoff) ** (2 * slope))
        p = 0.0 if rand_phase is None else rand_phase[k % len(rand_phase)]
        out += g * np.sin(k * ph + p)
    return out


SAW = [1.0 / k for k in range(1, 80)]
SQUARE = [1.0 / k if k % 2 else 0.0 for k in range(1, 80)]


def fm(f, n, ratio, index, carrier=1.0):
    pm = phase_of(np.asarray(f) * ratio, n)
    pc = phase_of(np.asarray(f) * carrier, n)
    return np.sin(pc + index * np.sin(pm))


# ----------------------------------------------------------------------------
# filters
# ----------------------------------------------------------------------------
def lp(x, fc, order=2):
    sos = signal.butter(order, min(fc, SR * 0.45), 'low', fs=SR, output='sos')
    return signal.sosfilt(sos, x, axis=0)


def hp(x, fc, order=2):
    sos = signal.butter(order, fc, 'high', fs=SR, output='sos')
    return signal.sosfilt(sos, x, axis=0)


def bp(x, lo, hi, order=2):
    sos = signal.butter(order, [lo, min(hi, SR * 0.45)], 'band', fs=SR, output='sos')
    return signal.sosfilt(sos, x, axis=0)


def loop_filter(x, kind, *args, order=2):
    """Apply an IIR filter to a looping signal in steady state (no seam)."""
    f = {'lp': lp, 'hp': hp, 'bp': bp}[kind]
    y = f(np.concatenate([x, x], axis=0), *args, order=order)
    return y[len(x):]


def fft_shape(x, gain_fn):
    """Circular (loop-safe) zero-phase spectral shaping. gain_fn(freqs)->gain."""
    X = rfft(x, axis=0)
    fr = np.fft.rfftfreq(len(x), 1 / SR)
    g = gain_fn(fr)
    if X.ndim == 2:
        g = g[:, None]
    return irfft(X * g, n=len(x), axis=0)


def resonator(x, f, q):
    """2-pole resonant band-pass (constant peak gain)."""
    b, a = signal.iirpeak(min(f, SR * 0.45), q, fs=SR)
    return signal.lfilter(b, a, x)


# ----------------------------------------------------------------------------
# instruments  (all return mono float arrays starting at note-on)
# ----------------------------------------------------------------------------
def epiano(f, dur, vel=0.7, rel=0.35, decay=None):
    decay = decay or 1.8 * (220 / f) ** 0.35
    n = int((dur + rel) * SR)
    t = tt(n)
    amp = np.exp(-t / decay) * gate_env(n, dur, rel, 0.002)
    idx = (0.4 + 1.3 * vel) * np.exp(-t / 0.3) + 0.12
    body = fm(f, n, 1.0, idx)
    tine = np.sin(2 * np.pi * f * t + (1.2 * vel) * np.exp(-t / 0.015) * np.sin(2 * np.pi * 14 * f * t))
    tine *= np.exp(-t / 0.06) * 0.35
    trem = 1 + 0.06 * np.sin(2 * np.pi * 4.5 * t)
    return (body + tine) * amp * trem * (0.4 + 0.6 * vel)


def bell(f, dur, vel=0.7, decay=2.5, ratio=3.5, bright=1.0):
    n = int(decay * 4.0 * SR)
    t = tt(n)
    idx = bright * (0.5 + 1.5 * vel) * np.exp(-t / (decay * 0.25))
    y = fm(f, n, ratio, idx) * np.exp(-t / decay)
    y += 0.35 * np.sin(2 * np.pi * f * 2 * t) * np.exp(-t / (decay * 0.4))
    y *= np.clip(t / 0.001, 0, 1)
    return tail_fade(y, 0.25) * (0.3 + 0.7 * vel)


def music_box(f, dur, vel=0.7, decay=2.0):
    n = int(decay * 4 * SR)
    t = tt(n)
    y = np.sin(2 * np.pi * f * t) * np.exp(-t / decay)
    y += 0.4 * np.sin(2 * np.pi * 4 * f * t) * np.exp(-t / (decay * 0.25))
    y += 0.15 * np.sin(2 * np.pi * 6.27 * f * t) * np.exp(-t / (decay * 0.08))
    y *= np.clip(t / 0.0015, 0, 1)
    return tail_fade(y, 0.25) * (0.3 + 0.7 * vel)


def marimba(f, dur, vel=0.7):
    dec = 0.5 * (300 / f) ** 0.4
    n = int(dec * 5 * SR)
    t = tt(n)
    y = np.sin(2 * np.pi * f * t) * np.exp(-t / dec)
    y += 0.3 * np.sin(2 * np.pi * 3.93 * f * t) * np.exp(-t / (dec * 0.2))
    y += 0.08 * np.sin(2 * np.pi * 9.2 * f * t) * np.exp(-t / 0.01)
    y *= np.clip(t / 0.001, 0, 1)
    return tail_fade(y, 0.2) * (0.3 + 0.7 * vel)


def celesta(f, dur, vel=0.7, decay=1.2):
    n = int(decay * 4 * SR)
    t = tt(n)
    y = fm(f, n, 4.0, (0.4 + 1.2 * vel) * np.exp(-t / 0.04)) * np.exp(-t / decay)
    y += 0.25 * np.sin(2 * np.pi * 2 * f * t) * np.exp(-t / (decay * 0.3))
    y *= np.clip(t / 0.001, 0, 1)
    return tail_fade(y, 0.25) * (0.3 + 0.7 * vel)


def karplus(f, dur, t60=1.5, bright=0.5, pick=0.18, seed=0, gate=None, mute_rel=0.06):
    """Karplus-Strong plucked string with Lagrange fractional delay (in tune)."""
    rng = np.random.default_rng(seed)
    D = SR / f
    N = int(np.floor(D - 1.5))
    d = D - 0.5 - N                      # Lagrange delay, in [1, 2)
    lag = np.array([np.prod([(d - j) / (k - j) for j in range(4) if j != k]) for k in range(4)])
    h = np.convolve([0.5, 0.5], lag)     # loop filter taps at offsets N..N+4
    g = 10 ** (-3 / (t60 * f))
    n = int(dur * SR)
    P = N + 6
    y = np.zeros(n + P)
    L = int(D)
    exc = rng.uniform(-1, 1, L)
    # brightness: one-pole low-pass on the excitation
    a = 1 - bright
    exc = signal.lfilter([1 - a], [1, -a], exc)
    # pick position comb
    k = max(1, int(pick * L))
    exc = exc - np.roll(exc, k)
    exc -= exc.mean()
    y[P:P + L] += exc
    for i in range(P, n + P, N):
        j = min(i + N, n + P)
        m = j - i
        acc = np.zeros(m)
        for q in range(5):
            acc += h[q] * y[i - N - q:i - N - q + m]
        y[i:j] += g * acc
    y = y[P:]
    y = hp(y, 30, 1)
    if gate is not None:
        y *= gate_env(n, gate, mute_rel, 0.0005)
    return tail_fade(y, 0.05) * (1.0 / max(np.abs(y).max(), 1e-9))


_SEED = [0]


def _next_seed():
    _SEED[0] += 1
    return _SEED[0]


def pluck(f, dur, vel=0.7, t60=1.2, bright=0.55, stacc=None):
    """stacc: fraction of the written duration before the string is damped."""
    gate = dur * stacc if stacc else None
    total = gate + 0.08 if gate else max(dur, t60 * 0.9)
    y = karplus(f, total, t60=t60, bright=bright * (0.7 + 0.4 * vel), seed=_next_seed(), gate=gate)
    return y * (0.3 + 0.7 * vel)


def nylon(f, dur, vel=0.7):
    y = karplus(f, max(dur + 0.25, 1.2), t60=1.6, bright=0.35, pick=0.12, seed=_next_seed(),
                gate=dur + 0.15, mute_rel=0.12)
    y = lp(y, 3500, 1)
    return y * (0.3 + 0.7 * vel)


def saw_blep(f, n, phase0=0.0):
    """PolyBLEP band-limited sawtooth (cheap)."""
    f = np.broadcast_to(np.asarray(f, float), (n,))
    dt = f / SR
    p = (np.cumsum(dt) + phase0) % 1.0
    y = 2 * p - 1
    m = p < dt
    t = p[m] / dt[m]
    y[m] -= t + t - t * t - 1
    m = p > 1 - dt
    t = (p[m] - 1) / dt[m]
    y[m] -= t * t + t + t + 1
    return y


def pad(f, dur, vel=0.7, att=1.0, rel=2.0, cutoff=1600, detune=9, nv=3, seed=0):
    """Stereo detuned-saw pad through a low-pass -> (n, 2)."""
    rng = np.random.default_rng(seed)
    n = int((dur + rel) * SR)
    env = adsr(n, dur, a=att, d=1.0, s=0.85, r=rel)
    out = np.zeros((n, 2))
    for ch in range(2):
        for v in range(nv):
            c = (v - (nv - 1) / 2) * detune + rng.uniform(-2, 2)
            fv = vibrato(f * 2 ** (c / 1200), n, rate=rng.uniform(0.2, 0.5), cents=4, delay=0, ramp=0.01)
            out[:, ch] += saw_blep(fv, n, rng.uniform())
    out = lp(lp(out, cutoff, 2), cutoff * 1.5, 2)
    out *= env[:, None] / nv * 1.1
    return out * (0.4 + 0.6 * vel)


def bass(f, dur, vel=0.8, rel=0.08, drive=1.5, bright=1.0):
    n = int((dur + rel) * SR)
    t = tt(n)
    cut = 250 + bright * 900 * vel * np.exp(-t / 0.08)
    y = harmonic(f, n, [1, 0.5, 0.3, 0.15, 0.1, 0.06], cutoff=cut, slope=1.5)
    y = np.tanh(drive * y) / np.tanh(drive)
    return y * gate_env(n, dur, rel, 0.004) * (0.4 + 0.6 * vel)


def sub(f, dur, vel=0.7, att=0.3, rel=1.0):
    n = int((dur + rel) * SR)
    t = tt(n)
    y = np.sin(2 * np.pi * f * t) + 0.15 * np.sin(4 * np.pi * f * t)
    return y * adsr(n, dur, a=att, d=1, s=0.9, r=rel) * vel


def tuba(f, dur, vel=0.8, rel=0.1):
    n = int((dur + rel) * SR)
    t = tt(n)
    fr = f * 2 ** ((-35 * np.exp(-t / 0.04)) / 1200)
    fr = fr * 2 ** (6 * np.sin(2 * np.pi * 5 * t) * np.clip(t - 0.15, 0, 1) / 1200)
    cut = 220 + 700 * vel * np.exp(-t / 0.07) + 120
    y = harmonic(fr, n, [1 / k ** 0.7 for k in range(1, 25)], cutoff=cut, slope=2.5)
    return np.tanh(1.3 * y) * gate_env(n, dur, rel, 0.018) * (0.4 + 0.6 * vel)


BASSOON_W = [0.5, 1.0, 0.85, 0.7, 0.5, 0.35, 0.25, 0.15, 0.1, 0.07, 0.05, 0.03]


def bassoon(f, dur, vel=0.8, rel=0.1, bend=0.0, wobble=0.0):
    """bend: cents glide over the note; wobble: comedic slow vibrato depth (cents)."""
    n = int((dur + rel) * SR)
    t = tt(n)
    glide = bend * np.clip(t / max(dur, 1e-3), 0, 1) ** 1.5
    vib = 12 * np.sin(2 * np.pi * 5.3 * t) * np.clip((t - 0.15) / 0.2, 0, 1)
    wob = wobble * np.sin(2 * np.pi * 3.2 * t)
    fr = f * 2 ** ((glide + vib + wob - 20 * np.exp(-t / 0.03)) / 1200)
    y = harmonic(fr, n, BASSOON_W, cutoff=1400, slope=2)
    y += 0.02 * lp(np.random.default_rng(int(f)).standard_normal(n), 2000) * np.exp(-t / 0.1)
    return 0.4 * y * gate_env(n, dur, rel, 0.025) * (0.4 + 0.6 * vel)


def lead_soft(f, dur, vel=0.8, rel=0.25, att=0.04, vib_cents=12):
    n = int((dur + rel) * SR)
    fr = vibrato(f, n, 5.2, vib_cents, delay=0.25)
    y = harmonic(fr, n, [1, 0.1, 0.22, 0.04, 0.07, 0.0, 0.025])
    br = np.random.default_rng(int(f * 10)).standard_normal(n)
    y += 0.03 * bp(br, f * 0.8, f * 3)
    return y * gate_env(n, dur, rel, att) * (0.4 + 0.6 * vel)


def flute(f, dur, vel=0.8, rel=0.2):
    n = int((dur + rel) * SR)
    t = tt(n)
    fr = vibrato(f, n, 4.8, 10, delay=0.3)
    y = harmonic(fr, n, [1, 0.28, 0.12, 0.05, 0.02])
    br = np.random.default_rng(int(f * 7)).standard_normal(n)
    y += (0.05 + 0.15 * np.exp(-t / 0.05)) * bp(br, f * 0.9, f * 4)
    return y * gate_env(n, dur, rel, 0.06) * (0.4 + 0.6 * vel)


def square_lead(f, dur, vel=0.8, rel=0.05):
    n = int((dur + rel) * SR)
    t = tt(n)
    fr = vibrato(f, n, 6, 8, delay=0.15)
    cut = 1800 + 2500 * np.exp(-t / 0.05)
    y = harmonic(fr, n, [1, 0.0, 0.33, 0.0, 0.2, 0.05, 0.14, 0, 0.11, 0, 0.09, 0, 0.07], cutoff=cut)
    return y * gate_env(n, dur, rel, 0.003) * (0.4 + 0.6 * vel)


def organ(f, dur, vel=0.7, rel=0.05):
    n = int((dur + rel) * SR)
    y = 0.6 * harmonic(f, n, [1, 0.7, 0.45, 0.2, 0.25, 0, 0, 0.12])
    return y * gate_env(n, dur, rel, 0.004) * (0.4 + 0.6 * vel)


def piano(f, dur, vel=0.7, rel=0.35):
    """Additive soft piano: slightly inharmonic partials, per-partial decay."""
    B = 0.00035
    tau = 2.6 * (261 / f) ** 0.45
    n = int((dur + rel) * SR)
    t = tt(n)
    y = np.zeros(n)
    bright = 0.6 + 0.8 * vel
    for k in range(1, 16):
        fk = k * f * np.sqrt(1 + B * k * k)
        if fk > SR * 0.42:
            break
        amp = (1 / k ** 1.6) * np.exp(-(k - 1) / (3.0 * bright))
        tk = tau / (1 + 0.45 * (k - 1))
        e = 0.65 * np.exp(-t / (tk * 0.25)) + 0.35 * np.exp(-t / tk)
        y += amp * e * np.sin(2 * np.pi * fk * t + 0.3 * k)
    hammer = lp(np.random.default_rng(int(f)).standard_normal(n), 2500) * np.exp(-t / 0.006) * 0.08 * vel
    y += hammer
    return y * gate_env(n, dur, rel, 0.002) * (0.3 + 0.7 * vel)


# ----------------------------------------------------------------------------
# drums
# ----------------------------------------------------------------------------
def _noise(n, seed):
    return np.random.default_rng(seed).standard_normal(n)


def kick(vel=0.9, f0=140, f1=48, decay=0.32, click=0.3, seed=1):
    n = int(decay * 3 * SR)
    t = tt(n)
    f = f1 + (f0 - f1) * np.exp(-t / 0.035)
    y = np.sin(phase_of(f, n)) * np.exp(-t / decay)
    y += click * hp(_noise(n, seed), 1500) * np.exp(-t / 0.003)
    return tail_fade(np.tanh(1.2 * y), 0.2) * vel


def snare(vel=0.8, decay=0.13, tone=190, seed=2, bright=1.0):
    n = int(decay * 4 * SR)
    t = tt(n)
    nz = bp(_noise(n, seed), 900, 7500 * bright) * np.exp(-t / decay)
    body = np.sin(phase_of(tone * (1 + 0.5 * np.exp(-t / 0.01)), n)) * np.exp(-t / 0.05)
    return tail_fade(0.8 * nz + 0.5 * body, 0.2) * vel


def rim(vel=0.7, f=1700, seed=3):
    n = int(0.08 * SR)
    t = tt(n)
    y = np.sin(2 * np.pi * f * t) * np.exp(-t / 0.012) + 0.5 * np.sin(2 * np.pi * f * 0.47 * t) * np.exp(-t / 0.02)
    y += 0.4 * hp(_noise(n, seed), 3000) * np.exp(-t / 0.002)
    return tail_fade(y, 0.2) * vel


def woodblock(vel=0.7, f=900):
    n = int(0.12 * SR)
    t = tt(n)
    y = np.sin(2 * np.pi * f * t) * np.exp(-t / 0.025) + 0.3 * np.sin(2 * np.pi * f * 2.7 * t) * np.exp(-t / 0.008)
    y *= np.clip(t / 0.0005, 0, 1)
    return tail_fade(y, 0.2) * vel


HAT_F = [205.3, 304.4, 369.6, 522.7, 540.0, 800.0]


def hat(vel=0.5, decay=0.035, seed=4):
    n = int(max(decay * 5, 0.05) * SR)
    t = tt(n)
    m = sum(np.sign(np.sin(2 * np.pi * f * 1.7 * t + i)) for i, f in enumerate(HAT_F)) / 6
    y = 0.6 * m + 0.6 * _noise(n, seed)
    y = hp(bp(y, 6000, 15000), 7000)
    return tail_fade(y * np.exp(-t / decay), 0.2) * vel


def shaker(vel=0.4, seed=5, length=0.09):
    n = int(length * SR)
    t = tt(n)
    e = np.clip(t / 0.012, 0, 1) * np.exp(-np.clip(t - 0.012, 0, None) / 0.03)
    y = bp(_noise(n, seed), 4500, 12000) * e
    return tail_fade(y, 0.2) * vel


def brush(vel=0.4, seed=6, length=0.25):
    n = int(length * SR)
    t = tt(n)
    e = np.clip(t / 0.03, 0, 1) * np.exp(-np.clip(t - 0.03, 0, None) / 0.07)
    y = bp(_noise(n, seed), 1500, 7000) * e
    return tail_fade(y, 0.2) * vel


# ----------------------------------------------------------------------------
# space
# ----------------------------------------------------------------------------
def make_ir(t60=2.0, pre=0.02, seed=0, dark=5500, er=True):
    rng = np.random.default_rng(seed)
    n = int(t60 * SR)
    t = tt(n)
    nz = rng.standard_normal((n, 2))
    lo = lp(nz, 2000)
    hi = nz - lo
    ir = lo * np.exp(-6.9 * t / t60)[:, None] + hi * np.exp(-6.9 * t / (t60 * 0.45))[:, None]
    ir = lp(ir, dark)
    ir *= np.clip(t / 0.01, 0, 1)[:, None]
    ir = tail_fade(ir, 0.1)
    if er:
        for d, g in [(0.011, 0.5), (0.017, 0.35), (0.023, 0.3), (0.031, 0.25)]:
            ir[int(d * SR), 0] += g * 4
            ir[int((d * 1.13) * SR), 1] += g * 4
    ir /= np.sqrt(np.sum(ir ** 2) / 2)
    return np.concatenate([np.zeros((int(pre * SR), 2)), ir])


def reverb_circ(x, ir):
    L = len(x)
    assert len(ir) < L
    X = rfft(x, axis=0)
    H = rfft(ir, n=L, axis=0)
    return irfft(X * H, n=L, axis=0)


def reverb_lin(x, ir, wet=0.3):
    if x.ndim == 1:
        x = np.stack([x, x], 1)
    n = len(x) + len(ir)
    out = np.zeros((n, 2))
    out[:len(x)] += x
    for c in range(2):
        w = signal.fftconvolve(x[:, c], ir[:, c])[:n]
        out[:len(w), c] += wet * w
    return out


def pan(x, p):
    """mono -> stereo, constant power; p in [-1, 1]."""
    a = (p + 1) * np.pi / 4
    return np.stack([x * np.cos(a), x * np.sin(a)], 1) * np.sqrt(2)


def widen(x, amount=1.3):
    m = (x[:, 0] + x[:, 1]) / 2
    s = (x[:, 0] - x[:, 1]) / 2 * amount
    return np.stack([m + s, m - s], 1)


# ----------------------------------------------------------------------------
# dynamics / mastering
# ----------------------------------------------------------------------------
def db(x):
    return 20 * np.log10(max(x, 1e-12))


def rms(x):
    return float(np.sqrt(np.mean(np.square(x))))


def limiter(x, thresh, wrap=True, win=0.006):
    a = np.abs(x).max(axis=1) if x.ndim == 2 else np.abs(x)
    mode = 'wrap' if wrap else 'nearest'
    w = int(win * SR) | 1
    pk = maximum_filter1d(a, w, mode=mode)
    g = np.minimum(1.0, thresh / np.maximum(pk, 1e-9))
    g = minimum_filter1d(g, w, mode=mode)
    g = uniform_filter1d(g, w, mode=mode)
    return x * (g[:, None] if x.ndim == 2 else g)


def master_loop(x, peak_db=-3.0, rms_db=-18.0, max_lim_db=5.0):
    x = loop_filter(x, 'hp', 28)
    thr = 10 ** (peak_db / 20) * 0.985
    g_rms = 10 ** (rms_db / 20) / rms(x)
    g_pk = thr / np.abs(x).max()
    g = min(g_rms, g_pk * 10 ** (max_lim_db / 20))
    x = limiter(x * g, thr, wrap=True)
    x = limiter(x, thr, wrap=True)
    return np.clip(x, -thr, thr)


def master_sfx(x, peak_db=-1.0, fin=0.001, fout=0.02, loop=False):
    x = np.asarray(x, float)
    if not loop:
        x = edge_fade(x, fin, fout)
    return x * (10 ** (peak_db / 20) / np.abs(x).max())


# ----------------------------------------------------------------------------
# song container
# ----------------------------------------------------------------------------
_KW_SOS = signal.butter(2, 180, 'high', fs=SR, output='sos')


def _KW(x):
    return signal.sosfilt(_KW_SOS, x)


class Song:
    def __init__(self, bpm, bars, beats=4, tail=8.0, seed=0):
        self.bpm, self.bars, self.beats = bpm, bars, beats
        self.spb = 60.0 / bpm
        self.L = int(round(bars * beats * self.spb * SR))
        self.T = min(int(tail * SR), self.L - 1)
        self.dry = np.zeros((self.L + self.T, 2))
        self.wet = np.zeros((self.L + self.T, 2))
        self.rng = np.random.default_rng(seed)
        self.stems = {}

    def bar(self, b):
        return b * self.beats

    def add(self, sig, beat, gain=1.0, p=0.0, send=0.2, jitter=0.004, stem='misc'):
        i = int(round(beat * self.spb * SR))
        if jitter:
            i += int(self.rng.normal(0, jitter) * SR)
        i %= self.L
        s = pan(sig, p) if sig.ndim == 1 else sig * np.array(
            [min(1, 1 - p), min(1, 1 + p)])[None, :]
        n = min(len(s), len(self.dry) - i)
        s = s[:n] * gain
        self.dry[i:i + n] += s
        if send:
            self.wet[i:i + n] += s * send
        # crude loudness weighting (de-emphasise lows) for the balance report
        self.stems[stem] = self.stems.get(stem, 0.0) + float(np.sum(_KW(s.sum(1)) ** 2))

    def play(self, inst, events, gain=1.0, p=0.0, send=0.2, transpose=0, stem=None,
             vel_rand=0.06, jitter=0.004, spread=0.0, **kw):
        stem = stem or inst.__name__
        for (b, d, ms, v) in events:
            for j, m in enumerate(ms):
                vv = float(np.clip(v + self.rng.normal(0, vel_rand), 0.05, 1.0))
                sig = inst(hz(m + transpose), d * self.spb, vv, **kw)
                pp = p + spread * ((j / max(len(ms) - 1, 1)) - 0.5) * 2 if spread else p
                self.add(sig, b, gain, pp, send, jitter, stem)

    def render(self, ir, wet=1.0):
        assert self.T < self.L
        dry = self.dry[:self.L].copy()
        dry[:self.T] += self.dry[self.L:]
        w = self.wet[:self.L].copy()
        w[:self.T] += self.wet[self.L:]
        return dry + wet * reverb_circ(w, ir)

    def stem_report(self):
        tot = sum(self.stems.values())
        return {k: round(10 * np.log10(v / tot + 1e-12), 1) for k, v in self.stems.items()}


# ----------------------------------------------------------------------------
# I/O
# ----------------------------------------------------------------------------
def write_ogg(path, x, quality_level=0.45):
    import soundfile as sf
    x = np.asarray(x, np.float32)
    sf.write(path, x, SR, format='OGG', subtype='VORBIS', compression_level=quality_level)
