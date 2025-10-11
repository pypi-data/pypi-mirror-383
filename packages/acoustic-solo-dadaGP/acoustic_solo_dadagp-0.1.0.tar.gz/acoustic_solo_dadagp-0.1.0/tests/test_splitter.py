from asdadagp.token_splitter import (
    split_bend_token,
    split_grace_token,
    split_rare_token,
    split_trill_token,
    split_wait_token,
    unsplit_bend_fx,
    unsplit_fx,
    unsplit_grace_nfx,
    unsplit_trill_nfx,
)


def test_wait_token():
    assert split_wait_token("wait:121") == [
        "wait:64",
        "wait:32",
        "wait:16",
        "wait:8",
        "wait:1",
    ]
    assert split_wait_token("wait:1") == ["wait:1"]
    assert split_wait_token("wait:480") == ["wait:480"]
    assert split_wait_token("wait:20080") == [
        "wait:16384",
        "wait:2048",
        "wait:1024",
        "wait:512",
        "wait:64",
        "wait:32",
        "wait:16",
    ]


def test_bend_token():
    assert split_bend_token(
        "nfx:bend:type5:pos0:val4:vib0:pos2:val4:vib0:pos4:val0:vib0:pos8:val0:vib0:pos12:val0:vib0"
    ) == [
        "nfx:bend:type5",
        "param:val4:vib0",
        "param:dur2",
        "param:val4:vib0",
        "param:dur2",
        "param:val0:vib0",
        "param:dur4",
        "param:val0:vib0",
        "param:dur4",
        "param:val0:vib0",
    ]
    assert split_bend_token(
        "bfx:tremolo_bar:type10:pos0:val0:vib0:pos9:val2:vib0:pos12:val2:vib0"
    ) == [
        "bfx:tremolo_bar:type10",
        "param:val0:vib0",
        "param:dur9",
        "param:val2:vib0",
        "param:dur3",
        "param:val2:vib0",
    ]
    assert split_bend_token("bfx:tremolo_bar:type10:pos0:val0:vib0:pos9:val2:vib0") == [
        "bfx:tremolo_bar:type10",
        "param:val0:vib0",
        "param:dur9",
        "param:val2:vib0",
    ]


def test_trill_token():
    assert split_trill_token("nfx:trill:fret36:duration240") == [
        "nfx:trill:fret36",
        "param:duration240",
    ]
    assert split_trill_token("nfx:trill:fret6:duration120") == [
        "nfx:trill:fret6",
        "param:duration120",
    ]

    assert (
        unsplit_trill_nfx(
            {"token": "nfx:trill:fret36", "params": ["param:duration240"]}
        )
        == "nfx:trill:fret36:duration240"
    )
    assert (
        unsplit_trill_nfx({"token": "nfx:trill:fret6", "params": ["param:duration120"]})
        == "nfx:trill:fret6:duration120"
    )
    # Doubled param, skip the second one
    assert (
        unsplit_trill_nfx(
            {
                "token": "nfx:trill:fret1",
                "params": [
                    "param:duration120",
                    "param:duration240",
                    "param:duration64",
                ],
            }
        )
        == "nfx:trill:fret1:duration120"
    )
    # Broken. Use most common trill param
    assert (
        unsplit_trill_nfx({"token": "nfx:trill:fret9", "params": []})
        == "nfx:trill:fret9:duration240"
    )
    assert (
        unsplit_trill_nfx(
            {"token": "nfx:trill:fret8", "params": ["dur6", "param:val-4:vib0"]}
        )
        == "nfx:trill:fret8:duration240"
    )


def test_grace_token():
    assert split_grace_token(
        "nfx:grace:fret43:duration128:dead0:beat0:transition3"
    ) == ["nfx:grace:fret43", "param:duration128:dead0:beat0:transition3"]
    assert split_grace_token("nfx:grace:fret11:duration64:dead0:beat0:transition2") == [
        "nfx:grace:fret11",
        "param:duration64:dead0:beat0:transition2",
    ]
    assert (
        unsplit_grace_nfx(
            {
                "token": "nfx:grace:fret43",
                "params": ["param:duration128:dead0:beat0:transition3"],
            }
        )
        == "nfx:grace:fret43:duration128:dead0:beat0:transition3"
    )
    assert (
        unsplit_grace_nfx(
            {
                "token": "nfx:grace:fret1",
                "params": ["param:duration64:dead1:beat0:transition2"],
            }
        )
        == "nfx:grace:fret1:duration64:dead1:beat0:transition2"
    )
    # Doubled param, skip the second one
    assert (
        unsplit_grace_nfx(
            {
                "token": "nfx:grace:fret7",
                "params": [
                    "param:duration64:dead1:beat0:transition2",
                    "param:duration128:dead0:beat0:transition2",
                ],
            }
        )
        == "nfx:grace:fret7:duration64:dead1:beat0:transition2"
    )
    # Broken params. Use most common grace param
    assert (
        unsplit_grace_nfx({"token": "nfx:grace:fret9", "params": []})
        == "nfx:grace:fret9:duration128:dead0:beat0:transition1"
    )
    assert (
        unsplit_grace_nfx(
            {"token": "nfx:grace:fret8", "params": ["dur6", "param:val-4:vib0"]}
        )
        == "nfx:grace:fret8:duration128:dead0:beat0:transition1"
    )


def test_rare_token():
    assert split_rare_token(
        "nfx:bend:type1:pos0:val0:vib0:pos6:val4:vib0:pos12:val4:vib0"
    ) == [
        "nfx:bend:type1",
        "param:val0:vib0",
        "param:dur6",
        "param:val4:vib0",
        "param:dur6",
        "param:val4:vib0",
    ]
    assert split_rare_token(
        "nfx:bend:type3:pos0:val0:vib0:pos2:val4:vib0:pos4:val4:vib0:pos6:val0:vib0:pos8:val0:vib0:pos10:val4:vib0:pos12:val4:vib0"
    ) == [
        "nfx:bend:type3",
        "param:val0:vib0",
        "param:dur2",
        "param:val4:vib0",
        "param:dur2",
        "param:val4:vib0",
        "param:dur2",
        "param:val0:vib0",
        "param:dur2",
        "param:val0:vib0",
        "param:dur2",
        "param:val4:vib0",
        "param:dur2",
        "param:val4:vib0",
    ]
    assert split_rare_token("nfx:bend:type1:pos1:val4:vib0:pos12:val2:vib0") == [
        "nfx:bend:type1",
        "param:dur1",
        "param:val4:vib0",
        "param:dur11",
        "param:val2:vib0",
    ]

    assert split_rare_token(
        "bfx:tremolo_bar:type6:pos0:val0:vib0:pos6:val-4:vib0:pos12:val0:vib0"
    ) == [
        "bfx:tremolo_bar:type6",
        "param:val0:vib0",
        "param:dur6",
        "param:val-4:vib0",
        "param:dur6",
        "param:val0:vib0",
    ]
    assert split_rare_token(
        "bfx:tremolo_bar:type6:pos0:val0:vib0:pos6:val-8:vib0:pos12:val0:vib0"
    ) == [
        "bfx:tremolo_bar:type6",
        "param:val0:vib0",
        "param:dur6",
        "param:val-8:vib0",
        "param:dur6",
        "param:val0:vib0",
    ]
    assert split_rare_token(
        "bfx:tremolo_bar:type10:pos0:val0:vib0:pos9:val4:vib0:pos12:val4:vib0"
    ) == [
        "bfx:tremolo_bar:type10",
        "param:val0:vib0",
        "param:dur9",
        "param:val4:vib0",
        "param:dur3",
        "param:val4:vib0",
    ]

    assert split_rare_token("nfx:grace:fret43:duration128:dead0:beat0:transition3") == [
        "nfx:grace:fret43",
        "param:duration128:dead0:beat0:transition3",
    ]
    assert split_rare_token("nfx:grace:fret11:duration64:dead0:beat0:transition2") == [
        "nfx:grace:fret11",
        "param:duration64:dead0:beat0:transition2",
    ]

    assert split_rare_token("nfx:trill:fret36:duration240") == [
        "nfx:trill:fret36",
        "param:duration240",
    ]
    assert split_rare_token("nfx:trill:fret6:duration120") == [
        "nfx:trill:fret6",
        "param:duration120",
    ]

    assert split_rare_token("wait:121") == [
        "wait:64",
        "wait:32",
        "wait:16",
        "wait:8",
        "wait:1",
    ]
    assert split_rare_token("wait:1") == ["wait:1"]
    assert split_rare_token("wait:480") == ["wait:480"]
    assert split_rare_token("wait:20080") == [
        "wait:16384",
        "wait:2048",
        "wait:1024",
        "wait:512",
        "wait:64",
        "wait:32",
        "wait:16",
    ]

    assert split_rare_token("bfx:tempo_change:270") == ["bfx:tempo_change:270"]
    assert split_rare_token("drums:note:36") == ["drums:note:36"]
    assert split_rare_token("nfx:palm_mute") == ["nfx:palm_mute"]


def test_bend_fx():
    # Missing params
    # Use the most common params
    assert (
        unsplit_bend_fx({"token": "bfx:tremolo_bar:type6", "params": []})
        == "bfx:tremolo_bar:type6:pos0:val0:vib0:pos6:val-4:vib0:pos12:val0:vib0"
    )
    assert (
        unsplit_bend_fx({"token": "bfx:tremolo_bar:type7", "params": []})
        == "bfx:tremolo_bar:type7:pos0:val0:vib0:pos9:val-4:vib0:pos12:val-4:vib0"
    )
    assert (
        unsplit_bend_fx({"token": "bfx:tremolo_bar:type8", "params": []})
        == "bfx:tremolo_bar:type8:pos0:val-4:vib0:pos3:val0:vib0:pos12:val0:vib0"
    )
    assert (
        unsplit_bend_fx({"token": "bfx:tremolo_bar:type9", "params": []})
        == "bfx:tremolo_bar:type9:pos0:val0:vib0:pos6:val2:vib0:pos12:val0:vib0"
    )
    assert (
        unsplit_bend_fx({"token": "bfx:tremolo_bar:type10", "params": []})
        == "bfx:tremolo_bar:type10:pos0:val0:vib0:pos9:val4:vib0:pos12:val4:vib0"
    )
    assert (
        unsplit_bend_fx({"token": "bfx:tremolo_bar:type11", "params": []})
        == "bfx:tremolo_bar:type11:pos0:val0:vib0:pos8:val0:vib0:pos12:val-16:vib0"
    )
    assert (
        unsplit_bend_fx({"token": "nfx:bend:type5", "params": []})
        == "nfx:bend:type5:pos0:val4:vib0:pos4:val4:vib0:pos8:val0:vib0:pos12:val0:vib0"
    )
    assert (
        unsplit_bend_fx({"token": "nfx:bend:type4", "params": []})
        == "nfx:bend:type4:pos0:val4:vib0:pos12:val4:vib0"
    )
    assert (
        unsplit_bend_fx({"token": "nfx:bend:type3", "params": []})
        == "nfx:bend:type3:pos0:val0:vib0:pos2:val4:vib0:pos4:val4:vib0:pos6:val0:vib0:pos8:val0:vib0:pos10:val4:vib0:pos12:val4:vib0"
    )
    assert (
        unsplit_bend_fx({"token": "nfx:bend:type2", "params": []})
        == "nfx:bend:type2:pos0:val0:vib0:pos3:val4:vib0:pos6:val4:vib0:pos9:val0:vib0:pos12:val0:vib0"
    )
    assert (
        unsplit_bend_fx({"token": "nfx:bend:type1", "params": []})
        == "nfx:bend:type1:pos0:val0:vib0:pos6:val4:vib0:pos12:val4:vib0"
    )

    # Invalid, try to fix
    # Warning: invalid tremolo_bar token. First position must be zero
    assert (
        unsplit_bend_fx(
            {
                "token": "bfx:tremolo_bar:type8",
                "params": [
                    "param:dur6",
                    "param:val0:vib0",
                    "param:dur6",
                    "param:val-4:vib0",
                    "param:dur6",
                    "param:val0:vib0",
                ],
            }
        )
        == "bfx:tremolo_bar:type8:pos0:val0:vib0:pos6:val-4:vib0:pos12:val0:vib0"
    )
    # Warning: invalid tremolo_bar token. Position cannot be greater than 12
    assert (
        unsplit_bend_fx(
            {
                "token": "bfx:tremolo_bar:type9",
                "params": [
                    "param:dur0",
                    "param:val0:vib0",
                    "param:dur12",
                    "param:val-4:vib0",
                    "param:dur6",
                    "param:val0:vib0",
                ],
            }
        )
        == "bfx:tremolo_bar:type9:pos0:val0:vib0:pos12:val-4:vib0"
    )
    # Warning: invalid tremolo_bar token. Replacing with most common bend token
    assert (
        unsplit_bend_fx(
            {
                "token": "bfx:tremolo_bar:type10",
                "params": [
                    "param:dur0",
                    "param:val0:vib0",
                    "param:dur4",
                    "param:val-4:vib0",
                    "param:dur6",
                    "param:val0",
                ],
            }
        )
        == "bfx:tremolo_bar:type10:pos0:val0:vib0:pos9:val4:vib0:pos12:val4:vib0"
    )
    # This just adds the durations together
    assert (
        unsplit_bend_fx(
            {
                "token": "bfx:tremolo_bar:type7",
                "params": [
                    "param:val0:vib0",
                    "param:dur1",
                    "param:dur3",
                    "param:dur3",
                    "param:val-4:vib0",
                ],
            }
        )
        == "bfx:tremolo_bar:type7:pos0:val0:vib0:pos7:val-4:vib0"
    )
    # Warning: invalid bend token. First position must be zero
    assert (
        unsplit_bend_fx(
            {
                "token": "nfx:bend:type5",
                "params": [
                    "param:dur6",
                    "param:val0:vib0",
                    "param:dur6",
                    "param:val-4:vib0",
                    "param:dur6",
                    "param:val0:vib0",
                ],
            }
        )
        == "nfx:bend:type5:pos0:val0:vib0:pos6:val-4:vib0:pos12:val0:vib0"
    )
    # Warning: invalid tremolo_bar token. Position cannot be greater than 12
    assert (
        unsplit_bend_fx(
            {
                "token": "nfx:bend:type4",
                "params": [
                    "param:dur0",
                    "param:val0:vib0",
                    "param:dur12",
                    "param:val-4:vib0",
                    "param:dur6",
                    "param:val0:vib0",
                ],
            }
        )
        == "nfx:bend:type4:pos0:val0:vib0:pos12:val-4:vib0"
    )
    # Warning: invalid tremolo_bar token. Replacing with most common bend token
    assert (
        unsplit_bend_fx(
            {
                "token": "nfx:bend:type3",
                "params": [
                    "param:dur0",
                    "param:val0:vib0",
                    "param:dur4",
                    "param:val-4:vib0",
                    "param:dur6",
                    "param:val0",
                ],
            }
        )
        == "nfx:bend:type3:pos0:val0:vib0:pos2:val4:vib0:pos4:val4:vib0:pos6:val0:vib0:pos8:val0:vib0:pos10:val4:vib0:pos12:val4:vib0"
    )
    # This just adds the durations together
    assert (
        unsplit_bend_fx(
            {
                "token": "nfx:bend:type1",
                "params": [
                    "param:val0:vib0",
                    "param:dur1",
                    "param:dur3",
                    "param:dur3",
                    "param:val-4:vib0",
                ],
            }
        )
        == "nfx:bend:type1:pos0:val0:vib0:pos7:val-4:vib0"
    )

    # Normal Tests
    assert (
        unsplit_bend_fx(
            {
                "token": "bfx:tremolo_bar:type6",
                "params": [
                    "param:val0:vib0",
                    "param:dur6",
                    "param:val-4:vib0",
                    "param:dur6",
                    "param:val0:vib0",
                ],
            }
        )
        == "bfx:tremolo_bar:type6:pos0:val0:vib0:pos6:val-4:vib0:pos12:val0:vib0"
    )
    assert (
        unsplit_bend_fx(
            {
                "token": "nfx:bend:type2",
                "params": [
                    "param:val0:vib0",
                    "param:dur2",
                    "param:val2:vib0",
                    "param:dur2",
                    "param:val2:vib0",
                    "param:dur2",
                    "param:val0:vib0",
                    "param:dur6",
                    "param:val0:vib0",
                ],
            }
        )
        == "nfx:bend:type2:pos0:val0:vib0:pos2:val2:vib0:pos4:val2:vib0:pos6:val0:vib0:pos12:val0:vib0"
    )
    # More than one bend point at the same time is OK
    assert (
        unsplit_bend_fx(
            {
                "token": "nfx:bend:type2",
                "params": [
                    "param:val0:vib0",
                    "param:dur3",
                    "param:val0:vib0",
                    "param:val-4:vib0",
                ],
            }
        )
        == "nfx:bend:type2:pos0:val0:vib0:pos3:val0:vib0:pos3:val-4:vib0"
    )


def test_split_unsplit():
    # Now test that splitting and unsplitting will give the samem result
    # token = unsplit_bend_fx(split_rare_token(token))
    # note: this test is only for nfx and bfx tokens
    def split_unsplit_task(fx, verbose=True):
        fx_split = split_rare_token(fx)
        fx_dict = {"token": fx_split[0], "params": fx_split[1:]}
        unsplit = unsplit_fx(fx_dict, verbose=verbose)
        assert fx == unsplit, "Expected %s got %s" % (fx, unsplit)

    split_unsplit_task("nfx:grace:fret43:duration128:dead0:beat0:transition3")
    split_unsplit_task("nfx:grace:fret4:duration32:dead0:beat0:transition2")

    split_unsplit_task("nfx:trill:fret36:duration240")
    split_unsplit_task("nfx:trill:fret6:duration120")

    split_unsplit_task(
        "bfx:tremolo_bar:type6:pos0:val0:vib0:pos6:val-4:vib0:pos12:val0:vib0"
    )
    split_unsplit_task("bfx:tremolo_bar:type1:pos0:val0:vib0:pos6:val-4:vib0")
    split_unsplit_task(
        "nfx:bend:type2:pos0:val0:vib0:pos2:val2:vib0:pos4:val2:vib0:pos6:val0:vib0:pos12:val0:vib0"
    )
