import pytest


@pytest.mark.smoke
def test_songdkl_help(script_runner):
    ret = script_runner.run('songdkl', '-h')
    assert ret.success
    assert ret.stderr == ''
