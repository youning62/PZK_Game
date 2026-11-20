"""Procedural sound effects.  Each function returns (signal, options)."""
import numpy as np
from synth import *  # noqa


def N(sec):
    return int(sec * SR)


def place(buf, sig, t, gain=1.0):
    i = int(t * SR)
    n = min(len(sig), len(buf) - i)
    buf[i:i + n] += gain * sig[:n]
    return buf


def noise(n, seed=0, ch=None):
    r = np.random.default_rng(seed)
    return r.standard_normal(n if ch is None else (n, ch))


def periodic_lfo(n, seed, harmonics=6, power=1.3):
    """Smooth random function exactly periodic over n samples (for loops)."""
    r = np.random.default_rng(seed)
    t = np.arange(n) / n
    y = np.zeros(n)
    for k in range(1, harmonics + 1):
        y += r.normal() / k ** power * np.sin(2 * np.pi * k * t + r.uniform(0, 6.28))
    y -= y.min()
    return y / y.max()


# ---------------------------------------------------------------- ambiences
def waves():
    L = N(18.0)
    t = np.arange(L) / SR
    out = np.zeros((L, 2))
    pink = lambda f: 1 / np.sqrt(np.maximum(f, 20) / 20)
    for ch in range(2):
        nz = noise(L, 100 + ch)
        rumble = fft_shape(nz, lambda f: pink(f) / (1 + (f / 350) ** 4))
        wash = fft_shape(noise(L, 200 + ch), lambda f: pink(f) * (f > 300) / (1 + (f / 7000) ** 4))
        fizz = fft_shape(noise(L, 300 + ch), lambda f: (f > 2500) / (1 + (f / 11000) ** 4))
        er = np.zeros(L)
        ew = np.zeros(L)
        ef = np.zeros(L)
        for (tc, amp) in [(1.2, 1.0), (7.3, 0.8), (12.6, 0.95)]:
            tc = tc + 0.12 * ch
            dt = ((t - tc + 9.0) % 18.0) - 9.0      # circular time from crest
            rise = np.exp(-(np.minimum(dt, 0) / 1.6) ** 2)
            er += amp * np.where(dt < 0, rise, np.exp(-dt / 1.8))
            ew += amp * np.where(dt < 0.2, np.exp(-((np.minimum(dt - 0.2, 0)) / 0.8) ** 2), np.exp(-(dt - 0.2) / 2.2))
            ef += amp * np.where(dt < 0.8, np.exp(-((np.minimum(dt - 0.8, 0)) / 0.7) ** 2), np.exp(-(dt - 0.8) / 2.8))
        sig = (rumble / rms(rumble) * (0.25 + 0.6 * er) * 0.8 +
               wash / rms(wash) * (0.12 + 0.7 * ew) * 0.5 +
               fizz / rms(fizz) * (0.05 + 0.5 * ef) * 0.25)
        out[:, ch] = sig
    return out, dict(loop=True, peak=-3.0)


def wind():
    L = N(12.0)
    out = np.zeros((L, 2))
    for ch in range(2):
        base = fft_shape(noise(L, 400 + ch), lambda f: 1 / np.sqrt(np.maximum(f, 30) / 30) / (1 + (f / 1200) ** 3))
        base = base / rms(base) * (0.35 + 0.65 * periodic_lfo(L, 10 + ch, 5))
        for j, fc in enumerate([480, 720, 1050]):
            band = fft_shape(noise(L, 500 + 10 * ch + j),
                             lambda f, fc=fc: np.exp(-0.5 * ((f - fc) / (fc * 0.06)) ** 2))
            base += 0.5 * band / rms(band) * periodic_lfo(L, 20 + 3 * j + ch, 6) ** 2
        out[:, ch] = base
    return out, dict(loop=True, peak=-3.0)


# ---------------------------------------------------------------- phone / ui
def phone_ding():
    out = np.zeros(N(1.0))
    for t0, note in [(0.0, 'B5'), (0.13, 'E6')]:
        f = hz(note)
        place(out, marimba(f, 0.3, 0.9), t0, 0.7)
        place(out, bell(f, 0.3, 0.6, decay=0.35, ratio=2.0, bright=0.4), t0, 0.4)
    return out, {}


def phone_vibrate():
    L = N(1.25)
    t = np.arange(L) / SR
    gate = np.zeros(L)
    for a, b in [(0.02, 0.47), (0.67, 1.12)]:
        gate += np.clip((t - a) / 0.02, 0, 1) * np.clip((b - t) / 0.02, 0, 1)
    f = 168 * (1 + 0.01 * np.sin(2 * np.pi * 7 * t))
    y = harmonic(f, L, [1, 0.6, 0.5, 0.35, 0.3, 0.2, 0.15, 0.1, 0.08, 0.06], cutoff=1800)
    rattle = bp(noise(L, 7), 2000, 6000) * (0.5 + 0.5 * np.sign(np.sin(phase_of(f, L)))) * 0.15
    y = (y + rattle) * (1 + 0.25 * np.sin(2 * np.pi * 31 * t)) * gate
    return y, {}


def ui_click():
    L = N(0.045)
    t = np.arange(L) / SR
    y = np.sin(2 * np.pi * 1500 * t) * np.exp(-t / 0.006)
    y += 0.5 * lp(noise(L, 9), 6000) * np.exp(-t / 0.002)
    y += 0.3 * np.sin(2 * np.pi * 420 * t) * np.exp(-t / 0.01)
    return y, dict(peak=-4.0, fout=0.01)


def ui_hover():
    L = N(0.03)
    t = np.arange(L) / SR
    y = np.sin(2 * np.pi * 2600 * t) * np.exp(-t / 0.004) + 0.2 * lp(noise(L, 10), 8000) * np.exp(-t / 0.0015)
    return y, dict(peak=-10.0, fout=0.008)


def alarm_soft():
    L = N(3.0)
    out = np.zeros(L)
    tone = lambda d: harmonic(988, N(d), [1, 0, 0.11, 0, 0.04]) * gate_env(N(d), d - 0.012, 0.012, 0.006)
    for g in range(3):
        for k in range(4):
            place(out, tone(0.085), 0.05 + g * 1.0 + k * 0.15, 0.8 + 0.05 * k)
    return out, dict(peak=-4.0)


# ---------------------------------------------------------------- engine
def _engine(rpm, throttle, cyl=8, seed=0):
    n = len(rpm)
    fire = rpm / 60 * cyl / 2
    r = np.random.default_rng(seed)
    rp = r.uniform(0, 6.28, 64)
    cut = 250 + 3500 * throttle
    tone = harmonic(fire, n, [1 / k ** 0.6 for k in range(1, 40)], cutoff=cut, slope=1.5, rand_phase=rp)
    lump = harmonic(fire / 2, n, [0.5, 0, 0.3], rand_phase=rp)       # burble / half order
    ph = phase_of(fire, n)
    comb = bp(noise(n, seed + 1), 300, 5000) * (0.5 + 0.5 * np.sin(ph)) ** 4
    y = tone + 0.5 * lump + (0.3 + 0.6 * throttle) * comb
    y = np.tanh(1.5 * y * (0.6 + 0.6 * throttle))
    intake = bp(noise(n, seed + 2), 600, 4000) * throttle * 0.15
    return lp(y + intake, 7000)


def engine_start():
    L = N(3.3)
    t = np.arange(L) / SR
    # starter motor: whining + compression pulses
    st_n = N(0.85)
    ts = t[:st_n]
    whine = harmonic(260 + 60 * ts, st_n, [1, 0.5, 0.3, 0.2, 0.15, 0.1], cutoff=1500)
    comp = 0.5 + 0.5 * np.sin(2 * np.pi * 9.5 * ts) ** 2
    starter = (0.35 * whine + 0.5 * lp(noise(st_n, 3), 900)) * comp * gate_env(st_n, 0.75, 0.1, 0.03)
    # engine rpm curve after catch
    def seg(x, pts):
        xs, ys = zip(*pts)
        return np.interp(x, xs, ys)
    rpm = seg(t, [(0, 250), (0.75, 300), (0.85, 1500), (1.05, 2600), (1.5, 1000), (1.75, 900),
                  (1.95, 2200), (2.25, 5600), (2.45, 5200), (2.9, 1300), (3.3, 950)])
    thr = seg(t, [(0, 0.1), (0.8, 0.2), (0.9, 0.9), (1.05, 0.5), (1.5, 0.2), (1.9, 0.2), (2.0, 1.0),
                  (2.35, 1.0), (2.45, 0.1), (3.3, 0.15)])
    eng = _engine(rpm, thr, seed=11)
    eng *= np.clip((t - 0.78) / 0.05, 0, 1) * (0.45 + 0.55 * thr)
    out = eng * 0.9
    place(out, starter, 0.0, 0.8)
    place(out, kick(0.8, 90, 40, 0.15, click=0.4), 0.82, 0.6)   # catch "whump"
    return out, dict(fout=0.15)


def engine_drive():
    L = N(3.2)
    t = np.arange(L) / SR
    rpm = np.interp(t, [0, 1.2, 1.28, 1.36, 3.2], [3000, 6800, 5200, 4800, 7000])
    thr = np.interp(t, [0, 1.18, 1.22, 1.34, 1.4, 3.2], [1, 1, 0.1, 0.1, 1, 1])
    # drive-by geometry: passes at t=1.5s, 6 m away, 45 m/s
    v, d0, tp, c = 45.0, 6.0, 1.5, 343.0
    x = v * (t - tp)
    dist = np.sqrt(x ** 2 + d0 ** 2)
    vr = np.gradient(dist, 1 / SR)
    dop = c / (c + vr)
    eng = _engine(rpm * dop, thr, seed=21)
    roar = lp(noise(L, 22), 1200) * 0.3
    sig = (eng + roar) * (d0 / dist) ** 0.9
    sig = lp(sig, 7000)
    panv = np.clip(x / 12, -1, 1)
    a = (panv + 1) * np.pi / 4
    out = np.stack([sig * np.cos(a), sig * np.sin(a)], 1) * np.sqrt(2)
    out *= np.clip(t / 0.3, 0, 1)[:, None]
    return out, dict(fout=0.4)


# ---------------------------------------------------------------- foley
def footsteps_sand():
    L = N(2.1)
    out = np.zeros(L)
    r = np.random.default_rng(31)
    for k in range(5):
        n = N(0.22)
        tt_ = np.arange(n) / SR
        e = np.clip(tt_ / 0.015, 0, 1) * np.exp(-tt_ / 0.06)
        crunch = lp(noise(n, 40 + k), 2200) * e
        grains = np.zeros(n)
        idx = r.integers(0, N(0.12), 60)
        grains[idx] = r.uniform(-1, 1, 60)
        grains = bp(grains, 2500, 7000) * e * 3
        thump = np.sin(2 * np.pi * 70 * tt_) * np.exp(-tt_ / 0.04) * 0.6
        step = crunch + 0.5 * grains + thump
        place(out, step, 0.05 + k * 0.4 + r.uniform(-0.02, 0.02), 0.8 + 0.2 * (k % 2))
        place(out, 0.4 * crunch, 0.05 + k * 0.4 + 0.09)
    return out, {}


def footsteps_heels():
    L = N(2.1)
    out = np.zeros(L)
    modes = [(240, 0.05, 0.6), (530, 0.035, 0.5), (1180, 0.02, 0.35), (2600, 0.01, 0.25)]
    for k in range(5):
        n = N(0.2)
        tt_ = np.arange(n) / SR
        click = hp(noise(n, 60 + k), 2500) * np.exp(-tt_ / 0.0015)
        wood = sum(a * np.sin(2 * np.pi * f * (1 + 0.03 * (k % 2)) * tt_) * np.exp(-tt_ / d) for f, d, a in modes)
        heel = click * 0.8 + wood
        toe = 0.35 * (lp(noise(n, 70 + k), 3000) * np.exp(-tt_ / 0.008) + 0.5 * wood)
        t0 = 0.05 + k * 0.4
        place(out, toe, t0 + 0.075)
        place(out, heel, t0, 0.9 + 0.1 * (k % 2))
    ir = make_ir(0.5, 0.005, seed=9, er=False)
    out = reverb_lin(out, ir, 0.15)[:, 0][:L]
    return out, {}


def splash():
    L = N(1.8)
    t = np.arange(L) / SR
    out = np.zeros(L)
    body = bp(noise(L, 80), 300, 6000) * np.clip(t / 0.01, 0, 1) * np.exp(-t / 0.18)
    body = lp(body, 5000)
    spray = hp(noise(L, 81), 3000) * np.clip((t - 0.03) / 0.05, 0, 1) * np.exp(-np.clip(t - 0.08, 0, None) / 0.35) * 0.4
    plop = np.sin(phase_of(60 + 80 * np.exp(-t / 0.03), L)) * np.exp(-t / 0.08) * 0.8
    out += body + spray + plop
    r = np.random.default_rng(82)
    for i in range(28):
        n = N(0.06)
        tb = np.arange(n) / SR
        f0 = r.uniform(500, 1800)
        bub = np.sin(phase_of(f0 * (1 + 3 * tb / 0.06), n)) * np.exp(-tb / 0.012)
        place(out, bub, r.uniform(0.05, 1.2) ** 1.3, r.uniform(0.05, 0.25))
    return out, dict(fout=0.2)


def thud():
    L = N(0.8)
    t = np.arange(L) / SR
    boom = np.sin(phase_of(42 + 90 * np.exp(-t / 0.05), L)) * np.exp(-t / 0.18)
    sand = lp(noise(L, 90), 1500) * np.exp(-t / 0.06) * 0.7
    poof = bp(noise(L, 91), 800, 4000) * np.clip((t - 0.02) / 0.04, 0, 1) * np.exp(-t / 0.15) * 0.18
    bonk = np.sin(phase_of(320 - 120 * t, L)) * np.exp(-t / 0.05) * 0.25
    return np.tanh(1.4 * (boom + sand + poof + bonk)), dict(fout=0.1)


def boing():
    L = N(1.1)
    t = np.arange(L) / SR
    depth = 0.35 * np.exp(-t / 0.35)
    f = (190 + 90 * (1 - np.exp(-t / 0.2))) * (1 + depth * np.sin(2 * np.pi * 13 * t))
    cut = 700 + 900 * (0.5 + 0.5 * np.sin(2 * np.pi * 13 * t + 1)) * np.exp(-t / 0.4) + 300
    y = harmonic(f, L, SAW[:30], cutoff=cut, slope=2.5)
    y *= np.clip(t / 0.004, 0, 1) * np.exp(-t / 0.35)
    y += 0.6 * np.sin(phase_of(f, L)) * np.exp(-t / 0.3)
    return y, dict(fout=0.15)


def record_scratch():
    L = N(0.9)
    # source: a 3 s chord to scrub through
    sn = N(3.0)
    src = np.zeros(sn)
    for m in chord('F3 A3 C4 E4 F2'):
        src += harmonic(hz(m), sn, SAW[:40], cutoff=3000)
    src += 0.3 * bp(noise(sn, 95), 200, 6000)
    src /= np.abs(src).max()
    t = np.arange(L) / SR
    # playhead velocity (1 = normal speed): back-and-forth "zwick-zwick", then stop
    vel = np.interp(t, [0, 0.03, 0.12, 0.17, 0.27, 0.33, 0.45, 0.6, 0.9],
                    [1, 1, -2.6, -0.5, 2.4, 1.0, -1.8, 0, 0])
    pos = N(1.5) + np.cumsum(vel)
    pos = np.clip(pos, 0, sn - 2)
    i = pos.astype(int)
    fr = pos - i
    y = src[i] * (1 - fr) + src[i + 1] * fr
    y = hp(y, 150) * np.clip(np.abs(vel) * 1.2, 0, 1)
    hiss = bp(noise(L, 96), 1000, 8000) * (0.08 + 0.25 * np.abs(vel) / 2.6) * (t < 0.6)
    out = y + hiss
    out *= np.clip((0.62 - t) / 0.05, 0, 1)
    return out, dict(fout=0.05)


def door():
    L = N(2.0)
    t = np.arange(L) / SR
    out = np.zeros(L)
    # creak: stick-slip pulse train through wooden resonances
    cn = N(1.0)
    tc = np.arange(cn) / SR
    r = np.random.default_rng(101)
    f = 55 + 70 * np.sin(np.pi * tc / 1.0) ** 0.7 + 12 * np.sin(2 * np.pi * 3.1 * tc)
    f *= 1 + 0.04 * lp(r.standard_normal(cn), 30) * 10
    ph = phase_of(f, cn)
    pulses = np.maximum(0, np.sin(ph)) ** 30
    creak = sum(resonator(pulses, fr, 12) * g for fr, g in [(620, 1.0), (1150, 0.7), (1900, 0.45), (2700, 0.3)])
    creak *= np.sin(np.pi * tc / 1.0) ** 0.5
    place(out, creak / np.abs(creak).max(), 0.05, 0.7)
    # close: thump + latch
    sn = N(0.6)
    ts = np.arange(sn) / SR
    thump = np.sin(phase_of(70 + 60 * np.exp(-ts / 0.02), sn)) * np.exp(-ts / 0.09)
    thump += sum(a * np.sin(2 * np.pi * fq * ts) * np.exp(-ts / d) for fq, d, a in [(180, 0.06, 0.5), (410, 0.04, 0.3), (950, 0.02, 0.2)])
    thump += 0.4 * lp(noise(sn, 102), 2000) * np.exp(-ts / 0.02)
    place(out, thump, 1.25, 1.0)
    for dt, g in [(0.0, 0.5), (0.035, 0.35)]:
        ln = N(0.05)
        tl = np.arange(ln) / SR
        latch = (hp(noise(ln, 103), 3000) * np.exp(-tl / 0.002) +
                 0.6 * np.sin(2 * np.pi * 3100 * tl) * np.exp(-tl / 0.01))
        place(out, latch, 1.27 + dt, g)
    out = reverb_lin(out, make_ir(0.6, 0.008, seed=10, er=False), 0.2)[:, 0][:L]
    return out, dict(fout=0.2)


def heartbeat():
    L = N(2.0)
    out = np.zeros(L)
    def beat(f0, f1, dec, g):
        n = N(0.3)
        tb = np.arange(n) / SR
        y = np.sin(phase_of(f1 + (f0 - f1) * np.exp(-tb / 0.02), n)) * np.clip(tb / 0.008, 0, 1) * np.exp(-tb / dec)
        y += 0.2 * lp(noise(n, int(f0)), 300) * np.exp(-tb / 0.03)
        return y * g
    for t0 in (0.05, 0.95):
        place(out, beat(85, 48, 0.08, 1.0), t0)
        place(out, beat(95, 58, 0.06, 0.75), t0 + 0.27)
    return lp(out, 400), dict(fout=0.1)


def crickets():
    L = N(3.2)
    t = np.arange(L) / SR
    out = np.zeros((L, 2))
    r = np.random.default_rng(111)
    for ch, (fc, period, off) in enumerate([(4600, 0.48, 0.1), (4150, 0.63, 0.35)]):
        env = np.zeros(L)
        t0 = off
        while t0 < 3.1:
            for p in range(4):
                a = t0 + p * 0.026
                env += np.clip(np.sin(np.pi * np.clip((t - a) / 0.016, 0, 1)), 0, 1) ** 2
            t0 += period * r.uniform(0.92, 1.08)
        car = np.sin(2 * np.pi * fc * t) + 0.15 * np.sin(2 * np.pi * 2 * fc * t)
        sig = car * env
        out[:, ch] += sig
        out[:, 1 - ch] += 0.3 * sig
    out = reverb_lin(out, make_ir(1.2, 0.02, seed=11), 0.25)[:L]
    out *= np.clip(t / 0.3, 0, 1)[:, None] * np.clip((3.2 - t) / 0.4, 0, 1)[:, None]
    return out, {}


# ---------------------------------------------------------------- bells / tones
def _strike(f, ratios, amps, decays, length):
    n = N(length)
    tb = np.arange(n) / SR
    y = sum(a * np.sin(2 * np.pi * f * r * tb + i) * np.exp(-tb / d) for i, (r, a, d) in enumerate(zip(ratios, amps, decays)))
    return y * np.clip(tb / 0.0008, 0, 1)


def glass_clink():
    L = N(1.8)
    out = np.zeros(L)
    for f0, g, dt in [(1250, 1.0, 0.0), (1323, 0.8, 0.002)]:
        y = _strike(f0, [1, 2.32, 4.25, 6.63], [1, 0.6, 0.35, 0.2], [0.9, 0.45, 0.2, 0.1], 1.7)
        place(out, y, 0.01 + dt, g)
    place(out, hp(noise(N(0.004), 120), 4000), 0.01, 0.5)
    return out, dict(fout=0.3)


def cash():
    L = N(1.6)
    out = np.zeros(L)
    n = N(0.2)
    tb = np.arange(n) / SR
    clunk = np.sin(phase_of(110 + 80 * np.exp(-tb / 0.01), n)) * np.exp(-tb / 0.04) + 0.5 * bp(noise(n, 130), 500, 4000) * np.exp(-tb / 0.02)
    place(out, clunk, 0.0, 0.8)
    place(out, clunk, 0.07, 0.5)
    ding = _strike(2100, [1, 2.76, 5.4, 8.93], [1, 0.5, 0.25, 0.1], [0.7, 0.35, 0.15, 0.06], 1.4)
    place(out, ding, 0.14, 0.9)
    place(out, _strike(2640, [1, 2.76, 5.4], [1, 0.4, 0.2], [0.5, 0.25, 0.1], 1.2), 0.15, 0.5)
    r = np.random.default_rng(131)
    for i in range(26):
        f0 = r.uniform(3000, 7000)
        c = _strike(f0, [1, 1.47, 2.09], [1, 0.6, 0.4], [r.uniform(0.02, 0.07)] * 3, 0.15)
        place(out, c, 0.2 + r.uniform(0, 0.7) ** 1.5, r.uniform(0.08, 0.25))
    return out, dict(fout=0.2)


def mirror_ding():
    L = N(1.7)
    out = np.zeros((L, 2))
    for ch, det in enumerate([1.0, 1.0015]):
        y = _strike(2637 * det, [1, 2.41, 4.1, 6.2], [1, 0.35, 0.2, 0.1], [0.8, 0.35, 0.15, 0.06], 1.6)
        out[:N(1.6), ch] += y
    r = np.random.default_rng(140)
    for i in range(6):
        f = hz(['E7', 'B7', 'G#7', 'E8', 'C#8', 'B7'][i])
        y = bell(f, 0.1, 0.4, decay=0.15, ratio=3.5, bright=0.3)
        place(out[:, i % 2], y, 0.03 + i * 0.05, 0.12)
    out = reverb_lin(out, make_ir(1.5, 0.02, seed=12), 0.3)[:L]
    return out, dict(fout=0.3)


def doorbell():
    L = N(2.4)
    out = np.zeros(L)
    for t0, note in [(0.0, 'E5'), (0.55, 'C5')]:
        y = _strike(hz(note), [1, 2.0, 2.76, 5.4], [1, 0.25, 0.3, 0.1], [1.4, 0.8, 0.5, 0.15], 1.85)
        place(out, y, t0)
    out = reverb_lin(out, make_ir(0.8, 0.01, seed=13, er=False), 0.2)[:, 0][:L]
    return out, dict(fout=0.4)


def sparkle():
    L = N(1.6)
    out = np.zeros((L, 2))
    r = np.random.default_rng(150)
    scale = ['C6', 'D6', 'E6', 'G6', 'A6', 'C7', 'D7', 'E7', 'G7', 'A7', 'C8']
    for i in range(14):
        k = min(len(scale) - 1, int(i * 0.7 + r.integers(0, 3)))
        y = bell(hz(scale[k]), 0.1, r.uniform(0.4, 0.8), decay=0.25, ratio=3.5, bright=0.5)
        p = r.uniform(-0.9, 0.9)
        out_seg = pan(y, p)
        i0 = N(0.02 + i * 0.045 + r.uniform(0, 0.02))
        n = min(len(out_seg), L - i0)
        out[i0:i0 + n] += out_seg[:n] * 0.5
    sh = hp(noise(L, 151, 2), 8000) * np.exp(-np.arange(L) / SR / 0.3)[:, None] * 0.05
    out += sh
    out = reverb_lin(out, make_ir(1.4, 0.02, seed=14), 0.4)[:L]
    return out, dict(fout=0.3)


def stat_up():
    L = N(1.3)
    out = np.zeros(L)
    for i, note in enumerate(['C5', 'E5', 'G5', 'C6']):
        place(out, marimba(hz(note), 0.1, 0.8), i * 0.065, 0.6)
        place(out, bell(hz(note), 0.1, 0.5, decay=0.3, ratio=2, bright=0.3), i * 0.065, 0.3)
    for note in ['E6', 'G6', 'C7']:
        place(out, bell(hz(note), 0.5, 0.7, decay=0.45, ratio=2.0, bright=0.5), 0.27, 0.35)
    out = reverb_lin(out, make_ir(1.0, 0.015, seed=15), 0.2)[:, 0][:L]
    return out, dict(fout=0.3)


def stat_down():
    L = N(2.5)
    out = np.zeros(L)
    notes = [('G3', 0.0, 0.32, 0), ('F#3', 0.4, 0.32, 0), ('F3', 0.8, 0.32, 0), ('E3', 1.2, 1.0, 1)]
    for name, t0, d, last in notes:
        n = N(d + 0.15)
        tb = np.arange(n) / SR
        f = hz(name) * np.ones(n)
        if last:
            f = f * 2 ** ((28 * np.sin(2 * np.pi * 6 * tb) * np.clip(tb / 0.3, 0, 1) - 60 * np.clip((tb - 0.5) / 0.5, 0, 1)) / 1200)
        # wah: mute opens then closes
        wah = np.sin(np.pi * np.clip(tb / d, 0, 1)) ** 0.8
        if last:
            wah = 0.5 + 0.5 * np.sin(2 * np.pi * 3 * tb - 1.5) * np.clip(tb / 0.2, 0, 1)
        cut = 300 + 1600 * wah
        y = harmonic(f, n, SAW[:40], cutoff=cut, slope=2)
        y = np.tanh(1.5 * y) * gate_env(n, d, 0.12, 0.02)
        place(out, y, t0)
    return out, dict(fout=0.15, peak=-3.0)


def shock():
    L = N(2.2)
    t = np.arange(L) / SR
    out = np.zeros((L, 2))
    boom = np.sin(phase_of(36 + 60 * np.exp(-t / 0.04), L)) * np.exp(-t / 0.5)
    stab = np.zeros((L, 2))
    for m in chord('C2 C3 F#3 C4 B4 F#5'):
        p = pad(hz(m), 0.12, 0.9, att=0.003, rel=0.5, cutoff=4000, detune=14, seed=int(m))
        n = min(len(p), L)
        stab[:n] += p[:n]
    stab *= np.exp(-t / 0.35)[:, None]
    crash = hp(noise(L, 160, 2), 3500) * np.exp(-t / 0.6)[:, None]
    crash += 0.4 * hp(sum(np.sign(np.sin(2 * np.pi * f * 2.3 * t + i)) for i, f in enumerate(HAT_F))[:, None] * np.ones((1, 2)), 5000) * np.exp(-t / 0.4)[:, None]
    hit = 0.8 * pan(boom, 0) + 0.6 * stab / np.abs(stab).max() + 0.25 * crash
    hit *= np.clip(t / 0.002, 0, 1)[:, None]
    out = reverb_lin(hit, make_ir(1.8, 0.02, seed=16), 0.35)[:L]
    out *= np.clip((2.2 - t) / 0.5, 0, 1)[:, None]
    return np.tanh(out * 1.2), {}


SFX = {
    'waves': waves, 'wind': wind, 'phone_ding': phone_ding, 'phone_vibrate': phone_vibrate,
    'engine_start': engine_start, 'engine_drive': engine_drive, 'footsteps_sand': footsteps_sand,
    'footsteps_heels': footsteps_heels, 'splash': splash, 'thud': thud, 'boing': boing,
    'record_scratch': record_scratch, 'sparkle': sparkle, 'stat_up': stat_up, 'stat_down': stat_down,
    'shock': shock, 'heartbeat': heartbeat, 'crickets': crickets, 'door': door, 'cash': cash,
    'glass_clink': glass_clink, 'ui_click': ui_click, 'ui_hover': ui_hover, 'mirror_ding': mirror_ding,
    'doorbell': doorbell, 'alarm_soft': alarm_soft,
}
