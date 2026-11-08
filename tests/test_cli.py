from pokerl.cli import main


def test_demo_runs(capsys):
    assert main(["demo", "--seed", "3"]) == 0
    out = capsys.readouterr().out
    assert "winner" in out.lower()


def test_verify_runs(capsys):
    assert main(["verify"]) == 0
    assert "OK" in capsys.readouterr().out


def test_dispatch_runs(capsys):
    assert main(["dispatch", "--no-readme"]) == 0
    assert "Daily Lab Dispatch" in capsys.readouterr().out
