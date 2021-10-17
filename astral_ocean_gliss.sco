//rtsetparams(44100, 2)
load("STRUM2");
load("FREEVERB")

srand(3)

max_dur = 50;
tempo = 100;

////////////
// GLISS  //
////////////

float make_note_slide_uncoor(float init_pitch, float start_time, float dur, float amp, float slide_start, float slide_len)
{
    if ((slide_start + slide_len) > dur)
    {
        STRUM2(start_time, dur, amp, init_pitch, 2, dur /2, (rand() + 1) / 2)
        return 0
    }

    pitch = maketable("line", "nonorm", "nointerp", 20 * dur, 0, init_pitch, slide_start, init_pitch, slide_start + slide_len, init_pitch * 4, dur, init_pitch * 4)
    STRUM2(start_time, dur, amp, pitch, 2, dur /2, (rand() + 1) / 2)
    return 0
}


// all slide at the same point in time, does not halt playback
float make_note_slide_coor(float init_pitch, float start_time, float dur, float abs_slide_start)
{
    rel_slide_start = abs_slide_start - start_time

    if ((rel_slide_start < 0) || (rel_slide_start > dur))
    {
        STRUM2(start_time, dur, 20000, init_pitch, 2, dur /2, (rand() + 1) / 2)
        return 0
    }

    pitch = maketable("line", "nonorm", "nointerp", 20 * dur, 0, init_pitch, rel_slide_start, init_pitch, rel_slide_start + 1, init_pitch * 4, dur, init_pitch * 4)
    STRUM2(start_time, dur, 20000, pitch, 2, dur /2, (rand() + 1) / 2)
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





////////////
// REVERB //
////////////

bus_config("STRUM2", "aux 0-1 out")
bus_config("FREEVERB", "aux 0-1 in", "out 0-1")

outskip = 0
inskip = 0
dur = 60
amp = .5
roomsize = 0.6
predelay = .03
ringdur = 3
damp = 70
dry = 40
wet = 30
width = 100

FREEVERB(outskip, inskip, dur, amp, roomsize, predelay, ringdur, damp, dry, wet, width)



////////////////
////  NODE  ////
////////////////

node_storage = {}

struct StrumNoteNode
{
    float rest,
    float len,
    float midi_pitch,
    float left_index,
    float right_index
}

float make_note_node(float rest, float len, float midi_pitch, float left_index, float right_index)
{
    struct StrumNoteNode note;
    note.rest = rest;
    note.len = len;
    note.midi_pitch = midi_pitch;
    note.left_index = left_index;
    note.right_index = right_index;
    node_storage[len(node_storage)] = note;
    return 0;
}



////////////////
//// NOTES  ////
////////////////

scheduled_notes = {}
struct StrumNotePlay
{
    float start_time,
    float dur,
    float midi_pitch
}

float schedule_note(float start_time, float dur, float midi_pitch)
{
    struct StrumNotePlay note;
    note.start_time = start_time;
    note.dur = dur;
    note.midi_pitch = midi_pitch;

    scheduled_notes[len(scheduled_notes)] = note;
    return 0;
}

float play_note(struct StrumNotePlay note)
{
    freq = cpsmidi(note.midi_pitch) + (rand() * note.start_time / 15);
    offset = (rand() + 1) / 4;
    amp = rand() * 8000 + 12000;
    start_time = note.start_time + offset


    // float make_note_slide_uncoor(float init_pitch, float start_time, float dur, float amp, float sslide_start)
    make_note_slide_uncoor(freq, start_time, note.dur, amp, 0.2, 1)
    if (note.midi_pitch < 40)
    {
        make_note_slide_uncoor(freq / 2, start_time, note.dur, amp + 2000, .1)
    }

    return 0;
}

////////////////
//// CURSOR ////
////////////////


all_cursors = {};
new_cursors = {};

limit_depths = {10};
limit_max_cursor_nums = {2};

list limit_cursors(float depth)
{
    // Remove unneeded cursors
    active_cursors = {};
    for (i = 0; i < len(all_cursors); i = i + 1)
    {
        curs = all_cursors[i];
        if (curs.index >= 0)
        {
            active_cursors[len(active_cursors)] = curs;
        }
    }
    all_cursors = active_cursors


    // Determine the max number of cursors
    max_curs = 2000;

    limit_depth_index = index(limit_depths, depth);

    if (limit_depth_index > -1)
    {
        max_curs = limit_max_cursor_nums[limit_depth_index];
    }


    if (len(all_cursors) > max_curs)
    {
        limited_cursors = {}
        for (i = 0; i < max_curs; i = i + 1)
        {
            curs = all_cursors[i];
            limited_cursors[len(limited_cursors)] = curs
        }

        all_cursors = limited_cursors
    }


    return all_cursors;
}

struct CursorStatus
{
    float index,
    float current_time
}

float new_cursor(float index, float current_time)
{
    struct CursorStatus ncurs;
    ncurs.index = index;
    ncurs.current_time = current_time;
    new_cursors[len(new_cursors)] = ncurs;
    return 0;
}

float schedule_and_get_next(struct CursorStatus cursor)
{
    if (cursor.index < 0)
    {
        return 0;
    }

    node = node_storage[cursor.index];
    rest_len = node.rest * 60 / tempo;
    note_len = node.len * 60 / tempo;
    current_time = rest_len + cursor.current_time;

    schedule_note(current_time, note_len, node.midi_pitch)


    //// The cursor stays on the left branch
    cursor.index = node.left_index;
    cursor.current_time = current_time;

    //// Make a new cursor for the right branch
    new_cursor(node.right_index, current_time)


    return 0;
}

//// Build the tree
/// pre_rest, dur, pitch, left index, right index
make_note_node(1.12, 3.2, 60, 1, -1)
make_note_node(0.7, 3.2, 61, 2, 3)
make_note_node(1.51, .5, 68, 0, 4)
make_note_node(1.82, 2.2, 79, 2, 1)
make_note_node(7, 2.2, 99, 5, -1)
make_note_node(1, 4, 63, 6, -1)
make_note_node(1, 4, 68, 7, -1)
make_note_node(5, 4, 56, 8, -1)
make_note_node(5, 4, 49, 6, 9)
make_note_node(6, 4, 37, -1, 0)




//// Traverse the tree
quit = 0
struct CursorStatus cursor;
cursor.index = 0;
cursor.current_time = 0;
depth = 0;

all_cursors[0] = cursor;

while (quit == 0)
{
    //// handle all current cursors
    for (i = 0; i < len(all_cursors); i = i + 1)
    {
        schedule_and_get_next(all_cursors[i])
    }

    //// add new cursors
    for (i = 0; i < len(new_cursors); i = i + 1)
    {
        all_cursors[len(all_cursors)] = new_cursors[i];
    }

    all_cursors = limit_cursors(depth)

    if (depth > 20)
    {
        quit = 1;
    }
    new_cursors = {}
    depth = depth + 1;
}


//// Playback scheduled notes
for (i = 0; i < len(scheduled_notes); i = i + 1)
{
    play_note(scheduled_notes[i])
}