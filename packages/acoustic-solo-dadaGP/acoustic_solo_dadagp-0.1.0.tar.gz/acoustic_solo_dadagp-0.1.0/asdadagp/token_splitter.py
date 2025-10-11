#####
## DADAGP v1.1

# in DadaGP v1.0 nfx and bfx tokens were one long string
# in DadaGP v1.1 nfx and bfx tokens may be split into multiple tokens. they may have param tokens attached to them, immediately following them.

# wait, nfx:grace, nfx:trill, nfx:bend, and bfx:tremolo_bar get split

## split_rare_token(token) is to be used to split rare tokens into smaller pieces
## thereby reducing the song_token vocabulary from 9792 to 2200 (a 78% reduction). song lengths increase negligbly (less than 1% longer)

## unsplit_fx(token_dict) is used tokens2guitarpro to convert the v1.1 pieces back into v1.0 tokens

#
####
#############
## Functins for SPLITTING / CONVERTING v1.0 => v1.1
#############

# Splits a number into unique powers of two which can be summed into that number
# 9 => [8,1]
# 7 => [4,2,1]
# 1 => [1]
# 1024 => [1024]
# 1023 => [512,256,128,64,32,16,8,4,2,1]
# 16384 => [16384]

import math

from .const import wait_token_list2


def binarization(n):
    l = []
    for i in range(1, 20):
        p = int(math.pow(2, i))
        r = n % (p)
        n -= r
        if r > 0:
            l.append(r)
    l.reverse()
    return l


# List of supported tokens
# Includes the 18 most common wait tokens which represent 99.7% of wait tokens
# Also inludes powers of 2 which are summed to represent any wait amount up to 2^15 (~35 beats long)
# wait_token_list2 = ['wait:1920', 'wait:16', 'wait:4096', 'wait:240', 'wait:3840', 'wait:512', 'wait:2048', 'wait:960',
#                     'wait:64', 'wait:2880', 'wait:320', 'wait:256', 'wait:32', 'wait:16384', 'wait:480', 'wait:8',
#                     'wait:1024', 'wait:640', 'wait:1', 'wait:360', 'wait:192', 'wait:128', 'wait:120', 'wait:40',
#                     'wait:60', 'wait:2', 'wait:8192', 'wait:4', 'wait:1440', 'wait:80', 'wait:180', 'wait:720',
#                     'wait:160']


def split_wait_token(token):
    if token in wait_token_list2:
        # common wait tokens are not split
        return [token]
    else:
        # uncommon wait tokens are split
        n = int(token.split(":")[1])
        return ["wait:%s" % b for b in binarization(n)]


# Bends/tremolo_bar tokens are split into variable parts [nfx:bend:type, dur, val:vib, dur, val:vib, dur, val:vib, ...]
# Dur is the forward advance of position
def split_bend_token(token):
    s = token.split(":")
    subtoken = []
    subtokens = []
    last_pos = 0
    for i in range(0, len(s)):
        if s[i][:3] == "pos":
            new_pos = int(s[i][3:])
            diff = new_pos - last_pos
            if diff <= 0:
                continue
            diff_token = "param:dur%s" % diff
            last_pos = new_pos
            subtokens.append(diff_token)
            continue
        subtoken.append(s[i])
        if i == 2:
            subtokens.append(":".join(subtoken))
            subtoken = []
        elif i % 3 == 2:
            subtokens.append("param:%s" % ":".join(subtoken))
            subtoken = []
    return subtokens


# Trills are split into two parts [nfx:trill:fret, duration]
def split_trill_token(token):
    s = token.split(":")
    subtokens = []
    subtokens.append("%s" % ":".join(s[0:3]))
    subtokens.append("param:%s" % ":".join(s[3:4]))
    return subtokens


# Graces are split into two parts [nfx]


def split_grace_token(token):
    s = token.split(":")
    subtokens = []
    subtokens.append("%s" % ":".join(s[0:3]))
    subtokens.append("param:%s" % ":".join(s[3:]))
    return subtokens


# Splits some rare tokens into multiple smaller pieces
# wait, nfx:trill, nfx:grace, nfx:bend, bfx:tremolo_bar
# Takes a token (string)
# returns a list of token strings
# If input is not a rare token, returns the token inside a list of length 1 [token]
def split_rare_token(token):
    s = token.split(":")
    # WAIT
    if s[0] == "wait":
        return split_wait_token(token)
    # TRILL
    elif len(s) > 2 and s[0] + ":" + s[1] == "nfx:trill":
        return split_trill_token(token)
    # GRACE
    elif len(s) > 2 and s[0] + ":" + s[1] == "nfx:grace":
        return split_grace_token(token)
    # BEND
    elif len(s) > 2 and s[0] + ":" + s[1] in ["nfx:bend", "bfx:tremolo_bar"]:
        return split_bend_token(token)
    return [token]


#
####
#############
## Functins for UNSPLITTING / converting  v1.1 => v1.0
#############

# in DadaGP v1.0 nfx and bfx tokens were one long string
# in DadaGP v1.1 nfx and bfx tokens may be split into multiple tokens. they may have param tokens attached to them, immediately following them.

# wait does not get unsplit
# nfx:grace, nfx:trill, nfx:bend, and bfx:tremolo_bar get unsplit


# This function unsplits the effects+params token set back to v1.0 (where each effect is one long string)
def unsplit_fx(fx, verbose=True):
    if isinstance(fx, str):
        # this is already in string format (v1.0)
        return fx
    fx_dict = fx
    token = fx_dict["token"]
    params = fx_dict["params"]
    s = token.split(":")
    if s[0] == "bfx":
        if s[1] == "tremolo_bar":
            # tremolo bar is the only bfx with params
            return unsplit_bend_fx(fx_dict, verbose)
        else:
            # ignore params for all other bfx
            return token
    elif s[0] == "nfx":
        if s[1] == "bend":
            return unsplit_bend_fx(fx_dict, verbose)
        elif s[1] == "grace":
            return unsplit_grace_nfx(fx_dict, verbose)
        elif s[1] == "trill":
            return unsplit_trill_nfx(fx_dict, verbose)
        else:
            # ignore params for all other nfx
            return token
    else:
        verbose and print("Unsplit_fx was given a non-fx token", s[0])
        assert False


######
# Grace


def unsplit_grace_nfx(fx_token, verbose=True):
    if isinstance(fx_token, str):
        # this is already in string format (v1.0)
        return fx_token
        # in v1.1, nfx is a dict
    # convert to v1.0 format (string)
    # {"token": "nfx:grace:fret43",
    #  "params": ['param:duration128:dead0:beat0:transition3']}
    top = fx_token["token"]
    s = top.split(":")
    assert s[1] == "grace"
    most_common = "duration128:dead0:beat0:transition1"
    if len(fx_token["params"]) == 0:
        # no params, use the most common
        return "%s:%s" % (top, most_common)
    # There's gotta be at least one well formatted param in here. Ignore anything else in here
    grace_params = None
    for p in fx_token["params"]:
        if "duration" in p and "dead" in p and "beat" in p and "transition" in p:
            grace_params = p
            break
    if not grace_params:
        # badly formatted param, use the most common
        return "%s:%s" % (top, most_common)
    # well formatted params
    grace_params = ":".join(grace_params.split(":")[1:])
    return "%s:%s" % (top, grace_params)


#####
# Trill


def unsplit_trill_nfx(fx_token, verbose=True):
    if isinstance(fx_token, str):
        # this is already in string format (v1.0)
        return fx_token
        # in v1.1, nfx is a dict
    # convert to v1.0 format (string)
    # {"token": "nfx:trill:fret36",
    #  "params": ['param:duration240']}
    top = fx_token["token"]
    s = top.split(":")
    assert s[1] == "trill"
    most_common = "duration240"
    if len(fx_token["params"]) == 0:
        # no params, use the most common
        return "%s:%s" % (top, most_common)
    # There's gotta be at least one well formatted param in here. Ignore anything else in here
    trill_params = None
    for p in fx_token["params"]:
        psplit = p.split(":")
        if len(psplit) == 2 and psplit[1][:8] == "duration":
            trill_params = p
            break
    if not trill_params:
        # badly formatted param, use the most common
        return "%s:%s" % (top, most_common)
    # well formatted params
    trill_params = ":".join(trill_params.split(":")[1:])
    return "%s:%s" % (top, trill_params)


######
# tremolo_bar and bend


# If this bfx tremolo bar has no params, replace it with the most common for the type
# If there is some other error, replace it with the most common tremolo token
def fix_broken_bfx_tremolo_bar(top):
    fixes = {
        "bfx:tremolo_bar:type6": "pos0:val0:vib0:pos6:val-4:vib0:pos12:val0:vib0",
        "bfx:tremolo_bar:type7": "pos0:val0:vib0:pos9:val-4:vib0:pos12:val-4:vib0",
        "bfx:tremolo_bar:type8": "pos0:val-4:vib0:pos3:val0:vib0:pos12:val0:vib0",
        "bfx:tremolo_bar:type9": "pos0:val0:vib0:pos6:val2:vib0:pos12:val0:vib0",
        "bfx:tremolo_bar:type10": "pos0:val0:vib0:pos9:val4:vib0:pos12:val4:vib0",
        "bfx:tremolo_bar:type11": "pos0:val0:vib0:pos8:val0:vib0:pos12:val-16:vib0",
    }
    most_common = "bfx:tremolo_bar:type6:pos0:val0:vib0:pos6:val-4:vib0:pos12:val0:vib0"
    if top in fixes:
        return "%s:%s" % (top, fixes[top])
    else:
        return most_common


# If this nfx bend has no params, replace it with the most common for the type
# If there is some other error, replace it with the most common bend token
def fix_broken_nfx_bend(top):
    fixes = {
        "nfx:bend:type5": "pos0:val4:vib0:pos4:val4:vib0:pos8:val0:vib0:pos12:val0:vib0",
        "nfx:bend:type4": "pos0:val4:vib0:pos12:val4:vib0",
        "nfx:bend:type3": "pos0:val0:vib0:pos2:val4:vib0:pos4:val4:vib0:pos6:val0:vib0:pos8:val0:vib0:pos10:val4:vib0:pos12:val4:vib0",
        "nfx:bend:type2": "pos0:val0:vib0:pos3:val4:vib0:pos6:val4:vib0:pos9:val0:vib0:pos12:val0:vib0",
        "nfx:bend:type1": "pos0:val0:vib0:pos6:val4:vib0:pos12:val4:vib0",
    }
    most_common = "nfx:bend:type1:pos0:val0:vib0:pos6:val4:vib0:pos12:val4:vib0"
    if top in fixes:
        return "%s:%s" % (top, fixes[top])
    else:
        return most_common


# Unsplits a v1.1 bfx:tremolo_bar or nfx:bend token dict back into a v1.0 string
# Also ideally this should fix/ignore any weirdly formatted token/params
def unsplit_bend_fx(fx_token, verbose=False):
    if isinstance(fx_token, str):
        # this is already in string format (v1.0)
        return fx_token
        # in v1.1, bfx/nfx is a dict
    # convert to v1.0 format (string)
    # {"token": "bfx:tremolo_bar:type10",
    #  "params": ['param:val0:vib0', 'param:dur9', 'param:val4:vib0', 'param:dur3', 'param:val4:vib0']}
    fx_type = fx_token["token"].split(":")[1]
    assert fx_type in ["tremolo_bar", "bend"]
    top = fx_token["token"]
    # Only Tremolo bar and Bend for this function
    position = 0
    duration = 0
    params = []
    num_bend_points = 0
    if len(fx_token["params"]) == 0:
        # Missing params token.
        # Replace this with the most common
        if fx_type == "tremolo_bar":
            return fix_broken_bfx_tremolo_bar(top)
        elif fx_type == "bend":
            return fix_broken_nfx_bend(top)
    try:
        for p in fx_token["params"]:
            param = p.split(":")[1:]
            if param[0][:3] == "dur":
                # convert durations to positions by cumulatively summing
                duration = int(param[0][3:])
                position += duration
            elif param[0][:3] == "val":
                if position > 12:
                    verbose and print(
                        "- Warning: invalid %s token. Position cannot be greater than 12"
                        % fx_type,
                        fx_token,
                    )
                    # ignore this bend point
                    continue
                if position > 0 and num_bend_points == 0:
                    verbose and print(
                        "- Warning: invalid %s token. First position must be zero"
                        % fx_type,
                        fx_token,
                    )
                    # ignore whatever duration token happened too early, set position to zero
                    position = 0
                # when we hit a val/vib, add the triplet
                params.append("pos%s" % position)
                params.extend(param)
                num_bend_points += 1
                duration = 0
    except:
        # Some error happened
        # Possibly the generator mixed preceded this param token with the wrong nfx token?
        if fx_type == "tremolo_bar":
            return fix_broken_bfx_tremolo_bar(top)
        elif fx_type == "bend":
            return fix_broken_nfx_bend(top)

    if len(params) % 3 != 0 or num_bend_points < 2:
        # some other error we didn't catch
        verbose and print(
            "- Warning: invalid %s token. Replacing with most common bend token "
            % fx_type,
            fx_token,
        )
        # Replace this with the most common
        if fx_type == "tremolo_bar":
            return fix_broken_bfx_tremolo_bar(top)
        elif fx_type == "bend":
            return fix_broken_nfx_bend(top)
    return "%s:%s" % (fx_token["token"], ":".join(params))
