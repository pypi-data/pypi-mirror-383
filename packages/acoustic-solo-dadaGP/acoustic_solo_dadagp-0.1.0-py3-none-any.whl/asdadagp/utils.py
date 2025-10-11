from typing import List, Tuple

import guitarpro
import guitarpro as gp

from .const import instrument_groups, supported_times
from .token_splitter import unsplit_fx


def diff(number_list):
    nums = len(number_list)
    if nums <= 1:
        return []
    diff_list = []
    for i in range(0, nums - 1):
        diff_list.append(number_list[i + 1] - number_list[i])
    return diff_list


# Returns the instrument group (string) given the Track object
def get_instrument_group(track):
    midinumber = track.channel.instrument
    if midinumber not in instrument_groups:
        raise ValueError(
            f"Error: Unsupported instrument {midinumber}. Only clean guitar is allowed."
        )
    return "clean"


# Test if the set of strings is a supported guitar tuning. Give it a notename list
# def is_good_guitar_tuning(strings):
#     return True  # Allowing all tunings


def get_tuning_type(instrument_group, strings):
    strnums = [noteNumber(s)[3] for s in strings]
    strdiff = list(diff(strnums))
    return f"{instrument_group}_tuning_{strdiff}"  # Store as a dynamic string


# TUNING FUNCTIONS


# Takes a NoteString like "E4" and gives you a few different representations. Mostly interested in midi_number
def noteNumber(n: str) -> Tuple[int, str, int, int]:
    octave = int(n[-1:])
    pitch_class = n[:-1]
    pitch_value = guitarpro.PitchClass(pitch_class).value
    midi_number = 12 + octave * 12 + pitch_value
    return octave, pitch_class, pitch_value, midi_number


# how many steps did we downtune the guitar?
# Note: dropD or dropAD does not count as downtuning in our representation
# The extra low notes will be represented as frets -2 and -1 on an E-standard-like fretboard
def guitar_downtunage(strings: List[str]) -> int:
    strnums = [noteNumber(s)[3] for s in strings]
    return strnums[0] - 64


# round tempo to nearest 10bpm
def roundtempo(tempo):
    return round(tempo / 10) * 10


def convert_spn_to_common(spn_tuning):
    # Mapping of sharp to flat equivalents
    sharp_to_flat = {"A#": "Bb", "C#": "Db", "D#": "Eb", "F#": "F#", "G#": "Ab"}

    # Convert each note, remove octave numbers
    common_tuning = []
    for note in spn_tuning:
        pitch = note[:-1]  # Remove octave number
        converted = sharp_to_flat.get(pitch, pitch)
        common_tuning.append(sharp_to_flat.get(pitch, pitch))  # Convert if needed

    return common_tuning


# It's important, for resolving token contradictions, that I use the the format measure_name[_params]
# because there should only be one each of "measure_name" token per measure.
def get_measure_tokens(measure):
    measure_tokens = ["new_measure"]
    # if(measure.tempo):
    #    measure_tokens.append("tempo:%s" % roundtempo(measure.tempo.value))
    # measure tempo is fucked and buggy, you should really look at beatEffect.mixTableChange.tempo
    header = measure.header
    if header.tripletFeel.value > 0:
        measure_tokens.append("measure:triplet_feel:%s" % header.tripletFeel.value)
    if header.isRepeatOpen:
        measure_tokens.append("measure:repeat_open")
    if header.repeatAlternative > 0:
        # sometimes this is a large value 16383 or 16384
        # For multiple endings for example endings 1-8
        # However pygp doesn't seem to support this
        print(header.repeatAlternative)
        if header.repeatAlternative <= 255:
            measure_tokens.append(
                "measure:repeat_alternative:%s" % header.repeatAlternative
            )
    if header.repeatClose > 0:
        measure_tokens.append("measure:repeat_close:%s" % header.repeatClose)
    if header.direction:
        measure_tokens.append(
            "measure:direction:%s" % header.direction.name.replace(" ", "")
        )
    if header.fromDirection:
        measure_tokens.append(
            "measure:from_direction:%s" % header.fromDirection.name.replace(" ", "")
        )
    return measure_tokens


# Return the instrument token prefix for notes
# If there are multiple drums tracks, they will all return the same prefix "drums"
# the same goes for leads and pads
def get_instrument_token_prefix(track, tracks_by_group):
    if track in tracks_by_group["clean"]:
        for i, test in enumerate(tracks_by_group["clean"]):
            if track == test:
                return "clean%s" % i
    else:
        print(track)
        assert False, "This track doesn't belong to a group"


# Given a NoteEffect object, returns a list of note effect tokens
def note_effect_list(effect):
    effects = []
    # simple effects true/false
    # accentuatedNote, ghostNote, hammer, heavyAccentuatedNote, letRing, palmMute, staccato, vibrato
    if effect.accentuatedNote:
        effects.append("nfx:accentuated_note")
    if effect.ghostNote:
        effects.append("nfx:ghost_note")
    if effect.hammer:
        effects.append("nfx:hammer")
    if effect.heavyAccentuatedNote:
        effects.append("nfx:heavy_accentuated_note")
    if effect.letRing:
        effects.append("nfx:let_ring")
    if effect.palmMute:
        effects.append("nfx:palm_mute")
    if effect.staccato:
        effects.append("nfx:staccato")
    if effect.vibrato:
        effects.append("nfx:vibrato")
    # complex effects
    if effect.bend:
        # type
        # - 0 nothing
        # - 1 simple bend
        # - 2 bendRelease
        # - 3 bendRelesaeBend
        # - 4 preBend
        # - 5 prebendRelease
        # - 6 Tremolo dip
        # - 7 Dive bar
        # - 8 relesaeUp
        # - 9 invertedDip
        # - 10 return bar
        # - 11 release bar
        # value 100?
        # points:
        # BendPoint (up to 4 bend points)
        # - position
        # - value (0-6) quartertones
        # - vibrato true/false
        # - BendPoint.getTime
        bend = "nfx:bend:type%s" % effect.bend.type.value
        for points in effect.bend.points:
            bend += ":pos%s:val%s:vib%s" % (
                points.position,
                points.value,
                int(points.vibrato),
            )
        effects.append(bend)
    if effect.grace:
        # duration number
        # fret number
        # isDead true/false
        # isOnBeat true/false
        # transition 0,1,2,3
        effects.append(
            "nfx:grace:fret%s:duration%s:dead%s:beat%s:transition%s"
            % (
                effect.grace.fret,
                effect.grace.duration,
                int(effect.grace.isDead),
                int(effect.grace.isOnBeat),
                effect.grace.transition.value,
            )
        )

    if effect.harmonic:
        # type = 1 natural harmonic
        # type = 2 artificial harmonic (pitch.value, octave.quindicesima)
        # type = 3 tapped harmonic
        # type = 4 pinch harmonic
        # type = 5 semi harmonic
        if effect.harmonic.type == 2:
            harmonic = "nfx:harmonic:%s:pitch%s:octave%s" % (
                effect.harmonic.type,
                effect.harmonic.pitch.value,
                effect.harmonic.octave.value,
            )
        elif effect.harmonic.type == 3:
            harmonic = "nfx:harmonic:%s:fret%s" % (
                effect.harmonic.type,
                effect.harmonic.fret,
            )
        else:
            harmonic = "nfx:harmonic:%s" % effect.harmonic.type
        effects.append(harmonic)
    # leftHandFinger -- ignoring it
    # rightHandFinger -- ignoring it
    if effect.slides:
        # you can have multiple slides
        # [<SlideType.shiftSlideTo: 1>]
        """intoFromAbove = -2
        intoFromBelow = -1
        none = 0
        shiftSlideTo = 1
        legatoSlideTo = 2
        outDownwards = 3
        outUpwards = 4
        """
        for slide in effect.slides:
            effects.append("nfx:slide:%s" % slide.value)
    if effect.tremoloPicking:
        # duration (how fast the picking happens)
        effects.append(
            "nfx:tremoloPicking:duration%s" % effect.tremoloPicking.duration.time
        )
    if effect.trill:
        # (switching between two notes really fast)
        # fret number
        # duration (how fast the switching happens)
        effects.append(
            "nfx:trill:fret%s:duration%s"
            % (effect.trill.fret, effect.trill.duration.time)
        )
    return effects


# Calculate the (E-standardized) fret number
# Adjust by tuning and offset and pitch_shift
# Drop tunings use frets -1 and -2
def get_fret(note, track, pitch_shift):
    # note.string -- 1st string is the highest string
    # note.value -- supposedly the fret number but not quite
    # note.realValue -- midinote number (don't use this, it ignores offset)
    # pitch_shift --- the instruments have been downtuned this many pitches
    # track.offset -- there is a capo on this fret
    # len(track.strings) -- number of strings
    # track.strings[0].value -- midinote number of 0th string (highest string)
    string = note.string
    instrument_group = get_instrument_group(track)
    strings = [str(s) for s in track.strings]
    tuning = get_tuning_type(instrument_group, strings)
    drop_shift = 0
    if instrument_group == "bass":
        if tuning == "b4_drop":
            if string == 4:
                drop_shift = 2
    else:
        # everything else is treated like a guitar
        if tuning == "g6_drop" or tuning == "g7_drop":
            if string == 6 or string == 7:
                drop_shift = 2
    return note.value + track.offset - drop_shift


# I'm trying to insert a new beatfx (event) into the current list of events for this measure.
# Test if there are already beatfx of the same type.
# Return a list of non-contradicting beatfx tokens
def oops_theres_a_conflicting_beatfx(new_event, events_this_measure):
    assert (
        new_event["type"] == "beatfx"
    ), "Only notes or rests should call this function"
    # Build a list of non-contracting beatfx tokens
    new_effects = []
    for i, event in enumerate(events_this_measure):
        if (
            event["start"] == new_event["start"]
            and event["type"] == ["beatfx"]
            and event["instrument_prefix"] == new_event["instrument_prefix"]
        ):
            # There was already a beatfx event with effects in the same beat on the same instrument
            # Loop through my new effects, see which ones we can keep
            for b1, effect1 in enumerate(new_event["beatfx"]):
                # because bfx follow the format bfx_name[_params..] we can compare contradictory tokens by name
                es1 = effect1.split(":")
                passes = True
                for b2, effect2 in enumerate(event["beatfx"]):
                    es2 = effect2.split(":")
                    if es1[0] == es2[0] and es1[1] == es2[1]:
                        # There's already a bfx with the same name.
                        # Ignore this effect
                        passes = False
                        break
                if passes:
                    # Ok there were no contradictions
                    new_effects.append(effect1)
    return new_effects


# I'm trying to insert a new note or rest (event) into the current list of events for this measure.
# Test if there is already a note in this spot (same beat/instrument/fret)
# If I'm inserting a note:
#   If there is a note there, return false
#   If there is a rest there, return true, and remove the rest (NOTE: THIS FUNCTION MUTATES events_this_measure)
#   If there is nothing there, return true
# If I'm inserting a rest:
#   If there's a note or rest there, return false
#   If there's nothing there, return true
def oops_theres_a_note_here(new_event, events_this_measure, verbose=False):
    assert new_event["type"] in [
        "note",
        "rest",
    ], "Only notes or rests should call this function"
    # Look through all the events this measure
    # If a conflicting note is discovered, return False
    # If a conflicting rest is discovered, delete it.
    # If there is no conflict, at the end of the loop, return True
    # warning: do not use enumerate, because i'll be using del to remove rest events
    i = 0
    while i < len(events_this_measure):
        event = events_this_measure[i]
        if (
            event["start"] == new_event["start"]
            and event["type"] in ["note", "rest"]
            and event["instrument_prefix"] == new_event["instrument_prefix"]
        ):
            # Found an note or rest at the same time on the same instrument.
            if event["type"] == "note":
                # Found a note
                if new_event["type"] == "rest":
                    # I was trying to insert a rest. Ignore my rest because there's already a note.
                    verbose and print(
                        "I was trying to insert a rest. Ignore my rest because there's already a note."
                    )
                    verbose and print(event, new_event)
                    return False
                if new_event["type"] == "note":
                    if new_event["string"] == event["string"]:
                        # There's already a note on this string. Ignore my note.
                        verbose and print(
                            "There's already a note on this string. Ignore my note."
                        )
                        verbose and print(event, new_event)
                        return False
                    else:
                        # Don't return true yet. There could still be a note on this string.
                        pass
            elif event["type"] == "rest":
                # Found a rest
                if new_event["type"] == "note":
                    # I want to insert a note here.
                    # Remove the rest.
                    verbose and print(
                        " I want to insert a note here. Remove the rest"
                    )  ####
                    # Will this really work I'm kind of scared
                    del events_this_measure[i]
                    continue
                    # careful, this is tricky, deleting elements from a list while iterating
                    # the continue avoids the i += 1 at the end of the loop
                    # Should I return true now to insert my note?
                    # In theory, there would only be a rest here, if there were no other rests and no other notes
                    # return True
                elif new_event["type"] == "rest":
                    # I watn to insert a rest, and there's already a rest here.
                    # Do nothing.
                    verbose and print(
                        "I wanted to insert a rest, but there's already a rest here. "
                    )
                    verbose and print(event, new_event)
                    return False
        # okay now handle cases where a note was already playing on the same instrument
        elif (
            event["type"] in ["note"]
            and event["start"] + event["duration"] > new_event["start"]
            and event["instrument_prefix"] == new_event["instrument_prefix"]
        ):
            # A note was already playing
            if new_event["type"] == "rest":
                # I'm trying to insert a rest, but notes are alread playing.
                # Ignore my new rest.
                verbose and print(
                    "I was trying to insert a rest. There's already a note playing though."
                )
                return False
            elif new_event["type"] == "note":
                # I'm trying to insert a note where a note was already playing
                if event["instrument_prefix"] == "drums":
                    # don't deny the new note. drum hits dont interefere with each other in this way
                    pass
                else:
                    if new_event["string"] == event["string"]:
                        # New note on same string.
                        # Don't deny the new note. Sorry old note, you're getting overwritten.
                        pass
                    else:
                        # A note is already playing on this string.
                        # If I accept the new note, it will silence the old note's ringing out.
                        # This ends up sounding choppy.
                        # Instead, I will let the old note ring out with let_ring note effect
                        # (note: we could also add a repeat of that note, and tie it, to ring it out, but I think this is more complicated)
                        # Add let_ring to the old event's notefx
                        # print("added let_ring")
                        # if "nfx:let_ring" not in event["effects"]:
                        #    event["effects"].append("nfx:let_ring")
                        pass
        i += 1
    return True  # found no conflicts


# It's important to maintain the format of bfx:name(:params..)
# Because we use that to resolve contradictory beatfx tokens


def beat_effect_list(effect):
    effects = []
    # simple effects true/false
    if effect.fadeIn:
        effects.append("bfx:fade_in")
    if effect.hasRasgueado:
        effects.append("bfx:has_rasgueado")
    if effect.vibrato:
        effects.append("bfx:vibrato")
    # complex effects
    # mixTableChange # IGNORE
    if effect.pickStroke.value > 0:
        # 0 (off) 1 (up) 2 (down)
        effects.append("bfx:pick_stroke:%s" % effect.pickStroke.value)
    if effect.slapEffect.value > 0:
        # 0,1,2,3
        effects.append("bfx:slap_effect:%s" % effect.slapEffect.value)
    if effect.stroke.direction.value > 0 and effect.stroke.value > 0:
        # direction: 0 (off) 1 (up) 2 (down)
        # value: an amount of time
        effects.append(
            "bfx:stroke:%s:%s" % (effect.stroke.direction.value, effect.stroke.value)
        )
        # tremoloBar
    if effect.tremoloBar:
        # treat it the same as bend I think ----
        # type
        # - 0 nothing
        # - 1 simple bend
        # - 2 bendRelease
        # - 3 bendRelesaeBend
        # - 4 preBend
        # - 5 prebendRelease
        # - 6 Tremolo dip
        # - 7 Dive bar
        # - 8 relesaeUp
        # - 9 invertedDip
        # - 10 return bar
        # - 11 release bar
        # value 100?
        # points:
        # BendPoint (up to 4 bend points)
        # - position
        # - value (0-6) quartertones
        # - vibrato true/false
        # - BendPoint.getTime
        tremoloBar = "bfx:tremolo_bar:type%s" % effect.tremoloBar.type.value
        for points in effect.tremoloBar.points:
            tremoloBar += ":pos%s:val%s:vib%s" % (
                points.position,
                points.value,
                int(points.vibrato),
            )
        effects.append(tremoloBar)
    # TEMPO
    if effect.mixTableChange and effect.mixTableChange.tempo:
        # if(effect.mixTableChange.tempo.value != tempo):
        # could be a change in tempo, or could be the same tempo. no harm if it's the same tempo.
        effects.append(
            "bfx:tempo_change:%s" % roundtempo(effect.mixTableChange.tempo.value)
        )
        if effect.mixTableChange.tempo.duration > 0:
            # start speeding up or slowing down into the next tempo marker
            # the duration amount doesn't really matter
            # because it always goes until the next tempo marker
            effects.append("bfx:tempo_interpolation")
    return effects


# Converts a list of NoteNames to a list of GuitarString pyguitarpro objects
def convert_strings_for_pygp(strings, pitch_shift=0):
    gs = []
    for i, x in enumerate(strings):
        note_number = int(noteNumber(x)[3]) + int(pitch_shift)
        gs.append(gp.GuitarString(number=i + 1, value=note_number))
    return gs


# time duration may be an int or Fraction
# if it is a supported time duration, it will return itself
# if it is not, it will find a neighboring duration that is supported
def convert_to_nearest_supported_time(x):
    if x == 0:
        return 0
    for i in range(1, len(supported_times)):
        t = supported_times[i]
        if t > x:
            t_larger = t
            t_smaller = supported_times[i - 1]
            if t_larger - x < x - t_smaller:
                return t_larger
            else:
                return t_smaller
    # x is too large.
    # return the max(?)
    return 5760


# take a list of bfx tokens and modify the beateffect
# give it beat.effect and a list
def tokens_to_beat_effect(effect, bfx_tokens):
    for token in bfx_tokens:
        # DadaGP v1.1 begin ====>
        token = unsplit_fx(
            token
        )  # convert v1.1 format (dict with param tokens) to v1.0 (long string)
        # <==== DadaGP v1.1 end

        t = token.split(":")
        if t[0] != "bfx":
            # the first part of the token should be bfx, if it's not, it shouldn't be here, ignore it
            print("This token shouldn't be here, it's not a BFX", token)
            continue
        if t[1] == "fade_in":
            effect.fadeIn = True
        elif t[1] == "has_rasgueado":
            effect.hasRasgueado = True
        elif t[1] == "vibrato":
            effect.vibrato = True
        elif t[1] == "pick_stroke":
            effect.pickStroke = gp.BeatStroke()
            effect.pickStroke.direction = gp.BeatStrokeDirection(int(t[2]))
        elif t[1] == "slap_effect":
            effect.slapEffect = gp.SlapEffect(int(t[2]))
        elif t[1] == "stroke":
            effect.stroke = gp.BeatStroke()
            effect.stroke.direction = gp.BeatStrokeDirection(int(t[2]))
            effect.stroke.value = int(t[3])
        elif t[1] == "tremolo_bar":
            effect.tremoloBar = gp.BendEffect()
            effect.tremoloBar.type = gp.BendType(int(t[2][4:]))
            # tremoloBar += ":pos%s:val%s:vib%s" % (points.position, points.value, int(points.vibrato))
            effect.tremoloBar.points = []
            effect.tremoloBar.value = 50
            # should only be a multiple of 3
            assert len(t) % 3 == 0, "Tremolo effect token has a typo. %s" % token
            num_points = int((len(t) - 3) / 3)
            # for each triplet, create a point:
            for p in range(num_points):
                point = guitarpro.models.BendPoint()
                point.position = int(t[3 + p * 3][3:])
                point.value = int(t[4 + p * 3][3:])
                point.vibrato = t[5 + p * 3][3:] == 1
                effect.tremoloBar.points.append(point)
        elif t[1] == "tempo_change":
            if not effect.mixTableChange:
                # if there's no mixTableChange on this effect, add it
                effect.mixTableChange = gp.MixTableChange()
            if not effect.mixTableChange.tempo:
                # default: zero duration means no change in tempo
                effect.mixTableChange.tempo = gp.MixTableItem(
                    value=int(t[2]), duration=0, allTracks=False
                )
            effect.mixTableChange.tempo.value = int(t[2])
        elif t[1] == "tempo_interpolation":
            if not effect.mixTableChange:
                effect.mixTableChange = gp.MixTableChange()
            if not effect.mixTableChange.tempo:
                # the default tempo needs to be whatever the current tempo is
                # I don't know what it is inside of this function.
                # There needs to be another runthrough that corrects these values.
                effect.mixTableChange.tempo = gp.MixTableItem(
                    value=120, duration=0, allTracks=False
                )
            # this acceleration/deceleration is supposed to last until the next tempo marker
            # I don't know how long that is, from inside of this function.
            # There needs to be another runthrough that corrects the current tempo and duration
            effect.mixTableChange.tempo.duration = 1


# take a list of nfx tokens and modify the note effect
# give it note and a list
def tokens_to_note_effect(note, nfx_tokens):
    effect = note.effect
    for token in nfx_tokens:
        # DadaGP v1.1 begin ====>
        token = unsplit_fx(
            token
        )  # convert v1.1 format (dict with param tokens) to v1.0 (long string)
        # <==== DadaGP v1.1 end
        t = token.split(":")
        if t[0] != "nfx":
            # the first part of the token should be nfx, if it's not, it shouldn't be here, ignore it
            print("This token shouldn't be here, it's not a NFX", token)
            continue
        if t[1] == "tie":
            note.type = gp.NoteType(2)
        elif t[1] == "dead":
            note.type = gp.NoteType(3)
        elif t[1] == "accentuated_note":
            effect.accentuatedNote = True
        elif t[1] == "ghost_note":
            effect.ghostNote = True
        elif t[1] == "hammer":
            effect.hammer = True
        elif t[1] == "heavy_accentuated_note":
            effect.heavyAccentuatedNote = True
        elif t[1] == "let_ring":
            effect.letRing = True
        elif t[1] == "palm_mute":
            effect.palmMute = True
        elif t[1] == "staccato":
            effect.staccato = True
        elif t[1] == "vibrato":
            effect.vibrato = True
        elif t[1] == "bend":
            # print("bend effect")
            effect.bend = gp.BendEffect()
            effect.bend.type = gp.BendType(int(t[2][4:]))
            # bend += ":pos%s:val%s:vib%s" % (points.position, points.value, int(points.vibrato))
            effect.bend.points = []
            effect.bend.value = 50
            # should only be a multiple of 3
            assert len(t) % 3 == 0, "Bend effect token has a typo. %s" % token
            num_points = int((len(t) - 3) / 3)
            # for each triplet, create a point:
            for p in range(num_points):
                point = guitarpro.models.BendPoint()
                point.position = int(t[3 + p * 3][3:])
                point.value = int(t[4 + p * 3][3:])
                point.vibrato = int(t[5 + p * 3][3:]) == 1
                effect.bend.points.append(point)
            # print(effect.bend)
        elif t[1] == "grace":
            # duration number
            # fret number
            # isDead true/false
            # isOnBeat true/false
            # transition 0,1,2,3
            # effects.append("nfx:grace:fret%s:duration%s:dead%s:beat%s:transition%s" % (effect.grace.fret,
            #                                                                        effect.grace.duration,
            #                                                                        int(effect.grace.isDead),
            #                                                                        int(effect.grace.isOnBeat),
            #                                                                        effect.grace.transition.value))
            effect.grace = gp.GraceEffect()
            # print(token)
            # print(int(t[2][4:]))
            effect.grace.fret = max(
                0, int(t[2][4:])
            )  # sometimes fret can be below zero?
            effect.grace.duration = int(t[3][8:])
            effect.grace.isDead = int(t[4][4:])
            effect.grace.isOnBeat = int(t[5][4:])
            effect.grace.transition = gp.GraceEffectTransition(int(t[6][10:]))
        elif t[1] == "harmonic":
            harmonic_type = int(t[2])
            if harmonic_type == 1:
                effect.harmonic = gp.NaturalHarmonic()
            elif harmonic_type == 2:
                effect.harmonic = gp.ArtificialHarmonic()
                effect.harmonic.pitch = gp.PitchClass(int(t[3][5:]))
                effect.harmonic.octave = gp.Octave(int(t[4][6:]))
            elif harmonic_type == 3:
                fret = int(t[3][4:])
                effect.harmonic = gp.TappedHarmonic(fret=fret)
            elif harmonic_type == 4:
                effect.harmonic = gp.PinchHarmonic()
            elif harmonic_type == 5:
                effect.harmonic = gp.SemiHarmonic()
        elif t[1] == "slide":
            slide = gp.SlideType(int(t[2]))
            effect.slides.append(slide)
        elif t[1] == "tremolo_picking":
            effect.tremoloPicking = gp.TremoloPickingEffect()
            effect.tremoloPicking.duration = gp.Duration.fromTime(int(t[2][8:]))
            print(token)
        elif t[1] == "trill":
            effect.trill = gp.TrillEffect()
            effect.trill.fret = int(t[2][4:])
            effect.trill.duration = gp.Duration.fromTime(int(t[3][8:]))
