"""Regenerate every procedural music / SFX asset of the game.

Usage (needs numpy, scipy and soundfile -- soundfile's wheel bundles libsndfile
with Ogg Vorbis support):

    python3 -m venv /tmp/pzk-audio-venv --system-site-packages
    /tmp/pzk-audio-venv/bin/pip install soundfile
    /tmp/pzk-audio-venv/bin/python tools/audio/generate_all.py            # everything
    /tmp/pzk-audio-venv/bin/python tools/audio/generate_all.py dream boing # just some

Tracks / SFX live in music.py + sfx.py (chapter 1) and music2.py + sfx2.py
(scam -> broke rider -> system -> LXX arc); all are merged below.

Writes game/audio/bgm/*.ogg (seamless 44.1 kHz stereo loops) and
game/audio/sfx/*.ogg, then re-reads every file and prints a verification table.
"""
import os
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import synth as S  # noqa: E402
import music  # noqa: E402
import sfx  # noqa: E402
import music2  # noqa: E402
import sfx2  # noqa: E402

GAME = os.path.normpath(os.path.join(HERE, '..', '..', 'game'))
BGM = os.path.join(GAME, 'audio', 'bgm')
SFXD = os.path.join(GAME, 'audio', 'sfx')
LOOP_SFX = {'waves', 'wind'} | sfx2.LOOP

TRACKS = {**music.TRACKS, **music2.TRACKS}
RMS_TARGET = {**music.RMS_TARGET, **music2.RMS_TARGET}
SFX = {**sfx.SFX, **sfx2.SFX}


def build(names):
    os.makedirs(BGM, exist_ok=True)
    os.makedirs(SFXD, exist_ok=True)
    for name, fn in TRACKS.items():
        if names and name not in names:
            continue
        t = time.time()
        x, song = fn()
        y = S.master_loop(x, peak_db=-3.0, rms_db=RMS_TARGET[name])
        S.write_ogg(os.path.join(BGM, name + '.ogg'), y)
        print(f'bgm/{name}.ogg  {time.time() - t:.1f}s  stems(dB of energy) {song.stem_report()}')
    for name, fn in SFX.items():
        if names and name not in names:
            continue
        x, opt = fn()
        loop = opt.get('loop', False)
        if loop:
            x = S.loop_filter(x, 'hp', 25)
        else:
            x = S.hp(x, 25)
        y = S.master_sfx(x, peak_db=opt.get('peak', -1.0), fout=opt.get('fout', 0.02), loop=loop)
        S.write_ogg(os.path.join(SFXD, name + '.ogg'), y, quality_level=0.4)
        print(f'sfx/{name}.ogg')


def verify():
    import soundfile as sf
    rows, ok = [], True
    files = [('bgm', n, True) for n in TRACKS] + [('sfx', n, n in LOOP_SFX) for n in SFX]
    for d, n, loop in files:
        p = os.path.join(GAME, 'audio', d, n + '.ogg')
        if not os.path.exists(p):
            rows.append(f'MISSING {p}')
            ok = False
            continue
        x, sr = sf.read(p, always_2d=True)
        dur = len(x) / sr
        pk = np.abs(x).max()
        bad = bool(np.isnan(x).any() or pk >= 0.999)
        seam = ''
        if loop:
            dif = np.abs(np.diff(x, axis=0)).max(axis=1)
            jump = np.abs(x[0] - x[-1]).max()
            p99 = np.percentile(dif, 99.9)
            e0 = S.rms(x[:2205])
            e1 = S.rms(x[-2205:])
            seam = f'seam jump {jump:.4f} (p99.9 step {p99:.4f}) edge rms {S.db(e1):.1f}/{S.db(e0):.1f} dB'
            if jump > 2 * p99:
                bad = True
        ok &= not bad
        rows.append(f"{'BAD ' if bad else 'ok  '}{d}/{n}.ogg  {dur:6.2f}s  {sr}Hz x{x.shape[1]}  "
                    f"{os.path.getsize(p) / 1024:7.1f} KB  peak {S.db(pk):6.2f} dBFS  rms {S.db(S.rms(x)):6.1f} dBFS  {seam}")
    print('\n'.join(rows))
    print('ALL OK' if ok else 'PROBLEMS FOUND')
    return ok


if __name__ == '__main__':
    args = set(sys.argv[1:])
    if args != {'--verify'}:
        build(args - {'--verify'})
    verify()
