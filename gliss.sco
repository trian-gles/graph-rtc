//rtsetparams(44100, 2)
load("STRUM2")

pitches = { 440, 550, 770, 500, 520}
times = { 0, 0.1, 0.2, 1, 1.2}

float make_note_slide_uncoor(float init_pitch, float start_time, float dur, float sslide_start)
{
    if ((slide_start + 1) > dur)
    {
        return 0
    }

    pitch = maketable("line", "nonorm", "nointerp", 20 * dur, 0, init_pitch, sslide_start, init_pitch, sslide_start + 1, init_pitch * 4, dur, init_pitch * 4)
    STRUM2(start_time, dur, 20000, pitch, 2, dur /2, 0.5)
    return 0
}


// all slide at the same point in time, does not halt playback
float make_note_slide_coor(float init_pitch, float start_time, float dur, float abs_slide_start)
{
    rel_slide_start = abs_slide_start - start_time

    if ((rel_slide_start < 0) || (rel_slide_start > dur))
    {
        STRUM2(start_time, dur, 20000, init_pitch, 2, dur /2, 0.5)
        return 0
    }

    pitch = maketable("line", "nonorm", "nointerp", 20 * dur, 0, init_pitch, rel_slide_start, init_pitch, rel_slide_start + 1, init_pitch * 4, dur, init_pitch * 4)
    STRUM2(start_time, dur, 20000, pitch, 2, dur /2, 0.5)
    return 0
}

float make_note_slide_coor_stop(float init_pitch, float start_time, float dur, float abs_slide_start)
{
    rel_slide_start = abs_slide_start - start_time

    if (rel_slide_start < 0)
    {
        STRUM2(start_time, dur, 20000, init_pitch, 2, dur /2, 0.5)
    }
    else if (rel_slide_start > dur)
    {
    }
    else
    {
        pitch = maketable("line", "nonorm", "nointerp", 20 * dur, 0, init_pitch, rel_slide_start, init_pitch, rel_slide_start + 1, init_pitch * 4, dur, init_pitch * 4)
        STRUM2(start_time, dur, 20000, pitch, 2, dur /2, 0.5)
    }

    return 0
}

slide_start = 1
dur = 6

for (i = 0; i < len(pitches); i = i + 1)
{
    init_pitch = pitches[i]
    start_time = times[i]
    make_note_slide_coor(init_pitch, start_time, dur, slide_start)
}


