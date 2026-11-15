import numpy as np, wave, sys
SR = 48000
DUR = 56.0
N = int(SR * DUR)
L = np.zeros(N); R = np.zeros(N)
rng = np.random.default_rng(7)
BEAT = 0.5

def t_(d): return np.arange(int(d * SR)) / SR
def add(sig, at, gain=1.0, pan=0.0):
    i = int(at * SR)
    if i >= N: return
    sig = sig[: N - i]
    l = gain * np.cos((pan + 1) * np.pi / 4) * np.sqrt(2)
    r = gain * np.sin((pan + 1) * np.pi / 4) * np.sqrt(2)
    L[i:i + len(sig)] += sig * l; R[i:i + len(sig)] += sig * r
def env(n, a=0.005, d=0.2, curve=1.0):
    t = np.arange(n) / SR
    e = np.minimum(1, t / max(a, 1e-4)) * np.exp(-t / d) ** curve
    return e
def lp(x, cutoff):
    # one-pole lowpass, cutoff may be array
    c = np.broadcast_to(np.asarray(cutoff, float), x.shape)
    a = 1 - np.exp(-2 * np.pi * c / SR)
    y = np.zeros_like(x); s = 0.0
    for i in range(len(x)):
        s += a[i] * (x[i] - s); y[i] = s
    return y
def lp_fast(x, cutoff):
    a = 1 - np.exp(-2 * np.pi * cutoff / SR)
    from scipy.signal import lfilter
    return lfilter([a], [1, -(1 - a)], x)
try:
    import scipy  # noqa
    LPF = lp_fast
except Exception:
    LPF = None
def mtof(m): return 440 * 2 ** ((m - 69) / 12)

# ---------- instruments ----------
def kick(g=1.0):
    t = t_(0.45); f = 45 + 110 * np.exp(-t / 0.045)
    ph = 2 * np.pi * np.cumsum(f) / SR
    s = np.sin(ph) * np.exp(-t / 0.22)
    s += 0.25 * np.sin(ph * 2) * np.exp(-t / 0.03)
    click = rng.standard_normal(len(t)) * np.exp(-t / 0.004) * 0.3
    return np.tanh((s + click) * 1.6) * g
def clap():
    t = t_(0.3); n = rng.standard_normal(len(t))
    e = np.zeros(len(t))
    for off in (0, 0.011, 0.022):
        i = int(off * SR); e[i:] += np.exp(-(t[: len(t) - i]) / 0.012) * 0.6
    e += np.exp(-t / 0.09) * 0.5
    s = n * e
    s = s - LPF(s, 900)
    return s * 0.7
def hat(open_=False):
    t = t_(0.25 if open_ else 0.06); n = rng.standard_normal(len(t))
    s = n - LPF(n, 7000)
    return s * np.exp(-t / (0.08 if open_ else 0.018)) * 0.5
def saw(f, t):
    return 2 * ((f * t) % 1) - 1
def pad(notes, dur, g=0.12):
    t = t_(dur); s = np.zeros(len(t))
    for m in notes:
        for det in (-0.12, 0.0, 0.12):
            s += saw(mtof(m + det), t + rng.random())
    s = LPF(s, 1400)
    a = np.minimum(1, t / 0.25) * np.minimum(1, (dur - t) / 0.3)
    return s * a * g / len(notes)
def bass(m, dur, g=0.5):
    t = t_(dur); f = mtof(m)
    s = np.sin(2 * np.pi * f * t) + 0.35 * np.tanh(3 * np.sin(2 * np.pi * f * t))
    a = np.minimum(1, t / 0.008) * np.exp(-t / 0.5) * np.minimum(1, (dur - t) / 0.02)
    return s * a * g
def pluck(m, g=0.18, d=0.25):
    t = t_(0.6); f = mtof(m)
    s = saw(f, t) * 0.6 + np.sin(2 * np.pi * f * t)
    s = LPF(s, 3500) * np.exp(-t / d)
    return s * g
def bell(m, g=0.25, d=0.6):
    t = t_(1.5); f = mtof(m)
    s = np.sin(2 * np.pi * f * t + 1.2 * np.sin(2 * np.pi * f * 3.5 * t) * np.exp(-t / 0.2))
    return s * np.exp(-t / d) * np.minimum(1, t / 0.002) * g
def click(g=0.25, f=2500):
    t = t_(0.03); n = rng.standard_normal(len(t))
    s = (n - LPF(n, f)) * np.exp(-t / 0.004)
    return s * g
def pop(m=84, g=0.3):
    t = t_(0.12); f = mtof(m) * (1 + 0.8 * np.exp(-t / 0.01))
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / 0.04) * g
def whoosh(dur=0.5, g=0.35, up=True):
    t = t_(dur); n = rng.standard_normal(len(t))
    x = t / dur
    shape = np.sin(np.pi * x) ** 2
    cut = 400 + 5000 * (x if up else 1 - x)
    s = lp(n, cut) if len(n) < 30000 else LPF(n, 2500)
    return s * shape * g
def riser(dur, g=0.3):
    t = t_(dur); n = rng.standard_normal(len(t))
    x = t / dur
    s = lp(n, 300 + 7000 * x ** 2) * x ** 2
    f = 200 + 900 * x ** 2
    s += 0.25 * np.sin(2 * np.pi * np.cumsum(f) / SR) * x ** 2
    return s * g
def impact(g=0.8):
    t = t_(2.2)
    f = 38 + 70 * np.exp(-t / 0.08)
    s = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / 0.6)
    n = rng.standard_normal(len(t))
    s += LPF(n, 4000) * np.exp(-t / 0.5) * 0.35
    return np.tanh(s * 1.4) * g
def motor(dur, g=0.06, base=420):
    t = t_(dur)
    f = base + 120 * np.sin(2 * np.pi * 3.1 * t) + 60 * np.sin(2 * np.pi * 7.3 * t)
    s = np.sign(np.sin(2 * np.pi * np.cumsum(f) / SR))
    s = LPF(s, 1800)
    return s * g * np.minimum(1, t / 0.05) * np.minimum(1, (dur - t) / 0.05)
def tick(g=0.18):
    t = t_(0.05)
    return np.sin(2 * np.pi * 1800 * t) * np.exp(-t / 0.008) * g

# ---------- music ----------
# I–V–vi–IV in C, one chord per bar (2 s)
CH = [[60, 64, 67, 72], [55, 62, 67, 71], [57, 60, 64, 69], [53, 57, 60, 65]]
ROOT = [36, 31, 33, 29]

# Intro 0–8: sparse, moody (Am pad + clock ticks)
add(pad([57, 60, 64], 4.2, 0.10), 0.0, 1)
add(pad([53, 57, 60], 4.0, 0.10), 4.0, 1)
for b in range(16):
    add(tick(0.14 if b % 2 == 0 else 0.08), b * BEAT, pan=-0.3 if b % 2 else 0.3)
add(bass(33, 3.9, 0.35), 0.0); add(bass(29, 3.3, 0.35), 4.0)
# sub pulse in 4-7
for b in range(8, 14): add(kick(0.45), b * BEAT)
add(riser(1.6, 0.35), 6.4)

# Logo 8–12
add(impact(0.9), 8.0)
add(pad([60, 64, 67, 72], 4.0, 0.12), 8.0)
add(bass(36, 1.9, 0.4), 8.0); add(bass(31, 1.9, 0.4), 10.0)
for a, b_ in [(8.45, 9.0), (9.0, 9.5), (9.5, 9.95)]:
    add(motor(b_ - a, 0.05, 380 + 80 * (a - 8.45)), a)
for i, m in enumerate([72, 76, 79, 84]): add(bell(m, 0.16, 0.8), 10.1 + i * 0.06, pan=(i - 1.5) * 0.3)
add(whoosh(0.5, 0.25), 10.4); add(pop(80, 0.18), 10.85)
add(riser(0.9, 0.22), 11.1)

# Groove 12–54
def groove(start, end, intensity=1.0):
    bar0 = int(round(start / 2))
    t = start
    while t < end - 1e-6:
        bi = int(round(t / 2)) % 4
        bar_end = min(t + 2, end)
        add(pad(CH[bi], bar_end - t + 0.05, 0.085 * intensity), t, 1)
        for k in range(4):
            bt = t + k * BEAT
            if bt >= end: break
            add(kick(0.85), bt)
            if k in (1, 3): add(clap(), bt, 0.55)
            add(hat(), bt + 0.25, 0.5, pan=0.25)
            if intensity > 1: add(hat(), bt + 0.125, 0.22, pan=-0.25); add(hat(), bt + 0.375, 0.22, pan=-0.25)
            # bass offbeat pattern
            add(bass(ROOT[bi] + 12, 0.22, 0.42), bt)
            add(bass(ROOT[bi] + 12, 0.22, 0.32), bt + 0.25)
        # pluck arp 16ths
        notes = CH[bi]
        for k in range(16):
            at = t + k * 0.125
            if at >= end: break
            m = notes[[0, 2, 1, 3, 2, 1, 3, 2][k % 8]] + 12
            add(pluck(m, 0.085 * intensity, 0.18), at, pan=0.35 if k % 2 else -0.35)
        t = bar_end
groove(12.0, 34.0, 1.0)
groove(34.0, 45.0, 1.15)
# proof section: half energy then build
for bi, t0 in enumerate([45.0, 47.0]):
    add(pad(CH[2 + bi], 2.05, 0.10), t0, 1)
    add(bass(ROOT[2 + bi] + 12, 1.9, 0.35), t0)
for b in range(8): add(hat(), 45.0 + b * 0.25 + 0.125, 0.3)
add(riser(1.6, 0.3), 47.5)
groove(49.0, 54.0, 1.2)
# ending
add(impact(0.85), 54.0)
add(pad([48, 60, 64, 67, 72, 76], 2.0, 0.16), 54.0, 1)
add(bass(24, 2.0, 0.5), 54.0)
for i, m in enumerate([72, 76, 79, 84, 88]): add(bell(m, 0.12, 0.9), 54.0 + i * 0.05, pan=(i - 2) * 0.25)

# ---------- SFX synced to visuals ----------
add(whoosh(0.45, 0.22), 0.05)
add(pop(60, 0.25), 1.4)
# error buzz on "0.00"
tt = t_(0.35); add(np.sign(np.sin(2 * np.pi * 110 * tt)) * np.exp(-tt / 0.2) * 0.06, 2.3)
add(whoosh(0.5, 0.25), 3.85)
for a in (4.7, 5.25, 5.8): add(whoosh(0.35, 0.18), a - 0.05); add(pop(52, 0.22), a + 0.25)
def typing(a, b, step=0.07):
    t = a
    while t < b: add(click(0.16, 3000 + rng.random() * 1500), t, pan=rng.uniform(-.2, .2)); t += step * rng.uniform(0.7, 1.3)
add(whoosh(0.6, 0.25), 11.9)
typing(12.8, 13.2); typing(13.5, 13.85); typing(14.0, 14.9)
for a, m in [(15.05, 84), (15.25, 86), (15.45, 88)]: add(pop(m, 0.2), a)
add(click(0.35, 1500), 15.75)
add(bell(79, 0.2, 0.4), 16.0); add(bell(84, 0.2, 0.6), 16.12)
add(whoosh(0.4, 0.18), 17.4)
add(pop(76, 0.2), 18.0)
add(bell(88, 0.18, 0.3), 18.5); add(bell(93, 0.16, 0.4), 18.6)
for a, m in [(18.75, 79), (19.45, 81), (20.1, 84)]: add(pop(m, 0.2), a)
add(click(0.3, 1500), 21.6)
add(whoosh(0.4, 0.18), 22.9)
for k in range(12): add(tick(0.1), 24.25 + k * 0.0625)
add(click(0.25), 25.25)
typing(25.5, 26.45)
add(click(0.35, 1500), 26.75)
add(whoosh(0.35, 0.2), 26.9); add(bell(84, 0.2, 0.4), 26.95); add(bell(91, 0.18, 0.6), 27.05)
add(whoosh(0.4, 0.18), 28.4)
for i, a in enumerate([28.75, 29.25, 29.75, 30.9, 31.4, 31.9]): add(pop(72 + i * 2, 0.17), a)
add(motor(1.1, 0.03), 29.75)
# ka-ching
for i, m in enumerate([91, 96, 100]): add(bell(m, 0.17, 0.5), 32.25 + i * 0.07)
add(click(0.25, 5000), 32.2)
add(riser(0.5, 0.2), 33.5)
add(impact(0.95), 34.05)
add(whoosh(0.5, 0.25), 37.4)
for i in range(4): add(whoosh(0.3, 0.12), 37.8 + i * 0.55); add(pop(76 + i * 3, 0.16), 37.95 + i * 0.55)
add(whoosh(0.5, 0.25), 41.5)
penta = [72, 74, 76, 79, 81, 84, 86, 88, 91, 93, 96, 98]
for i in range(12): add(bell(penta[i], 0.09, 0.25), 41.95 + i * 0.12, pan=((i % 3) - 1) * 0.4)
add(whoosh(0.5, 0.25), 45.0)
# counter ticks accelerate
t = 45.4
while t < 47.4:
    add(tick(0.12), t); x = (t - 45.4) / 2.0; t += 0.11 - 0.06 * np.sin(np.pi * x)
add(impact(0.75), 47.4)
for i, m in enumerate([84, 88, 91]): add(bell(m, 0.14, 0.7), 47.4 + i * 0.04)
add(impact(0.85), 49.1)
add(motor(4.8, 0.025, 360), 49.2)
add(pop(84, 0.25), 50.3); add(whoosh(0.4, 0.2), 50.75)
add(click(0.35, 1500), 52.6); add(bell(88, 0.16, 0.5), 52.7)

# ---------- master ----------
mix = np.stack([L, R])
# fade in/out edges
mix[:, : int(0.02 * SR)] *= np.linspace(0, 1, int(0.02 * SR))
fo = int(1.2 * SR); mix[:, -fo:] *= np.linspace(1, 0, fo) ** 2
peak = np.max(np.abs(mix)); mix = mix / peak * 1.6
mix = np.tanh(mix) * 0.89
out = (mix.T * 32767).astype(np.int16)
with wave.open(sys.argv[1], 'wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(out.tobytes())
print('ok', peak)
