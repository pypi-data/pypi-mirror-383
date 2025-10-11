import os

import guitarpro as gp
from asdadagp.encoder import guitarpro2tokens

DATA_FOLDER_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "tests", "data"
)


def test_strings_tokens():
    # The song has a downtuning of -14 semitones, so all tunings are shifted down
    # Original celtic tuning: D5, A4, G4, D4, A3, D3
    # With -14 semitones downtuning: D4, A3, G3, D3, A2, D2
    celtic_tuning_downtuned = {
        "s1": "D4",  # D5 -> D4
        "s2": "A3",  # A4 -> A3
        "s3": "G3",  # G4 -> G3
        "s4": "D3",  # D4 -> D3
        "s5": "A2",  # A3 -> A2
        "s6": "D2",  # D3 -> D2
    }

    gp_path = os.path.join(DATA_FOLDER_PATH, "bensusan_pierre-dame_lombarde.gp5")
    song = gp.parse(gp_path)
    tokens = guitarpro2tokens(song, "unknown", verbose=True, note_tuning=True)

    # Test that note tokens end with the correct downtuned tunings
    for token in tokens:
        if "note" in token:
            start = token.index("note") + len("note")
            guitar_string = token[start + 1 : start + 3]
            expected_tuning = celtic_tuning_downtuned[guitar_string]
            assert token.endswith(
                expected_tuning
            ), f"Token {token} should end with {expected_tuning} for string {guitar_string}"

    assert tokens[3] == "start"

    # Test the note_tuning=False case
    # Note: Even with note_tuning=False, the downtuning is still applied to the tuning tokens
    tokens_without_tuning = guitarpro2tokens(
        song, "unknown", verbose=True, note_tuning=False
    )

    # The downtuned celtic tuning (same as when note_tuning=True)
    downtuned_celtic_tuning = {
        "s1": "D4",  # D5 -> D4
        "s2": "A3",  # A4 -> A3
        "s3": "G3",  # G4 -> G3
        "s4": "D3",  # D4 -> D3
        "s5": "A2",  # A3 -> A2
        "s6": "D2",  # D3 -> D2
    }

    for i in range(3, 9):
        expected_tuning = downtuned_celtic_tuning[f"s{i-2}"]
        actual_tuning = tokens_without_tuning[i]
        assert (
            actual_tuning == expected_tuning
        ), f"Expected {expected_tuning} at position {i}, got {actual_tuning}"

    assert tokens_without_tuning[9] == "start"
