import os
import pathlib
import shutil
import tarfile
import time
import urllib.request

import nox

DIR = pathlib.Path(__file__).parent.resolve()
VENV_DIR = pathlib.Path('./.venv').resolve()

nox.options.sessions = ['test', 'coverage']


@nox.session
def build(session: nox.Session) -> None:
    """
    Build an SDist and wheel with ``flit``.
    """

    dist_dir = DIR.joinpath("dist")
    if dist_dir.exists():
        shutil.rmtree(dist_dir)

    session.install(".[dev]")
    session.run("flit", "build")


@nox.session
def dev(session: nox.Session) -> None:
    """
    Sets up a python development environment for the project.

    This session will:
    - Create a python virtualenv for the session
    - Install the `virtualenv` cli tool into this environment
    - Use `virtualenv` to create a global project virtual environment
    - Invoke the python interpreter from the global project environment to install
      the project and all it's development dependencies.
    """

    session.install("virtualenv")
    # VENV_DIR here is a pathlib.Path location of the project virtualenv
    # e.g. .venv
    session.run("virtualenv", os.fsdecode(VENV_DIR), silent=True)

    python = os.fsdecode(VENV_DIR.joinpath("bin/python"))

    # Use the venv's interpreter to install the project along with
    # all it's dev dependencies, this ensures it's installed in the right way
    session.run(python, "-m", "pip", "install", "-e", ".[dev,test,doc]", external=True)


@nox.session
def tests(session) -> None:
    """
    Run the unit and regular tests.
    """
    session.install(".[tests]")
    session.run("pytest", *session.posargs)


@nox.session
def coverage(session) -> None:
    """
    Run the unit and regular tests, and save coverage report
    """
    session.install(".[tests]", "pytest-cov")
    session.run(
        "pytest", "--cov=./", "--cov-report=xml", *session.posargs
    )


@nox.session
def docs(session: nox.Session) -> None:
    """
    Build the docs.

    To run ``sphinx-autobuild``,  do:

    .. code-block::console

       nox -s doc -- autobuild

    Otherwise the docs will be built once using
    """
    session.install(".[docs]")
    if session.posargs:
        if "autobuild" in session.posargs:
            print("Building docs at http://127.0.0.1:8000 with sphinx-autobuild -- use Ctrl-C to quit")
            session.run("sphinx-autobuild", "doc", "doc/_build/html")
        else:
            print("Unsupported argument to docs")
    else:
        session.run("sphinx-build", "-nW", "--keep-going", "-b", "html", "doc/", "doc/_build/html")


# ---- used by sessions that "clean up" data for tests
def clean_dir(dir_path):
    """
    "clean" a directory by removing all files
    (that are not hidden)
    without removing the directory itself
    """
    dir_path = pathlib.Path(dir_path)
    dir_contents = dir_path.glob('*')
    for content in dir_contents:
        if content.is_dir():
            shutil.rmtree(content)
        else:
            if content.name.startswith('.'):
                # e.g., .gitkeep file we don't want to delete
                continue
            content.unlink()


DATA_FOR_TESTS_DIR = './tests/data-for-tests/'
SOURCE_TEST_DATA_DIR = f"{DATA_FOR_TESTS_DIR}source/"
SOURCE_TEST_DATA_DIRS = [
    dir_ for dir_
    in sorted(pathlib.Path(SOURCE_TEST_DATA_DIR).glob('*/'))
    if dir_.is_dir()
]


@nox.session(name='test-data-clean-source')
def test_data_clean_source(session) -> None:
    """
    Clean (remove) 'source' test data, used by TEST_DATA_GENERATE_SCRIPT.
    """
    clean_dir(SOURCE_TEST_DATA_DIR)


SOURCE_TEST_DATA_URL = 'https://osf.io/z6pf4/download'
SOURCE_TEST_DATA_TAR = f'{SOURCE_TEST_DATA_DIR}source-test-data.tar.gz'


@nox.session(name='test-data-tar-source')
def test_data_tar_source(session) -> None:
    """
    Make a .tar.gz file of just the source test data used to run tests on CI.
    """
    session.log(f"Making tarfile with source data: {SOURCE_TEST_DATA_TAR}")
    session.run("python", "./tests/scripts/make_source_test_data.py")


@nox.session(name='test-data-download-source')
def test_data_download_source(session) -> None:
    """
    Download and extract a .tar.gz file of 'source' test data, used by TEST_DATA_GENERATE_SCRIPT.
    """
    session.log(f'Downloading: {SOURCE_TEST_DATA_URL}')
    urllib.request.urlretrieve(SOURCE_TEST_DATA_URL, SOURCE_TEST_DATA_TAR)
    session.log(f'Extracting downloaded tar: {SOURCE_TEST_DATA_TAR}')
    shutil.unpack_archive(filename=SOURCE_TEST_DATA_TAR, extract_dir=SOURCE_TEST_DATA_DIR, format="gztar")
