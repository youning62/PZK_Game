"""Background music for the game.  Each function returns a seamless stereo loop."""
import numpy as np
from synth import *  # noqa


def ev(b, d, notes, v=0.7):
    return (b, d, chord(notes) if isinstance(notes, str) else notes, v)


# ============================================================================
# dream  -- 70 BPM, D major, maj7 shimmer
# ============================================================================
def dream():
    s = Song(70, 20, seed=11)
    P1 = [('D2', 'D3 A3 C#4 E4 F#4', 'D4 F#4 A4 C#5 E5 A5'),
          ('B1', 'B2 F#3 A3 C#4 D4', 'B3 D4 F#4 A4 C#5 F#5'),
          ('G1', 'G2 D3 F#3 A3 B3', 'G3 B3 D4 F#4 A4 D5'),
          ('A1', 'A2 E3 B3 C#4 E4', 'A3 C#4 E4 B4 C#5 E5')]
    P2 = [('G1', 'G2 D3 F#3 A3 B3', 'G3 B3 D4 F#4 A4 D5'),
          ('F#1', 'F#2 C#3 E3 A3 C#4', 'F#3 A3 C#4 E4 A4 C#5'),
          ('E1', 'E2 B2 D3 F#3 G3', 'E3 G3 B3 D4 F#4 B4'),
          ('A1', 'A2 E3 G3 B3 D4', 'A3 D4 E4 G4 B4 E5')]
    prog = P1 + P1 + P2 + P2 + P1
    arp_pat = [0, 2, 1, 3, 2, 4, 3, 5]
    for bar, (root, pad_v, arp) in enumerate(prog):
        b0 = s.bar(bar)
        for m in chord(pad_v):
            s.add(pad(hz(m), 4 * s.spb, 0.6, att=1.4, rel=2.6, cutoff=1300, seed=bar * 10 + int(m)),
                  b0, 0.10, 0, 0.55, 0, 'pad')
        s.add(sub(hz(root) * 2, 4 * s.spb, 0.8, att=0.6, rel=1.2), b0, 0.12, 0, 0.05, 0, 'sub')
        a = chord(arp)
        for i, k in enumerate(arp_pat):
            vv = 0.55 + 0.15 * (i % 2 == 0)
            s.add(bell(hz(a[k] + 12), 0.3, vv, decay=1.6, ratio=4.0, bright=0.6),
                  b0 + i * 0.5, 0.07, -0.45 if i % 2 else 0.45, 0.7, 0.006, 'bell')
    mel = ('F#5:2 E5:1 A5:1 | D5:2 C#5:1 B4:1 | D5:3 A4:1 | B4:2 C#5:1 E5:1 | '
           'F#5:2 A5:1 G5:1 | E5:3 C#5:1 | D5:2 F#5:1 B4:1 | E5:4 | '
           'B5:2 A5:1 F#5:1 | A5:2 E5:2 | G5:1.5 F#5:0.5 E5:1 D5:1 | E5:2 D5:2')
    e, _ = parse(mel, start=s.bar(4), vel=0.6)
    s.play(lead_soft, e, 0.11, 0.1, 0.8, stem='lead', att=0.25, rel=1.0, vib_cents=8)
    s.play(music_box, e, 0.035, -0.2, 0.9, transpose=12, stem='mbox')
    return s.render(make_ir(4.5, 0.04, seed=1, dark=6000), wet=0.9), s


# ============================================================================
# comedy -- 120 BPM, F major oom-pah pizzicato
# ============================================================================
CH_COM = {'F': ('F2', 'C2', 'A3 C4 F4'), 'C7': ('C2', 'G1', 'Bb3 C4 E4'),
          'F7': ('F2', 'C2', 'A3 Eb4 F4'), 'Bb': ('Bb1', 'F2', 'Bb3 D4 F4'),
          'G7': ('G1', 'D2', 'B3 D4 F4')}


def comedy():
    s = Song(120, 32, seed=22)
    A = ['F', 'F', 'C7', 'C7', 'F', 'F7', ('Bb', 'C7'), 'F']
    B = ['Bb', 'Bb', 'F', 'F', 'G7', 'G7', 'C7', 'C7']
    form = A + A + B + A
    for bar, c in enumerate(form):
        b0 = s.bar(bar)
        halves = c if isinstance(c, tuple) else (c, c)
        pause = (bar == 23)          # comic pause at end of B
        for h, cn in enumerate(halves):
            root, fifth, vo = CH_COM[cn]
            bb = b0 + 2 * h
            s.add(tuba(hz(root if h == 0 or halves[0] != halves[1] else fifth), 0.55 * s.spb, 0.85),
                  bb, 0.32, 0, 0.08, 0.003, 'tuba')
            if pause and h == 1:
                continue
            for m in chord(vo):
                s.add(pluck(hz(m), 0.5 * s.spb, 0.6, t60=0.5, bright=0.6, stacc=0.5),
                      bb + 1, 0.22, 0.25, 0.15, 0.004, 'pizz')
        # percussion
        if not pause:
            s.add(kick(0.5, 110, 50, 0.2), b0, 0.25, 0, 0.0, 0, 'kick')
            for k in (1, 3):
                s.add(woodblock(0.5, 1250), b0 + k, 0.14, -0.3, 0.12, 0.003, 'wood')
            for k in range(8):
                s.add(shaker(0.35 + 0.2 * (k % 2), seed=k), b0 + k * 0.5, 0.07, 0.35, 0.05, 0.004, 'shaker')
        else:
            s.add(kick(0.5, 110, 50, 0.2), b0, 0.25, 0, 0.0, 0, 'kick')
    melA = ('C5:0.5 r:0.5 A4:0.5 r:0.5 F4:0.5 A4:0.5 C5:1 | D5:0.5 C5:0.5 A4:0.5 F4:0.5 G4:1 r:1 | '
            'E4:0.5 G4:0.5 Bb4:0.5 r:0.5 C5:0.5 Bb4:0.5 G4:1 | E4:0.5 F4:0.5 G4:0.5 E4:0.5 C4:1 r:1 | '
            'C5:0.5 r:0.5 A4:0.5 r:0.5 F4:0.5 A4:0.5 C5:1 | Eb5:0.5 D5:0.5 C5:0.5 A4:0.5 F4:1 r:1 | '
            'D5:0.5 F5:0.5 D5:0.5 Bb4:0.5 E5:0.5 G5:0.5 E5:0.5 C5:0.5 | F5:0.5 r:0.5 C5:0.5 r:0.5 F4:1 r:1')
    melB = ('F4:0.5 Bb4:0.5 D5:0.5 F5:0.5 D5:1 Bb4:1 | C5:0.5 D5:0.5 Eb5:0.5 D5:0.5 C5:0.5 Bb4:0.5 G4:1 | '
            'A4:0.5 C5:0.5 F5:0.5 C5:0.5 A4:1 r:1 | G4:0.5 A4:0.5 Bb4:0.5 A4:0.5 G4:0.5 F4:0.5 E4:0.5 F4:0.5 | '
            'D5:0.5 r:0.5 B4:0.5 r:0.5 G4:0.5 B4:0.5 D5:0.5 F5:0.5 | E5:0.5 D5:0.5 B4:0.5 G4:0.5 A4:1 B4:1 | '
            'C5:0.5 r:0.5 C5:0.5 r:0.5 Bb4:0.5 r:0.5 Bb4:0.5 r:0.5 | G4:0.25 A4:0.25 Bb4:0.25 B4:0.25 C5:1 r:2')
    e1, _ = parse(melA, s.bar(0), 0.75)
    e2, _ = parse(melA, s.bar(8), 0.8)
    e3, _ = parse(melB, s.bar(16), 0.8)
    e4, _ = parse(melA, s.bar(24), 0.8)
    s.play(marimba, e1 + e4, 0.30, -0.15, 0.15, transpose=12, stem='marimba')
    s.play(pluck, e2 + e4, 0.20, 0.1, 0.15, stem='pizzlead', t60=0.6, bright=0.7, stacc=0.6)
    s.play(bassoon, [(b, d * 0.8, m, v) for b, d, m, v in e3], 0.55, -0.1, 0.15, stem='bassoon')
    s.play(marimba, e3, 0.18, 0.2, 0.15, transpose=12, stem='marimba')
    return s.render(make_ir(1.2, 0.01, seed=2), wet=0.6), s


# ============================================================================
# heroine -- 95 BPM, A minor, cool & elegant
# ============================================================================
def heroine():
    s = Song(95, 24, seed=33)
    prog = [('A1', 'E2', 'G3 B3 C4 E4'), ('A1', 'E2', 'G3 B3 C4 E4'),
            ('F1', 'C2', 'G3 A3 C4 E4'), ('F1', 'C2', 'G3 A3 C4 E4'),
            ('D2', 'A1', 'F3 A3 C4 E4'), ('G1', 'D2', 'F3 B3 E4'),
            ('C2', 'G1', 'E3 G3 B3 D4'), ('E1', 'B1', 'D3 A3 B3 E4')]
    comp = [(0, 1.4, 0.7), (1.5, 0.9, 0.55), (3, 0.9, 0.6)]
    for bar in range(24):
        root, fifth, vo = prog[bar % 8]
        b0 = s.bar(bar)
        phrase = bar // 8
        vo_c = chord(vo)
        if bar % 8 == 7:   # E7sus -> E7 resolution on beat 3
            vo2 = chord('D3 G#3 B3 E4')
        for (o, d, v) in comp:
            notes = vo2 if (bar % 8 == 7 and o >= 2) else vo_c
            for m in notes:
                s.add(epiano(hz(m), d * s.spb, v), b0 + o, 0.09, -0.2, 0.25, 0.006, 'epiano')
        s.play(bass, [ev(b0, 1.4, [midi(root) + 12], 0.85), ev(b0 + 1.5, 0.5, [midi(root) + 12], 0.6),
                      ev(b0 + 2, 0.9, [midi(fifth) + 12], 0.75), ev(b0 + 3.5, 0.45, [midi(root) + 24], 0.6)],
               0.17, 0, 0.03, stem='bass', drive=1.2, bright=0.6)
        # beat (lighter in phrase 1)
        bg = 0.7 if phrase == 0 else 1.0
        s.add(kick(0.8, 120, 46, 0.3), b0, 0.30 * bg, 0, 0, 0.002, 'kick')
        s.add(kick(0.6, 120, 46, 0.3), b0 + 2.5, 0.30 * bg, 0, 0, 0.002, 'kick')
        for k in (1, 3):
            s.add(snare(0.6, 0.1, 210, seed=k, bright=0.7), b0 + k, 0.30 * bg, 0.05, 0.25, 0.003, 'snare')
        for k in range(8):
            sw = 0.08 if k % 2 else 0
            s.add(hat(0.5 if k % 2 else 0.7, 0.03, seed=k), b0 + k * 0.5 + sw, 0.16 * bg, 0.3, 0.05, 0.003, 'hat')
    mel = ('E5:1.5 D5:0.5 C5:1 B4:1 | A4:1.5 B4:0.5 C5:1 E5:1 | A5:2 G5:1 E5:1 | F5:1.5 E5:0.5 C5:2 | '
           'D5:1 E5:1 F5:1 A5:1 | G5:1.5 F5:0.5 E5:1 D5:1 | E5:1.5 D5:0.5 B4:1 C5:1 | A4:1 B4:1 G#4:2')
    e2, _ = parse(mel, s.bar(8), 0.75)
    e3, _ = parse(mel, s.bar(16), 0.85)
    s.play(lead_soft, e2 + e3, 0.20, 0.1, 0.35, stem='lead', att=0.03, rel=0.3)
    s.play(bell, e3, 0.05, -0.3, 0.5, transpose=12, stem='bell', decay=1.2, ratio=3.0, bright=0.5)
    # mysterious answering motif in phrase 1
    hook, _ = parse('r:2 E5:0.5 A5:0.5 B5:0.5 C6:0.5 | r:4 | r:2 E5:0.5 A5:0.5 B5:0.5 G5:0.5 | r:4 |'
                    ' r:2 F5:0.5 A5:0.5 C6:0.5 B5:0.5 | r:4 | r:2 E5:0.5 G5:0.5 B5:0.5 G#5:0.5 | r:4', 0, 0.6)
    s.play(celesta, hook, 0.09, 0.35, 0.6, stem='celesta')
    return s.render(make_ir(1.9, 0.02, seed=3), wet=0.7), s


# ============================================================================
# awkward -- 80 BPM, sparse plucks, bassoon, ticking clock
# ============================================================================
def awkward():
    s = Song(80, 20, seed=44)
    A_pl = ('E5:0.5 r:1 E5:0.25 r:0.25 G5:0.5 r:1.5 | F5:0.5 r:1 F5:0.25 r:0.25 Ab5:0.5 r:1.5 | '
            'G5:0.5 E5:0.5 r:1 C5:0.5 r:1.5 | ')
    A_end = 'B4:0.25 C5:0.25 D5:0.5 r:2 G4:0.5 r:0.5'
    A2_end = 'B4:0.25 C5:0.25 D5:0.5 r:2 F5:0.25 E5:0.25 r:0.5'
    A_bn = ('C3:0.5 r:1.5 G2:0.5 r:1.5 | Db3:0.5 r:1.5 Ab2:0.5 r:1.5 | C3:0.5 r:1.5 G2:0.5 r:1.5 | '
            'G2:0.5 r:0.5 B2:0.5 r:0.5')
    P_pl = 'E5:0.25 r:3.75 | r:4 | r:4 | r:3 G5:0.5 r:0.5'
    B_pl = ('A5:0.5 r:1 A5:0.25 r:0.25 C6:0.5 r:1.5 | Ab5:0.5 r:1 Ab5:0.25 r:0.25 C6:0.5 r:1.5 | '
            'G5:0.5 E5:0.5 r:1 C5:0.5 r:1.5 | D5:0.25 r:0.75 D5:0.25 r:0.75 D5:0.25 r:1.75')
    B_bn = 'F2:0.5 r:1.5 C3:0.5 r:1.5 | F2:0.5 r:1.5 Ab2:0.5 r:1.5 | C3:0.5 r:1.5 G2:0.5 r:1.5'
    pl, bn, qbn = [], [], []
    for ph, kind in enumerate(['A', 'A2', 'P', 'B', 'A']):
        b0 = s.bar(ph * 4)
        if kind in ('A', 'A2'):
            pl += parse(A_pl + (A_end if kind == 'A' else A2_end), b0, 0.7)[0]
            bn += parse(A_bn, b0, 0.8)[0]
            qbn.append(ev(b0 + 14, 1.0, 'D3', 0.8))            # questioning "?" bend up
            for bar, vo in enumerate(['E4 G4', 'F4 Ab4', 'E4 G4', 'F4 B4']):
                s.play(pluck, [ev(b0 + 4 * bar, 1, vo, 0.45)], 0.10, -0.35, 0.3, stem='chord', t60=0.7, bright=0.4)
        elif kind == 'P':
            pl += parse(P_pl, b0, 0.65)[0]
            s.add(bassoon(hz('C3'), 2 * s.spb, 0.8, bend=-150, wobble=25), b0 + 8, 0.22, -0.1, 0.25, 0, 'bassoon')
        else:
            pl += parse(B_pl, b0, 0.7)[0]
            bn += parse(B_bn, b0, 0.8)[0]
            s.add(bassoon(hz('G2'), 1.2 * s.spb, 0.8, wobble=40), b0 + 12, 0.22, -0.1, 0.25, 0, 'bassoon')
            for bar, vo in enumerate(['A4 C5', 'Ab4 C5', 'E4 G4', 'F4 B4']):
                s.play(pluck, [ev(b0 + 4 * bar, 1, vo, 0.45)], 0.10, -0.35, 0.3, stem='chord', t60=0.7, bright=0.4)
    s.play(pluck, pl, 0.5, 0.2, 0.3, stem='pluck', t60=0.9, bright=0.55, stacc=0.9)
    s.play(bassoon, bn, 0.14, -0.1, 0.25, stem='bassoon', wobble=8)
    for e in qbn:
        s.add(bassoon(hz(e[2][0]), e[1] * s.spb, 0.8, bend=120), e[0], 0.2, -0.1, 0.25, 0, 'bassoon')
    for b in range(20 * 4):           # tick-tock clock
        s.add(woodblock(0.5, 2200 if b % 2 == 0 else 1700), b, 0.10, 0.5, 0.1, 0.0, 'clock')
    return s.render(make_ir(1.3, 0.015, seed=4), wet=0.6), s


# ============================================================================
# dinner -- 100 BPM bossa nova in F
# ============================================================================
CH_DIN = {'Fmaj9': ('F2', 'C3', 'A3 C4 E4 G4'), 'Gm9': ('G2', 'D3', 'Bb3 D4 F4 A4'),
          'C13': ('C2', 'G2', 'Bb3 E4 A4'), 'Am7': ('A2', 'E2', 'G3 C4 E4'),
          'D7b9': ('D2', 'A2', 'F#3 C4 Eb4'), 'C7sus': ('C2', 'G2', 'Bb3 D4 F4 G4'),
          'Bbmaj7': ('Bb1', 'F2', 'A3 D4 F4'), 'Bbm6': ('Bb1', 'F2', 'G3 Db4 F4'),
          'Abdim7': ('Ab2', 'D2', 'Ab3 B3 D4 F4')}


def dinner():
    s = Song(100, 24, seed=55)
    A = ['Fmaj9', 'Fmaj9', 'Gm9', 'C13', 'Am7', 'D7b9', 'Gm9', 'C7sus']
    B = ['Bbmaj7', 'Bbm6', 'Am7', 'Abdim7', 'Gm9', 'C13', 'Fmaj9', 'C7sus']
    form = A + A + B
    clave = [0, 1.5, 3, 4 + 1, 4 + 2.5]   # 2-bar bossa comping pattern (beats)
    for bar, c in enumerate(form):
        root, fifth, vo = CH_DIN[c]
        b0 = s.bar(bar)
        # bass: root (dotted quarter) + fifth
        s.play(bass, [ev(b0, 1.4, [midi(root) + 12], 0.8), ev(b0 + 1.5, 0.45, [midi(fifth) + 12], 0.45),
                      ev(b0 + 2, 1.4, [midi(fifth) + 12], 0.75), ev(b0 + 3.5, 0.45, [midi(root) + 12], 0.45)],
               0.14, 0, 0.05, stem='bass', drive=1.0, bright=0.35)
        # nylon comping
        for o in clave:
            bb = (bar // 2) * 8 + o
            if s.bar(bar) <= bb < s.bar(bar) + 4:
                for j, m in enumerate(chord(vo)):
                    s.add(nylon(hz(m), 0.45 * s.spb, 0.55), bb + j * 0.012, 0.32, -0.3, 0.2, 0.003, 'nylon')
        # thumb on 1 & 3 on the guitar too
        s.add(nylon(hz(midi(root) + 12), 0.9 * s.spb, 0.6), b0, 0.09, -0.25, 0.15, 0.003, 'nylon')
        # percussion: shaker 16ths, rim on clave, brush swish on 2 & 4
        for k in range(16):
            acc = 0.5 if k % 4 == 2 else (0.35 if k % 2 else 0.25)
            s.add(shaker(acc, seed=k, length=0.07), b0 + k * 0.25, 0.10, 0.35, 0.08, 0.003, 'shaker')
        for o in clave:
            bb = (bar // 2) * 8 + o
            if s.bar(bar) <= bb < s.bar(bar) + 4:
                s.add(rim(0.45, 1500), bb, 0.08, -0.15, 0.15, 0.003, 'rim')
        for k in (1, 3):
            s.add(brush(0.5, seed=k), b0 + k - 0.05, 0.07, 0.1, 0.2, 0.003, 'brush')
        s.add(kick(0.5, 90, 45, 0.2, click=0.05), b0, 0.18, 0, 0, 0.002, 'kick')
        s.add(kick(0.4, 90, 45, 0.2, click=0.05), b0 + 2, 0.15, 0, 0, 0.002, 'kick')
    melA = ('E5:1.5 D5:0.5 C5:1 A4:1 | G4:1.5 A4:0.5 r:2 | A4:1 Bb4:1 D5:1.5 F5:0.5 | E5:3 r:1 | '
            'E5:1.5 D5:0.5 C5:1 G4:1 | F#4:1.5 A4:0.5 Eb5:2 | D5:1.5 C5:0.5 Bb4:1 A4:1 | G4:3 r:1')
    melB = ('D5:1.5 C5:0.5 D5:1 F5:1 | Db5:2 F5:1 G5:1 | E5:1.5 C5:0.5 A4:2 | B4:1.5 D5:0.5 F5:2 | '
            'A5:1.5 G5:0.5 F5:1 D5:1 | E5:1 F5:0.5 G5:0.5 A5:2 | G5:1.5 E5:0.5 C5:2 | G4:1 Bb4:1 C5:1 D5:1')
    e1, _ = parse(melA, 0, 0.7)
    e2, _ = parse(melA, s.bar(8), 0.7)
    e3, _ = parse(melB, s.bar(16), 0.75)
    s.play(flute, e1 + e3, 0.14, 0.15, 0.4, stem='flute')
    s.play(epiano, e2, 0.13, 0.15, 0.35, stem='vibes', decay=1.2)
    s.play(music_box, e2, 0.03, 0.3, 0.5, transpose=12, stem='vibes_hi', decay=1.0)
    return s.render(make_ir(1.8, 0.02, seed=5), wet=0.7), s


# ============================================================================
# tender -- 66 BPM, C major soft piano
# ============================================================================
def tender():
    s = Song(66, 16, seed=66)
    lh = {'Cmaj7': 'C3 G3 B3 E4', 'Am7': 'A2 E3 G3 C4', 'Fmaj7': 'F2 C3 E3 A3',
          'Gsus': 'G2 D3 G3 C4', 'G': 'G2 D3 G3 B3', 'Em7': 'E2 B2 D3 G3', 'Dm9': 'D2 A2 E3 F3',
          'G7sus': 'G2 D3 F3 C4', 'G7': 'G2 D3 F3 B3', 'C7': 'C3 G3 Bb3 E4', 'Fm6': 'F2 C3 D3 Ab3'}
    prog = ['Cmaj7', 'Am7', 'Fmaj7', ('Gsus', 'G'), 'Em7', 'Am7', 'Dm9', ('G7sus', 'G'),
            'Cmaj7', 'Em7', 'Am7', 'C7', 'Fmaj7', 'Fm6', 'Dm9', ('G7sus', 'G7')]
    pat = [0, 1, 2, 3, 2, 1, 2, 3]
    for bar, c in enumerate(prog):
        b0 = s.bar(bar)
        halves = c if isinstance(c, tuple) else (c, c)
        for i, k in enumerate(pat):
            cn = halves[i // 4]
            notes = chord(lh[cn])
            vv = 0.55 if i == 0 else 0.38
            hold = (4 - (i % 4) * 0.5) if i % 4 == 0 else 1.2
            s.add(piano(hz(notes[k]), hold * s.spb, vv), b0 + i * 0.5, 0.15, -0.2 + 0.1 * k, 0.35, 0.008, 'lh')
        for h, cn in enumerate(dict.fromkeys(halves)):
            d = 4 if len(set(halves)) == 1 else 2
            for m in chord(lh[cn])[1:]:
                s.add(pad(hz(m + 12), d * s.spb, 0.5, att=0.9, rel=1.8, cutoff=900, nv=2, seed=bar * 7 + int(m)),
                      b0 + 2 * h, 0.07, 0, 0.5, 0, 'pad')
    mel = ('E5:1.5 D5:0.5 E5:1 G5:1 | C5:2.5 B4:0.5 A4:1 | A4:1.5 G4:0.5 A4:1 C5:1 | D5:3 r:1 | '
           'B4:1.5 C5:0.5 D5:1 E5:1 | G5:2 E5:1 C5:1 | F5:1.5 E5:0.5 D5:1 A4:1 | C5:2 B4:2 | '
           'G5:1.5 F5:0.5 E5:1 D5:1 | E5:2 B4:1 D5:1 | C5:1.5 B4:0.5 A4:1 E5:1 | G5:2 E5:1 Bb4:1 | '
           'A5:2.5 G5:0.5 F5:1 | Ab5:2 F5:1 D5:1 | E5:1.5 F5:0.5 E5:1 D5:1 | D5:2 B4:2')
    e, _ = parse(mel, 0, 0.75)
    s.play(piano, e, 0.30, 0.15, 0.4, stem='rh', jitter=0.01)
    return s.render(make_ir(2.6, 0.025, seed=6, dark=4500), wet=0.75), s


# ============================================================================
# delivery -- 150 BPM, E minor comic hustle
# ============================================================================
def delivery():
    s = Song(150, 40, seed=77)
    A = ['Em', 'Em', 'C', 'D', 'Em', 'Em', 'C', 'B7']
    B = ['Am', 'Am', 'Em', 'Em', 'C', 'D', 'B7', 'B7']
    roots = {'Em': 'E2', 'C': 'C2', 'D': 'D2', 'B7': 'B1', 'Am': 'A1'}
    stabs = {'Em': 'E4 G4 B4', 'C': 'E4 G4 C5', 'D': 'F#4 A4 D5', 'B7': 'D#4 A4 B4', 'Am': 'E4 A4 C5'}
    form = A + A + B + A + B
    for bar, c in enumerate(form):
        b0 = s.bar(bar)
        r = midi(roots[c])
        bl = [ev(b0 + k * 0.5, 0.4, [r + (12 if k % 2 else 0)], 0.9 if k % 2 == 0 else 0.7) for k in range(8)]
        s.play(bass, bl, 0.22, 0, 0.02, stem='bass', drive=2.0, bright=1.0)
        for k in (0.5, 1.5, 2.5, 3.5):
            for m in chord(stabs[c]):
                s.add(organ(hz(m), 0.22 * s.spb, 0.6), b0 + k, 0.07, -0.3, 0.15, 0.002, 'stab')
        fill = (bar % 8 == 7)
        s.add(kick(0.9, 150, 50, 0.22), b0, 0.33, 0, 0, 0.001, 'kick')
        s.add(kick(0.8, 150, 50, 0.22), b0 + 2, 0.33, 0, 0, 0.001, 'kick')
        s.add(kick(0.6, 150, 50, 0.22), b0 + 2.5, 0.25, 0, 0, 0.001, 'kick')
        s.add(snare(0.8, 0.12, 200, seed=1), b0 + 1, 0.22, 0.05, 0.15, 0.002, 'snare')
        if fill:
            for k in range(6):
                s.add(snare(0.4 + 0.1 * k, 0.09, 220, seed=k), b0 + 2.5 + k * 0.25, 0.17, -0.2 + 0.08 * k, 0.15, 0.002, 'snare')
        else:
            s.add(snare(0.8, 0.12, 200, seed=2), b0 + 3, 0.22, 0.05, 0.15, 0.002, 'snare')
        for k in range(8):
            open_ = (k % 2 == 1) and (k == 7)
            s.add(hat(0.6 if k % 2 else 0.45, 0.12 if open_ else 0.03, seed=k), b0 + k * 0.5, 0.13, 0.3, 0.05, 0.002, 'hat')
    melA = ('E5:0.5 r:0.5 E5:0.5 G5:0.5 r:0.5 E5:0.5 B4:1 | E5:0.5 F#5:0.5 G5:0.5 A5:0.5 B5:0.5 r:0.5 G5:1 | '
            'C6:0.5 r:0.5 B5:0.5 A5:0.5 G5:0.5 E5:0.5 C5:1 | D5:0.5 F#5:0.5 A5:0.5 F#5:0.5 D5:1 r:1 | '
            'E5:0.5 r:0.5 E5:0.5 G5:0.5 r:0.5 E5:0.5 B4:1 | B5:0.5 A5:0.5 G5:0.5 F#5:0.5 E5:0.5 r:0.5 B4:1 | '
            'C5:0.5 E5:0.5 G5:0.5 C6:0.5 B5:0.5 A5:0.5 G5:0.5 E5:0.5 | D#5:0.5 r:0.5 F#5:0.5 r:0.5 A5:0.5 G5:0.5 F#5:0.5 D#5:0.5')
    melB = ('A5:1 r:0.5 A5:0.5 G5:0.5 E5:0.5 C5:1 | E5:0.5 D5:0.5 C5:0.5 B4:0.5 A4:1 r:1 | '
            'G5:1 r:0.5 G5:0.5 F#5:0.5 E5:0.5 B4:1 | E5:0.5 F#5:0.5 G5:0.5 B5:0.5 E6:1 r:1 | '
            'E6:0.5 D6:0.5 C6:0.5 B5:0.5 A5:0.5 G5:0.5 E5:1 | F#5:0.5 G5:0.5 A5:0.5 B5:0.5 C6:0.5 B5:0.5 A5:1 | '
            'B5:0.5 r:0.5 A5:0.5 r:0.5 F#5:0.5 r:0.5 D#5:0.5 r:0.5 | B4:0.25 C#5:0.25 D#5:0.25 E5:0.25 F#5:0.5 A5:0.5 B5:1 r:1')
    lead = []
    for ph, (m, b) in enumerate([(melA, 8), (melB, 16), (melA, 24), (melB, 32)]):
        lead += parse(m, s.bar(b), 0.8)[0]
    stac = [(b, d * 0.7, m, v) for b, d, m, v in lead]
    s.play(square_lead, stac, 0.18, 0.15, 0.15, stem='lead')
    s.play(marimba, parse(melA, s.bar(24), 0.8)[0], 0.20, -0.25, 0.1, transpose=-12, stem='marimba')
    return s.render(make_ir(1.0, 0.01, seed=7), wet=0.5), s


# ============================================================================
# tension -- 90 BPM, D minor comic suspense
# ============================================================================
def tension():
    s = Song(90, 24, seed=88)
    prog = [('D2', 'D3 F3 A3'), ('D2', 'D3 F3 A3'), ('Bb1', 'D3 F3 Bb3'), ('A1', 'C#3 E3 A3'),
            ('D2', 'D3 F3 A3'), ('D2', 'D3 F3 A3'), ('Eb2', 'Eb3 G3 Bb3'), ('A1', 'C#3 G3 A3')]
    for bar in range(24):
        root, vo = prog[bar % 8]
        b0 = s.bar(bar)
        ph = bar // 8
        r = midi(root)
        for k in range(8):
            s.add(bass(hz(r), 0.3 * s.spb, 0.75 if k % 2 == 0 else 0.5, drive=1.0, bright=0.25),
                  b0 + k * 0.5, 0.20, 0, 0.05, 0.002, 'pulse')
        s.add(kick(0.6, 80, 40, 0.3, click=0.0), b0, 0.25, 0, 0, 0, 'kick')
        for k in range(16):
            acc = 0.7 if k % 4 == 0 else 0.35
            s.add(hat(acc, 0.02, seed=k), b0 + k * 0.25, 0.15, 0.4 if k % 2 else -0.4, 0.1, 0.001, 'tick')
        if ph >= 1:
            for k in (1, 3):
                s.add(rim(0.5, 1400), b0 + k, 0.08, 0.2, 0.2, 0.002, 'rim')
        if ph == 2 or ph == 0:
            for m in chord(vo):
                s.add(pad(hz(m), 4 * s.spb, 0.5, att=0.8, rel=1.5, cutoff=900 if ph == 0 else 1400,
                          seed=bar * 5 + int(m)), b0, 0.05 if ph == 0 else 0.06, 0, 0.4, 0, 'pad')
    motif = ('D5:0.5 r:0.5 E5:0.5 r:0.5 F5:0.5 r:0.5 G#5:1 | A5:1 r:3 | '
             'D5:0.5 r:0.5 F5:0.5 r:0.5 Bb5:0.5 r:0.5 A5:1 | E5:1 C#5:1 r:2 | '
             'D5:0.5 r:0.5 E5:0.5 r:0.5 F5:0.5 r:0.5 G#5:1 | A5:0.5 Bb5:0.5 B5:0.5 C6:0.5 C#6:1 r:1 | '
             'Eb5:0.5 r:0.5 G5:0.5 r:0.5 Bb5:0.5 r:0.5 G5:1 | A5:0.5 r:0.5 G5:0.5 r:0.5 E5:0.5 C#5:0.5 A4:1')
    e2, _ = parse(motif, s.bar(8), 0.75)
    e3, _ = parse(motif, s.bar(16), 0.8)
    s.play(celesta, e2 + e3, 0.16, 0.2, 0.35, stem='celesta')
    s.play(pluck, e3, 0.25, -0.3, 0.25, transpose=-12, stem='pizz', t60=0.5, bright=0.5, stacc=0.6)
    for b0 in (s.bar(8), s.bar(16)):
        s.add(bassoon(hz('D3'), 0.5 * s.spb, 0.8), b0 + 4 + 2, 0.4, -0.15, 0.2, 0, 'bassoon')
        s.add(bassoon(hz('C#3'), 1.0 * s.spb, 0.8, bend=-60), b0 + 4 + 2.5, 0.4, -0.15, 0.2, 0, 'bassoon')
        s.add(bassoon(hz('A2'), 1.2 * s.spb, 0.8, bend=200), b0 + 12 + 2.3, 0.4, -0.15, 0.2, 0, 'bassoon')
    return s.render(make_ir(1.6, 0.02, seed=8), wet=0.6), s


TRACKS = {'dream': dream, 'comedy': comedy, 'heroine': heroine, 'awkward': awkward,
          'dinner': dinner, 'tender': tender, 'delivery': delivery, 'tension': tension}

# per-track loudness targets (dBFS RMS); sparse/soft tracks a touch lower
RMS_TARGET = {'dream': -19, 'comedy': -18, 'heroine': -18, 'awkward': -20,
              'dinner': -18.5, 'tender': -19.5, 'delivery': -17.5, 'tension': -18.5}
