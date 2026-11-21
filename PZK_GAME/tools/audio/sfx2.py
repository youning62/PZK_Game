"""Procedural SFX for the 'scammed -> rider -> system -> LXX' arc.  Each returns (signal, options).

Loops (rain, city_ambience, office_ambience) are built circularly: noise is
shaped with fft_shape, events are placed with wrap-around and reverb is circular.
"""
import numpy as np
from synth import *  # noqa
from sfx import N, place, noise, periodic_lfo, _strike
from music2 import chip, brass, strings, blip, crash, kazoo  # noqa


def place_wrap(buf, sig, t, gain=1.0):
    i = int(t * SR) % len(buf)
    idx = (np.arange(len(sig)) + i) % len(buf)
    np.add.at(buf, idx, gain * sig)
    return buf


def env_lin(t, pts):
    xs, ys = zip(*pts)
    return np.interp(t, xs, ys)


def room(x, t60=0.6, wet=0.25, seed=0, L=None):
    st = x if x.ndim == 2 else np.stack([x, x], 1)
    y = reverb_lin(st, make_ir(t60, 0.008, seed=seed, er=False), wet)
    return y[:L or len(x)]


# ---------------------------------------------------------------- system UI
def system_boot():
    L = N(2.6)
    out = np.zeros((L, 2))
    # power-on thump
    n = N(0.4)
    tb = np.arange(n) / SR
    place(out, pan(np.sin(phase_of(50 + 120 * np.exp(-tb / 0.03), n)) * np.exp(-tb / 0.12), 0), 0.0, 0.6)
    # rising sweep
    sn = N(1.75)
    ts = np.arange(sn) / SR
    f = 110 * (2200 / 110) ** ((ts / 1.75) ** 1.5)
    sw = harmonic(f, sn, [1, 0, 0.35, 0, 0.18, 0, 0.1]) * np.clip(ts / 0.05, 0, 1) * np.clip((1.75 - ts) / 0.1, 0, 1)
    sw *= 0.25 + 0.75 * ts / 1.75
    place(out, pan(sw, 0), 0.03, 0.22)
    # accelerating ascending chip blips
    notes = 'C4 D4 E4 G4 A4 C5 D5 E5 G5 A5 C6 D6 E6 G6'.split()
    K = len(notes)
    for k, nm in enumerate(notes):
        t0 = 0.08 + 1.6 * (1 - (1 - k / K) ** 1.7)
        place(out, pan(chip(hz(nm), 0.045, 0.6 + 0.02 * k, duty=0.25), 0.6 if k % 2 else -0.6), t0, 0.28)
    # data flicker: sample-and-hold noise bursts
    r = np.random.default_rng(301)
    for k in range(10):
        bn = N(r.uniform(0.015, 0.04))
        hold = np.repeat(r.uniform(-1, 1, bn // 30 + 1), 30)[:bn]
        place(out, pan(hold * gate_env(bn, bn / SR - 0.004, 0.004, 0.001), r.uniform(-0.9, 0.9)),
              0.2 + 1.4 * k / 10 + r.uniform(0, 0.05), 0.12)
    # "online" chord
    for i, nm in enumerate(['C6', 'G6', 'E7', 'C7']):
        place(out, pan(bell(hz(nm), 0.5, 0.75, decay=0.55, ratio=2.0, bright=0.5), -0.4 + 0.27 * i), 1.78 + i * 0.03, 0.3)
    place(out, pan(pad(hz('C5'), 0.25, 0.7, att=0.02, rel=0.4, cutoff=4000)[:, 0], 0), 1.78, 0.25)
    out = reverb_lin(out, make_ir(1.4, 0.02, seed=31), 0.35)[:L]
    return out, dict(fout=0.15)


def system_ding():
    L = N(0.8)
    out = np.zeros((L, 2))
    for t0, nm, p in [(0.0, 'E6', -0.25), (0.075, 'B6', 0.25)]:
        f = hz(nm)
        n = N(0.6)
        tb = np.arange(n) / SR
        y = fm(f, n, 2.0, 0.8 * np.exp(-tb / 0.02)) * np.exp(-tb / 0.18)
        y += 0.3 * np.sin(2 * np.pi * 2 * f * tb) * np.exp(-tb / 0.06)
        y *= np.clip(tb / 0.001, 0, 1)
        place(out, pan(y, p), t0, 0.6)
    out = reverb_lin(out, make_ir(0.8, 0.012, seed=32), 0.2)[:L]
    return out, dict(peak=-2.0, fout=0.15)


def system_scan():
    L = N(1.5)
    t = np.arange(L) / SR
    sweep = 0.5 - 0.5 * np.cos(2 * np.pi * t / 1.5)
    f = 700 + 1700 * sweep
    tone = harmonic(f, L, [1, 0, 0.25, 0, 0.1])
    gate = (np.sin(2 * np.pi * 14 * t) > -0.2).astype(float)
    gate = signal.lfilter([0.02], [1, -0.98], gate)        # soften the gating edges
    beep = tone * gate
    nz = noise(L, 33)
    laser = np.zeros(L)
    hop = N(0.01)
    for i in range(0, L, hop):               # time-varying resonant band
        seg = nz[i:i + hop * 3]
        fc = float(f[i]) * 2.2
        y = resonator(seg, fc, 18)[:hop]
        laser[i:i + len(y)] += y
    sig = 0.55 * beep + 0.5 * laser / max(rms(laser), 1e-9) * 0.25
    sig *= np.clip(t / 0.05, 0, 1) * np.clip((1.5 - t) / 0.12, 0, 1)
    p = np.clip(-0.9 + 1.8 * t / 1.5, -1, 1)
    a = (p + 1) * np.pi / 4
    out = np.stack([sig * np.cos(a), sig * np.sin(a)], 1) * np.sqrt(2)
    out = reverb_lin(out, make_ir(0.7, 0.01, seed=34), 0.2)[:L]
    return out, dict(fout=0.1)


# ---------------------------------------------------------------- stamps / errors
def _thunk(seed=40, weight=1.0):
    n = N(0.4)
    tb = np.arange(n) / SR
    y = np.sin(phase_of(55 + 70 * np.exp(-tb / 0.02), n)) * np.exp(-tb / 0.07) * weight
    y += 0.6 * bp(noise(n, seed), 250, 2500) * np.exp(-tb / 0.012)          # rubber slap
    y += sum(a * np.sin(2 * np.pi * fq * tb) * np.exp(-tb / d)
             for fq, d, a in [(160, 0.06, 0.5), (340, 0.04, 0.35), (720, 0.02, 0.25), (1500, 0.008, 0.15)])
    y += 0.25 * hp(noise(n, seed + 1), 3000) * np.exp(-tb / 0.003)
    return np.tanh(1.3 * y)


def stamp_approve():
    L = N(1.5)
    out = np.zeros(L)
    place(out, _thunk(41), 0.0, 0.9)
    for nm, dt, g in [('E6', 0.13, 0.55), ('G#6', 0.16, 0.45), ('B6', 0.19, 0.4)]:
        y = _strike(hz(nm), [1, 2.0, 3.01, 4.2], [1, 0.3, 0.15, 0.08], [0.6, 0.25, 0.1, 0.05], 1.2)
        place(out, y, dt, g)
    out = room(out, 0.9, 0.2, 42, L)
    return out, dict(fout=0.2)


def stamp_reject():
    L = N(1.1)
    out = np.zeros(L)
    place(out, _thunk(43, 1.2), 0.0, 0.9)
    for t0 in (0.14, 0.42):
        n = N(0.22)
        tb = np.arange(n) / SR
        f = 98 * (1 - 0.03 * tb / 0.22)
        y = harmonic(f, n, SQUARE[:40], cutoff=2200) + 0.5 * harmonic(f * 1.06, n, SAW[:30], cutoff=1500)
        y = np.tanh(2.0 * y) * gate_env(n, 0.2, 0.02, 0.005)
        place(out, y, t0, 0.45)
    out = room(out, 0.6, 0.15, 44, L)
    return out, dict(fout=0.1)


def error_buzz():
    L = N(0.6)
    out = np.zeros(L)
    for t0 in (0.0, 0.3):
        n = N(0.24)
        tb = np.arange(n) / SR
        y = harmonic(140, n, SAW[:50], cutoff=2600) + harmonic(147, n, SQUARE[:40], cutoff=2000)
        y *= 1 + 0.5 * np.sign(np.sin(2 * np.pi * 35 * tb))
        y = np.tanh(1.8 * y) * gate_env(n, 0.22, 0.015, 0.004)
        place(out, y, t0 + 0.005, 1.0)
    return out, dict(fout=0.03)


# ---------------------------------------------------------------- money
def _coin(f0, seed, length=0.5, g=1.0):
    r = np.random.default_rng(seed)
    y = _strike(f0, [1, 1.52 + r.uniform(-0.03, 0.03), 2.31, 3.67, 5.1], [1, 0.7, 0.5, 0.35, 0.2],
                [0.25, 0.15, 0.1, 0.06, 0.03], length)
    n = len(y)
    y += 0.5 * hp(noise(n, seed), 4000) * np.exp(-np.arange(n) / SR / 0.002)
    return y * g


def coin():
    L = N(1.0)
    out = np.zeros(L)
    for k, (t0, g) in enumerate([(0.0, 1.0), (0.17, 0.55), (0.29, 0.35), (0.37, 0.22), (0.42, 0.12)]):
        place(out, _coin(3300 * (1 + 0.01 * k), 50 + k, 0.55), t0, g)
    # spin-down rattle
    for k in range(10):
        t0 = 0.45 + 0.3 * (1 - (1 - k / 10) ** 2)
        place(out, _coin(3300, 60 + k, 0.08), t0, 0.08 * (1 - k / 12))
    out = room(out, 0.5, 0.15, 51, L)
    return out, dict(fout=0.15)


def money_rain():
    L = N(2.3)
    out = np.zeros((L, 2))
    r = np.random.default_rng(70)
    place(out, pan(_strike(2100, [1, 2.76, 5.4, 8.93], [1, 0.5, 0.25, 0.1], [0.7, 0.35, 0.15, 0.06], 1.4), 0), 0.0, 0.6)
    k = 0
    for i in range(110):
        t0 = 0.05 + 1.9 * r.beta(1.3, 2.6)
        f0 = r.uniform(2500, 5200)
        c = _coin(f0, 100 + i, r.uniform(0.15, 0.45), r.uniform(0.15, 0.5))
        place(out, pan(c, r.uniform(-0.9, 0.9)), t0)
    # pile "shhh" of coins settling
    t = np.arange(L) / SR
    sh = bp(noise(L, 71, 2), 3000, 11000) * (env_lin(t, [(0, 0), (0.3, 1), (1.6, 0.6), (2.3, 0)]) ** 2)[:, None] * 0.06
    out += sh
    out = reverb_lin(out, make_ir(1.0, 0.015, seed=72), 0.2)[:L]
    return out, dict(fout=0.3)


# ---------------------------------------------------------------- seals
def _metal_clunk(seed, f0=1.0):
    n = N(1.0)
    tb = np.arange(n) / SR
    y = np.sin(phase_of(48 + 90 * np.exp(-tb / 0.02), n)) * np.exp(-tb / 0.15)
    y += sum(a * np.sin(2 * np.pi * fq * f0 * tb + i) * np.exp(-tb / d)
             for i, (fq, d, a) in enumerate([(410, 0.3, 0.5), (980, 0.2, 0.4), (1730, 0.12, 0.3), (2930, 0.06, 0.2)]))
    y += 0.5 * bp(noise(n, seed), 300, 4000) * np.exp(-tb / 0.01)
    return np.tanh(1.5 * y)


def _shimmer(notes, L, t0, gain, seed, rising=True):
    out = np.zeros((L, 2))
    r = np.random.default_rng(seed)
    for i, nm in enumerate(notes):
        f = hz(nm)
        n = N(1.6)
        tb = np.arange(n) / SR
        y = (np.sin(2 * np.pi * f * tb) + 0.3 * np.sin(2 * np.pi * 2.01 * f * tb)) * (1 + 0.3 * np.sin(2 * np.pi * 7 * tb))
        e = np.clip(tb / 0.35, 0, 1) ** 2 * np.exp(-np.clip(tb - 0.35, 0, None) / 0.5) if rising else np.exp(-tb / 0.6)
        place(out, pan(y * e, r.uniform(-0.8, 0.8)), t0 + i * 0.06, gain)
    return out


def seal_lock():
    L = N(2.6)
    out = np.zeros((L, 2))
    # chain rattle into the lock
    r = np.random.default_rng(80)
    for k in range(9):
        c = _coin(r.uniform(1800, 3200), 200 + k, 0.08, 0.25)
        place(out, pan(c, r.uniform(-0.5, 0.5)), 0.02 + k * 0.035 + r.uniform(0, 0.01))
    place(out, pan(_metal_clunk(81), 0), 0.36, 1.0)
    place(out, pan(_metal_clunk(82, 1.3) * 0.4, 0.2), 0.43)
    out += _shimmer(['D6', 'F6', 'A6', 'C#7', 'E7'], L, 0.38, 0.09, 83)
    n = N(1.8)
    dark = pad(hz('D3'), 0.6, 0.6, att=0.05, rel=1.2, cutoff=900)
    place(out, dark[:min(len(dark), L)], 0.36, 0.25)
    out = reverb_lin(out, make_ir(2.2, 0.03, seed=84), 0.45)[:L]
    return out, dict(fout=0.4)


def seal_unlock():
    L = N(2.8)
    out = np.zeros((L, 2))
    for t0, g in [(0.0, 0.6), (0.05, 0.45)]:
        ln = N(0.06)
        tl = np.arange(ln) / SR
        latch = hp(noise(ln, 90 + int(t0 * 100)), 3000) * np.exp(-tl / 0.002) + 0.6 * np.sin(2 * np.pi * 3300 * tl) * np.exp(-tl / 0.012)
        place(out, pan(latch, 0), t0, g)
    # spring release
    n = N(0.4)
    tb = np.arange(n) / SR
    spr = np.sin(phase_of(700 * (1 + 0.25 * np.exp(-tb / 0.1) * np.sin(2 * np.pi * 30 * tb)), n)) * np.exp(-tb / 0.1)
    place(out, pan(spr, 0.2), 0.08, 0.25)
    place(out, pan(_metal_clunk(91, 1.5) * 0.5, -0.1), 0.1)
    # triumphant chime arpeggio + chord
    for i, nm in enumerate(['C6', 'E6', 'G6', 'C7', 'E7']):
        place(out, pan(bell(hz(nm), 0.3, 0.8, decay=0.9, ratio=2.0, bright=0.6), -0.6 + 0.3 * i), 0.3 + i * 0.07, 0.3)
    for j, nm in enumerate(['C4', 'G4', 'C5', 'E5']):
        b = brass(hz(nm), 0.9, 0.85, rel=0.6, att=0.05)
        place(out, pan(b, -0.3 + 0.2 * j), 0.62, 0.12)
    out += _shimmer(['G7', 'C8', 'E7', 'G7', 'C8'], L, 0.6, 0.05, 92, rising=False)
    out = reverb_lin(out, make_ir(2.0, 0.025, seed=93), 0.4)[:L]
    return out, dict(fout=0.4)


def glitch():
    L = N(0.7)
    out = np.zeros((L, 2))
    r = np.random.default_rng(110)
    t0 = 0.0
    prev = None
    while t0 < 0.66:
        d = r.uniform(0.015, 0.06)
        n = N(d)
        kind = r.integers(0, 5)
        tb = np.arange(n) / SR
        if kind == 0:     # sample&hold square tone
            f = r.uniform(200, 3000)
            y = np.sign(np.sin(2 * np.pi * f * tb)) * 0.6
        elif kind == 1:   # bitcrushed noise
            y = np.round(np.repeat(r.uniform(-1, 1, n // 12 + 1), 12)[:n] * 3) / 3
        elif kind == 2 and prev is not None:  # stutter
            y = np.tile(prev[:max(N(0.008), 1)], n // max(N(0.008), 1) + 1)[:n]
        elif kind == 3:   # falling zap
            y = np.sin(phase_of(4000 * np.exp(-tb / 0.01) + 150, n))
        else:
            y = np.zeros(n)
        y = y * gate_env(n, d - 0.002, 0.002, 0.0005)
        place(out, pan(y, r.uniform(-0.9, 0.9)), t0, r.uniform(0.4, 1.0))
        if np.any(y):
            prev = y
        t0 += d
    out = lp(out, 12000)
    return out, dict(fout=0.02)


def _key(seed, heavy=False):
    r = np.random.default_rng(seed)
    n = N(0.09)
    tb = np.arange(n) / SR
    k = 0.7 if heavy else 1.0
    click = hp(noise(n, seed), 3500) * np.exp(-tb / 0.0012) * 0.6
    body = bp(noise(n, seed + 1), 900 * k, 3500 * k) * np.exp(-tb / 0.008)
    thock = np.sin(2 * np.pi * r.uniform(260, 380) * k * tb) * np.exp(-tb / 0.012) * 0.5
    up = np.zeros(n)
    place(up, hp(noise(N(0.02), seed + 2), 2500) * np.exp(-np.arange(N(0.02)) / SR / 0.002) * 0.3, 0.045)
    return (click + body + thock) * (1.3 if heavy else 1.0) + up


def typing():
    L = N(2.0)
    out = np.zeros(L)
    r = np.random.default_rng(120)
    t0, i = 0.02, 0
    while t0 < 1.88:
        heavy = i % 7 == 6
        place(out, _key(1000 + i, heavy), t0, r.uniform(0.6, 1.0))
        t0 += r.uniform(0.06, 0.15) + (0.25 if i == 9 else 0)
        i += 1
    out = room(out, 0.4, 0.12, 121, L)
    return out, dict(peak=-3.0, fout=0.05)


# ---------------------------------------------------------------- ambiences (loops)
def rain():
    L = N(15.0)
    out = np.zeros((L, 2))
    r = np.random.default_rng(130)
    for ch in range(2):
        hiss = fft_shape(noise(L, 131 + ch), lambda f: (f > 400) / np.sqrt(np.maximum(f, 400) / 400) / (1 + (f / 9000) ** 3))
        hiss = hiss / rms(hiss) * (0.8 + 0.2 * periodic_lfo(L, 132 + ch, 4))
        rumble = fft_shape(noise(L, 133 + ch), lambda f: 1 / (1 + (f / 250) ** 3) * (f > 25))
        rumble = rumble / rms(rumble)
        # drops: sparse impulses, circularly convolved with a short drop kernel
        imp = np.zeros(L)
        k = 2600
        pos = r.integers(0, L, k)
        np.add.at(imp, pos, r.uniform(0.2, 1.0, k) * r.choice([-1, 1], k))
        drops = fft_shape(imp, lambda f: np.exp(-0.5 * ((f - 3200) / 1800) ** 2) + 0.4 * np.exp(-0.5 * ((f - 900) / 400) ** 2))
        drops = drops / rms(drops)
        # a few closer, plinky drips (e.g. off an awning)
        drip = np.zeros(L)
        for j in range(18):
            f0 = r.uniform(900, 2200)
            n = N(0.05)
            tb = np.arange(n) / SR
            d = np.sin(phase_of(f0 * (1 + 1.5 * tb / 0.05), n)) * np.exp(-tb / 0.01)
            place_wrap(drip, d, r.uniform(0, 15), r.uniform(0.3, 1.0) * 0.5)
        out[:, ch] = 0.5 * hiss + 0.35 * rumble + 0.2 * drops + 0.5 * drip
    ir = make_ir(1.2, 0.02, seed=134)
    out = out + 0.3 * reverb_circ(out, ir)
    return out, dict(loop=True, peak=-3.0)


def city_ambience():
    L = N(15.0)
    out = np.zeros((L, 2))
    t = np.arange(L) / SR
    r = np.random.default_rng(140)
    for ch in range(2):
        rumble = fft_shape(noise(L, 141 + ch), lambda f: 1 / np.sqrt(np.maximum(f, 30) / 30) / (1 + (f / 220) ** 3) * (f > 20))
        rumble = rumble / rms(rumble) * (0.6 + 0.4 * periodic_lfo(L, 142 + ch, 4))
        roar = fft_shape(noise(L, 143 + ch), lambda f: 1 / np.sqrt(np.maximum(f, 100) / 100) / (1 + (f / 1400) ** 3) * (f > 80))
        roar = roar / rms(roar) * (0.4 + 0.6 * periodic_lfo(L, 144 + ch, 7))
        out[:, ch] = 0.8 * rumble + 0.35 * roar
    # distant car passes (circular gaussian swells with pan sweep)
    for j, (tc, w, dirn, g) in enumerate([(2.0, 1.6, 1, 0.6), (6.5, 2.2, -1, 0.45), (10.3, 1.3, 1, 0.55), (13.4, 1.9, -1, 0.4)]):
        dt = ((t - tc + 7.5) % 15.0) - 7.5
        e = np.exp(-0.5 * (dt / w) ** 2)
        car = fft_shape(noise(L, 150 + j), lambda f: (f > 80) / (1 + (f / 900) ** 3))
        car = car / rms(car) * e * g
        p = np.clip(dirn * dt / (2 * w), -1, 1)
        a = (p + 1) * np.pi / 4
        out[:, 0] += car * np.cos(a) * np.sqrt(2)
        out[:, 1] += car * np.sin(a) * np.sqrt(2)
    # crowd murmur: a few formant-filtered "voices" with syllabic envelopes
    for v in range(6):
        src = noise(L, 160 + v)
        fc1, fc2 = r.uniform(350, 700), r.uniform(1100, 2200)
        vo = fft_shape(src, lambda f: np.exp(-0.5 * ((f - fc1) / 150) ** 2) + 0.6 * np.exp(-0.5 * ((f - fc2) / 300) ** 2))
        syl = periodic_lfo(L, 170 + v, harmonics=70, power=0.6) ** 3
        talk = periodic_lfo(L, 180 + v, harmonics=3, power=1.0)
        sig = vo / rms(vo) * syl * np.clip(talk * 1.6 - 0.4, 0, 1) * 0.09
        out += pan(sig, r.uniform(-0.8, 0.8))
    # a distant horn (soft) and a bicycle bell
    n = N(0.5)
    tb = np.arange(n) / SR
    horn = (harmonic(392, n, SAW[:20], cutoff=1200) + harmonic(470, n, SAW[:20], cutoff=1200)) * gate_env(n, 0.42, 0.06, 0.02)
    place_wrap(out, pan(lp(horn, 1500), -0.5), 8.4, 0.05)
    place_wrap(out, pan(lp(horn[:N(0.18)] * gate_env(N(0.18), 0.15, 0.03, 0.01), 1500), -0.5), 9.05, 0.04)
    bb = _strike(2900, [1, 1.47, 2.6], [1, 0.5, 0.3], [0.4, 0.2, 0.1], 0.8)
    place_wrap(out, pan(bb, 0.6), 4.3, 0.035)
    place_wrap(out, pan(bb, 0.6), 4.42, 0.03)
    out = loop_filter(out, 'lp', 6000)
    out = out + 0.35 * reverb_circ(out, make_ir(1.8, 0.04, seed=190, dark=3500))
    return out, dict(loop=True, peak=-3.0)


def office_ambience():
    L = N(12.0)
    out = np.zeros((L, 2))
    t = np.arange(L) / SR
    for ch in range(2):
        air = fft_shape(noise(L, 200 + ch), lambda f: (f > 40) / np.sqrt(np.maximum(f, 60) / 60) / (1 + (f / 1800) ** 2))
        air = air / rms(air) * (0.9 + 0.1 * periodic_lfo(L, 201 + ch, 3))
        out[:, ch] = 0.5 * air
    hum = 0.08 * np.sin(2 * np.pi * 50 * t) + 0.05 * np.sin(2 * np.pi * 100 * t + 1) + 0.02 * np.sin(2 * np.pi * 150 * t)
    buzz = 0.006 * sum(np.sin(2 * np.pi * 100 * k * t + k) / k for k in range(2, 12))   # fluorescent light
    out += (hum + buzz)[:, None]
    # distant keyboards
    r = np.random.default_rng(210)
    kb = np.zeros((L, 2))
    for b, (start, dur, p) in enumerate([(0.8, 2.6, -0.6), (4.9, 1.8, 0.5), (8.2, 2.9, -0.2)]):
        tk = start
        i = 0
        while tk < start + dur:
            place_wrap(kb, pan(_key(3000 + b * 100 + i, i % 8 == 7), p), tk, r.uniform(0.4, 1.0))
            tk += r.uniform(0.07, 0.17)
            i += 1
    # a mouse click pair and a distant chair creak-ish thump
    mc = hp(noise(N(0.02), 220), 2000) * np.exp(-np.arange(N(0.02)) / SR / 0.0015)
    for tm in (3.9, 4.05, 11.2):
        place_wrap(kb, pan(mc, 0.3), tm, 0.6)
    kb = loop_filter(kb, 'lp', 5000)
    out += 0.06 * kb / np.abs(kb).max()
    out = out + 0.3 * reverb_circ(out, make_ir(1.0, 0.02, seed=230, dark=4000))
    return out, dict(loop=True, peak=-3.0)


# ---------------------------------------------------------------- foley / props
def elevator_ding():
    L = N(2.2)
    out = np.zeros(L)
    y = _strike(hz('E6'), [1, 2.0, 2.76, 5.4], [1, 0.2, 0.25, 0.08], [1.2, 0.6, 0.35, 0.1], 2.0)
    place(out, y, 0.005, 1.0)
    place(out, _strike(hz('E5'), [1, 2.0], [1, 0.3], [1.0, 0.4], 2.0), 0.005, 0.25)
    out = room(out, 1.0, 0.25, 240, L)
    return out, dict(fout=0.4)


def ebike_horn():
    L = N(0.85)
    out = np.zeros(L)
    for k, (t0, d) in enumerate([(0.0, 0.17), (0.25, 0.32)]):
        n = N(d + 0.03)
        tb = np.arange(n) / SR
        sag = 1 - (0.05 * np.clip((tb - 0.15) / 0.15, 0, 1) if k == 1 else 0)
        y = 0
        for f0 in (415, 493):
            y = y + harmonic(f0 * sag, n, SQUARE[:30], cutoff=3000)
        y = resonator(y, 1800, 3) * 2 + 0.3 * y
        y = np.tanh(2.5 * y) * gate_env(n, d, 0.02, 0.006)
        place(out, y, t0)
    return out, dict(fout=0.05)


def ebike_start():
    L = N(2.3)
    out = np.zeros(L)
    t = np.arange(L) / SR
    for i, nm in enumerate(['C6', 'G6', 'C7']):
        place(out, chip(hz(nm), 0.07, 0.8, duty=0.5), 0.0 + i * 0.11, 0.35)
    rl = N(0.02)
    place(out, hp(noise(rl, 250), 2000) * np.exp(-np.arange(rl) / SR / 0.002), 0.42, 0.4)   # relay click
    mt = N(1.8)
    tm = np.arange(mt) / SR
    f = env_lin(tm, [(0, 150), (0.9, 900), (1.2, 1000), (1.8, 950)])
    whine = harmonic(f, mt, [1, 0.35, 0.2, 0.1, 0.05]) + 0.25 * harmonic(f * 3.02, mt, [1, 0.3])
    pwm = 0.06 * np.sin(2 * np.pi * 7800 * tm)
    whine = (whine + pwm) * np.clip(tm / 0.2, 0, 1) * (0.6 + 0.4 * np.clip(tm / 0.9, 0, 1))
    whine += 0.15 * bp(noise(mt, 251), 2000, 7000) * np.clip(tm / 0.9, 0, 1)
    place(out, whine, 0.45, 0.35)
    return out, dict(fout=0.3)


def claw_machine():
    L = N(2.6)
    out = np.zeros(L)
    place(out, chip(hz('A6'), 0.06, 0.7, duty=0.5), 0.0, 0.3)
    place(out, chip(hz('E7'), 0.08, 0.7, duty=0.5), 0.08, 0.3)
    # gantry motor whirr
    mn = N(1.15)
    tm = np.arange(mn) / SR
    f = 95 * (1 + 0.04 * np.sin(2 * np.pi * 1.3 * tm))
    mot = harmonic(f, mn, SAW[:30], cutoff=1500) * (1 + 0.35 * np.sin(2 * np.pi * 28 * tm))
    mot += 0.4 * bp(noise(mn, 260), 800, 4000) * (0.5 + 0.5 * np.sin(2 * np.pi * 28 * tm)) ** 2
    mot *= gate_env(mn, 1.1, 0.05, 0.05)
    place(out, mot, 0.2, 0.35)
    place(out, _thunk(261, 0.3) * 0.3, 1.35)
    # claw descends (lower falling whine)
    dn = N(0.45)
    td = np.arange(dn) / SR
    dw = harmonic(320 - 180 * td / 0.45, dn, [1, 0.5, 0.3], cutoff=1500) * gate_env(dn, 0.42, 0.03, 0.02)
    place(out, dw, 1.4, 0.3)
    # clunk drop: plastic capsule into the chute + rattle
    cn = N(0.5)
    tc = np.arange(cn) / SR
    clunk = np.sin(phase_of(90 + 120 * np.exp(-tc / 0.015), cn)) * np.exp(-tc / 0.06)
    clunk += sum(a * np.sin(2 * np.pi * fq * tc) * np.exp(-tc / d) for fq, d, a in [(620, 0.03, 0.5), (1450, 0.015, 0.35)])
    clunk += 0.4 * bp(noise(cn, 262), 500, 5000) * np.exp(-tc / 0.01)
    place(out, clunk, 1.9, 1.0)
    for k, (dt, g) in enumerate([(0.11, 0.4), (0.18, 0.25), (0.23, 0.15)]):
        place(out, clunk[:N(0.1)] * 0.8, 1.9 + dt, g)
    out = room(out, 0.5, 0.15, 263, L)
    return out, dict(fout=0.2)


def door_burst():
    L = N(1.2)
    out = np.zeros(L)
    n = N(0.8)
    tb = np.arange(n) / SR
    boom = np.sin(phase_of(48 + 110 * np.exp(-tb / 0.025), n)) * np.exp(-tb / 0.16)
    crack = bp(noise(n, 270), 300, 6000) * np.exp(-tb / 0.03)
    wood = sum(a * np.sin(2 * np.pi * fq * tb) * np.exp(-tb / d) for fq, d, a in [(140, 0.12, 0.6), (290, 0.08, 0.4), (610, 0.04, 0.3)])
    bang = np.tanh(1.8 * (boom + 0.8 * crack + wood))
    place(out, bang, 0.0, 1.0)
    place(out, bang * 0.55, 0.09)            # door hits the wall
    # hinge/handle rattle
    r = np.random.default_rng(271)
    for k in range(6):
        c = _strike(r.uniform(1800, 3500), [1, 1.6, 2.7], [1, 0.4, 0.2], [0.05, 0.03, 0.02], 0.12)
        place(out, c, 0.12 + k * 0.03 + r.uniform(0, 0.01), 0.12 * (1 - k / 7))
    out = room(out, 0.9, 0.3, 272, L)
    return out, dict(fout=0.2)


def camera_flash():
    L = N(1.4)
    out = np.zeros(L)
    for t0, g in [(0.0, 0.8), (0.07, 0.6)]:
        n = N(0.04)
        tb = np.arange(n) / SR
        c = hp(noise(n, 280 + int(t0 * 100)), 2500) * np.exp(-tb / 0.002) + 0.5 * np.sin(2 * np.pi * 2400 * tb) * np.exp(-tb / 0.006)
        c += 0.4 * np.sin(2 * np.pi * 600 * tb) * np.exp(-tb / 0.01)
        place(out, c, t0, g)
    fp = N(0.06)
    place(out, hp(noise(fp, 285), 5000) * np.exp(-np.arange(fp) / SR / 0.01), 0.02, 0.35)  # flash pop
    wn = N(1.1)
    tw = np.arange(wn) / SR
    f = 1500 * (9000 / 1500) ** (tw / 1.1)
    wh = np.sin(phase_of(f, wn)) + 0.15 * np.sin(phase_of(2 * f, wn))
    wh *= np.clip(tw / 0.15, 0, 1) * np.clip((1.1 - tw) / 0.25, 0, 1)
    place(out, wh, 0.2, 0.12)
    return out, dict(fout=0.1)


def knock():
    L = N(1.2)
    out = np.zeros(L)
    modes = [(170, 0.05, 1.0), (360, 0.035, 0.6), (810, 0.015, 0.35), (1650, 0.007, 0.2)]
    for k, (t0, g) in enumerate([(0.0, 0.9), (0.2, 0.85), (0.4, 1.0)]):
        n = N(0.25)
        tb = np.arange(n) / SR
        w = sum(a * np.sin(2 * np.pi * f * (1 + 0.02 * k) * tb + i) * np.exp(-tb / d) for i, (f, d, a) in enumerate(modes))
        w += 0.5 * lp(noise(n, 290 + k), 3000) * np.exp(-tb / 0.004)
        place(out, w * np.clip(tb / 0.0005, 0, 1), t0 + 0.005, g)
    out = room(out, 0.6, 0.2, 291, L)
    return out, dict(fout=0.2)


def phone_call():
    L = N(3.0)
    out = np.zeros(L)
    phrase = [('E6', 0.0), ('G6', 0.11), ('C7', 0.22), ('G6', 0.33), ('E6', 0.44), ('G6', 0.55), ('C7', 0.66), ('D7', 0.77)]
    for start in (0.0, 1.45):
        for nm, dt in phrase:
            f = hz(nm)
            place(out, marimba(f, 0.1, 0.85), start + dt, 0.55)
            place(out, chip(f, 0.08, 0.6, duty=0.5), start + dt, 0.12)
        place(out, bell(hz('C7'), 0.3, 0.6, decay=0.4, ratio=2.0, bright=0.4), start + 0.9, 0.3)
    out = room(out, 0.5, 0.12, 300, L)
    return out, dict(fout=0.15)


def sad_trombone():
    L = N(2.7)
    out = np.zeros(L)
    notes = [('Bb3', 0.0, 0.34), ('A3', 0.42, 0.34), ('Ab3', 0.84, 0.34), ('G3', 1.26, 1.25)]
    for k, (nm, t0, d) in enumerate(notes):
        last = k == 3
        n = N(d + 0.2)
        tb = np.arange(n) / SR
        cents = -40 * np.exp(-tb / 0.04)
        if last:
            cents = cents + 35 * np.sin(2 * np.pi * 5.5 * tb) * np.clip(tb / 0.4, 0, 1) - 80 * np.clip((tb - 0.7) / 0.6, 0, 1)
        f = hz(nm) * 2 ** (cents / 1200)
        if last:
            wah = 0.5 + 0.5 * np.sin(2 * np.pi * 2.6 * tb - 1.6) * np.clip(tb / 0.15, 0, 1)
        else:
            wah = np.sin(np.pi * np.clip(tb / d, 0, 1)) ** 0.7
        cut = 250 + 1500 * wah
        y = harmonic(f, n, SAW[:45], cutoff=cut, slope=2)
        y = 0.6 * y + 0.5 * resonator(y, 550, 2.5)
        y = np.tanh(1.8 * y) * gate_env(n, d, 0.15, 0.03)
        place(out, y, t0)
    out = room(out, 0.7, 0.15, 310, L)
    return out, dict(fout=0.2)


def _orch_hit(notes, vel, length, seed):
    n = N(length + 0.6)
    tb = np.arange(n) / SR
    y = np.zeros((n, 2))
    for j, nm in enumerate(notes):
        f = hz(nm)
        b = brass(f, length, vel, rel=0.5, att=0.006)
        s_ = strings(f * 2, length, vel, att=0.005, dec=0.2, sus=0.6, rel=0.5, seed=seed + j)
        m = min(n, len(b))
        y[:m] += pan(b[:m], -0.5 + j / max(len(notes) - 1, 1))
        m = min(n, len(s_))
        y[:m] += 0.6 * pan(s_[:m], 0.5 - j / max(len(notes) - 1, 1))
    f0 = hz(notes[0])
    timp = np.sin(phase_of(f0 * (1 + 0.3 * np.exp(-tb / 0.02)), n)) * np.exp(-tb / 0.5)
    timp += 0.4 * np.sin(phase_of(f0 * 1.5, n)) * np.exp(-tb / 0.25)
    timp += 0.3 * lp(noise(n, seed), 1500) * np.exp(-tb / 0.02)
    y += 1.2 * pan(timp * vel, 0)
    k = kick(vel, 120, 38, 0.35)
    y[:len(k)] += 0.8 * pan(k, 0)[:n]
    return y


def dramatic_sting():
    L = N(2.5)
    out = np.zeros((L, 2))
    place(out, _orch_hit(['C2', 'G2', 'C3', 'G3'], 0.8, 0.18, 320), 0.0, 0.7)
    place(out, _orch_hit(['C2', 'G2', 'C3', 'G3'], 0.85, 0.18, 330), 0.32, 0.75)
    big = _orch_hit(['C2', 'C3', 'Eb3', 'F#3', 'C4'], 1.0, 0.9, 340)
    place(out, big, 0.72, 1.0)
    c = crash(0.8, 1.0, seed=341)
    place(out, pan(c, 0)[:L], 0.72, 0.25)
    out = reverb_lin(out, make_ir(2.0, 0.02, seed=342), 0.35)[:L]
    out = np.tanh(out / np.abs(out).max() * 1.5)
    return out, dict(fout=0.5)


SFX = {
    'system_boot': system_boot, 'system_ding': system_ding, 'system_scan': system_scan,
    'stamp_approve': stamp_approve, 'stamp_reject': stamp_reject, 'error_buzz': error_buzz,
    'coin': coin, 'money_rain': money_rain, 'seal_lock': seal_lock, 'seal_unlock': seal_unlock,
    'glitch': glitch, 'typing': typing, 'rain': rain, 'city_ambience': city_ambience,
    'office_ambience': office_ambience, 'elevator_ding': elevator_ding, 'ebike_horn': ebike_horn,
    'ebike_start': ebike_start, 'claw_machine': claw_machine, 'door_burst': door_burst,
    'camera_flash': camera_flash, 'knock': knock, 'phone_call': phone_call,
    'sad_trombone': sad_trombone, 'dramatic_sting': dramatic_sting,
}

LOOP = {'rain', 'city_ambience', 'office_ambience'}
