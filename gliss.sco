rtsetparams(44100, 2)
load("STRUM2")

init_pitch = 440
slide_start = 1
dur = 6


pitch = maketable("line", "nonorm", "nointerp", 20 * dur, 0, init_pitch, slide_start, init_pitch, slide_start + 1, init_pitch * 4, dur, 880)
print(pitch)
STRUM2(0, dur, 20000, pitch, 2, dur /2, 0.5)