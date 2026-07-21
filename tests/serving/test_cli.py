"""Tests for the yasched CLI (init/check), no server started."""

from pathlib import Path

from yasched.backending.loading.DatabaseLoader import DatabaseLoader
from yasched.serving.cli import main


def test_init_creates_agenda(tmp_path):
    agenda = tmp_path / "agenda.yaml"
    rc = main(["init", "--agenda", str(agenda)])
    assert rc == 0
    assert agenda.exists()
    # the created agenda must itself be loadable
    db = DatabaseLoader.load(agenda)
    assert db.topics


def test_init_does_not_overwrite_without_force(tmp_path):
    agenda = tmp_path / "agenda.yaml"
    agenda.write_text("topics: []\n", encoding="utf-8")
    main(["init", "--agenda", str(agenda)])
    assert agenda.read_text(encoding="utf-8") == "topics: []\n"  # untouched


def test_init_force_overwrites(tmp_path):
    agenda = tmp_path / "agenda.yaml"
    agenda.write_text("topics: []\n", encoding="utf-8")
    main(["init", "--agenda", str(agenda), "--force"])
    assert agenda.read_text(encoding="utf-8") != "topics: []\n"


def test_check_ok_and_missing(tmp_path, teacher_path, capsys):
    assert main(["check", "--agenda", str(teacher_path)]) == 0
    assert "topics=7" in capsys.readouterr().out
    assert main(["check", "--agenda", str(tmp_path / "missing.yaml")]) == 1


def test_agenda_flag_before_subcommand(teacher_path, capsys):
    assert main(["--agenda", str(teacher_path), "check"]) == 0


def test_personal_template_parses():
    template = Path("resources/personal_template/agenda.yaml")
    db = DatabaseLoader.load(template)
    assert db.topics and db.tasks
    assert "urgent" in db.traits
