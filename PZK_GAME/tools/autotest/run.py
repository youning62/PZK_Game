"""Random-walk every branch: copies the harness in, runs N seeded playthroughs, removes it."""
import os, shutil, subprocess, sys, glob, collections
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
RENPY = "/Volumes/renpy-8.4.1-sdk/renpy-8.4.1-sdk/renpy.app/Contents/MacOS/renpy"
n = int(sys.argv[1]) if len(sys.argv) > 1 else 20
dst = os.path.join(ROOT, "game", "zz_autotest.rpy")
logs = os.path.join(ROOT, "autotest_logs")
shutil.rmtree(logs, ignore_errors=True); os.makedirs(logs)
shutil.copy(os.path.join(ROOT, "tools", "autotest", "zz_autotest.rpy"), dst)
try:
    for seed in range(1, n + 1):
        env = dict(os.environ, PZK_AUTOTEST=str(seed), PZK_START=os.environ.get("PZK_START", "start"), RENPY_GL_VSYNC="0", SDL_HINT_VIDEO_ALLOW_SCREENSAVER="1")
        try:
            r = subprocess.run([RENPY, ROOT, "run"], env=env, timeout=300, capture_output=True)
            code = r.returncode
        except subprocess.TimeoutExpired:
            code = "TIMEOUT"
        log = open(os.path.join(logs, "run_%d.log" % seed), encoding="utf-8").read() if os.path.exists(os.path.join(logs, "run_%d.log" % seed)) else ""
        end = [l for l in log.splitlines() if l.startswith("END")]
        print(seed, code, end[0] if end else ("EXCEPTION" if "EXCEPTION" in log else "NO END"), flush=True)
        if "EXCEPTION" in log:
            print(log[log.index("EXCEPTION"):][:3000])
finally:
    for f in [dst, dst + "c"]:
        if os.path.exists(f): os.remove(f)
labels = collections.Counter()
for f in glob.glob(os.path.join(logs, "*.log")):
    for l in open(f, encoding="utf-8"):
        if l.startswith("LABEL "): labels[l.split()[1]] += 1
print("labels reached:", dict(sorted(labels.items())))
