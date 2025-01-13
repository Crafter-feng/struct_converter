import pytest
from cli import CLI

def test_cli_initialization():
    cli = CLI()
    assert cli is not None

def test_cli_parse_arguments():
    cli = CLI()
    args = cli.parse_args(['input.c', 'output.py'])
    assert args.input == 'input.c'
    assert args.output == 'output.py'

def test_cli_invalid_arguments():
    cli = CLI()
    with pytest.raises(SystemExit):
        cli.parse_args([])  # No arguments provided 