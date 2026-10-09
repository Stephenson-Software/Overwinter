"""Usage reporting and the settings behind it: what the environment switches,
who wins when two switches disagree, what is sent, and that the notice is
printed once per install. No test here reaches the trace service - an
enabled client is always a recording stand-in."""

import io
import os

import pytest

from overwinter import usageReporting
from overwinter.config import (
    USAGE_REPORTING_ENDPOINT_DEFAULT,
    USAGE_REPORTING_KEY_DEFAULT,
    Config,
)


class RecordingClient:
    """Stands in for TraceClient: built with the same arguments, reports
    into a list instead of onto a thread."""

    def __init__(self, baseUrl, application, key=None, enabled=True):
        self.baseUrl = baseUrl
        self.application = application
        self.key = key
        self.enabled = enabled
        self.reports = []

    def report(self, name, value=None, tags=None):
        self.reports.append((name, tags))


@pytest.fixture
def recording(monkeypatch):
    monkeypatch.setattr(usageReporting, "TraceClient", RecordingClient)
    monkeypatch.setattr(usageReporting, "isBrowserBuild", lambda: False)


# --- config -----------------------------------------------------------------


def test_the_save_directory_follows_the_environment_and_defaults_to_data(
    monkeypatch, tmp_path
):
    monkeypatch.setenv("OVERWINTER_SAVE_DIR", str(tmp_path / "elsewhere"))
    assert Config().dataDirectory == str(tmp_path / "elsewhere")
    monkeypatch.setenv("OVERWINTER_SAVE_DIR", "")
    assert Config().dataDirectory == "data"
    monkeypatch.delenv("OVERWINTER_SAVE_DIR")
    assert Config().dataDirectory == "data"


@pytest.mark.parametrize("value", ["0", "false", "FALSE", "no", " off "])
def test_reporting_is_switched_off_by_any_false_value(monkeypatch, value):
    monkeypatch.setenv("OVERWINTER_USAGE_REPORTING_ENABLED", value)
    assert Config().usageReportingEnabled is False


@pytest.mark.parametrize("value", [None, "", "  ", "true", "1", "maybe"])
def test_reporting_stays_on_for_anything_that_is_not_a_false_value(monkeypatch, value):
    if value is None:
        monkeypatch.delenv("OVERWINTER_USAGE_REPORTING_ENABLED")
    else:
        monkeypatch.setenv("OVERWINTER_USAGE_REPORTING_ENABLED", value)
    assert Config().usageReportingEnabled is True


def test_the_endpoint_and_key_default_when_unset_or_blank(monkeypatch):
    monkeypatch.setenv("OVERWINTER_USAGE_REPORTING_ENDPOINT", "   ")
    monkeypatch.delenv("OVERWINTER_USAGE_REPORTING_KEY", raising=False)
    config = Config()
    assert config.usageReportingEndpoint == USAGE_REPORTING_ENDPOINT_DEFAULT
    assert config.usageReportingKey == USAGE_REPORTING_KEY_DEFAULT


def test_the_endpoint_and_key_can_be_overridden_and_are_trimmed(monkeypatch):
    monkeypatch.setenv("OVERWINTER_USAGE_REPORTING_ENDPOINT", " http://local ")
    monkeypatch.setenv("OVERWINTER_USAGE_REPORTING_KEY", " k3y ")
    config = Config()
    assert config.usageReportingEndpoint == "http://local"
    assert config.usageReportingKey == "k3y"


# --- the client ---------------------------------------------------------------


def test_the_environment_opt_outs_win_over_the_setting(monkeypatch):
    monkeypatch.setenv("OVERWINTER_USAGE_REPORTING_ENABLED", "true")
    monkeypatch.setenv("DO_NOT_TRACK", "1")
    client = usageReporting.createClient(Config())
    assert not client.enabled
    assert client.disabled_reason == "environment"

    monkeypatch.delenv("DO_NOT_TRACK")
    monkeypatch.setenv("TRACE_USAGE_REPORTING", "off")
    client = usageReporting.createClient(Config())
    assert not client.enabled
    assert client.disabled_reason == "environment"


def test_the_setting_switches_the_client_off():
    # conftest sets OVERWINTER_USAGE_REPORTING_ENABLED=false for every test.
    client = usageReporting.createClient(Config())
    assert not client.enabled
    assert client.disabled_reason == "config"


def test_the_browser_build_never_builds_an_enabled_client(monkeypatch):
    monkeypatch.setenv("OVERWINTER_USAGE_REPORTING_ENABLED", "true")
    monkeypatch.setattr(usageReporting.sys, "platform", "emscripten")
    assert usageReporting.isBrowserBuild()
    assert not usageReporting.createClient(Config()).enabled


def test_the_client_is_built_from_the_settings(monkeypatch, recording):
    monkeypatch.setenv("OVERWINTER_USAGE_REPORTING_ENABLED", "true")
    monkeypatch.setenv("OVERWINTER_USAGE_REPORTING_ENDPOINT", "http://local")
    monkeypatch.setenv("OVERWINTER_USAGE_REPORTING_KEY", "k3y")
    client = usageReporting.createClient(Config())
    assert client.baseUrl == "http://local"
    assert client.application == usageReporting.PROGRAM_NAME == "Overwinter"
    assert client.key == "k3y"
    assert client.enabled is True


# --- the version ----------------------------------------------------------------


def test_the_version_is_read_from_version_txt():
    with open("version.txt", encoding="utf-8") as versionFile:
        expected = versionFile.read().strip()
    assert usageReporting.readVersion() == expected
    assert usageReporting.versionTags() == {"version": expected}


def test_a_missing_or_empty_version_file_is_none_not_a_placeholder(
    monkeypatch, tmp_path
):
    assert usageReporting.readVersion(str(tmp_path / "absent.txt")) is None
    empty = tmp_path / "version.txt"
    empty.write_text("  \n", encoding="utf-8")
    assert usageReporting.readVersion(str(empty)) is None
    monkeypatch.setattr(usageReporting, "VERSION_FILE", str(empty))
    assert usageReporting.versionTags() is None


# --- the notice -----------------------------------------------------------------


def test_the_notice_names_both_events_and_how_to_turn_it_off():
    for words in (
        "startup",
        "save-loaded",
        "program name and version only",
        "OVERWINTER_USAGE_REPORTING_ENABLED=false",
        "TRACE_USAGE_REPORTING=off",
        usageReporting.DETAILS_URL,
    ):
        assert words in usageReporting.NOTICE, words


def test_the_notice_is_printed_once_per_install():
    config = Config()
    first = io.StringIO()
    assert usageReporting.showNoticeOnce(config, first) is True
    assert first.getvalue() == usageReporting.NOTICE + "\n"
    marker = usageReporting.noticeMarkerPath(config)
    with open(marker, encoding="utf-8") as markerFile:
        assert markerFile.read() == usageReporting.NOTICE + "\n"

    second = io.StringIO()
    assert usageReporting.showNoticeOnce(config, second) is False
    assert second.getvalue() == ""


def test_the_notice_is_still_printed_when_the_marker_cannot_be_written(
    monkeypatch, tmp_path
):
    # A file where the save directory should be: makedirs fails.
    blocker = tmp_path / "not-a-directory"
    blocker.write_text("", encoding="utf-8")
    monkeypatch.setenv("OVERWINTER_SAVE_DIR", str(blocker))
    config = Config()
    for _ in range(2):
        output = io.StringIO()
        assert usageReporting.showNoticeOnce(config, output) is True
        assert usageReporting.NOTICE in output.getvalue()
    assert not os.path.exists(usageReporting.noticeMarkerPath(config))


# --- start ----------------------------------------------------------------------


def test_start_says_so_once_and_reports_startup_with_the_version(
    monkeypatch, recording
):
    monkeypatch.setenv("OVERWINTER_USAGE_REPORTING_ENABLED", "true")
    config = Config()
    output = io.StringIO()
    client = usageReporting.start(config, output)
    assert client.reports == [("startup", usageReporting.versionTags())]
    assert usageReporting.NOTICE in output.getvalue()

    again = io.StringIO()
    client = usageReporting.start(config, again)
    assert client.reports == [("startup", usageReporting.versionTags())]
    assert again.getvalue() == ""


def test_start_with_reporting_off_prints_nothing_and_leaves_no_marker():
    config = Config()
    output = io.StringIO()
    client = usageReporting.start(config, output)
    assert not client.enabled
    assert output.getvalue() == ""
    assert not os.path.exists(usageReporting.noticeMarkerPath(config))
