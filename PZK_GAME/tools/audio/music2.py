"""Background music for the 'scammed -> broke -> rider -> system -> LXX' arc.

Same conventions as music.py: every function returns (stereo loop, Song) and the
loop is exactly a whole number of bars with all tails wrapped to the start.
Also holds the extra instruments (kazoo, brass, strings, chip, clap, ...) that
sfx2.py reuses.
"""
import numpy as np
from synth import *  # noqa
from music import ev  # noqa


# ============================================================================
# extra instruments
# ============================================================================
def _nz(n, seed):
    return np.random.default_rng(seed).standard_normal(n)


def kazoo(f, dur, vel=0.8, rel=0.08, bend=0.0, wobble=18.0):
    """Buzzy nasal kazoo: saw through vocal-ish formants + rasp.  bend = cents droop."""
    n = int((dur + rel) * SR)
    t = tt(n)
    glide = bend * np.clip((t - 0.15) / max(dur - 0.1, 1e-3), 0, 1) ** 1.4
    vib = wobble * np.sin(2 * np.pi * 5.6 * t) * np.clip((t - 0.08) / 0.15, 0, 1)
    fr = f * 2 ** ((glide + vib - 70 * np.exp(-t / 0.035)) / 1200)
    src = harmonic(fr, n, SAW[:45])
    y = (0.7 * resonator(src, 650, 3.5) + 1.0 * resonator(src, 1350, 5) +
         0.6 * resonator(src, 2500, 6) + 0.15 * src)
    rasp = bp(_nz(n, int(f)), 1200, 5000) * (0.5 + 0.5 * np.sin(phase_of(fr, n))) ** 6
    y = np.tanh(2.2 * (y + 0.25 * rasp))
    return 0.5 * y * gate_env(n, dur, rel, 0.02) * (0.4 + 0.6 * vel)


def brass(f, dur, vel=0.8, rel=0.12, att=0.03, bright=1.0, vib=8.0):
    n = int((dur + rel) * SR)
    t = tt(n)
    fr = f * 2 ** ((-30 * np.exp(-t / 0.03) +
                    vib * np.sin(2 * np.pi * 5.2 * t) * np.clip((t - 0.25) / 0.3, 0, 1)) / 1200)
    swell = 1 - np.exp(-t / 0.04)
    cut = (250 + 2600 * bright * vel * (0.55 + 0.45 * np.exp(-t / 0.25))) * swell + 150
    y = harmonic(fr, n, SAW[:40], cutoff=cut, slope=1.6)
    y = np.tanh(1.6 * y)
    return 0.6 * y * adsr(n, dur, a=att, d=0.3, s=0.8, r=rel) * (0.4 + 0.6 * vel)


def strings(f, dur, vel=0.7, att=0.008, rel=0.1, cutoff=2400, nv=3, seed=0, dec=0.15, sus=0.7):
    """Section strings (detuned saws). Short att/dec = spiccato; long att = legato."""
    rng = np.random.default_rng(seed + int(f))
    n = int((dur + rel) * SR)
    y = np.zeros(n)
    for v in range(nv):
        c = (v - (nv - 1) / 2) * 7 + rng.uniform(-2, 2)
        fv = vibrato(f * 2 ** (c / 1200), n, rate=rng.uniform(5, 6), cents=7, delay=0.12, ramp=0.25)
        y += saw_blep(fv, n, rng.uniform())
    cut = cutoff * (0.55 + 0.6 * vel)
    y = lp(lp(y, cut), cut * 1.7)
    bow = bp(_nz(n, seed + 7), 1500, 6000) * np.exp(-tt(n) / 0.02) * 0.3
    return (y / nv + bow) * adsr(n, dur, a=att, d=dec, s=sus, r=rel) * (0.4 + 0.6 * vel)


def chip(f, dur, vel=0.7, duty=0.25, rel=0.02, vib=0.0, slide=0.0):
    """Band-limited pulse wave (NES-ish). slide = cents glide over the note."""
    n = int((dur + rel) * SR)
    t = tt(n)
    cents = vib * np.sin(2 * np.pi * 6 * t) * np.clip((t - 0.12) / 0.1, 0, 1)
    cents = cents + slide * np.clip(t / max(dur, 1e-3), 0, 1)
    fr = f * 2 ** (cents / 1200)
    w = [np.sin(np.pi * k * duty) / k for k in range(1, 40)]
    y = harmonic(fr, n, w)
    env = gate_env(n, dur, rel, 0.002) * (0.75 + 0.25 * np.exp(-t / 0.08))
    return 0.8 * y * env * (0.4 + 0.6 * vel)


def blip(f, dur, vel=0.7):
    """Sine bleep with a tiny FM chirp."""
    n = int((dur + 0.03) * SR)
    t = tt(n)
    y = np.sin(phase_of(f * (1 + 0.04 * np.exp(-t / 0.01)), n))
    return y * gate_env(n, dur, 0.03, 0.002) * (0.3 + 0.7 * vel)


def clap(vel=0.7, seed=7, decay=0.12, tone=1.0):
    n = int(0.45 * SR)
    t = tt(n)
    nz = bp(_nz(n, seed), 900 * tone, 5200 * tone)
    env = np.zeros(n)
    for k, o in enumerate([0.0, 0.009, 0.019, 0.028]):
        tk = t - o
        env += (tk >= 0) * np.exp(-np.clip(tk, 0, None) / 0.004) * (0.8 + 0.1 * k)
    tk = t - 0.028
    env += (tk >= 0) * np.exp(-np.clip(tk, 0, None) / decay) * 0.7
    return tail_fade(nz * env, 0.2) * vel


def tom(vel=0.7, f=110, decay=0.25, seed=8):
    n = int(decay * 3 * SR)
    t = tt(n)
    y = np.sin(phase_of(f * (1 + 0.6 * np.exp(-t / 0.03)), n)) * np.exp(-t / decay)
    y += 0.3 * np.sin(phase_of(f * 1.6, n)) * np.exp(-t / (decay * 0.4))
    y += 0.25 * bp(_nz(n, seed), 400, 5000) * np.exp(-t / 0.01)
    return tail_fade(np.tanh(1.3 * y), 0.2) * vel


def crash(vel=0.7, decay=0.9, seed=9, length=None):
    n = int((length or decay * 3) * SR)
    t = tt(n)
    m = sum(np.sign(np.sin(2 * np.pi * f * 2.9 * t + i)) for i, f in enumerate(HAT_F)) / 6
    y = hp(0.5 * m + _nz(n, seed), 4000) * np.exp(-t / decay) * np.clip(t / 0.002, 0, 1)
    return tail_fade(y, 0.3) * vel


def mute_marimba(f, dur, vel=0.7):
    y = marimba(f, dur, vel)
    t = tt(len(y))
    return lp(y * np.exp(-t / 0.12), 3000, 1)


def crackle_layer(L, seed=0, density=7.0, hiss=0.006):
    """Vinyl crackle + hiss, exactly L samples, circular (loop-safe)."""
    r = np.random.default_rng(seed)
    out = np.zeros((L, 2))
    k = int(density * L / SR)
    pos = r.integers(0, L, k)
    amp = r.uniform(0.1, 1.0, k) ** 3
    for ch in range(2):
        imp = np.zeros(L)
        np.add.at(imp, (pos + ch * r.integers(0, 40)) % L, amp * r.choice([-1, 1], k))
        c = fft_shape(imp, lambda f: (f > 900) / (1 + (f / 6000) ** 2))
        h = fft_shape(r.standard_normal(L), lambda f: (f > 300) / (1 + (f / 4000) ** 2))
        out[:, ch] = 0.6 * c + hiss * h / rms(h)
    return out


# ============================================================================
# scam -- 100 BPM, E minor sneaky heist
# ============================================================================
def scam():
    s = Song(100, 24, seed=101)
    prog = ['Em', 'Em', 'Am', 'B7', 'Em', 'C', 'Am', 'B7']
    root = {'Em': 'E2', 'Am': 'A1', 'B7': 'B1', 'C': 'C2'}
    third = {'Em': 3, 'Am': 3, 'B7': 4, 'C': 4}
    stabv = {'Em': 'E3 B3 E4 G4', 'Am': 'A2 E3 A3 C4', 'B7': 'B2 F#3 A3 D#4', 'C': 'C3 G3 C4 E4'}
    padv = {'Em': 'E3 G3 B3', 'Am': 'E3 A3 C4', 'B7': 'D#3 A3 B3', 'C': 'E3 G3 C4'}
    for bar in range(24):
        c = prog[bar % 8]
        b0 = s.bar(bar)
        ph = bar // 8
        r = midi(root[c]) + 12
        stab_at = 2.5 if bar % 8 == 3 else (3.0 if bar % 8 == 7 else None)
        walk = [(0, 0, 0.9), (1, third[c], 0.6), (1.5, 5, 0.55), (2, 6, 0.6), (2.5, 7, 0.75), (3.5, 12, 0.6)]
        for o, semi, v in walk:
            if stab_at is not None and o >= stab_at:
                continue
            s.add(pluck(hz(r + semi), 0.45 * s.spb, v, t60=0.6, bright=0.45, stacc=0.55),
                  b0 + o, 0.42, -0.1, 0.12, 0.003, 'pizzbass')
        # clock ticks + 16th hat ticking
        for k in range(4):
            s.add(woodblock(0.45, 2100 if k % 2 == 0 else 1650), b0 + k, 0.06, 0.45, 0.1, 0.0, 'clock')
        for k in range(16):
            if stab_at is not None and stab_at <= k * 0.25 < stab_at + 0.5:
                continue
            acc = 0.6 if k % 4 == 0 else 0.3
            s.add(hat(acc, 0.018, seed=k), b0 + k * 0.25, 0.10, -0.35 if k % 2 else 0.35, 0.05, 0.001, 'tick')
        s.add(kick(0.6, 90, 42, 0.25, click=0.05), b0, 0.22, 0, 0, 0, 'kick')
        if ph == 2:
            s.add(kick(0.5, 90, 42, 0.25, click=0.05), b0 + 2.5, 0.18, 0, 0, 0, 'kick')
        if ph >= 1:
            for k in (1, 3):
                if stab_at is None or k < stab_at:
                    s.add(rim(0.45, 1350), b0 + k, 0.07, 0.15, 0.2, 0.002, 'rim')
        if ph == 2:
            for m in chord(padv[c]):
                s.add(pad(hz(m), 4 * s.spb, 0.5, att=0.6, rel=1.2, cutoff=700, seed=bar * 3 + int(m)),
                      b0, 0.035, 0, 0.35, 0, 'pad')
        # sudden stabs
        if stab_at is not None:
            sb = b0 + stab_at
            for j, m in enumerate(chord(stabv[c])):
                s.add(brass(hz(m), 0.35 * s.spb, 0.95, rel=0.15, att=0.008), sb, 0.09, -0.4 + 0.27 * j, 0.45, 0, 'stab')
                s.add(strings(hz(m + 12), 0.3 * s.spb, 0.9, seed=j), sb, 0.06, 0.4 - 0.27 * j, 0.45, 0, 'stab')
            s.add(kick(1.0, 130, 40, 0.3), sb, 0.20, 0, 0.1, 0, 'stab')
            s.add(crash(0.5, 0.5, seed=bar), sb, 0.10, 0.2, 0.4, 0, 'stab')
            s.add(pluck(hz(midi(root[c])), 0.5 * s.spb, 0.95, t60=0.8, bright=0.5), sb, 0.28, 0, 0.2, 0, 'pizzbass')
    mel = ('E4:0.5 r:0.5 F#4:0.5 G4:0.5 r:1 B4:0.5 r:0.5 | A#4:0.5 B4:0.5 r:3 | '
           'C5:0.5 r:0.5 B4:0.5 A4:0.5 r:0.5 G4:0.5 E4:1 | D#4:0.5 F#4:0.5 A4:0.5 B4:0.5 r:2 | '
           'E4:0.5 r:0.5 F#4:0.5 G4:0.5 r:1 B4:0.5 r:0.5 | E5:0.5 D#5:0.5 D5:0.5 C#5:0.5 C5:1 r:1 | '
           'A4:0.5 r:0.5 C5:0.5 E5:0.5 r:0.5 D#5:0.5 B4:1 | F#4:0.5 A4:0.5 D#4:0.5 r:0.5 E4:1 r:1')
    e1, _ = parse(mel, s.bar(8), 0.75)
    e2, _ = parse(mel, s.bar(16), 0.8)
    s.play(pluck, e1, 0.45, 0.25, 0.2, transpose=12, stem='pizzlead', t60=0.5, bright=0.45, stacc=0.5)
    s.play(strings, [(b, d * 0.85, m, v) for b, d, m, v in e2], 0.24, 0.2, 0.3, stem='strings',
           att=0.03, dec=0.3, sus=0.6, rel=0.12)
    s.play(celesta, e2, 0.03, -0.3, 0.45, transpose=24, stem='celesta')
    # phase 0: a bassoon tiptoe answering phrase
    tip, _ = parse('r:2 B2:0.5 r:0.5 C3:0.5 r:0.5 | r:4 | r:2 E3:0.5 r:0.5 D#3:0.5 r:0.5 | r:4 |'
                   ' r:2 B2:0.5 r:0.5 C3:0.5 r:0.5 | r:4 | r:2 F#3:0.5 r:0.5 G3:0.5 F#3:0.5 | r:4', 0, 0.75)
    s.play(bassoon, [(b, d * 0.6, m, v) for b, d, m, v in tip], 0.28, 0.25, 0.2, stem='bassoon')
    return s.render(make_ir(1.4, 0.015, seed=21), wet=0.6), s


# ============================================================================
# broke -- 90 BPM limping 3/4 waltz, C minor, kazoo + tuba
# ============================================================================
def broke():
    s = Song(90, 28, beats=3, seed=102)
    A = ['Cm', 'Cm', 'Fm', 'Fm', 'G7', 'G7', 'Cm', 'G7']
    B = ['Ab', 'Ab', 'Fm', 'Fm', 'G7', 'G7', 'Cm', 'G7']
    tag = ['Cm', 'Ab7', 'Db', 'G7']
    form = A + A + B + tag
    CH = {'Cm': ('C2', 'G1', 'Eb3 G3 C4'), 'Fm': ('F1', 'C2', 'F3 Ab3 C4'),
          'G7': ('G1', 'D2', 'F3 B3 D4'), 'Ab': ('Ab1', 'Eb2', 'Eb3 Ab3 C4'),
          'Ab7': ('Ab1', 'Eb2', 'Eb3 Gb3 C4'), 'Db': ('Db2', 'Ab1', 'F3 Ab3 Db4')}
    limp = 0.16
    for bar, c in enumerate(form):
        b0 = s.bar(bar)
        root, fifth, vo = CH[c]
        tn = root if (bar % 2 == 0 or form[bar - 1] != c) else fifth
        s.add(tuba(hz(tn), 0.8 * s.spb, 0.85), b0, 0.34, 0, 0.08, 0.004, 'tuba')
        s.add(kick(0.45, 100, 45, 0.2, click=0.05), b0, 0.20, 0, 0, 0.002, 'kick')
        for k, off in ((1, 0.0), (2, limp)):
            for m in chord(vo):
                s.add(pluck(hz(m), 0.4 * s.spb, 0.55 if k == 1 else 0.45, t60=0.5, bright=0.45, stacc=0.45),
                      b0 + k + off, 0.30, 0.25, 0.15, 0.006, 'pah')
            s.add(brush(0.45, seed=bar * 3 + k, length=0.18), b0 + k + off, 0.12, -0.2, 0.15, 0.004, 'brush')
        if bar >= 24:          # tag: tuba sighs down
            s.add(woodblock(0.4, 700), b0 + 2.5, 0.05, 0.4, 0.2, 0, 'wood')
    melA = ('G4:1 Eb4:1 C4:1 | D4:2 r:1 | F4:1 Ab4:1 G4:1 | F4:1.5 Eb4:0.5 r:1 | '
            'D4:1 F4:1 Ab4:1 | B4:2 G4:1 | C5:1 G4:1 Eb4:1 | D4:3')
    melA2 = ('G4:1 Eb4:1 C4:1 | D4:2 r:1 | F4:1 Ab4:1 G4:1 | F4:1.5 Eb4:0.5 r:1 | '
             'D4:1 F4:1 Ab4:1 | B4:2 G4:1 | Eb4:1 D4:1 B3:1 | C4:3')
    melB = ('Eb4:1 C4:1 Ab3:1 | Eb4:1 F4:1 G4:1 | Ab4:2 F4:1 | C4:3 | '
            'B3:1 D4:1 F4:1 | Ab4:1 G4:1 F4:1 | Eb4:1 D4:1 C4:1 | D4:3')
    melT = 'G4:1 F#4:1 F4:1 | E4:1 Eb4:1 D4:1 | Db4:3 | B3:3'
    lead = (parse(melA, s.bar(0), 0.8)[0] + parse(melA2, s.bar(8), 0.8)[0] +
            parse(melB, s.bar(16), 0.8)[0] + parse(melT, s.bar(24), 0.8)[0])
    for b, d, ms, v in lead:
        long_ = d >= 2
        bend = -90 if long_ else 0
        if b >= s.bar(27):
            bend = -260               # final deflating droop
        sig = kazoo(hz(ms[0]), d * s.spb * 0.92, v, bend=bend, wobble=30 if long_ else 15)
        s.add(sig, b, 0.40, 0.1, 0.18, 0.006, 'kazoo')
    # bassoon "sigh" counterline in A' and B
    cnt = ('r:3 | r:2 G3:1 | r:3 | r:1 Ab3:1 G3:1 | r:3 | r:1 D3:1 F3:1 | r:3 | r:1 G3:2 | '
           'C3:3 | Eb3:3 | F3:3 | Eb3:2 D3:1 | D3:3 | B2:3 | C3:3 | B2:3')
    e, _ = parse(cnt, s.bar(8), 0.7)
    for b, d, ms, v in e:
        s.add(bassoon(hz(ms[0]), d * s.spb * 0.9, v, bend=-40 if d >= 2 else 0, wobble=10),
              b, 0.20, -0.25, 0.2, 0.005, 'bassoon')
    return s.render(make_ir(1.2, 0.012, seed=22), wet=0.55), s


# ============================================================================
# rider -- 118 BPM, D major light funk/pop hustle
# ============================================================================
def rider():
    s = Song(118, 32, seed=103)
    A = ['Dmaj7', 'Bm7', 'Em7', 'A7']
    B = ['Gmaj7', 'F#m7', 'Em7', 'A7']
    form = A * 4 + B * 2 + A * 2
    gtr = {'Dmaj7': 'F#4 A4 C#5', 'Bm7': 'F#4 A4 D5', 'Em7': 'G4 B4 D5', 'A7': 'G4 C#5 E5',
           'Gmaj7': 'F#4 B4 D5', 'F#m7': 'E4 A4 C#5'}
    epv = {'Dmaj7': 'D3 F#3 A3 C#4', 'Bm7': 'B2 D3 F#3 A3', 'Em7': 'E3 G3 B3 D4', 'A7': 'E3 G3 A3 C#4',
           'Gmaj7': 'D3 F#3 G3 B3', 'F#m7': 'E3 F#3 A3 C#4'}
    roots = {'Dmaj7': 'D2', 'Bm7': 'B1', 'Em7': 'E2', 'A7': 'A1', 'Gmaj7': 'G1', 'F#m7': 'F#1'}
    stab_offs = [0.5, 1.25, 1.5, 2.5, 3.25, 3.5]
    for bar, c in enumerate(form):
        b0 = s.bar(bar)
        r = midi(roots[c]) + 12
        bl = [(0, 0, 0.9, 0.4), (0.75, 0, 0.5, 0.2), (1.5, 12, 0.65, 0.3), (2.5, 7, 0.75, 0.4),
              (3, 0, 0.6, 0.3), (3.5, 12, 0.55, 0.3)]
        s.play(bass, [ev(b0 + o, d, [r + sm], v) for o, sm, v, d in bl], 0.15, 0, 0.03,
               stem='bass', drive=1.4, bright=0.7)
        for o in stab_offs:
            vv = 0.75 if o in (0.5, 2.5) else 0.55
            for j, m in enumerate(chord(gtr[c])):
                s.add(pluck(hz(m), 0.25 * s.spb, vv, t60=0.5, bright=0.75, stacc=0.6),
                      b0 + o + j * 0.008, 0.20, -0.35, 0.12, 0.002, 'gtr')
        for k in range(16):           # muted "chk" ghost strums
            if k * 0.25 in stab_offs or k % 2 == 0:
                continue
            s.add(shaker(0.35, seed=k, length=0.04), b0 + k * 0.25, 0.10, -0.3, 0.05, 0.002, 'gtr')
        if bar >= 8:
            for m in chord(epv[c]):
                s.add(epiano(hz(m), 3.5 * s.spb, 0.4), b0, 0.045, 0.2, 0.3, 0.004, 'epiano')
        # drums
        s.add(kick(0.85, 120, 48, 0.22), b0, 0.30, 0, 0, 0.001, 'kick')
        s.add(kick(0.6, 120, 48, 0.22), b0 + 1.75, 0.22, 0, 0, 0.001, 'kick')
        s.add(kick(0.75, 120, 48, 0.22), b0 + 2.5, 0.27, 0, 0, 0.001, 'kick')
        for k in (1, 3):
            s.add(clap(0.75, seed=bar * 2 + k), b0 + k, 0.22, 0.05, 0.25, 0.002, 'clap')
            s.add(snare(0.5, 0.08, 210, seed=k), b0 + k, 0.10, 0.0, 0.15, 0.002, 'clap')
        for k in range(16):
            sw = 0.03 if k % 2 else 0
            open_ = k == 14
            s.add(hat(0.55 if k % 4 == 2 else 0.35, 0.15 if open_ else 0.025, seed=k),
                  b0 + k * 0.25 + sw, 0.11, 0.3, 0.04, 0.002, 'hat')
    melA = ('F#5:0.5 A5:0.5 r:0.5 F#5:0.5 E5:0.5 D5:0.5 r:1 | D5:0.5 F#5:0.5 r:0.5 B5:1 A5:0.5 F#5:1 | '
            'G5:0.5 F#5:0.5 E5:0.5 D5:0.5 B4:1 D5:1 | E5:1.5 F#5:0.5 E5:2 | '
            'F#5:0.5 A5:0.5 r:0.5 F#5:0.5 E5:0.5 D5:0.5 r:1 | D5:0.5 F#5:0.5 r:0.5 B5:1 C#6:0.5 D6:1 | '
            'B5:0.5 A5:0.5 G5:0.5 E5:0.5 D5:0.5 B4:0.5 D5:1 | E5:2 r:0.5 A4:0.5 C#5:0.5 E5:0.5')
    melB = ('B5:1 A5:0.5 F#5:0.5 D5:1 B4:1 | C#5:1 E5:0.5 F#5:0.5 A5:2 | '
            'G5:0.5 F#5:0.5 E5:0.5 D5:0.5 E5:1 G5:1 | A5:3 r:1 | '
            'B5:1 A5:0.5 F#5:0.5 D5:1 B4:1 | C#5:1 E5:0.5 F#5:0.5 A5:1 C#6:1 | '
            'B5:0.5 A5:0.5 G5:0.5 F#5:0.5 E5:1 C#5:1 | E5:2 A5:1 r:1')
    e1, _ = parse(melA, s.bar(8), 0.8)
    e2, _ = parse(melB, s.bar(16), 0.8)
    e3, _ = parse(melA, s.bar(24), 0.85)
    s.play(pluck, e1 + e2 + e3, 0.60, 0.15, 0.2, stem='lead', t60=0.7, bright=0.75, stacc=0.75)
    s.play(marimba, e1 + e3, 0.09, -0.15, 0.15, stem='marimba')
    s.play(flute, [(b, d * 0.9, m, v) for b, d, m, v in e2 + e3], 0.06, 0.25, 0.35, stem='whistle')
    # intro riff (bars 0-7) so the groove has a hook before the tune
    riff = 'r:3 A4:0.25 B4:0.25 D5:0.5 | r:4 | r:3 D5:0.25 E5:0.25 F#5:0.5 | r:2 E5:0.5 D5:0.5 B4:0.5 A4:0.5'
    for k in range(2):
        e, _ = parse(riff, s.bar(4 * k), 0.75)
        s.play(marimba, e, 0.20, -0.1, 0.15, stem='marimba')
    return s.render(make_ir(1.1, 0.01, seed=23), wet=0.5), s


# ============================================================================
# system -- 110 BPM, digital "booting up" synth/chip
# ============================================================================
def system():
    s = Song(110, 24, seed=104)
    A = ['Fmaj7', 'G6', 'Am7', 'Em7']
    B = ['Dm9', 'Fmaj7', 'Gsus', 'G']
    form = A * 4 + B * 2
    arpv = {'Fmaj7': 'F4 A4 C5 E5', 'G6': 'G4 B4 D5 E5', 'Am7': 'A4 C5 E5 G5', 'Em7': 'E4 G4 B4 D5',
            'Dm9': 'D4 F4 A4 E5', 'Gsus': 'G4 C5 D5 F5', 'G': 'G4 B4 D5 F#5'}
    padv = {'Fmaj7': 'F3 C4 E4 A4', 'G6': 'G3 D4 E4 B4', 'Am7': 'A3 E4 G4 C5', 'Em7': 'E3 B3 D4 G4',
            'Dm9': 'D3 A3 E4 F4', 'Gsus': 'G3 D4 F4 C5', 'G': 'G3 D4 F#4 B4'}
    roots = {'Fmaj7': 'F2', 'G6': 'G2', 'Am7': 'A2', 'Em7': 'E2', 'Dm9': 'D2', 'Gsus': 'G2', 'G': 'G2'}
    pat = [0, 1, 2, 3, 4, 3, 2, 1, 0, 2, 1, 3, 2, 4, 3, 5]
    dr = np.random.default_rng(55)
    for bar, c in enumerate(form):
        b0 = s.bar(bar)
        a = chord(arpv[c])
        a = a + [x + 12 for x in a]
        boot = bar < 8
        for i, k in enumerate(pat):
            vv = 0.75 if i % 4 == 0 else 0.5
            g = 0.10 * (0.55 + 0.45 * min(1, (bar + i / 16) / 4)) if boot else 0.10
            sig = chip(hz(a[k]), 0.2 * s.spb, vv, duty=0.125, rel=0.03)
            s.add(sig, b0 + i * 0.25, g, -0.4 if i % 2 else 0.4, 0.25, 0.0, 'arp')
            s.add(sig, b0 + i * 0.25 + 0.75, g * 0.35, 0.6 if i % 2 else -0.6, 0.3, 0.0, 'arp')   # dotted-8th echo
        for m in chord(padv[c]):
            s.add(pad(hz(m), 4 * s.spb, 0.6, att=0.4, rel=1.2, cutoff=1400 + 1600 * (not boot), detune=12,
                      seed=bar * 11 + int(m)), b0, 0.055, 0, 0.5, 0, 'pad')
        r = midi(roots[c])
        for k in range(8):
            s.add(bass(hz(r if k % 4 != 3 else r + 12), 0.4 * s.spb, 0.8 if k % 2 == 0 else 0.6, drive=1.3, bright=0.5),
                  b0 + k * 0.5, 0.12 if not boot else 0.09, 0, 0.02, 0.001, 'bass')
        # drums
        if boot:
            s.add(kick(0.7, 140, 45, 0.25), b0, 0.26, 0, 0, 0, 'kick')
            s.add(kick(0.5, 140, 45, 0.25), b0 + 2, 0.20, 0, 0, 0, 'kick')
            for k in range(8):
                s.add(hat(0.4, 0.02, seed=k), b0 + k * 0.5 + 0.5 * (k % 2 == 0) * 0, 0.09, 0.3, 0.05, 0, 'hat')
        else:
            for k in range(4):
                s.add(kick(0.85, 140, 45, 0.25), b0 + k, 0.28, 0, 0, 0, 'kick')
            for k in (1, 3):
                s.add(clap(0.7, seed=bar + k, tone=1.2), b0 + k, 0.18, 0, 0.25, 0, 'clap')
            for k in range(16):
                s.add(hat(0.55 if k % 2 else 0.3, 0.02, seed=k), b0 + k * 0.25, 0.10, 0.3, 0.04, 0, 'hat')
        # random data bleeps
        for k in range(16):
            if dr.random() < 0.22:
                f = hz(int(dr.choice([84, 86, 88, 91, 93, 96, 98, 100])))
                s.add(blip(f, 0.06, dr.uniform(0.4, 0.8)), b0 + k * 0.25, 0.035, dr.uniform(-0.8, 0.8), 0.4, 0, 'bleep')
    # boot-up runs at bars 0 and 16
    run = [midi(x) for x in 'C4 D4 E4 G4 A4 C5 D5 E5 G5 A5 C6 D6 E6 G6 A6 C7'.split()]
    for b0 in (s.bar(0), s.bar(16)):
        for i, m in enumerate(run):
            s.add(chip(hz(m), 0.1 * s.spb, 0.5 + 0.03 * i, duty=0.25), b0 + i * 0.125, 0.07, -0.6 + 0.08 * i, 0.35, 0, 'boot')
    # noise riser into the loop point
    n = int(2 * s.spb * SR)
    t = tt(n)
    rs = _nz(n, 3)
    rs = bp(rs, 800, 9000) * (t / t[-1]) ** 2
    s.add(rs, s.bar(23) + 2, 0.04, 0, 0.4, 0, 'riser')
    melA = ('A5:0.5 C6:0.5 E6:1 D6:0.5 C6:0.5 A5:1 | B5:0.5 D6:0.5 G6:1 E6:1 D6:1 | '
            'C6:0.5 E6:0.5 A6:1 G6:0.5 E6:0.5 C6:1 | B5:2 G5:1 B5:1 | '
            'A5:0.5 C6:0.5 E6:1 D6:0.5 C6:0.5 A5:1 | B5:0.5 D6:0.5 G6:1 A6:1 B6:1 | '
            'C7:1 B6:0.5 A6:0.5 G6:1 E6:1 | E6:4')
    melB = ('F5:1 A5:1 E6:2 | C6:1 A5:0.5 C6:0.5 E6:2 | D6:1 C6:0.5 D6:0.5 G6:2 | D6:2 B5:2 | '
            'F5:1 A5:1 E6:1 F6:1 | G6:1 E6:0.5 C6:0.5 A5:2 | C6:1 D6:1 F6:1 G6:1 | G6:4')
    e1, _ = parse(melA, s.bar(8), 0.8)
    e2, _ = parse(melB, s.bar(16), 0.8)
    s.play(chip, [(b, d * 0.9, m, v) for b, d, m, v in e1], 0.16, 0.1, 0.3, transpose=-12, stem='lead',
           duty=0.5, vib=12, rel=0.04)
    s.play(chip, [(b, d * 0.9, m, v) for b, d, m, v in e2], 0.15, 0.1, 0.3, transpose=-12, stem='lead',
           duty=0.25, vib=12, rel=0.04)
    s.play(bell, e2, 0.05, -0.3, 0.5, stem='bell', decay=0.8, ratio=2.0, bright=0.6)
    return s.render(make_ir(1.6, 0.02, seed=24), wet=0.55), s


# ============================================================================
# lxx_theme -- 124 BPM, C minor "CEO walks in"
# ============================================================================
def lxx_theme():
    s = Song(124, 32, seed=105)
    A = ['Cm', 'Cm', 'Ab', 'Ab', 'Fm', 'Fm', 'G', 'G']
    B = ['Ab', 'Eb', 'Bb', 'Fm', 'Ab', 'Eb', 'G', 'G']
    form = A + A + B + A
    roots = {'Cm': 'C2', 'Ab': 'Ab1', 'Fm': 'F1', 'G': 'G1', 'Eb': 'Eb2', 'Bb': 'Bb1'}
    stabv = {'Cm': 'C3 G3 C4 Eb4', 'Ab': 'Ab2 Eb3 Ab3 C4', 'Fm': 'F2 C3 F3 Ab3', 'G': 'G2 D3 G3 B3',
             'Eb': 'Eb3 G3 Bb3 Eb4', 'Bb': 'Bb2 F3 Bb3 D4'}
    hiv = {'Cm': 'G4 C5 Eb5', 'Ab': 'Ab4 C5 Eb5', 'Fm': 'Ab4 C5 F5', 'G': 'G4 B4 D5',
           'Eb': 'G4 Bb4 Eb5', 'Bb': 'F4 Bb4 D5'}
    ost = [0, 0, 12, 0, 0, 12, 0, 7, 0, 0, 12, 0, 7, 12, 7, 0]
    accents = {0, 3, 6, 10, 13}
    for bar, c in enumerate(form):
        b0 = s.bar(bar)
        sec = bar // 8
        r = midi(roots[c])
        for i, sm in enumerate(ost):
            v = 0.95 if i in accents else 0.6
            s.add(strings(hz(r + 12 + sm), 0.2 * s.spb, v, att=0.004, dec=0.06, sus=0.35, rel=0.06, cutoff=1800,
                          seed=i), b0 + i * 0.25, 0.20, -0.25, 0.15, 0.002, 'ostinato')
            if i in accents:
                s.add(strings(hz(r + sm), 0.2 * s.spb, v, att=0.004, dec=0.08, sus=0.3, rel=0.06, cutoff=900,
                              seed=i + 20), b0 + i * 0.25, 0.14, 0.2, 0.1, 0.002, 'ostinato')
        s.add(sub(hz(r) * 2, 3.8 * s.spb, 0.8, att=0.02, rel=0.2), b0, 0.10, 0, 0, 0, 'sub')
        # brass stabs
        hits = []
        if bar % 2 == 0:
            hits.append((0, 0.5, 0.95))
        if bar % 4 == 3:
            hits += [(2.5, 0.35, 0.85), (3.0, 0.7, 0.95)]
        if sec == 0 and bar % 2 == 1:
            hits.append((1.5, 0.35, 0.8))
        for o, d, v in hits:
            for j, m in enumerate(chord(stabv[c])):
                s.add(brass(hz(m), d * s.spb, v, rel=0.12, att=0.01), b0 + o, 0.075, -0.3 + 0.2 * j, 0.35, 0.002, 'brass')
        if sec == 2:
            for m in chord(hiv[c]):
                s.add(pad(hz(m), 4 * s.spb, 0.55, att=0.25, rel=0.8, cutoff=2600, detune=8, seed=bar * 5 + int(m)),
                      b0, 0.05, 0, 0.5, 0, 'hstrings')
        # drums
        s.add(kick(0.95, 150, 44, 0.28), b0, 0.34, 0, 0, 0.001, 'kick')
        s.add(kick(0.8, 150, 44, 0.28), b0 + 2, 0.30, 0, 0, 0.001, 'kick')
        if bar % 2 == 1:
            s.add(kick(0.7, 150, 44, 0.28), b0 + 2.75, 0.24, 0, 0, 0.001, 'kick')
        fill = bar % 8 == 7
        for k in (1, 3):
            if fill and k == 3:
                continue
            s.add(snare(0.9, 0.12, 200, seed=k, bright=1.2), b0 + k, 0.27 if sec else 0.18, 0.05, 0.25, 0.001, 'snare')
        if fill:
            for i, f in enumerate([220, 220, 165, 165, 120, 120, 90, 90]):
                s.add(tom(0.6 + 0.04 * i, f), b0 + 2 + i * 0.25, 0.20, 0.5 - 0.14 * i, 0.2, 0.001, 'toms')
        if bar % 8 == 0:
            s.add(crash(0.7, 1.2, seed=bar), b0, 0.09, -0.3, 0.3, 0, 'crash')
        for k in range(16):
            s.add(hat(0.6 if k % 2 == 0 else 0.35, 0.022, seed=k), b0 + k * 0.25, 0.09, 0.35, 0.04, 0.001, 'hat')
    melA = ('G4:1.5 C5:0.5 D5:1 Eb5:1 | D5:1.5 C5:0.5 G4:2 | Ab4:1.5 C5:0.5 Eb5:1 G5:1 | F5:3 Eb5:1 | '
            'F5:1.5 Ab5:0.5 G5:1 F5:1 | Eb5:1.5 D5:0.5 C5:2 | D5:1.5 Eb5:0.5 F5:1 G5:1 | B4:2 D5:2')
    melB = ('C5:1 Eb5:1 Ab5:2 | G5:1 Eb5:1 Bb4:2 | D5:1 F5:1 Bb5:2 | Ab5:1.5 G5:0.5 F5:2 | '
            'Eb5:1 Ab5:1 C6:2 | Bb5:1 G5:1 Eb5:2 | D5:1 G5:1 B5:1 D6:1 | C6:0.5 B5:0.5 Ab5:0.5 G5:0.5 F5:1 D5:1')
    e1, _ = parse(melA, s.bar(8), 0.85)
    e2, _ = parse(melB, s.bar(16), 0.85)
    e3, _ = parse(melA, s.bar(24), 0.9)
    s.play(brass, [(b, d * 0.92, m, v) for b, d, m, v in e1 + e3], 0.20, 0.1, 0.3, stem='brasslead', transpose=-12)
    s.play(brass, [(b, d * 0.92, m, v) for b, d, m, v in e1 + e3], 0.10, -0.1, 0.3, stem='brasslead')
    s.play(strings, e2, 0.15, 0.15, 0.4, stem='strlead', att=0.06, dec=0.4, sus=0.8, rel=0.25)
    s.play(strings, e3, 0.08, -0.2, 0.4, transpose=12, stem='strlead', att=0.05, dec=0.4, sus=0.8, rel=0.2)
    s.play(bell, e2, 0.04, -0.3, 0.5, transpose=12, stem='bell', decay=0.9, ratio=3.0, bright=0.5)
    return s.render(make_ir(1.7, 0.02, seed=25), wet=0.6), s


# ============================================================================
# office -- 105 BPM, minimal corporate pulse, A minor
# ============================================================================
def office():
    s = Song(105, 24, seed=106)
    prog = ['Am9', 'Am9', 'Fmaj7', 'Fmaj7', 'Cmaj7', 'Cmaj7', 'G6', 'G6']
    tones = {'Am9': 'A4 C5 E5 B5', 'Fmaj7': 'F4 A4 C5 E5', 'Cmaj7': 'C5 E5 G5 B5', 'G6': 'G4 B4 D5 E5'}
    epv = {'Am9': 'G3 B3 C4 E4', 'Fmaj7': 'E3 A3 C4 F4', 'Cmaj7': 'E3 G3 B3 D4', 'G6': 'D3 E3 G3 B3'}
    roots = {'Am9': 'A1', 'Fmaj7': 'F1', 'Cmaj7': 'C2', 'G6': 'G1'}
    pats = [[0, 2, 1, 3, 2, 0, 3, 1], [0, 2, 1, 3, 2, 0, 3, 1], [0, 3, 1, 2, 3, 1, 2, 0]]
    for bar in range(24):
        c = prog[bar % 8]
        b0 = s.bar(bar)
        sec = bar // 8
        tn = chord(tones[c])
        for i, k in enumerate(pats[sec]):
            if sec == 0 and bar < 2 and i % 2:
                continue
            s.add(mute_marimba(hz(tn[k]), 0.4, 0.7 if i % 4 == 0 else 0.5), b0 + i * 0.5, 0.36, -0.25, 0.2, 0.003, 'marimba')
        r = midi(roots[c]) + 12
        s.play(bass, [ev(b0, 1.4, [r], 0.7), ev(b0 + 2.5, 1.0, [r], 0.55)], 0.15, 0, 0.03,
               stem='bass', drive=1.0, bright=0.25)
        if sec >= 1 and bar % 2 == 0:
            for m in chord(epv[c]):
                s.add(epiano(hz(m), 7 * s.spb, 0.4), b0, 0.05, 0.25, 0.35, 0.005, 'epiano')
        # drums: soft hats always, kick/rim from section 2
        for k in range(8 if sec == 0 else 16):
            step = 0.5 if sec == 0 else 0.25
            s.add(hat(0.4 if (k * step) % 1 == 0.5 else 0.22, 0.018, seed=k), b0 + k * step, 0.09, 0.35, 0.05, 0.002, 'hat')
        s.add(kick(0.55, 100, 45, 0.22, click=0.05), b0, 0.20 if sec else 0.12, 0, 0, 0.001, 'kick')
        if sec >= 1:
            s.add(kick(0.45, 100, 45, 0.22, click=0.05), b0 + 2.5, 0.16, 0, 0, 0.001, 'kick')
            s.add(rim(0.45, 1500), b0 + 3, 0.07, -0.15, 0.2, 0.002, 'rim')
        if sec == 2:
            for k in range(8):
                s.add(shaker(0.3 + 0.15 * (k % 2), seed=k, length=0.06), b0 + k * 0.5 + 0.25, 0.06, -0.4, 0.05, 0.002, 'shaker')
    mel = 'E5:3 D5:1 | C5:2 B4:2 | C5:3 A4:1 | G4:4 | E5:2 G5:2 | E5:2 C5:2 | D5:3 B4:1 | A4:4'
    e, _ = parse(mel, s.bar(16), 0.6)
    s.play(epiano, e, 0.10, 0.1, 0.4, transpose=12, stem='eplead', decay=1.2)
    s.play(bell, e, 0.03, -0.2, 0.5, transpose=12, stem='bell', decay=0.9, ratio=2.0, bright=0.3)
    return s.render(make_ir(1.3, 0.015, seed=26), wet=0.55), s


# ============================================================================
# city_date -- 82 BPM lo-fi chill hop, F major
# ============================================================================
def city_date():
    s = Song(82, 20, seed=107)
    A = ['Gm9', 'C13', 'Fmaj9', 'Dm9']
    B = ['Bbmaj9', 'Am7', 'Gm9', 'C7sus']
    form = A + A + B + A + B
    rh = {'Gm9': 'Bb3 D4 F4 A4', 'C13': 'Bb3 E4 A4', 'Fmaj9': 'A3 C4 E4 G4', 'Dm9': 'F3 A3 C4 E4',
          'Bbmaj9': 'A3 D4 F4 C5', 'Am7': 'G3 C4 E4', 'C7sus': 'Bb3 D4 F4 G4'}
    roots = {'Gm9': ('G1', 'D2'), 'C13': ('C2', 'G1'), 'Fmaj9': ('F1', 'C2'), 'Dm9': ('D2', 'A1'),
             'Bbmaj9': ('Bb1', 'F2'), 'Am7': ('A1', 'E2'), 'C7sus': ('C2', 'G1')}
    for bar, c in enumerate(form):
        b0 = s.bar(bar)
        for o, d, v in [(0.06, 1.6, 0.55), (2.56, 1.1, 0.42)]:
            for j, m in enumerate(chord(rh[c])):
                s.add(epiano(hz(m), d * s.spb, v, rel=0.5), b0 + o + j * 0.015, 0.10, -0.2, 0.3, 0.008, 'rhodes')
        r, f5 = roots[c]
        s.play(bass, [ev(b0, 1.6, [midi(r) + 12], 0.8), ev(b0 + 2.5, 0.4, [midi(f5) + 12], 0.55),
                      ev(b0 + 3, 0.9, [midi(r) + 12], 0.65)], 0.18, 0, 0.02, stem='bass', drive=1.0, bright=0.2)
        # dusty boom-bap
        s.add(lp(kick(0.9, 100, 45, 0.3, click=0.1), 2500), b0, 0.32, 0, 0, 0.004, 'kick')
        s.add(lp(kick(0.65, 100, 45, 0.3, click=0.1), 2500), b0 + 1.75, 0.22, 0, 0, 0.004, 'kick')
        s.add(lp(kick(0.8, 100, 45, 0.3, click=0.1), 2500), b0 + 2.5, 0.28, 0, 0, 0.004, 'kick')
        for k in (1, 3):
            s.add(lp(snare(0.8, 0.16, 180, seed=k, bright=0.6), 3800), b0 + k + 0.02, 0.24, 0.05, 0.25, 0.004, 'snare')
        for k in range(8):
            sw = 0.09 if k % 2 else 0
            s.add(lp(hat(0.5 if k % 2 == 0 else 0.32, 0.03, seed=k), 7500), b0 + k * 0.5 + sw, 0.18, 0.3, 0.05, 0.006, 'hat')
    s.add(crackle_layer(s.L, seed=7), 0, 0.25, 0, 0, 0, 'crackle')
    melA = 'r:0.5 D5:0.5 F5:0.5 A5:1 G5:0.5 F5:1 | E5:1.5 D5:0.5 C5:2 | r:0.5 C5:0.5 E5:0.5 G5:0.5 A5:1 E5:1 | F5:2 D5:1 r:1'
    melB = 'D5:1 F5:0.5 A5:0.5 C6:2 | C5:1 E5:0.5 G5:0.5 B5:1 A5:1 | Bb5:1.5 A5:0.5 F5:1 D5:1 | E5:2 G5:1 r:1'
    lead = (parse(melA, s.bar(4), 0.6)[0] + parse(melB, s.bar(8), 0.6)[0] +
            parse(melA, s.bar(12), 0.65)[0] + parse(melB, s.bar(16), 0.65)[0])
    s.play(epiano, [(b + 0.03, d, m, v) for b, d, m, v in lead], 0.13, 0.2, 0.4, stem='lead', decay=1.4, jitter=0.01)
    s.play(bell, parse(melB, s.bar(16), 0.5)[0], 0.035, -0.3, 0.5, stem='bell', decay=1.0, ratio=2.0, bright=0.3)
    x = s.render(make_ir(1.6, 0.02, seed=27, dark=4500), wet=0.55)
    x = fft_shape(x, lambda f: 1 / np.sqrt(1 + (f / 9000) ** 4))   # tape-ish top roll-off, loop-safe
    return x, s


# ============================================================================
# lxx_soft -- 72 BPM, A major / F#m, celesta + music box over warm pad
# ============================================================================
def lxx_soft():
    s = Song(72, 16, seed=108)
    prog = ['F#m9', 'Dmaj7', 'Amaj7', ('Esus', 'E'), 'Bm9', 'Dmaj7', 'F#m7', ('Esus', 'E')]
    padv = {'F#m9': 'F#3 A3 C#4 G#4', 'Dmaj7': 'D3 F#3 A3 C#4', 'Amaj7': 'A2 E3 G#3 C#4',
            'Esus': 'E3 A3 B3', 'E': 'E3 G#3 B3', 'Bm9': 'B2 D3 F#3 C#4', 'F#m7': 'F#3 A3 C#4 E4'}
    roots = {'F#m9': 'F#1', 'Dmaj7': 'D2', 'Amaj7': 'A1', 'Esus': 'E2', 'E': 'E2', 'Bm9': 'B1', 'F#m7': 'F#1'}
    for bar in range(16):
        c = prog[bar % 8]
        b0 = s.bar(bar)
        halves = c if isinstance(c, tuple) else (c,)
        d = 4 / len(halves)
        for h, cn in enumerate(halves):
            for m in chord(padv[cn]):
                s.add(pad(hz(m), d * s.spb, 0.5, att=1.0, rel=2.0, cutoff=1000, nv=3, seed=bar * 13 + int(m)),
                      b0 + h * d, 0.075, 0, 0.6, 0, 'pad')
        r = midi(roots[halves[0]]) + 12
        s.add(piano(hz(r), 3.5 * s.spb, 0.45), b0, 0.20, -0.1, 0.4, 0.006, 'piano')
        s.add(piano(hz(r + 7), 1.5 * s.spb, 0.32), b0 + 2, 0.13, -0.1, 0.4, 0.006, 'piano')
        if bar >= 8:   # gentle piano broken chord in the second pass
            notes = chord(padv[halves[-1]])
            for i, k in enumerate([1, 2, 3, 2]):
                k = min(k, len(notes) - 1)
                s.add(piano(hz(notes[k] + 12), 1.2 * s.spb, 0.3), b0 + 1 + i * 0.75, 0.09, 0.15, 0.45, 0.01, 'piano')
    mel = ('C#6:1.5 B5:0.5 A5:1 F#5:1 | A5:2 E5:2 | E5:1 F#5:0.5 G#5:0.5 A5:1 C#6:1 | B5:3 r:1 | '
           'D6:1.5 C#6:0.5 B5:1 F#5:1 | A5:1.5 G#5:0.5 F#5:2 | C#5:1 F#5:1 A5:1 C#6:1 | B5:2 G#5:2')
    e1, _ = parse(mel, 0, 0.6)
    e2, _ = parse(mel, s.bar(8), 0.65)
    s.play(celesta, e1, 0.20, 0.15, 0.55, stem='celesta', decay=1.6, jitter=0.008)
    s.play(music_box, e2, 0.16, 0.25, 0.6, stem='mbox', decay=1.8, jitter=0.008)
    s.play(celesta, e2, 0.08, -0.2, 0.6, transpose=-12, stem='celesta', decay=1.4, jitter=0.008)
    return s.render(make_ir(3.2, 0.03, seed=28, dark=5000), wet=0.85), s


TRACKS = {'scam': scam, 'broke': broke, 'rider': rider, 'system': system,
          'lxx_theme': lxx_theme, 'office': office, 'city_date': city_date, 'lxx_soft': lxx_soft}

RMS_TARGET = {'scam': -20, 'broke': -18.5, 'rider': -17.5, 'system': -18,
              'lxx_theme': -17.5, 'office': -19, 'city_date': -18.5, 'lxx_soft': -19.5}
