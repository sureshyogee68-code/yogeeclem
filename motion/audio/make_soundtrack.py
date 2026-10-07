"""Synthesize a 31.5 s soundtrack for the SSITO motion: warm pad, soft pulse,
and whoosh/hit accents synced to scene transitions. Output: soundtrack.wav"""
import os
import wave
import numpy as np

SR = 48000
DUR = 31.5
N = int(SR * DUR)
t = np.arange(N) / SR
rng = np.random.default_rng(7)


def env(start, attack, release, length=None):
    e = np.zeros(N)
    s = int(start * SR)
    a = int(attack * SR)
    r = int(release * SR)
    hold = int((length or 0) * SR)
    seg = np.concatenate([np.linspace(0, 1, a, endpoint=False) ** 2, np.ones(hold), np.exp(-np.linspace(0, 6, r))])
    seg = seg[: max(0, N - s)]
    e[s : s + len(seg)] = seg
    return e


def lowpass(x, k):
    # one-pole low-pass, k in (0,1]
    y = np.empty_like(x)
    acc = 0.0
    for i in range(len(x)):
        acc += k * (x[i] - acc)
        y[i] = acc
    return y


def note(f):
    return 440.0 * 2 ** ((f - 69) / 12)


out = np.zeros(N)

# --- Pad: two chord voicings (Dmaj9 -> Bm9 -> Gmaj7 -> Dmaj9), detuned saws softened
chords = [
    (0.0, [50, 57, 62, 64, 69]),
    (8.6, [47, 54, 62, 64, 69]),
    (16.8, [43, 50, 59, 62, 66]),
    (24.4, [45, 52, 61, 64, 69]),
    (27.4, [50, 57, 62, 66, 69, 76]),
]
pad = np.zeros(N)
for idx, (start, notes) in enumerate(chords):
    end = chords[idx + 1][0] + 0.8 if idx + 1 < len(chords) else DUR
    seg = (t >= start) & (t < end)
    fade = np.clip((t - start) / 1.2, 0, 1) * np.clip((end - t) / 0.8, 0, 1)
    for m in notes:
        for det in (-0.08, 0.08):
            f = note(m + det)
            pad += seg * fade * (np.sin(2 * np.pi * f * t) + 0.25 * np.sin(2 * np.pi * 2 * f * t)) / len(notes)
pad *= 0.16 * (0.85 + 0.15 * np.sin(2 * np.pi * 0.25 * t))
out += pad

# --- Sub pulse (heartbeat-like) every half second from 4.1 s, stops for CTA swell
bpm_t = np.arange(4.1, 27.2, 0.5)
for i, b in enumerate(bpm_t):
    s = int(b * SR)
    L = int(0.35 * SR)
    tt = np.arange(L) / SR
    f = 55 * (1 + 1.5 * np.exp(-tt * 30))
    k = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-tt * 9) * (0.32 if i % 2 == 0 else 0.18)
    out[s : s + L] += k[: N - s]

# --- Ticks (hi clicks) on the services cycle
for i in range(7):
    s = int((9.3 + i * 0.7) * SR)
    L = int(0.06 * SR)
    noise = rng.standard_normal(L) * np.exp(-np.arange(L) / SR * 90)
    click = np.diff(np.concatenate([[0], noise])) * 0.12
    out[s : s + L] += click

# --- Whooshes into transitions
def whoosh(at, length=0.7, gain=0.25):
    L = int(length * SR)
    s = int((at - length * 0.8) * SR)
    n = rng.standard_normal(L)
    sweep = np.linspace(0.02, 0.35, L) ** 1.5
    y = np.empty(L)
    acc = 0.0
    for i in range(L):
        acc += sweep[i] * (n[i] - acc)
        y[i] = acc
    shape = np.sin(np.pi * np.linspace(0, 1, L)) ** 2
    out[s : s + L] += y * shape * gain


for at in (1.3, 4.1, 8.6, 14.2, 16.8, 20.4, 24.4, 27.4):
    whoosh(at)

# --- Soft impacts (logo, gold statement, CTA)
def hit(at, gain=0.5):
    s = int(at * SR)
    L = int(1.6 * SR)
    tt = np.arange(L) / SR
    body = np.sin(2 * np.pi * 48 * tt) * np.exp(-tt * 4)
    shimmer = sum(np.sin(2 * np.pi * note(m) * tt) for m in (74, 81, 86)) / 3 * np.exp(-tt * 2.5) * 0.35
    y = (body + shimmer) * gain
    out[s : s + L] += y[: N - s]


hit(1.65, 0.45)
hit(14.95, 0.5)
hit(28.1, 0.45)
# button click
s = int(30.45 * SR)
L = int(0.08 * SR)
out[s : s + L] += np.sin(2 * np.pi * 1800 * np.arange(L) / SR) * np.exp(-np.arange(L) / SR * 60) * 0.25

# master: fade in/out, soft clip, normalize
out *= np.clip(t / 0.4, 0, 1) * np.clip((DUR - t) / 1.5, 0, 1)
out = np.tanh(out * 1.2)
out /= np.max(np.abs(out)) + 1e-9
out *= 0.85
stereo = np.stack([out, np.roll(out, 240)], axis=1)  # tiny haas widening
pcm = (stereo * 32767).astype(np.int16)

path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "soundtrack.wav")
with wave.open(path, "wb") as w:
    w.setnchannels(2)
    w.setsampwidth(2)
    w.setframerate(SR)
    w.writeframes(pcm.tobytes())
print("wrote", path)
