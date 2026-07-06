from app.mcp.sandbox import SANDBOX_DIR, check_path


def test_valid_subpath_allowed():
    assert check_path("notes.txt") is None


def test_dotdot_escape_blocked():
    assert check_path("../../etc/passwd") == "path_escape"


def test_absolute_path_blocked():
    assert check_path("/etc/passwd") == "path_escape"


def test_dotdot_obfuscation_bypass_not_exploitable():
    # "....//" is the classic bypass for a NAIVE sanitizer that does a single
    # string.replace("../", "") pass: stripping the middle "../" out of
    # "....//" leaves "../" behind, reconstituting the escape sequence.
    # check_path() never does string stripping - it resolves the real path
    # first (realpath treats "...." as a literal 4-dot directory name, not
    # "..") and only then checks containment, so this input never escapes:
    # it resolves to a literal (nonexistent) subpath *inside* the sandbox.
    assert check_path("....//....//etc/passwd") is None


def test_sibling_directory_footgun_blocked():
    # Regression guard: a naive `candidate.startswith(base)` check would wrongly
    # allow this, since the string "<sandbox>-evil/secret" starts with the
    # string "<sandbox>" when there's no trailing separator. commonpath()
    # compares path components, not raw strings, and correctly rejects it.
    sibling = str(SANDBOX_DIR) + "-evil"
    assert check_path(f"../{SANDBOX_DIR.name}-evil/secret.txt") == "path_escape"
    assert not sibling.startswith(str(SANDBOX_DIR) + "/")  # sanity check on the setup itself
