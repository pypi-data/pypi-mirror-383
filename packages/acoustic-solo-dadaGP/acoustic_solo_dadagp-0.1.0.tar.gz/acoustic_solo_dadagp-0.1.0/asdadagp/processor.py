import logging
import re
from dataclasses import dataclass
from typing import List, Tuple, Union

_LOGGER = logging.getLogger(__name__)


@dataclass
class TokenMeasure:
    """
    Represents the information stored in a measure.
    """

    tokens: List[str]
    repeat_open: bool  # whether a repeat starts from this measure
    repeat_close: bool  # whether a repeat ends at this measure
    repeat_alternative: bool  # whether a repeat alternative starts from this measure


def repeat_related_measure_indices(
    measures: List[TokenMeasure],
) -> Tuple[List[int], List[int], List[int]]:
    """
    Returns the indices of measures that are related to repeats.

    :param measures: list of measures in the tab
    :return: a tuple of three lists:
        - indices of measures that open a repeat,
        - indices of measures that close a repeat,
        - indices of measures that are alternatives in a repeat.
    """
    opens = []
    closes = []
    alternatives = []
    for i in range(len(measures)):
        m = measures[i]
        if m.repeat_open:
            opens.append(i)
        if m.repeat_close:
            closes.append(i)
        if m.repeat_alternative:
            alternatives.append(i)

    return opens, closes, alternatives


def measures_playing_order(
    measures: List[TokenMeasure], tokens: bool = False
) -> Union[List[int], List[List[str]]]:
    """
    Returns the playing order of measures in a tab, considering repeats and alternatives.

    :param measures: list of measures in the tab
    :param tokens: return measure tokens instead of indices

    :return: a list of indices of measures in the playing order,
        or a list of lists of tokens if `tokens` is True.
    """

    opens, closes, alternatives = repeat_related_measure_indices(measures)

    if not opens:
        result = list(range(len(measures)))
    else:
        result = []
        current_measure = 0

        if not alternatives:
            if len(opens) != len(closes):
                raise ValueError(
                    f"Number of repeat opens ({len(opens)}) does not match number of repeat closes ({len(closes)}) when there is no repeat alternatives"
                )

            for i in range(len(opens)):
                # played previous non-repeating measures
                result.extend(list(range(current_measure, opens[i])))
                repeated_part = list(range(opens[i], closes[i] + 1))

                # play repeat
                result.extend(repeated_part)
                result.extend(repeated_part)

                current_measure = closes[i] + 1

            result.extend(list(range(current_measure, len(measures))))
        else:

            for i in range(len(opens)):
                current_open = opens[i]
                # add unrepeated part
                result.extend(list(range(current_measure, current_open)))
                try:
                    current_limit = opens[i + 1]
                except IndexError:  # last repeat in the song
                    current_limit = len(measures)

                available_alt = [
                    loc for loc in alternatives if current_open < loc < current_limit
                ]

                if not available_alt:  # current repeat doesn't have alternative
                    available_cl = [
                        loc for loc in closes if current_open <= loc < current_limit
                    ]  # supposed to only has 1
                    if not available_cl:
                        raise ValueError(
                            f"The repeat at measure {current_open} missed a close; the problem may come from the gp file that was encoded into tokens"
                        )
                    repeated_part = list(range(current_open, available_cl[0] + 1))

                    result.extend(repeated_part)
                    result.extend(repeated_part)

                    current_measure = available_cl[0] + 1
                else:  # with alternative
                    repeated_part = list(range(current_open, available_alt[0]))
                    result.extend(repeated_part)
                    # second alternative can be missing in some tabs
                    if len(available_alt) == 1:
                        available_cl = [
                            loc
                            for loc in closes
                            if available_alt[0] <= loc < current_limit
                        ]
                        if not available_cl:
                            raise ValueError(
                                f"The repeat alternative at measure {current_open} missed a close; the problem may come from the gp file that was encoded into tokens"
                            )

                        alt = list(range(available_alt[0], available_cl[0] + 1))

                        result.extend(alt)
                        result.extend(repeated_part)

                        current_measure = available_cl[0] + 1
                    else:
                        for j in range(len(available_alt)):
                            current_alt = available_alt[j]

                            try:
                                # end before next alternative
                                alt = list(range(current_alt, available_alt[j + 1]))
                                result.extend(alt)
                                result.extend(repeated_part)
                            except IndexError:
                                # the last alternative
                                current_measure = current_alt
            result.extend(list(range(current_measure, len(measures))))
    if not tokens:
        return result

    else:
        measure_tokens = []
        for i in result:
            measure_tokens.append(measures[i].tokens)
        return measure_tokens


def split_tokens_to_measures(tokens: List[str]) -> List[List[str]]:
    """
    Splits a list of tokens into measures based on the "new_measure" token.

    :param tokens: list of all tokens in the tab

    :return: a list of measures, where each measure is a list of tokens.
    """
    result = []
    current = []
    for t in tokens:
        if t == "new_measure":
            if current:  # only append if current is not empty
                result.append(current)
                current = []
        else:
            current.append(t)

    if current:
        result.append(current)

    return result


def tokens_to_measures(tokens: List[str]) -> List[TokenMeasure]:
    """
    Converts a list of tokens into a list of TokenMeasure objects, each representing a measure.

    :param tokens:
    :type tokens:
    :return:
    :param tokens: List of strings representing musical tokens from a tab, including measure headers (e.g., "measure:repeat_open") and musical notation tokens. The last token may be "end".
    :type tokens: List[str]
    :return: List of TokenMeasure objects, each representing a measure.
    :rtype: List[TokenMeasure]
    """
    result = []
    # the last token is "end"
    if tokens[-1] == "end":
        tokens = tokens[:-1]
    token_measures = split_tokens_to_measures(tokens)
    for i, measure in enumerate(token_measures):
        # The first is the header
        if i == 0:
            continue

        measure_headers = [t for t in measure if t.startswith("measure:")]
        mus_tokens = [t for t in measure if not t.startswith("measure:")]

        repeat_open = False
        repeat_close = False
        repeat_alt = False

        for header in measure_headers:
            if header == "measure:repeat_open":
                repeat_open = True
            if header.startswith("measure:repeat_close"):
                repeat_close = True
            if header.startswith("measure:repeat_alternative"):
                repeat_alt = True

        result.append(TokenMeasure(mus_tokens, repeat_open, repeat_close, repeat_alt))

    return result


def get_string_tunings(tokens: List[str]) -> List[str]:
    """
    Extracts string tunings from the provided tokens.

    :param tokens: List of tokens from which to extract string tunings.
    :return: tuning of the song / tab
    """
    if tokens[9] == "start":
        note_tuning = False
    elif tokens[3] == "start":
        note_tuning = True
    else:
        note_tuning = True
        _LOGGER.warning("'start' token not found in expected positions.")

    if note_tuning:
        string_tuning_dict = {}
        while len(string_tuning_dict) < 6:
            for token in tokens:
                if (token.startswith("clean") and "note" in token) or token.startswith(
                    "note"
                ):
                    start = token.index("note") + len("note")
                    guitar_string = int(token[start + 2])
                    tuning = token.split(":")[-1]
                    string_tuning_dict[guitar_string] = tuning

        return [string_tuning_dict[i] for i in range(1, 7)]
    else:
        return tokens[
            3:9
        ]  # Assuming the first 6 tokens after "start" are the string tunings


def merge_tracks_and_prune(notes: List[str]) -> List[str]:
    """
    Merges multiple acoustic tracks, sort notes within a beat, and remove the "cleanX:" prefix from the notes.

    :param notes: List of notes, each prefixed with "cleanX:" where X is the track number.
    :return: notes without the "cleanX:" prefix
    """

    processed_notes = [re.sub(r"clean\d+:", "", token).strip() for token in notes]
    if set(processed_notes) == {"rest"}:
        return ["rest"]
    else:
        return sort_notes([note for note in processed_notes if note != "rest"])


def sort_notes(pruned_notes: List[str]) -> List[str]:
    """
    Sorts the notes within same beat based on the "s<number>:" prefix in each token.

    :param pruned_notes: List of notes that have been pruned of the "cleanX:" prefix.
    :return: List of notes sorted by the "s<number>:" prefix.
    """
    # Define a key function for sorting based on "s<number>:" in the token.
    def extract_s_number(s):
        match = re.search(r"s(\d+):", s)
        # If not found, push token to the end.
        return int(match.group(1)) if match else float("inf")

    sorted_notes = sorted(pruned_notes, key=extract_s_number)
    return sorted_notes


def tracks_check(tokens: List[str], merge_track: bool = True) -> List[str]:
    """
    Processes the tokens by merging tracks and removing the "clean0:" prefix from the notes.

    :param tokens: List of tokens from the tab.
    :param merge_track: If True, merge all tracks and remove the "cleanX:" prefix, otherwise, only remain "clean0:".
    :return: List of processed tokens with "cleanX:" prefixes removed and tracks merged if specified.
    """
    processed = []
    if not merge_track:
        # only remain clean0
        for token in tokens:
            if token.startswith("clean"):
                if token[5] == "0":
                    processed.append(token.replace("clean0:", ""))
                else:
                    continue
            else:
                processed.append(token)
    else:
        current_group = []
        for token in tokens:
            # Group any 'clean' tracks
            if token.startswith("clean"):
                current_group.append(token)
                continue
            else:
                if current_group:
                    merged = merge_tracks_and_prune(current_group)
                    processed.extend(merged)
                    current_group = []

                processed.append(token)

        if current_group:
            merged = merge_tracks_and_prune(current_group)
            processed.extend(merged)

    return processed


def pre_decoding_processing(tokens: List[str]) -> Tuple[List[str], List[str]]:
    """
    Pre-processes the tokens before decoding by separating head and body,
    normalizing note/rest prefixes, and handling tuning blocks.

    :param tokens: List of tokens from the tab.
    :return: A tuple containing:
        - List of processed tokens with normalized prefixes and tuning handling.
        - List of string tunings extracted from the tokens.
    """
    # Decide head/body without repeated slicing
    if len(tokens) > 3 and tokens[3] == "start":
        head = tokens[:4]
        tune_in_token = True
        start_idx = 4
    else:
        # Build head without append inside hot loop
        head = tokens[:3] + ["start"]
        tune_in_token = False
        # Not include the string tunings if they are in the header
        start_idx = 10

    tunings = get_string_tunings(tokens)

    results: List[str] = []
    append = results.append
    startswith = str.startswith
    endswith = str.endswith
    rfind = str.rfind

    # Pre-extend with head once
    results.extend(head)

    # Iterate body
    for t in tokens[start_idx:]:
        # add track prefix if the token preprocessing removed them
        if startswith(t, "note") or startswith(t, "rest"):
            t = "clean0:" + t

        # Remove the string tuning suffix in note/clean tokens if exists
        if tune_in_token and (
            startswith(t, "note")
            or (startswith(t, "clean") and not endswith(t, "rest"))
        ):
            i = rfind(t, ":")
            if i != -1:
                t = t[:i]
        append(t)

    return results, tunings
