"""Tests for the CLI entry point behaviour."""

from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace
from unittest import mock

import pytest

from talks_reducer import cli


def test_main_launches_gui_when_no_args(monkeypatch: pytest.MonkeyPatch) -> None:
    """The GUI should be launched when no CLI arguments are provided."""

    launch_calls: list[list[str]] = []

    def fake_launch(argv: list[str]) -> bool:
        launch_calls.append(list(argv))
        return True

    def fail_build_parser() -> None:
        raise AssertionError("Parser should not be built when GUI launches")

    monkeypatch.setattr(cli, "_launch_gui", fake_launch)
    monkeypatch.setattr(cli, "_build_parser", fail_build_parser)

    cli.main([])

    assert launch_calls == [[]]


def test_main_runs_cli_with_arguments(monkeypatch: pytest.MonkeyPatch) -> None:
    """Providing CLI arguments should bypass the GUI and run the pipeline."""

    parsed_args = SimpleNamespace(
        input_file=["input.mp4"],
        output_file=None,
        temp_folder=None,
        silent_threshold=None,
        silent_speed=None,
        sounded_speed=None,
        frame_spreadage=None,
        sample_rate=None,
        small=False,
        server_url=None,
    )

    parser_mock = mock.Mock()
    parser_mock.parse_args.return_value = parsed_args

    outputs: list[cli.ProcessingOptions] = []

    class DummyReporter:
        def log(self, _message: str) -> None:  # pragma: no cover - simple stub
            pass

    def fake_speed_up_video(options: cli.ProcessingOptions, reporter: object):
        outputs.append(options)
        return SimpleNamespace(output_file=Path("/tmp/output.mp4"))

    def fake_gather_input_files(_paths: list[str]) -> list[str]:
        return ["/tmp/input.mp4"]

    def fail_launch(_argv: list[str]) -> bool:
        raise AssertionError("GUI should not be launched when arguments exist")

    monkeypatch.setattr(cli, "_build_parser", lambda: parser_mock)
    monkeypatch.setattr(cli, "gather_input_files", fake_gather_input_files)
    monkeypatch.setattr(cli, "speed_up_video", fake_speed_up_video)
    monkeypatch.setattr(cli, "TqdmProgressReporter", lambda: DummyReporter())
    monkeypatch.setattr(cli, "_launch_gui", fail_launch)

    cli.main(["input.mp4"])

    parser_mock.parse_args.assert_called_once_with(["input.mp4"])
    assert len(outputs) == 1
    assert outputs[0].input_file == Path("/tmp/input.mp4")


def test_main_launches_server_tray_when_flag_set(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The --server flag should launch the system tray helper."""

    tray_calls: list[list[str]] = []

    def fake_tray(argv: list[str]) -> bool:
        tray_calls.append(list(argv))
        return True

    def fail_build_parser() -> None:
        raise AssertionError("Parser should not be built when launching the tray")

    monkeypatch.setattr(cli, "_launch_server_tray", fake_tray)
    monkeypatch.setattr(cli, "_build_parser", fail_build_parser)
    monkeypatch.setattr(cli, "_launch_gui", lambda argv: False)

    cli.main(["--server", "--share", "--port", "9005"])

    assert tray_calls == [["--share", "--port", "9005"]]


def test_main_exits_when_server_tray_unavailable(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Tray startup failure should mimic a CLI error."""

    monkeypatch.setattr(cli, "_launch_server_tray", lambda argv: False)
    monkeypatch.setattr(cli, "_launch_gui", lambda argv: False)

    with pytest.raises(SystemExit):
        cli.main(["--server"])


def test_main_exits_when_server_unavailable(monkeypatch: pytest.MonkeyPatch) -> None:
    """A missing Gradio server should raise SystemExit to mimic CLI failures."""

    monkeypatch.setattr(cli, "_launch_server", lambda argv: False)
    monkeypatch.setattr(cli, "_launch_gui", lambda argv: False)

    with pytest.raises(SystemExit):
        cli.main(["server"])


def test_main_uses_remote_server_when_url_provided(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The CLI should delegate to the remote server client when --url is set."""

    parsed_args = SimpleNamespace(
        input_file=["input.mp4"],
        output_file=None,
        temp_folder=None,
        silent_threshold=0.25,
        silent_speed=5.0,
        sounded_speed=1.75,
        frame_spreadage=None,
        sample_rate=None,
        small=True,
        server_url="http://localhost:9005/",
    )

    parser_mock = mock.Mock()
    parser_mock.parse_args.return_value = parsed_args

    def fake_gather_input_files(_paths: list[str]) -> list[str]:
        return ["/tmp/input.mp4"]

    calls: list[SimpleNamespace] = []

    def fake_send_video(**kwargs):
        calls.append(SimpleNamespace(**kwargs))
        return Path("/tmp/result.mp4"), "Summary", "Log"

    monkeypatch.setattr(cli, "_build_parser", lambda: parser_mock)
    monkeypatch.setattr(cli, "gather_input_files", fake_gather_input_files)
    monkeypatch.setattr(cli, "_launch_gui", lambda argv: False)
    import talks_reducer.service_client as service_client_module

    monkeypatch.setattr(service_client_module, "send_video", fake_send_video)

    cli.main(["input.mp4", "--url", "http://localhost:9005/"])

    assert len(calls) == 1
    assert calls[0].input_path == Path("/tmp/input.mp4")
    assert calls[0].small is True
    assert calls[0].silent_threshold == 0.25
    assert calls[0].silent_speed == 5.0
    assert calls[0].sounded_speed == 1.75


def test_launch_server_tray_prefers_external_binary(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The packaged binary should be used when available."""

    binary_path = Path("/tmp/talks-reducer-server-tray")
    monkeypatch.setattr(cli, "_find_server_tray_binary", lambda: binary_path)

    run_calls: list[tuple[list[str], dict[str, object]]] = []

    def fake_run(args: list[str], **kwargs: object) -> SimpleNamespace:
        run_calls.append((list(args), dict(kwargs)))
        return SimpleNamespace(returncode=0)

    monkeypatch.setattr(cli.subprocess, "run", fake_run)

    assert cli._launch_server_tray_binary(["--foo"]) is True
    assert run_calls[0][0] == [str(binary_path), "--foo"]


def test_launch_server_tray_binary_hides_console_without_parent(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Windows launches should hide the console when detached."""

    binary_path = Path("C:/tray.exe")
    monkeypatch.setattr(cli, "_find_server_tray_binary", lambda: binary_path)
    monkeypatch.setattr(cli, "_should_hide_subprocess_console", lambda: True)
    monkeypatch.setattr(cli, "sys", SimpleNamespace(platform="win32"))

    calls: list[dict[str, object]] = []

    class DummySubprocess:
        CREATE_NO_WINDOW = 0x08000000

        @staticmethod
        def run(args: list[str], **kwargs: object) -> SimpleNamespace:
            calls.append(dict(kwargs))
            return SimpleNamespace(returncode=0)

    monkeypatch.setattr(cli, "subprocess", DummySubprocess)

    assert cli._launch_server_tray_binary([]) is True
    assert calls and calls[0].get("creationflags") == DummySubprocess.CREATE_NO_WINDOW


def test_launch_server_tray_binary_handles_failures(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A missing executable should fall back to the Python module."""

    monkeypatch.setattr(cli, "_find_server_tray_binary", lambda: None)

    assert cli._launch_server_tray_binary([]) is False


def test_launch_server_tray_falls_back_to_module(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """When the binary is unavailable, the module entry point is invoked."""

    monkeypatch.setattr(cli, "_launch_server_tray_binary", lambda argv: False)

    calls: list[list[str]] = []

    class DummyModule:
        @staticmethod
        def main(argv: list[str]) -> None:
            calls.append(list(argv))

    monkeypatch.setattr(cli, "import_module", lambda name, package=None: DummyModule)

    assert cli._launch_server_tray(["--bar"]) is True
    assert calls == [["--bar"]]


def test_main_launches_server_when_requested(monkeypatch: pytest.MonkeyPatch) -> None:
    """The server subcommand should dispatch to the Gradio launcher."""

    server_calls: list[list[str]] = []

    def fake_server(argv: list[str]) -> bool:
        server_calls.append(list(argv))
        return True

    monkeypatch.setattr(cli, "_launch_server", fake_server)
    monkeypatch.setattr(cli, "_launch_gui", lambda argv: False)

    cli.main(["server", "--share"])

    assert server_calls == [["--share"]]
