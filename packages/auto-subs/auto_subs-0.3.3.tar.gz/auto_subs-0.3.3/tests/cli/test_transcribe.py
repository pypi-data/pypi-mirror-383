from pathlib import Path
from unittest.mock import MagicMock, patch

from typer.testing import CliRunner

from auto_subs.cli import app

runner = CliRunner()


@patch("auto_subs.cli.transcribe.transcribe_api")
def test_cli_transcribe_success(mock_api_transcribe: MagicMock, fake_media_file: Path) -> None:
    """Test successful transcription of a single media file."""
    mock_api_transcribe.return_value = "WEBVTT\n\n00:00:00.100 --> 00:00:01.200\nHello world"
    output_file = fake_media_file.with_suffix(".vtt")

    result = runner.invoke(
        app,
        [
            "transcribe",
            str(fake_media_file),
            "-f",
            "vtt",
            "--model",
            "tiny",
            "-o",
            str(output_file),
        ],
    )

    assert result.exit_code == 0
    mock_api_transcribe.assert_called_once()
    args, kwargs = mock_api_transcribe.call_args
    assert args[0] == fake_media_file
    assert kwargs["output_format"] == "vtt"
    assert kwargs["model_name"] == "tiny"
    assert "Successfully saved subtitles" in result.stdout


@patch("auto_subs.cli.transcribe.transcribe_api")
def test_cli_transcribe_batch(mock_api_transcribe: MagicMock, tmp_path: Path) -> None:
    """Test successful transcription of a directory of media files."""
    input_dir = tmp_path / "input"
    output_dir = tmp_path / "output"
    input_dir.mkdir()
    output_dir.mkdir()

    (input_dir / "test1.mp3").touch()
    (input_dir / "test2.mp4").touch()
    (input_dir / "ignored.txt").touch()

    mock_api_transcribe.return_value = "1\n00:00:00,100 --> 00:00:01,200\nHello"

    result = runner.invoke(app, ["transcribe", str(input_dir), "-o", str(output_dir), "-f", "srt"])

    assert result.exit_code == 0
    assert mock_api_transcribe.call_count == 2
    assert "Transcribing: test1.mp3" in result.stdout
    assert "Transcribing: test2.mp4" in result.stdout
    assert "ignored.txt" not in result.stdout
    assert (output_dir / "test1.srt").exists()
    assert (output_dir / "test2.srt").exists()


@patch("auto_subs.cli.transcribe.transcribe_api")
def test_cli_transcribe_karaoke_with_ass(mock_transcribe_api: MagicMock, fake_media_file: Path) -> None:
    """Test that the --karaoke flag is correctly passed to the API for ASS format."""
    mock_transcribe_api.return_value = "[Script Info]\nDialogue: ..."
    runner.invoke(app, ["transcribe", str(fake_media_file), "-f", "ass", "--karaoke"])

    mock_transcribe_api.assert_called_once()
    _, kwargs = mock_transcribe_api.call_args
    assert kwargs["ass_settings"].highlight_style is not None


@patch("auto_subs.cli.transcribe.transcribe_api")
def test_cli_transcribe_karaoke_with_non_ass_warning(mock_transcribe_api: MagicMock, fake_media_file: Path) -> None:
    """Test that a warning is shown when using --karaoke with a non-ASS format."""
    mock_transcribe_api.return_value = "1\n00:00:00,100 --> 00:00:01,200\nHello"
    result = runner.invoke(app, ["transcribe", str(fake_media_file), "-f", "srt", "--karaoke"])

    assert result.exit_code == 0
    assert "Warning: --karaoke flag is only applicable for ASS format." in result.stdout
    _, kwargs = mock_transcribe_api.call_args
    assert kwargs["ass_settings"].highlight_style is None


@patch(
    "auto_subs.cli.transcribe.transcribe_api",
    side_effect=ImportError("whisper not found"),
)
def test_cli_transcribe_import_error(mock_transcribe_api: MagicMock, fake_media_file: Path) -> None:
    """Test that a friendly message is shown on ImportError."""
    result = runner.invoke(app, ["transcribe", str(fake_media_file)])

    assert result.exit_code == 1
    assert "Error: whisper not found" in result.stdout
    assert "Please ensure 'auto-subs[transcribe]' is installed" in result.stdout


@patch(
    "auto_subs.cli.transcribe.transcribe_api",
    side_effect=Exception("A generic error occurred"),
)
def test_cli_transcribe_generic_error(mock_transcribe_api: MagicMock, fake_media_file: Path) -> None:
    """Test that a generic error during transcription is caught and reported."""
    result = runner.invoke(app, ["transcribe", str(fake_media_file)])

    assert result.exit_code == 1
    assert f"An unexpected error occurred while processing {fake_media_file.name}" in result.stdout
    assert "A generic error occurred" in result.stdout
