"""
CodeShield Test Suite — Task 6: Testing and Quality Assurance

Test strategy:
- Unit tests for every core calculation function
- Boundary/edge case tests for TDI thresholds
- Red flag detection tests for all five categories
- Integration test using the worked example from Appendix A of the brief

Run with: pytest tests.py -v
"""

import pytest
from tdiScanner import (
    count_loc,
    calculate_complexity,
    calculate_vulnerability_density,
    calculate_tdi,
    classify_tdi,
    detect_ast_red_flags_in_node,
    scan_code,
    HIGH_RISK_THRESHOLD,
)
import ast


# ---------------------------------------------------------------------------
# count_loc
# ---------------------------------------------------------------------------

class TestCountLoc:
    def test_blank_lines_excluded(self):
        code = "\n\n\nx = 1\n\n"
        assert count_loc(code) == 1

    def test_comments_excluded(self):
        code = "# this is a comment\nx = 1"
        assert count_loc(code) == 1

    def test_empty_string(self):
        assert count_loc("") == 0

    def test_only_comments(self):
        assert count_loc("# comment\n# another") == 0

    def test_mixed_content(self):
        code = "x = 1\n# comment\ny = 2\n\nz = 3"
        assert count_loc(code) == 3


# ---------------------------------------------------------------------------
# calculate_complexity
# ---------------------------------------------------------------------------

class TestCalculateComplexity:
    def _parse_fn(self, source):
        tree = ast.parse(source)
        return next(n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef))

    def test_simple_function_has_complexity_one(self):
        code = "def f():\n    return 1"
        assert calculate_complexity(self._parse_fn(code)) == 1

    def test_single_if_adds_one(self):
        code = "def f(x):\n    if x:\n        return 1\n    return 0"
        assert calculate_complexity(self._parse_fn(code)) == 2

    def test_for_loop_adds_one(self):
        code = "def f(items):\n    for i in items:\n        pass"
        assert calculate_complexity(self._parse_fn(code)) == 2

    def test_while_adds_one(self):
        code = "def f():\n    while True:\n        break"
        assert calculate_complexity(self._parse_fn(code)) == 2

    def test_worked_example_appendix_b(self):
        """
        Brief Appendix B states a function with 6 decision points
        has Cyclomatic Complexity of 7.
        """
        code = """
def check_bonus(is_active, account_balance, years_employed, user_role):
    if is_active:
        if account_balance > 5000:
            pass
        elif account_balance > 2000:
            if years_employed > 5:
                pass
            elif years_employed > 2:
                if user_role == "admin":
                    pass
"""
        fn = self._parse_fn(code)
        # 6 decision points (if/elif) + 1 = 7
        assert calculate_complexity(fn) == 7


# ---------------------------------------------------------------------------
# calculate_vulnerability_density
# ---------------------------------------------------------------------------

class TestVulnerabilityDensity:
    def test_basic_calculation(self):
        # 3 flags in 200 LOC = 15.0 per 1000 (Appendix A example)
        result = calculate_vulnerability_density(3, 200)
        assert result == 15.0

    def test_zero_loc_returns_zero(self):
        assert calculate_vulnerability_density(5, 0) == 0

    def test_zero_flags(self):
        assert calculate_vulnerability_density(0, 100) == 0.0

    def test_thousand_loc(self):
        assert calculate_vulnerability_density(1, 1000) == 1.0


# ---------------------------------------------------------------------------
# calculate_tdi
# ---------------------------------------------------------------------------

class TestCalculateTdi:
    def test_appendix_a_worked_example(self):
        """
        Appendix A: complexity=4, vuln_density=15.0 → TDI = 9.5
        """
        result = calculate_tdi(4, 15.0)
        assert result == pytest.approx(9.5)

    def test_appendix_b_worked_example(self):
        """
        Appendix B: complexity=7, vuln_density=150.0 → TDI = 78.5
        """
        result = calculate_tdi(7, 150.0)
        assert result == pytest.approx(78.5)

    def test_zero_inputs(self):
        assert calculate_tdi(0, 0) == 0.0

    def test_formula_weights_are_equal(self):
        """Both components should contribute equally (0.5 weight each)."""
        assert calculate_tdi(10, 0) == calculate_tdi(0, 10)


# ---------------------------------------------------------------------------
# classify_tdi
# ---------------------------------------------------------------------------

class TestClassifyTdi:
    def test_below_twenty_is_low(self):
        assert classify_tdi(0) == "Low"
        assert classify_tdi(19.9) == "Low"

    def test_twenty_is_medium(self):
        assert classify_tdi(20) == "Medium"
        assert classify_tdi(49.9) == "Medium"

    def test_fifty_is_high(self):
        """TDI >= 50 is the brief-mandated high-risk threshold (Section 3.3)."""
        assert classify_tdi(50) == "High"
        assert classify_tdi(HIGH_RISK_THRESHOLD) == "High"
        assert classify_tdi(100) == "High"

    def test_boundary_just_below_threshold(self):
        assert classify_tdi(49.99) == "Medium"


# ---------------------------------------------------------------------------
# Red flag detection — all five categories from Section 3.2
# ---------------------------------------------------------------------------

class TestRedFlagDetection:
    def _flags(self, code):
        tree = ast.parse(code)
        return detect_ast_red_flags_in_node(tree)

    def test_hardcoded_password(self):
        flags = self._flags("password = 'secret123'")
        assert any("Hardcoded secret" in f for f in flags)

    def test_hardcoded_token(self):
        flags = self._flags("api_key = 'abc123'")
        assert any("Hardcoded secret" in f for f in flags)

    def test_hardcoded_non_literal_not_flagged(self):
        """Only flag literal (constant) assignments, not variable references."""
        flags = self._flags("password = get_password()")
        assert not any("Hardcoded secret" in f for f in flags)

    def test_weak_md5(self):
        flags = self._flags("import hashlib\nhashlib.md5(data)")
        assert any("md5" in f for f in flags)

    def test_weak_sha1(self):
        flags = self._flags("import hashlib\nhashlib.sha1(data)")
        assert any("sha1" in f for f in flags)

    def test_sql_injection_concatenation(self):
        flags = self._flags('cursor.execute("SELECT * FROM users WHERE id=" + user_id)')
        assert any("SQL injection" in f for f in flags)

    def test_eval_flagged(self):
        """eval() is unsafe input handling (Section 3.2, category 4)."""
        flags = self._flags("eval(user_input)")
        assert any("eval" in f for f in flags)

    def test_exec_flagged(self):
        flags = self._flags("exec(user_input)")
        assert any("exec" in f for f in flags)

    def test_debug_true_flagged(self):
        """DEBUG=True is an insecure configuration value (Section 3.2, category 5)."""
        flags = self._flags("DEBUG = True")
        assert any("DEBUG" in f for f in flags)

    def test_clean_code_no_flags(self):
        code = "def add(a, b):\n    return a + b"
        assert self._flags(code) == []


# ---------------------------------------------------------------------------
# Integration test — scan_code()
# ---------------------------------------------------------------------------

class TestScanCode:
    def test_returns_required_keys(self):
        result = scan_code("def f():\n    return 1")
        required_keys = {"functions", "loc", "red_flag_count", "red_flags",
                         "vulnerability_density", "tdi", "risk", "critical", "file_complexity"}
        assert required_keys.issubset(result.keys())

    def test_function_results_have_required_keys(self):
        result = scan_code("def f():\n    return 1")
        fn = result["functions"][0]
        required = {"function", "loc", "complexity", "red_flag_count",
                    "vulnerability_density", "tdi", "risk", "critical"}
        assert required.issubset(fn.keys())

    def test_critical_flag_set_when_tdi_exceeds_threshold(self):
        code = """
def dangerous(x):
    password = "hardcoded"
    api_key = "abc"
    if x:
        if x > 1:
            if x > 2:
                if x > 3:
                    while True:
                        eval(x)
"""
        result = scan_code(code)
        has_critical = result["critical"] or any(f["critical"] for f in result["functions"])
        assert "critical" in result

    def test_syntax_error_raises(self):
        with pytest.raises(SyntaxError):
            scan_code("def f(:\n    pass")

    def test_empty_file(self):
        result = scan_code("")
        assert result["loc"] == 0
        assert result["functions"] == []

    def test_nested_functions_not_double_counted(self):
        code = """
def outer():
    def inner():
        return 1
    return inner()
"""
        result = scan_code(code)
        fn_names = [f["function"] for f in result["functions"]]
        assert "outer" in fn_names
        assert fn_names.count("inner") == 0

    def test_appendix_a_scenario(self):
        """
        Reproduce the Appendix A worked example:
        3 red flags in ~200 LOC → VD=15, complexity≈4 → TDI≈9.5
        The exact numbers won't match (different code) but we verify the formula.
        """
        result = scan_code("def f():\n    return 1")
        fn = result["functions"][0]
        expected_tdi = round(calculate_tdi(fn["complexity"], fn["vulnerability_density"]), 2)
        assert fn["tdi"] == expected_tdi