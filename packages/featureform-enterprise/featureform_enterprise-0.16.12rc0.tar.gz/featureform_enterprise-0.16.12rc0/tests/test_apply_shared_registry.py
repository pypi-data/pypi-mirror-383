from unittest.mock import MagicMock
import featureform.cli as cli_module
from click.testing import CliRunner


def test_context_isolation_between_apply_calls(tmp_path, monkeypatch):
    """Test that different apply() calls don't share context"""

    config_file = tmp_path / "config.py"
    config_file.write_text("context['value'] = 42")

    # Patch Client in the cli module (where it's imported)
    mock_client_instance = MagicMock()
    mock_client_class = MagicMock(return_value=mock_client_instance)
    monkeypatch.setattr(cli_module, 'Client', mock_client_class)

    runner = CliRunner()

    # First apply call
    result = runner.invoke(cli_module.apply, [str(config_file)])
    assert result.exit_code == 0

    # Modify file - if contexts were shared, the assert would fail
    config_file.write_text("""
assert 'value' not in context, "Context should be fresh for each apply() call"
context['value'] = 100
""")

    # Second apply call - should get a fresh context
    result = runner.invoke(cli_module.apply, [str(config_file)])
    assert result.exit_code == 0

    # If we get here without AssertionError, contexts are properly isolated
    assert mock_client_class.call_count == 2
    assert mock_client_instance.apply.call_count == 2


def test_context_shared_across_files_in_single_apply(tmp_path, monkeypatch):
    """Test that files in a single apply() call share the same context"""

    file1 = tmp_path / "file1.py"
    file1.write_text("context['shared'] = 'hello'")

    file2 = tmp_path / "file2.py"
    file2.write_text("""
assert context['shared'] == 'hello', "Should see file1's value"
context['shared'] = 'world'
""")

    file3 = tmp_path / "file3.py"
    file3.write_text("""
assert context['shared'] == 'world', "Should see file2's modification"
""")

    mock_client_instance = MagicMock()
    mock_client_class = MagicMock(return_value=mock_client_instance)
    monkeypatch.setattr(cli_module, 'Client', mock_client_class)

    runner = CliRunner()

    # All three files in one apply call
    result = runner.invoke(cli_module.apply, [str(file1), str(file2), str(file3)])
    assert result.exit_code == 0

    # If assertions in files didn't raise, context was properly shared
    assert mock_client_class.call_count == 1
    assert mock_client_instance.apply.call_count == 1


def test_context_shared_in_directory(tmp_path, monkeypatch):
    """Test that files in a directory share the same context (alphabetical order)"""

    # Create directory with multiple files (alphabetical order matters)
    (tmp_path / "a_first.py").write_text("context['counter'] = 1")
    (tmp_path / "b_second.py").write_text("context['counter'] += 10")
    (tmp_path / "c_third.py").write_text("context['counter'] *= 2")

    mock_client_instance = MagicMock()
    mock_client_class = MagicMock(return_value=mock_client_instance)
    monkeypatch.setattr(cli_module, 'Client', mock_client_class)

    runner = CliRunner()

    result = runner.invoke(cli_module.apply, [str(tmp_path)])
    assert result.exit_code == 0

    # Context should have been shared across files
    # (1 + 10) * 2 = 22 would be in context if we could inspect it
    # The fact that no AssertionError was raised proves it worked
    assert mock_client_class.call_count == 1
    assert mock_client_instance.apply.call_count == 1


def test_context_with_url(tmp_path, monkeypatch):
    """Test that URLs can also use shared context"""

    # Create a local file first
    local_file = tmp_path / "local.py"
    local_file.write_text("context['from_file'] = 'local'")

    # Mock URL reading
    import urllib.request

    mock_response = MagicMock()
    mock_response.read.return_value = b"context['from_url'] = 'remote'\nassert context['from_file'] == 'local'"
    mock_response.__enter__.return_value = mock_response
    mock_response.__exit__.return_value = None

    def mock_urlopen(url):
        return mock_response

    monkeypatch.setattr(urllib.request, 'urlopen', mock_urlopen)

    # Mock Client
    mock_client_instance = MagicMock()
    mock_client_class = MagicMock(return_value=mock_client_instance)
    monkeypatch.setattr(cli_module, 'Client', mock_client_class)

    runner = CliRunner()

    # Apply both file and URL
    result = runner.invoke(cli_module.apply, [str(local_file), "https://example.com/config.py"])
    assert result.exit_code == 0

    # If no AssertionError, context was shared between file and URL
    assert mock_client_class.call_count == 1