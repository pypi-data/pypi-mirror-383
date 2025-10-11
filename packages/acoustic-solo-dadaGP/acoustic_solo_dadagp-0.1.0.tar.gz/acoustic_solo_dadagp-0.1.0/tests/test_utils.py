import os
from fractions import Fraction

import guitarpro as gp
from asdadagp.utils import (
    convert_strings_for_pygp,
    convert_to_nearest_supported_time,
    diff,
    guitar_downtunage,
    noteNumber,
)

DATA_FOLDER_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "tests", "data"
)


def test_diff():
    assert diff([]) == []
    assert diff([9]) == []
    assert diff([9, 9]) == [0]
    assert diff([9, 10]) == [1]
    assert diff([9, 8]) == [-1]
    assert diff([1, 2, 3, 4]) == [1, 1, 1]
    assert diff([69, 64, 60, 55, 50, 45]) == [-5, -4, -5, -5, -5]


def test_note_number():
    assert noteNumber("C#1") == (1, "C#", 1, 25)
    assert noteNumber("E5") == (5, "E", 4, 76)


def test_downtune():
    # Tests
    assert guitar_downtunage(["E5", "B4", "G4", "D4", "A3", "E3"]) == 12
    assert guitar_downtunage(["E5", "B4", "G4", "D4", "A3", "D3"]) == 12
    assert guitar_downtunage(["D5", "A4", "F4", "C4", "G3", "C3"]) == 10


def test_time_support():
    assert convert_to_nearest_supported_time(Fraction(99 / 3)) == 30
    assert convert_to_nearest_supported_time(99 / 3) == 30
    assert convert_to_nearest_supported_time(480) == 480
    assert convert_to_nearest_supported_time(480.1) == 480
    assert convert_to_nearest_supported_time(481) == 480
    assert (
        convert_to_nearest_supported_time(920 * 1000) == 5760
    )  ## if duration is too large, use the max supported duration


def test_load_score():
    blankgp5 = gp.parse(os.path.join(DATA_FOLDER_PATH, "blank.gp5"))
    blankgp5.tracks = []
    new_track = gp.Track(blankgp5)
    strings = ["E5", "B4", "G4", "D4", "A3", "E3"]
    new_track.strings = convert_strings_for_pygp(strings)
    assert new_track.strings[0].value == 76
    # print(new_track.strings)
    # Test pitchshift
    new_track.strings = convert_strings_for_pygp(strings, -2)
    # print(new_track.strings)
    assert new_track.strings[0].value == 74
