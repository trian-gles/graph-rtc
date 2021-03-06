score_gate = """
load("STRUM2");
load("FREEVERB")

srand(4)

max_dur = 50;
tempo = 100;

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
    float left_gate_maxdepth,
    float left_index,
    float right_gate_mindepth,
    float right_index
}

float make_note_node(float rest, float len, float midi_pitch, float left_gate_maxdepth, float left_index, float right_gate_mindepth, float right_index)
{
    struct StrumNoteNode note;
    note.rest = rest;
    note.len = len;
    note.midi_pitch = midi_pitch;
    note.left_gate_maxdepth = left_gate_maxdepth;
    note.left_index = left_index;
    note.right_gate_mindepth = right_gate_mindepth;
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
    STRUM2(note.start_time + offset, note.dur, amp, freq, 10, note.dur, (rand() + 1) / 2);
    if (note.midi_pitch < 40)
    {
        STRUM2(note.start_time + offset, note.dur, amp + 2000, freq / 2, 10, note.dur, (rand() + 1) / 2);
    }
    return 0;
}

////////////////
//// CURSOR ////
////////////////

all_cursors = {};
new_cursors = {};

list limit_cursors(float depth)
{
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

    if ((depth == 7) || (depth == 11))
    {
        limited_cursors = {}
        for (i = 0; i < len(all_cursors); i = i + 1)
        {
            curs = all_cursors[i];
            if (rand() > -0.5)
            {
                limited_cursors[len(limited_cursors)] = curs
            }
        }

        all_cursors = limited_cursors
    }
    
    if (depth == 17)
    {
        limited_cursors = {}
        for (i = 0; i < len(all_cursors); i = i + 1)
        {
            curs = all_cursors[i];
            if (rand() > -0.5)
            {
                limited_cursors[len(limited_cursors)] = curs
            }
        }

        all_cursors = limited_cursors
    }

    return all_cursors;
}

struct CursorStatus
{
    float index,
    float current_time,
    float depth
}

float new_cursor(float index, float current_time, float depth)
{
    struct CursorStatus ncurs;
    ncurs.index = index;
    ncurs.current_time = current_time;
    ncurs.depth = depth;
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

    //// Make a new cursor for the right branch
    if (cursor.depth > node.right_gate_mindepth)
    {
        new_cursor(node.right_index, current_time, cursor.depth + 1)
    }
    

    //// The cursor stays on the left branch
    if (cursor.depth < node.left_gate_maxdepth)
    {
        cursor.index = node.left_index;
        cursor.current_time = current_time;
        cursor.depth = cursor.depth + 1
    }
    

    


    return 0;
}

//// Build the tree
/* rest before note, length of note, pitch, left maxdepth, left index, right mindepth, right index */
make_note_node(0.7, 1, 50, 23, 1, 20, -1)   //0
make_note_node(1.11, 1, 47, 15, 2, 5, 3)    //1
make_note_node(0.51, .5, 78, 17, 0, 1, 4)   //2
make_note_node(2.82, 2.2, 79, 16, 2, 6, 1)  //3 
make_note_node(7, 2.2, 81, 12, 10, 13, 5)   //4
make_note_node(1, 4, 74, 23, 6, 18, 3)      //5
make_note_node(1, 4, 67, 23, 7, 16, 2)     //6
make_note_node(5, 4, 55, 23, 8, 15, 2)      //7
make_note_node(5, 4, 91, 20, 6, 8, 9)       //8
make_note_node(6, 4, 40, 0, -1, 8, 10)      //9
make_note_node(5, 4, 57, 23, 11, 15, -1)    //10
make_note_node(5, 4, 92, 21, -1, 8, -1)     //11




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

    if (depth > 23)
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

"""