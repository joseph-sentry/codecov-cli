import pytest
from click.testing import CliRunner

from codecov_cli import main
from codecov_cli.helpers import request as request_module


def test_existing_commands():
    assert sorted(main.cli.commands.keys()) == [
        "create-commit",
        "create-report",
        "create-report-results",
        "do-upload",
        "empty-upload",
        "get-report-results",
        "label-analysis",
        "pr-base-picking",
        "process-test-results",
        "send-notifications",
        "static-analysis",
        "upload-coverage",
        "upload-process",
    ]


class TestHttpHeaderOption:
    @pytest.fixture(autouse=True)
    def reset_extra_headers(self):
        request_module._extra_headers = {}
        yield
        request_module._extra_headers = {}

    def test_http_header_valid(self):
        runner = CliRunner()
        result = runner.invoke(
            main.cli,
            [
                "--http-header",
                "CF-Access-Client-Id:abc123",
                "--http-header",
                "CF-Access-Client-Secret:xyz789",
                "do-upload",
                "--help",
            ],
            obj={},
        )
        assert result.exit_code == 0
        assert request_module._extra_headers == {
            "CF-Access-Client-Id": "abc123",
            "CF-Access-Client-Secret": "xyz789",
        }

    def test_http_header_invalid_format(self):
        runner = CliRunner()
        result = runner.invoke(
            main.cli,
            ["--http-header", "InvalidHeader", "do-upload", "--help"],
            obj={},
        )
        assert result.exit_code != 0
        assert "Invalid header format" in result.output

    def test_http_header_value_with_colon(self):
        runner = CliRunner()
        result = runner.invoke(
            main.cli,
            ["--http-header", "X-Test:value:with:colons", "do-upload", "--help"],
            obj={},
        )
        assert result.exit_code == 0
        assert request_module._extra_headers == {"X-Test": "value:with:colons"}

    def test_http_header_empty_name(self):
        runner = CliRunner()
        result = runner.invoke(
            main.cli,
            ["--http-header", ":value", "do-upload", "--help"],
            obj={},
        )
        assert result.exit_code != 0
        assert "Header name cannot be empty" in result.output
