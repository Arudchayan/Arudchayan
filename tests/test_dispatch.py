from pokerl.dispatch import DISPATCH_END, DISPATCH_START, build_dispatch, render_dispatch, update_readme


def test_dispatch_is_deterministic():
    a = build_dispatch(__import__("datetime").date(2026, 11, 8))
    b = build_dispatch(__import__("datetime").date(2026, 11, 8))
    assert a == b
    assert a["species"] in {s for s in __import__("pokerl.dex", fromlist=["SPECIES"]).SPECIES}


def test_dispatch_renders_markdown():
    payload = build_dispatch(__import__("datetime").date(2026, 11, 8))
    text = render_dispatch(payload)
    assert "Daily Lab Dispatch" in text
    assert payload["species_name"] in text
    assert "Today's experiment" in text


def test_dispatch_updates_markers(tmp_path):
    readme = tmp_path / "README.md"
    readme.write_text(f"before\n{DISPATCH_START}\nold\n{DISPATCH_END}\nafter\n", encoding="utf-8")
    payload = build_dispatch(__import__("datetime").date(2026, 11, 8))
    assert update_readme(payload, readme)
    text = readme.read_text(encoding="utf-8")
    assert "old" not in text
    assert payload["species_name"] in text
    assert text.startswith("before")
    assert text.rstrip().endswith("after")
