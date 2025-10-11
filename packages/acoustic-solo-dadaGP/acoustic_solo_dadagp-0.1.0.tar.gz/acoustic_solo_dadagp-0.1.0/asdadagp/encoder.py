import guitarpro as gp

from .const import instrument_groups
from .token_splitter import split_rare_token
from .utils import beat_effect_list  # is_good_guitar_tuning,
from .utils import (
    convert_spn_to_common,
    get_fret,
    get_instrument_group,
    get_instrument_token_prefix,
    get_measure_tokens,
    get_tuning_type,
    guitar_downtunage,
    note_effect_list,
    oops_theres_a_conflicting_beatfx,
    oops_theres_a_note_here,
    roundtempo,
)


# Takes a GP file, converts to token format
def guitarpro2tokens(song, artist, verbose=False, note_tuning=False):
    # - Map every track in song to an instrument group
    # - Remove SoundFX tracks
    # - Throw error if any track has an instrument change event in mixTable
    # - Throw error if song has more than 3 distorted guitars, 2 clean guitars, or 1 bass
    # - Non-guitar instruments will become either piano (leads) or choir (pads) and treated like a guitar track.
    # - Multiple drums tracks get combined into one track. Same for leads/pads.
    # - Throw error if any guitar/bass/pad/lead track has a non-supported tuning
    #     - 6,7 string guitars and 4,5,6 string basses allowed
    #     - Drop D or Drop AD is allowed, and those extra low notes will be on Frets -2 or -1
    #     - Downtuning is allowed, but only if all guitar/bass/pad/lead tracks are downtuned together the same pitch_shift
    #     - Capo offsets will be removed. Frets will be shifted
    #         - Normally if capo is at fret 2, and open strings are played, GP tabs this at fret 0, which I disagree with.
    #         - Instead, if capo was at fret 2, those open strings will now be at fret 2. As expected!

    ##############################
    ## Identify channels by group

    tracks_by_group = {
        # "drums": [],
        # "distorted": [],
        "clean": [],
        # "bass": [],
        # "leads": [],
        # "pads": [],
        "remove": [],
    }

    for i, track in enumerate(song.tracks):
        group = get_instrument_group(track)
        tracks_by_group[group].append(track)

    # remove sfx tracks
    while True:
        removed = False
        for i, track in enumerate(song.tracks):
            if get_instrument_group(track) == "remove":
                del song.tracks[i]
                removed = True
                break
        if removed:
            continue
        break

    # max_bass = 1
    max_clean = 3
    # max_distorted = 3
    # n_bass = len(tracks_by_group["bass"])
    n_clean = len(tracks_by_group["clean"])
    # n_distorted = len(tracks_by_group["distorted"])
    # assert n_bass <= max_bass, "Too many bass guitar channels. Max %s. You have %s" % (
    #     max_bass,
    #     n_bass,
    # )
    assert (
        n_clean <= max_clean
    ), "Too many clean/acoustic guitar channels. Max %s. You have %s" % (
        max_clean,
        n_clean,
    )

    verbose and print(tracks_by_group)

    # Throw error if there is an instrument change
    for t, track in enumerate(song.tracks):
        for m, measure in enumerate(track.measures):
            for v, voice in enumerate(measure.voices):
                for b, beat in enumerate(voice.beats):
                    if beat.effect.mixTableChange:
                        assert (
                            beat.effect.mixTableChange.instrument == None
                        ), "Instrument Change Not Supported"

    #############################################
    # TUNING SHIFT

    # Pre-processing

    ## All Guitar/Bass/Leads/Pads have
    ##  - no weird tuning combinations
    ##  - Downtuning is supported, but only if all tracks are downtuned the same pitch_shift together.
    ##  - Guitar is basically always 7 string, with possible dropD or dropAD represented as fret -2 or -1
    ##  - Bass is basically always 6 string, with possible dropD or drop AD represented as fret -2 or -1
    ##  - Pads/Leads are treated the same as a guitar track.
    ##  - In Post, the stringing will be determined based on what notes were generated.
    ##      - If no string7 notes then use 6 string, etc.
    ##      - If no -2 or -1 frets, then use E standard or BE standard.
    ##  - In Post, the uniform pitch shift will be applied
    ##  - In Pre, remember to add the capo offset to the fret number

    # Verify support TUNING
    downtunages = []
    tuning_types = {}  # keep tracking of tuning types
    ref_strings = []
    for t, track in enumerate(song.tracks):
        midinumber = track.channel.instrument
        group_name = instrument_groups[midinumber]
        strings = [str(string) for string in track.strings]
        if ref_strings == []:
            ref_strings = strings
        else:
            if ref_strings != strings:
                raise ValueError(
                    "Error: All guitar tracks must have the same strings. "
                    "Track %s has strings %s, but previous track had %s"
                    % (
                        t,
                        " ".join(strings),
                        " ".join(ref_strings),
                    )
                )
            else:
                ref_strings = strings
        if track.isPercussionTrack:
            tuning_types[t] = "drums"
            continue
        if group_name == "clean":
            # assert is_good_guitar_tuning(
            #     strings
            # ), "Error: Track %s has unsupported guitar tuning: %s" % (
            #     t,
            #     " ".join(strings),
            # )
            downtunages.append(guitar_downtunage(strings))
        tuning_types[t] = get_tuning_type(group_name, strings)

    verbose and print("Downtuning scheme:", downtunages)
    allthesame = all([x % 12 == downtunages[0] % 12 for x in downtunages])
    # for example, (-3, -3, -3) are all the same downtune
    # also, (-3, -3, -15) is all the same downtune. That third instrument will end up changing octave to meet the others.
    assert (
        allthesame
    ), "Error: Guitar/bass/pads/leads tracks must be all be downtuned by same pitch."

    # Find the PITCH SHIFT
    # if downtunages are all the exact same, use that pitch
    # if downtunages are different, but mod 12 equivalent, then choose the pitch closest to zero.
    # Note: Whatever -12 pitchshift there was just gets shifted to 0. That instrument may change octave.
    # Find the pitch closest to zero by sorting
    downtunages.sort(key=lambda x: abs(int(x)))
    if len(downtunages) == 0:
        pitch_shift = 0
    else:
        pitch_shift = downtunages[0]
    verbose and print("Pitch Shift:", pitch_shift)
    verbose and print(tuning_types)

    #############################################
    # CONDITIONING

    # Tempo
    # song.tempo is the initial tempo
    # Note: please ignore measure.tempo, it's wrong and seems to be a bug in guitarpro
    # tempo may change later in the song in a beatEffect
    tempo_token = "tempo:%s" % roundtempo(song.tempo)

    downtune_token = "downtune:%s" % pitch_shift

    # head_tokens = [artist, downtune_token, tempo_token, "start"]
    head_tokens = [artist, downtune_token, tempo_token]
    if not note_tuning:
        head_tokens.extend(ref_strings)
    head_tokens.append("start")

    tunings = ["Order of strings: (1,2,3,4,5,6)"]

    scientific_pitch_tuning = f"spn_tuning:{strings}"
    tunings.append(scientific_pitch_tuning)

    common_tuning = f"tuning:{convert_spn_to_common(strings)}"
    tunings.append(common_tuning)

    verbose and print("=========\nHead tokens")
    verbose and print(f"{head_tokens}, \n{tunings}")

    ######################################################
    ## BUILD THE LIST OF EVENTS

    events_all = []  # a list of measures. each measure is a list of events.
    # there's four types of events: measure, note, rest, beatfx
    # measure event tokens always come at the beginning of the measure before the notes
    # notefx tokens always come immediately after the note
    # beatfx tokens always come at the end of the beat
    # the order of beats matters
    # but the order of notes/tracks within a beat doesn't matter (this can be changed for dataset augmentation)

    # measures (im representing measures as the top of the hierarchy so that autoregression always moves forward in time)
    for m, _ in enumerate(song.tracks[0].measures):
        measure = song.tracks[0].measures[m]
        events_this_measure = []  # just this measures' events
        # Measure event is always the first event in the list:
        # (hack: setting track to -1 ensures the measure tokens will come before the note tokens when sorting0
        event = {
            "type": "measure",
            "track": -1,
            "start": measure.start,
            "tokens": get_measure_tokens(measure),
        }
        events_this_measure.append(event)
        # tracks in measures
        for t, track in enumerate(song.tracks):
            instrument_prefix = get_instrument_token_prefix(track, tracks_by_group)
            measure = track.measures[m]
            # voices in tracks (i guess tracks have 2 voices? i will just combine them into one voice)
            for v, voice in enumerate(measure.voices):
                # print(m, t, v)
                for b, beat in enumerate(voice.beats):
                    # in the latest version of pyguitarpro (September 25 2020)
                    # duration.time may be int or Fraction
                    # We could convert Fraction to int for wait:## format
                    # But Fraction may be rounded to an integer that is not supported by fromTime
                    # Use this function which finds the nearest time supported by FromTime
                    # beat_duration = convert_to_nearest_supported_time(beat.duration.time)
                    # beat_start = convert_to_nearest_supported_time(beat.start - measure.start) + measure.start
                    beat_duration = beat.duration.time
                    beat_start = beat.start
                    # print(beat_start, beat.start)
                    if beat.status.name == "empty":
                        # there's supposedly nothing in this measure for this voice/track
                        # however even an empty beat can still have beat effects
                        # and we care about tempo changes via mixtable changes
                        pass
                    elif beat.status.name == "normal":
                        # note or a set of notes
                        for n, note in enumerate(beat.notes):
                            # NOTE EFFECTS
                            # woah I almsot forgot note.type, which hands tied notes and dead notes
                            notefx = []
                            if note.type.value == 2:
                                notefx.append("nfx:tie")
                            elif note.type.value == 3:
                                notefx.append("nfx:dead")
                            # elif(note.type==1):
                            #   a rest note? ˙hmm
                            notefx.extend(note_effect_list(note.effect))
                            if track.isPercussionTrack:
                                # Need to verify how percussion behaves on strings/values
                                string = note.string
                                fret = note.value
                            else:
                                # strings are 1-indexed. They start from string 1 and go to string 6 or 7
                                # GP's string value is OK to copy over into our representation
                                # UNLESS it's a 4 or 5 string bass, which I want to start from string 2
                                # the reason for this is that 6 string bass adds in the high C string which we want as string 1
                                if (
                                    instrument_prefix == "bass"
                                    and len(track.strings) < 6
                                ):
                                    string = note.string + 1
                                else:
                                    string = note.string
                                fret = get_fret(note, track, pitch_shift)
                            # Tricky calculation to get the fret number
                            # note.velocity=95 -- maybe ignore velocity for now
                            event = {
                                "type": "note",
                                "track": t,
                                "instrument_prefix": instrument_prefix,
                                "start": beat_start,
                                "duration": beat_duration,
                                "string": string,
                                "fret": fret,
                                "effects": notefx,
                            }
                            # Test if there's already a note/rest in this spot
                            # This may happen when combining tracks into one track
                            # Or if the generator is so dumb that it puts two notes on the same string
                            # Note: If there was a rest here, remove it, replace it with a note.
                            test = oops_theres_a_note_here(
                                event, events_this_measure, verbose
                            )
                            if test:
                                events_this_measure.append(event)
                            else:
                                verbose and print(
                                    "Note insertion: Oops theres already a note here",
                                    m,
                                    beat_start,
                                    instrument_prefix,
                                )
                    elif beat.status.name == "rest":
                        # print(beat.status.name)
                        # a rest
                        event = {
                            "type": "rest",
                            "track": t,
                            "duration": beat_duration,
                            "instrument_prefix": instrument_prefix,
                            "start": beat_start,
                        }
                        # Test if there's already a note/rest in this spot
                        # This may happen when combining tracks into one track
                        # Or if the generator is so dumb that it puts two notes on the same string
                        # print("rest",event)
                        test = oops_theres_a_note_here(
                            event, events_this_measure, verbose
                        )
                        if test:
                            events_this_measure.append(event)
                        else:
                            verbose and print(
                                "Rest insertion: Oops theres already a note here",
                                m,
                                beat_start,
                                instrument_prefix,
                            )
                    ## Beat Effects come after the notes/rests
                    beatfx = beat_effect_list(beat.effect)
                    if len(beatfx):
                        event = {
                            "type": "beatfx",
                            "effects": beatfx,
                            "duration": beat_duration,
                            "instrument_prefix": instrument_prefix,
                            "start": beat_start,
                            "track": t,
                        }
                        # Test if there's already a beatfx in this spot that conflicts (contradicting value)
                        # This may happen when combining tracks into one track
                        # Or if the generator is too dumb and puts two opposing beatfx's on same the same beat
                        test = oops_theres_a_conflicting_beatfx(
                            event, events_this_measure
                        )
                        if test:
                            verbose and print(
                                "Oops theres already a beatfx here",
                                m,
                                beat_start,
                                instrument_prefix,
                            )
                        else:
                            # Add the BeatFX event
                            events_this_measure.append(event)
                        # Check if this was an empty measure. An empty measure with a beatfx should get a rest.
                        # This will happen in the case of a tempo change on an empty measure
                        if beat.status.name == "empty":
                            event = {
                                "type": "rest",
                                "track": t,
                                "duration": beat_duration,
                                "instrument_prefix": instrument_prefix,
                                "start": beat_start,
                            }
                            # Test if there's already a note/rest in this spot
                            # This may happen when combining tracks into one track
                            # Or if the generator is so dumb that it puts two notes on the same string
                            # print("rest",event)
                            test = oops_theres_a_note_here(
                                event, events_this_measure, verbose
                            )
                            if test:
                                # Add the "fake" rest which the beat effect attaches to
                                events_this_measure.append(event)
                            else:
                                verbose and print(
                                    "Rest insertion: Oops theres already a note here",
                                    m,
                                    beat_start,
                                    instrument_prefix,
                                )
        events_all.extend(events_this_measure)

    verbose and print("=========\nFirst 5 events:")
    verbose and print(events_all[:5])

    #############################################
    ## CONVERT LIST OF EVENTS INTO LIST OF BODY TOKENS

    # body_tokens remove start/durations from notes/rests and introduce waits between them
    # also note_effects immediately proceed their notes
    body_tokens = []
    t = 0

    # sort by start time
    # Measure tokens first
    # Then note/rest/notefx/beatfx tokens sorted by track number
    # Notefx tokens come right after note tokens
    # Beatfx tokens come right after all note/notefx tokens for that beat
    events_sorted = sorted(
        events_all,
        key=lambda x: (
            x["start"] * 1000 + x["track"] * 10 + int(x["type"] == "beatfx")
        ),
    )
    for e in events_sorted:
        e = e.copy()

        # test if we moved ahead in time. Whether it's a new measure/note/rest anything. If so, emit a wait token
        if e["start"] > t:
            if t > 0:
                # ignore the first wait
                # yes. calculate how much time we advanced
                wait_time = e["start"] - t
                # append the WAIT token for amount of time advancement
                body_tokens.append("wait:%s" % wait_time)
                # remember old start value
            t = e["start"]
        if e["type"] == "measure":
            # w_events.append(e)
            # since the first measure start on beat 1 (960 ticks), this also removes the unnecesary wait960
            t = e["start"]
            body_tokens.extend(e["tokens"])
        if e["type"] == "note" or e["type"] == "rest":
            effects = []
            if e["type"] == "note":
                tuning_for_string = strings[
                    e["string"] - 1
                ]  # Assuming 1-based index                # note has effects. append them after the note
                effects = e["effects"]
                # del e["start"]
                del e["effects"]
                # append the NOTE  token
                # w_events.append(e)
                note_token = (
                    f"{e['instrument_prefix']}:note:s{e['string']}:f{e['fret']}"
                )
                if note_tuning:
                    note_token += f":{tuning_for_string}"
                body_tokens.append(note_token)
                # body_tokens.append(
                #     f"{e['instrument_prefix']}:note:s{e['string']}:f{e['fret']}:{tuning_for_string}"
                # )

                if len(effects) > 0:
                    # append the NOTE EFFECTS
                    body_tokens.extend(effects)
                    pass
            elif e["type"] == "rest":
                # append the REST
                # w_events.append(e)
                body_tokens.append("%s:rest" % (e["instrument_prefix"]))
                pass
        if e["type"] == "beatfx":
            # append the BEAT EFFECTS after the notes/rests of that beat
            # w_events.append(e)
            body_tokens.extend(e["effects"])
            pass
    # If the last event has duration information, this becomes the last "wait" token
    if "duration" in e:
        body_tokens.append("wait:%s" % e["duration"])

    # DadaGP v1.1 begin ===>
    # Split some rare tokens into many tokens
    body_tokens_v1_1 = []
    for token in body_tokens:
        body_tokens_v1_1.extend(split_rare_token(token))
    # <=== DadaGP 1.1 end

    end_tokens = ["end"]
    all_tokens = head_tokens + body_tokens_v1_1 + end_tokens
    verbose and print("=========\nFirst 20 tokens:")
    verbose and print(all_tokens[:20])
    verbose and print("=========\nTotal tokens:", len(all_tokens))
    return all_tokens


def asdadagp_encode(
    input_file, output_file, note_tuning: bool = False, artist_token: str = "Unknown"
):
    song = gp.parse(input_file)
    # Convert the song to tokens
    tokens = guitarpro2tokens(song, artist_token, verbose=True, note_tuning=note_tuning)
    # Write the tokens to text file
    f = open(output_file, "w")
    f.write("\n".join(tokens))
    f.close()
