import math
import os
from fractions import Fraction

import guitarpro
import guitarpro as gp

from .utils import (
    convert_strings_for_pygp,
    convert_to_nearest_supported_time,
    tokens_to_beat_effect,
    tokens_to_note_effect,
)

SCRIPTS_PATH = os.path.dirname(os.path.abspath(__file__))


from typing import List, Union

from .processor import pre_decoding_processing


# Given a list of tokens, constructs a guitarpro song object
def tokens2guitarpro(
    all_tokens: List[str], verbose: bool = False, tunings: Union[None, List[str]] = None
):
    # Interpret a token list back into a GP song file
    ## TODO: some kinda validation/flexibility for weird files the net generates?
    ## For now let's just support valid dataset files
    head = all_tokens[:4]
    body = all_tokens[4:]
    artist_token = head[0]
    assert head[1].split(":")[0] == "downtune"
    assert head[2].split(":")[0] == "tempo"
    assert head[3] == "start"
    initial_tempo = int(head[2].split(":")[1])
    pitch_shift = int(head[1].split(":")[1])
    verbose and print(artist_token, initial_tempo, pitch_shift)

    ###########
    ## Instruments / Strings / Droptuning
    ## Check which instruments we got

    instrument_check = {"clean0": False, "clean1": False}
    for token in body:
        tokensplit = token.split(":")
        if len(tokensplit) > 1 and tokensplit[1] == "note":
            instrument = tokensplit[0]
            assert instrument in instrument_check.keys(), (
                "Unknown instrument %s" % instrument
            )
            instrument_check[instrument] = True
    verbose and print(instrument_check)

    instrument_stringinfo = {
        "clean0": False,
        "clean1": False,
    }

    for instrument in instrument_stringinfo:
        if not instrument_check[instrument]:
            # this instrument doesn't exist in the score
            continue

        else:
            # everything else
            ## Guitars / Pads / Leads info
            # Check which strings we got
            # "g6_standard", "g7_standard", "g6_drop", "g7_drop"
            # Treat all like guitar

            strings = 6
            drop_tuning = False

            # Note: Strings are 1-indexed
            string_count = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0, 7: 0}
            for token in body:
                t = token.split(":")
                if len(t) > 1 and t[1] == "note" and t[0] == instrument:
                    string = int(t[2][1:])  # ex "s4"
                    fret = int(t[3][1:])  # ex "f5"
                    if fret == -1 or fret == -2:
                        if string == 6 or string == 7:
                            drop_tuning = True
                        else:
                            assert False, "Drop tuning only allowed on string 6 and 7"
                    string_count[string] += 1
            # print(string_count)
            if string_count[7] > 0:
                # it's a 7 string, it has the low string (strings 1,2,3,4,5,6,7)
                strings = 7
            else:
                # it's a 6 string (strings 1,2,3,4,5,6)
                strings = 6
            instrument_stringinfo[instrument] = {
                "drop_tuning": drop_tuning,
                "strings": strings,
            }

    verbose and print(instrument_stringinfo)

    ##########
    ## READ MEASURES

    ## Interpret the body tokens into a dictionary object

    ## Group the body into measures
    ## Each measure has measure_tokens
    ## Group each measure into tracks (by instrument)
    ## Each track is a list of beats with a clock time
    ## Each beat has beat effects (bfx) and a list of notes
    ## Each note has note effects (nfx) and a note token

    all_measures = []
    this_measure = {}

    clock = 960  # increments whenever we see a wait
    # clock starts at 960 for some reason??? 1-indexed quarter notes i guess

    current_note = None
    current_beat = None
    current_effect = None
    orphaned_nfx = []
    orphaned_bfx = []

    # If notes appear that have no duration (they are not followed by wait token before the end of the measure)
    # use this value for their duration:
    last_reported_duration = 480
    # clocktime of the last beat we iterated over
    last_reported_beat_clock = 480

    for i, token in enumerate(body):
        # Check if this measure has ended
        if token in ["end", "new_measure"] and len(this_measure):
            # End of measure. Wrap it up
            # move the old measure to all_measures
            all_measures.append(this_measure)
            # If there was a previous measure with notes, and it ended with notes and no wait token
            # We could do nothing and drop those notes, or we could give them an arbitary duration
            # ..by moving the clock forward here by some arbitrary amount
            if last_reported_beat_clock == clock:
                if last_reported_duration == 0:
                    # defeats the purpose to move it ahead by zero
                    # this is a failsafe, just in case the calculation failed in a corner case
                    last_reported_duration = 480
                # move the clock ahead
                clock += last_reported_duration
        # Ok now deal with the next token
        if token == "end":
            # End of the song
            break
        if token == "new_measure":
            # starting a new measure
            this_measure = {"trackbeats": {}, "measure_tokens": [], "clock": clock}
            # reset
            current_note = None
            current_beat = None
            current_effect = None
            orphaned_nfx = []
            orphaned_bfx = []
        else:
            # In the middle of a measure
            # this_measure["tokens"].append(token)
            t = token.split(":")
            if t[0] == "measure":
                # measure token
                # these are supposed to only be at the very beginning
                # (but if they appear somewhere in the middle of the measure that might be ok?)
                # Measure tokens are of the format measure:type[:params]
                # Per measure there can only be one of each type of measure token
                # Check if that type already exists
                passed = True
                for mt in this_measure["measure_tokens"]:
                    if mt.split(":")[1] == t[1]:
                        # this type is already here, ignore it
                        verbose and print("Measure Token contradiction", mt, token)
                        passed = False
                if passed:
                    # No contradictions, add the token
                    this_measure["measure_tokens"].append(token)
            elif len(t) > 1 and (t[1] == "note" or t[1] == "rest"):
                # we have encountered a new note or rest token
                # (technically a rest can't co-exist with a note in the same instrument_beat.. but hmm)
                instrument = t[0]

                current_note = {"token": token, "nfx": []}
                current_effect = None

                # Experimental: If there were orphaned nfx, attach them now
                if len(orphaned_nfx):
                    current_note["nfx"] = orphaned_nfx
                orphaned_nfx = []

                if not instrument in this_measure["trackbeats"]:
                    # first time this instrument appeared in this measure
                    this_measure["trackbeats"][instrument] = {}

                if not clock in this_measure["trackbeats"][instrument]:
                    # first time this instrument appeared in this measure at this clocktime
                    # that means it's a new beat
                    current_beat = {"bfx": [], "notes": []}
                    this_measure["trackbeats"][instrument][clock] = current_beat
                    # Experimental: If there were orphaned bfx, attach them now
                    if len(orphaned_bfx):
                        current_beat["bfx"] = orphaned_bfx
                    orphaned_bfx = []

                # add the note to the beat
                this_measure["trackbeats"][instrument][clock]["notes"].append(
                    current_note
                )

                # calculate the latest time difference between beats
                if clock - last_reported_beat_clock == 0:
                    # same beat, no time difference occured, skip for now
                    pass
                else:
                    # a time difference occured!
                    # the last duration is this beat's clock minus the last beat's clock
                    # warning: this definition of duration is inter-instrument (time since the last beat of any instrument)
                    last_reported_duration = clock - last_reported_beat_clock
                # remember this beat's clocktime for later
                last_reported_beat_clock = clock

            elif t[0] == "nfx":
                current_effect = {"token": token, "params": []}
                if current_note:
                    # great we know what note this effect belongs to
                    current_note["nfx"].append(current_effect)
                else:
                    # uhh this token is out of place.
                    # we could just skip it
                    # verbose and print("warning: nfx token doesn't belong to a note", token)
                    # OR we could attach to the next note like so:
                    orphaned_nfx.append(current_effect)
            elif t[0] == "bfx":
                current_effect = {"token": token, "params": []}
                if current_beat:
                    # great we know what beat this effect belongs to
                    # Now we are no longer attached to a particular note
                    # actually I guess that is optional. A beat effect could appear between a note and notefx i guess.
                    # current_note = None
                    current_beat["bfx"].append(current_effect)
                else:
                    # uhh this token is out of place.
                    # verbose and print("warning: bfx token doesn't belong to a beat", token)
                    # we could skip it
                    # OR we could attach to the next beat like so:
                    orphaned_bfx.append(current_effect)
            elif t[0] == "param":
                if current_effect:
                    # great we know what effect this param belongs to
                    current_effect["params"].append(token)
                else:
                    # uhh this token is out of place. skip it
                    verbose and print(
                        "warning: param token doesn't belong to an effect", token
                    )
            elif t[0] == "wait":
                # wait token can come any time inside a measure
                # it resets the beat/note, and we may move to a new beat/note
                current_beat = None
                current_note = None
                current_effect = None
                time = int(t[1])
                clock += time  # move the clock upward

    final_clock = clock
    verbose and print("Final clock:", final_clock)
    verbose and print("=======\nFirst measure")
    verbose and print(all_measures[0])

    ###########
    ## NEW GP FILE
    # CREATE a new GP5 file from BLANKGP5

    ## LOAD the BLANK GP5 SCORE
    blankgp5 = gp.parse(os.path.join(SCRIPTS_PATH, "blank.gp5"))
    blankgp5.tracks = []
    blankgp5.tempo = initial_tempo

    # Determine the order the tracks will come in
    track_numbering = []
    for i in instrument_check:
        if instrument_check[i]:
            track_numbering.append(i)
    verbose and print(track_numbering)

    #############
    # Creating the GP Instrument Tracks

    # Most common instruments in dataset:
    # 30     47073   Distortion Guitar
    # 29     21111   Overdriven Guitar
    # 33     18085   Electric Bass (finger)
    # 34     12438   Electric Bass (pick)
    # 25     11933   Acoustic Guitar (steel)
    # 24     10201   Acoustic Guitar (nylon)
    # 27     8483    Electric Guitar (clean)
    # 48     5606    String Ensemble 1
    # 26     4453    Electric Guitar (jazz)
    # 0      4047    Acoustic Grand Piano
    # 52     2546    Choir Aahs
    # 81     2009    Lead 2 (sawtooth)
    verbose and print("pitch_shift", pitch_shift)
    blankgp5.tracks = []
    for i, instrument in enumerate(track_numbering):
        verbose and print(i, instrument)
        new_track = gp.Track(blankgp5)
        new_track.number = i + 1  # track numbers are 1-indexed
        new_track.offset = 0
        # there used to be a bug here when loading 9 instruments (because channels 16 and 17 were used)
        # This should only be values 0-15
        new_track.channel.channel = i
        # im not sure about this, but seems to work ok
        new_track.channel.effectChannel = max(15, 9 + i)
        if instrument == "clean0":
            new_track.channel.instrument = 27  # Electric Guitar (clean)
            # new_track.color = gp.Color(r=255, g=150, b=100, a=1)
            new_track.color = gp.Color(r=255, g=150, b=100)
            new_track.name = "Clean Guitar"
        elif instrument == "clean1":
            new_track.channel.instrument = 26  # Electric Guitar (jazz)
            # new_track.color = gp.Color(r=255, g=180, b=100, a=1)
            new_track.color = gp.Color(r=255, g=180, b=100)
            new_track.name = "Clean Guitar 2"
        else:
            assert False, "Unsupported instrument"
        # Now set the strings
        drop = instrument_stringinfo[instrument]["drop_tuning"]
        n_strings = instrument_stringinfo[instrument]["strings"]
        if tunings:
            strings = tunings
        else:
            if n_strings == 6:
                if drop:
                    strings = ["E5", "B4", "G4", "D4", "A3", "D3"]
                else:
                    strings = ["E5", "B4", "G4", "D4", "A3", "E3"]
            elif n_strings == 7:
                if drop:
                    strings = ["E5", "B4", "G4", "D4", "A3", "D3", "A2"]
                else:
                    strings = ["E5", "B4", "G4", "D4", "A3", "E3", "B2"]
        new_track.strings = convert_strings_for_pygp(strings, pitch_shift)

        blankgp5.tracks.append(new_track)

    #################
    ## BUILD THE MEASURES

    # Blank the measures
    blankgp5.measureHeaders = []
    for t, track in enumerate(blankgp5.tracks):
        track.measures = []

    # Now build the measures

    # tempo = initial_tempo
    for m, measure in enumerate(all_measures):
        # the time of the begining of the mesaure
        measure_clock = measure["clock"]
        # the time at the end of the measure
        if m < len(all_measures) - 1:
            # Subtract the measure start time from the next measure start time
            end_measure_clock = all_measures[m + 1]["clock"]
        else:
            # Last measure, subtract the measure start time from the total length
            end_measure_clock = final_clock
            # create a measure header
        header = (
            guitarpro.models.MeasureHeader()
        )  # same header for every track's same measure?
        header.start = measure["clock"]
        # use the measure tokens to change the parameters of the header
        for measure_token in measure["measure_tokens"]:
            mt = measure_token.split(":")
            if mt[0] == "measure":
                # all measure tokens begin like this
                # If contradicting measure tokens exist, the later one will overwrite the previous one
                if mt[1] == "triplet_feel":
                    header.tripletFeel = gp.TripletFeel(int(mt[2]))
                elif mt[1] == "repeat_open":
                    header.isRepeatOpen = True
                elif mt[1] == "repeat_alternative":
                    header.repeatAlternative = int(mt[2])
                elif mt[1] == "repeat_close":
                    header.repeatClose = int(mt[2])
                elif mt[1] == "direction":
                    header.direction = int(mt[2])
                elif mt[1] == "from_direction":
                    header.fromDirection = int(mt[2])
        # Get the measure length
        measure_duration = end_measure_clock - measure_clock

        if measure_duration == 0:
            # flexibility
            # raise Exception("measure duration zero")
            continue
        # quarterTime = 960*4
        # round down to the nearest 32th measure_duration
        thirtysecondths = math.floor(measure_duration / 120)
        # Now find the simplest fraction
        signature = Fraction(thirtysecondths, 32)
        n = signature.numerator
        d = signature.denominator

        # We don't want measures of 1:1.. we want 4:4 instead. Minimum dominator is 4
        if d == 2:
            n *= 2
            d *= 2
        elif d == 1:
            n *= 4
            d *= 4

        # print(n,d, n/d)
        # numerator cannot be greater than 32
        # if it is above 32, try to round down to a simpler fraction
        while n > 32:
            n -= 1
            signature = Fraction(n, d)
            n = signature.numerator
            d = signature.denominator
            # We don't want measures of 1:1.. we want 4:4 instead. Minimum dominator is 4
            if d == 2:
                n *= 2
                d *= 2
            elif d == 1:
                n *= 4
                d *= 4
        # print(n,d, n/d)
        # finally, if all else fails, force it to be 32 max
        n = min(32, n)
        # print(n,d, n/d)

        # timesignatures can go down to 32ths
        d = guitarpro.models.Duration(value=d)
        header.timeSignature = guitarpro.models.TimeSignature(
            numerator=n, denominator=d
        )
        print("measure_clock", measure_clock, end_measure_clock, final_clock)
        print(
            "Measure:",
            m,
            "TS:",
            n,
            "/",
            d,
            "measure_duration",
            measure_duration,
            "thirtysecondths",
            thirtysecondths,
        )
        # header.tempo = tempo # don't use mesaureHeader.tempo it's fucked
        blankgp5.addMeasureHeader(header)

        ##########
        # TRACKS
        for t, track in enumerate(blankgp5.tracks):
            # create a measure
            gp_measure = guitarpro.models.Measure(track, header)
            gp_measure.start = measure["clock"]
            # This creates two voices, ignore the second
            gp_voice = gp_measure.voices[0]
            instrument = track_numbering[t]
            if instrument in measure["trackbeats"]:
                # this instrument is present in this measure
                beats = measure["trackbeats"][instrument]
                clocks = list(beats.keys())
                # print("beats", beats)

                # Check if the first beat is also the measure start
                if len(clocks) > 0 and gp_measure.start != clocks[0]:
                    # The first beat is not the measure start
                    # So we need to insert the initial rest
                    initial_rest = {
                        "notes": [{"token": instrument + ":rest"}],
                        "bfx": [],
                    }
                    beats[gp_measure.start] = initial_rest
                    clocks.insert(0, gp_measure.start)
                    # okay continue as usual

                ## BEATS
                for b, clock in enumerate(clocks):
                    beat = beats[clock]
                    if b < len(clocks) - 1:
                        # print("next event is the next beat", clock, clocks[b+1])
                        # the next event in this track is the next beat in this measure
                        duration = clocks[b + 1] - clock
                    else:
                        # the next event in this track is the next measure
                        duration = end_measure_clock - clock
                    # create the guitarpro beat object
                    gp_beat = guitarpro.models.Beat(gp_voice)

                    if duration == 0:
                        # This beat has zero duration for some reason
                        # It shouldn't have zero duration, it accidentally got this way somehow
                        # In this case, just ignore the beat entirely
                        # gp_beat.duration = 0
                        # raise Exception("beat duration zero")
                        continue
                    else:
                        try:
                            # Handy function for converting clock duration to its equivalent notelength/dotted/tuplet
                            # This function might fail if the model generates a weird time combination
                            gp_beat.duration = gp.models.Duration.fromTime(duration)
                            # print(duration, m, len(all_measures), b, len(clocks))
                        except:
                            # It's anweird duration
                            # Instead round it to the nearest supported time
                            new_time = convert_to_nearest_supported_time(duration)
                            gp_beat.duration = gp.models.Duration.fromTime(new_time)

                            verbose and print(
                                "Duration Conversion Measure %s, Track %s: %s => %s"
                                % (m, t, duration, new_time)
                            )
                            # todo:
                            # Instead of rounding, maybe it's better to split it into multiple beats to additively reach the duration
                            # Notes get ties
                            # Rests double up

                    bfx_tokens = beat["bfx"]
                    ## Modify Beat.Effect with beat effect tokens
                    tokens_to_beat_effect(gp_beat.effect, bfx_tokens)

                    gp_beat.start = clock
                    ## NOTES
                    for n, note in enumerate(beat["notes"]):
                        # print(instrument, note)
                        # Could be note or rest
                        note_info = note["token"].split(":")
                        assert note_info[0] == instrument
                        if note_info[1] == "rest":
                            # rest
                            # do nothing. at the end of the beat we'll figure out what type of beat it was (normal, rest)
                            continue
                        elif note_info[1] == "note":
                            if instrument != "drums":
                                # a non-drum note
                                string = int(note_info[2][1:])  # s4
                                fret = int(note_info[3][1:])  # f0, f20, f-2, etc

                                # get information about the instrument tuning type
                                stringinfo = instrument_stringinfo[instrument]
                                # if this is on a drop string the fret value has to be +2
                                if stringinfo["drop_tuning"]:
                                    if instrument == "bass":
                                        if string == 5 or string == 6:
                                            fret += 2
                                    else:
                                        if string == 6 or string == 7:
                                            fret += 2
                                # 4 and 5 string basses start on string2 in token format, bring it back to string1 for GP
                                if instrument == "bass" and stringinfo["strings"] < 6:
                                    string -= 1

                                ## TODO: PLEASE DOUBLE CHECK NO TWO NOTES ON SAME STRING.
                                ignore = False
                                for notes2 in gp_beat.notes:
                                    if notes2.string == string:
                                        # note already on string. ignore this note
                                        ignore = True
                                        break
                                if ignore:
                                    continue
                            # create the guitarpro note object
                            gp_note = guitarpro.models.Note(gp_beat)
                            gp_note.string = string
                            gp_note.value = fret
                            gp_note.type = gp.NoteType(1)
                            nfx = note["nfx"]
                            ## Add nfx to gp_note
                            tokens_to_note_effect(gp_note, nfx)
                            # Add the note to the list of notes
                            gp_beat.notes.append(gp_note)
                    # Okay we're done adding notes (if there were any)
                    # If there were notes, change the beat status to "normal"
                    # If there were no notes, change the beat status to "rest"
                    if len(gp_beat.notes) == 0:
                        gp_beat.status = guitarpro.BeatStatus.rest
                    else:
                        gp_beat.status = guitarpro.BeatStatus.normal
                    gp_voice.beats.append(gp_beat)
            else:
                # this instrument isn't present in this measure
                pass
            track.measures.append(gp_measure)  # append it to gp_measure

    verbose and print("Measures:", (len(blankgp5.measureHeaders)))
    verbose and print("Measures:", (len(blankgp5.tracks[0].measures)))
    #########
    ### DONE
    # print(blankgp5.tracks[8].measures[0].voices[0].beats[0].notes[2])
    return blankgp5


# tokens --> guitarpro
def asdadagp_decode(input_file, output_file):
    text_file = open(input_file, "r")
    tokens = text_file.read().split("\n")

    processed_tokens, tunings = pre_decoding_processing(tokens)

    # Convert the tokens to a song
    song = tokens2guitarpro(tokens, verbose=True, tunings=tunings)
    # Appears at the top of the GP score
    song.artist = tokens[0]
    song.album = "Generated by DadaGP"
    song.title = "untitled"
    guitarpro.write(song, output_file)  # GP file transcoded into tokens and back again
