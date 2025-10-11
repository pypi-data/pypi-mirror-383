import os
from typing import List

import guitarpro as gp
import pytest
from asdadagp.encoder import guitarpro2tokens
from asdadagp.processor import (
    get_string_tunings,
    measures_playing_order,
    repeat_related_measure_indices,
    split_tokens_to_measures,
    tokens_to_measures,
    tracks_check,
)

DATA_FOLDER_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "tests", "data"
)


@pytest.fixture
def celtic_tuning_gp_path():
    return os.path.join(DATA_FOLDER_PATH, "bensusan_pierre-dame_lombarde.gp5")


@pytest.fixture
def multi_tracks_gp_path():
    return os.path.join(DATA_FOLDER_PATH, "dyens-roland-la_bicyclette.gp4")


@pytest.fixture
def multi_track_tokens(multi_tracks_gp_path):
    song = gp.parse(multi_tracks_gp_path)
    tokens = guitarpro2tokens(song, "unknown", verbose=True, note_tuning=True)
    return tokens


@pytest.fixture
def repeat_bars_gp_path():
    # https://www.songsterr.com/a/wsa/leo-brouwer-un-dia-de-noviembre-classical-guitar-tab-s903099
    return os.path.join(DATA_FOLDER_PATH, "brower-leo-un_dia_de_noviembre.gp4")


@pytest.fixture
def repeat_bars_tokens(repeat_bars_gp_path):
    song = gp.parse(repeat_bars_gp_path)
    tokens = guitarpro2tokens(song, "unknown", verbose=True, note_tuning=True)
    return tokens


def test_get_string_tunings(celtic_tuning_gp_path, multi_tracks_gp_path):
    def gp_file_tuning(
        gp_path: str,
        correct_tuning: List[str],
        note_tuning: bool = True,
    ):
        song = gp.parse(gp_path)
        tokens = guitarpro2tokens(
            song, "unknown", verbose=True, note_tuning=note_tuning
        )
        tuning_results = get_string_tunings(tokens)
        assert (
            tuning_results == correct_tuning
        ), f"Expected {correct_tuning}, got {tuning_results}"

    celtic_tunings = [
        "D4",
        "A3",
        "G3",
        "D3",
        "A2",
        "D2",
    ]
    # celtic_tunings = ["D5", "A4", "G4", "D4", "A3", "D3"]

    dyens_tuning = ["E4", "B3", "G3", "D3", "G2", "F2"]
    # dyens_tuning = ["E5", "B4", "G4", "D4", "G3", "F3"]
    gp_file_tuning(
        celtic_tuning_gp_path,
        celtic_tunings,
        note_tuning=True,
    )
    gp_file_tuning(
        celtic_tuning_gp_path,
        celtic_tunings,
        note_tuning=False,
    )

    gp_file_tuning(
        multi_tracks_gp_path,
        dyens_tuning,
        note_tuning=True,
    )
    gp_file_tuning(
        multi_tracks_gp_path,
        dyens_tuning,
        note_tuning=False,
    )


def test_extra_track_merge(multi_track_tokens):
    sound_notes = [
        token
        for token in multi_track_tokens
        if token.startswith("clean") and "note" in token
    ]

    processed_tokens = tracks_check(multi_track_tokens)
    assert isinstance(processed_tokens, list)
    processed_sound_note = [
        token for token in processed_tokens if token.startswith("note")
    ]

    assert len(sound_notes) == len(
        processed_sound_note
    )  # Ensure no tokens are lost in processing


def test_extra_tracks_removal(multi_track_tokens):
    main_track = [token for token in multi_track_tokens if token.startswith("clean0")]
    main_track_notes = [token for token in main_track if "note" in token]

    processed_tokens = tracks_check(multi_track_tokens, False)
    assert isinstance(processed_tokens, list)
    processed_sound_note = [
        token for token in processed_tokens if token.startswith("note")
    ]

    assert len(main_track_notes) == len(
        processed_sound_note
    )  # Ensure no tokens are lost in processing

    assert len(main_track) == len(processed_sound_note) + processed_tokens.count("rest")


def test_split_measures(repeat_bars_tokens):
    # 77 bars + header
    measure_tokens = split_tokens_to_measures(repeat_bars_tokens)
    assert len(measure_tokens) == 78

    processed_tokens = tracks_check(repeat_bars_tokens, True)
    processed_measure_tokens = split_tokens_to_measures(processed_tokens)
    assert len(processed_measure_tokens) == 78


def test_measures(repeat_bars_tokens):
    print(len(repeat_bars_tokens))
    print(repeat_bars_tokens[-10:])

    measures = tokens_to_measures(repeat_bars_tokens)
    assert len(measures) == 77

    all_instrumental_tokens = [t for measure in measures for t in measure.tokens]
    assert len(all_instrumental_tokens) == 1129

    opens, closes, alternatives = repeat_related_measure_indices(measures)
    assert opens == [1, 9, 28]
    assert closes == [8, 25, 49]
    assert alternatives == [25, 26, 49, 50]

    measure_play_order = measures_playing_order(measures)
    assert len(measure_play_order) == 122

    assert measure_play_order == [0] + list(range(1, 9)) + list(range(1, 9)) + list(
        range(9, 26)
    ) + list(range(9, 25)) + [26, 27] + list(range(28, 50)) + list(
        range(28, 49)
    ) + list(
        range(50, 77)
    )

    play_order_tokens = measures_playing_order(measures, tokens=True)
    assert len(play_order_tokens) == 122


def test_alternative_endings():
    """Test how the system handles repeat structures with alternative endings."""

    # Structure: Intro -> Verse (repeat) -> Chorus (repeat with alternatives) -> Outro
    tokens = [
        "artist",
        "downtune:0",
        "tempo:90",
        "start",  # Header
        "new_measure",  # Measure 0: Intro
        "note:s1:f0:E5",
        "wait:480",
        "new_measure",  # Measure 1: Verse start (repeat open)
        "measure:repeat_open",
        "note:s1:f2:F5",
        "wait:480",
        "new_measure",  # Measure 2: Verse middle
        "note:s1:f4:G5",
        "wait:480",
        "new_measure",  # Measure 3: Verse end (repeat close)
        "measure:repeat_close:2",
        "note:s1:f5:A5",
        "wait:480",
        "new_measure",  # Measure 4: Chorus start (repeat open)
        "measure:repeat_open",
        "note:s2:f0:B4",
        "wait:480",
        "new_measure",  # Measure 5: Chorus middle
        "note:s2:f2:C5",
        "wait:480",
        "new_measure",  # Measure 6: First ending (alternative 1)
        "measure:repeat_alternative:1",
        "note:s2:f4:D5",
        "wait:480",
        "new_measure",  # Measure 7: Second ending (alternative 2)
        "measure:repeat_alternative:2",
        "note:s2:f5:E5",
        "wait:480",
        "new_measure",  # Measure 8: Chorus end (repeat close)
        "measure:repeat_close:2",
        "note:s2:f7:F5",
        "wait:480",
        "new_measure",  # Measure 9: Outro
        "note:s1:f0:E5",
        "wait:960",
        "end",
    ]

    # Test basic measure splitting
    measures = split_tokens_to_measures(tokens)
    # Note: split_tokens_to_measures includes the "end" token in the last measure
    assert (
        len(measures) == 11
    )  # Header + 9 musical measures + end token in last measure

    # Test measure structure analysis
    token_measures = tokens_to_measures(tokens)
    # tokens_to_measures skips the header measure and creates TokenMeasure objects for the remaining measures
    # So we get 10 TokenMeasure objects (9 musical measures + 1 header measure that gets skipped)
    assert len(token_measures) == 10  # 10 musical measures (excluding header)

    # Test repeat structure detection
    opens, closes, alternatives = repeat_related_measure_indices(token_measures)
    assert opens == [
        1,
        4,
    ]  # Repeats start at measures 1 and 4 (indices 1 and 4 in token_measures)
    assert closes == [
        3,
        8,
    ]  # Repeats end at measures 3 and 8 (indices 3 and 8 in token_measures)
    assert alternatives == [
        6,
        7,
    ]  # Alternatives at measures 6 and 7 (indices 6 and 7 in token_measures)

    # Test playing order calculation
    measure_play_order = measures_playing_order(token_measures)

    # Expected playing order (based on actual behavior):
    # 0: Intro
    # 1,2,3: Verse first time (repeat open to repeat close)
    # 1,2,3: Verse second time (repeat)
    # 4,5,6: Chorus first time (goes to alternative 1)
    # 4,5,7: Chorus second time (goes to alternative 2)
    # 8: Chorus end (repeat close)
    # 9: Outro

    expected_order = [
        0,  # Intro
        1,
        2,
        3,  # Verse first time (measures 1-3)
        1,
        2,
        3,  # Verse second time (repeat)
        4,
        5,
        6,  # Chorus first time (goes to alternative 1)
        4,
        5,
        7,  # Chorus second time (goes to alternative 2)
        8,  # Chorus end (repeat close)
        9,  # Outro
    ]

    assert measure_play_order == expected_order
    assert len(measure_play_order) == 15  # Total measures when played

    # Test that alternatives are properly handled
    # First time through chorus: measures 4,5,6 (alternative 1)
    # Second time through chorus: measures 4,5,7 (alternative 2)

    # Verify the structure makes sense
    # Playing order: [0, 1, 2, 3, 1, 2, 3, 4, 5, 6, 4, 5, 7, 8, 9]
    # Indices:       0  1  2  3  4  5  6  7  8  9  10 11 12 13 14
    chorus_first_time = measure_play_order[7:10]  # [4, 5, 6]
    chorus_second_time = measure_play_order[10:13]  # [4, 5, 7]

    assert chorus_first_time[:2] == chorus_second_time[:2]  # Same start (4, 5)
    assert chorus_first_time[2] != chorus_second_time[2]  # Different endings
    assert chorus_first_time[2] == 6  # First alternative
    assert chorus_second_time[2] == 7  # Second alternative


def test_complex_alternative_endings():
    """Test more complex alternative ending scenarios."""

    # Test case: Multiple repeat sections with alternatives
    tokens = [
        "artist",
        "start",
        "new_measure",  # Measure 0: Header
        "note:s1:f0:E5",
        "wait:480",
        "new_measure",  # Measure 1: Section A start (repeat open)
        "measure:repeat_open",
        "note:s1:f2:F5",
        "wait:480",
        "new_measure",  # Measure 2: Section A middle
        "note:s1:f4:G5",
        "wait:480",
        "new_measure",  # Measure 3: Section A end (repeat close)
        "measure:repeat_close:2",
        "note:s1:f5:A5",
        "wait:480",
        "new_measure",  # Measure 4: Section B start (repeat open)
        "measure:repeat_open",
        "note:s2:f0:B4",
        "wait:480",
        "new_measure",  # Measure 5: Section B middle
        "note:s2:f2:C5",
        "wait:480",
        "new_measure",  # Measure 6: First ending (alternative 1)
        "measure:repeat_alternative:1",
        "note:s2:f4:D5",
        "wait:480",
        "new_measure",  # Measure 7: Second ending (alternative 2)
        "measure:repeat_alternative:2",
        "note:s2:f5:E5",
        "wait:480",
        "new_measure",  # Measure 8: Third ending (alternative 3)
        "measure:repeat_alternative:3",
        "note:s2:f7:F5",
        "wait:480",
        "new_measure",  # Measure 9: Section B end (repeat close)
        "measure:repeat_close:3",
        "note:s2:f9:G5",
        "wait:480",
        "new_measure",  # Measure 10: Final section
        "note:s1:f0:E5",
        "wait:960",
        "end",
    ]

    measures = split_tokens_to_measures(tokens)
    assert len(measures) == 12  # Header + 11 musical measures

    token_measures = tokens_to_measures(tokens)
    assert len(token_measures) == 11  # Excluding header

    # Test repeat structure
    opens, closes, alternatives = repeat_related_measure_indices(token_measures)
    assert opens == [1, 4]  # Repeats start at measures 1 and 4
    assert closes == [3, 9]  # Repeats end at measures 3 and 9
    assert alternatives == [6, 7, 8]  # Alternatives at measures 6, 7, 8

    # Test playing order with 3 alternatives
    measure_play_order = measures_playing_order(token_measures)

    # Expected: Section A (2x), Section B (3x with different alternatives), Final
    # Based on actual behavior: [0, 1, 2, 3, 1, 2, 3, 4, 5, 6, 4, 5, 7, 4, 5, 8, 9, 10]
    # 0: Header
    # 1,2,3: Section A first time
    # 1,2,3: Section A second time
    # 4,5,6: Section B first time (goes to alt1)
    # 4,5,7: Section B second time (goes to alt2)
    # 4,5,8: Section B third time (goes to alt3)
    # 9: Section B end (repeat close)
    # 10: Final section

    expected_order = [
        0,  # Header
        1,
        2,
        3,  # Section A first time
        1,
        2,
        3,  # Section A second time
        4,
        5,
        6,  # Section B first time (alt1)
        4,
        5,
        7,  # Section B second time (alt2)
        4,
        5,
        8,  # Section B third time (alt3)
        9,  # Section B end
        10,  # Final section
    ]

    assert measure_play_order == expected_order
    assert len(measure_play_order) == 18  # Total measures when played

    # Verify all alternatives are used
    # Playing order: [0, 1, 2, 3, 1, 2, 3, 4, 5, 6, 4, 5, 7, 4, 5, 8, 9, 10]
    # Indices:       0  1  2  3  4  5  6  7  8  9  10 11 12 13 14 15 16 17
    section_b_plays = [
        measure_play_order[7:10],
        measure_play_order[10:13],
        measure_play_order[13:16],
    ]
    assert section_b_plays[0][2] == 6  # First alternative
    assert section_b_plays[1][2] == 7  # Second alternative
    assert section_b_plays[2][2] == 8  # Third alternative


def test_alternative_endings_edge_cases():
    """Test edge cases in alternative ending handling."""

    # Test case: Alternative without proper repeat structure
    tokens = [
        "artist",
        "start",
        "new_measure",
        "measure:repeat_alternative:1",
        "note:s1:f0:E5",
        "wait:480",
        "new_measure",
        "note:s1:f2:F5",
        "wait:480",
        "end",
    ]

    measures = split_tokens_to_measures(tokens)
    token_measures = tokens_to_measures(tokens)

    # This should handle gracefully even with malformed structure
    opens, closes, alternatives = repeat_related_measure_indices(token_measures)
    assert alternatives == [0]  # Alternative detected
    assert opens == []  # No repeat opens
    assert closes == []  # No repeat closes

    # Test case: Multiple alternatives in same measure
    tokens = [
        "artist",
        "start",
        "new_measure",
        "measure:repeat_open",
        "note:s1:f0:E5",
        "wait:480",
        "new_measure",
        "measure:repeat_alternative:1",
        "measure:repeat_alternative:2",
        "note:s1:f2:F5",
        "wait:480",
        "new_measure",
        "measure:repeat_close:2",
        "note:s1:f4:G5",
        "wait:480",
        "end",
    ]

    measures = split_tokens_to_measures(tokens)
    token_measures = tokens_to_measures(tokens)

    opens, closes, alternatives = repeat_related_measure_indices(token_measures)
    assert opens == [0]
    assert closes == [2]
    assert alternatives == [1]  # Should detect the measure as having alternatives

    # Test playing order
    measure_play_order = measures_playing_order(token_measures)
    # Should handle multiple alternatives in same measure gracefully
    assert len(measure_play_order) > 0


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])
