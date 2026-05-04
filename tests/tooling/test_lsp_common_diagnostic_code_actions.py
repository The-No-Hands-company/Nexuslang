"""Coverage for common parser/type diagnostic quick-fix code actions."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from nexuslang.lsp.code_actions import CodeActionsProvider


class MockServer:
    def __init__(self):
        self.documents = {}
        self.workspace_index = None


def _provider() -> CodeActionsProvider:
    return CodeActionsProvider(MockServer())


def _range(line: int = 0):
    return {
        "start": {"line": line, "character": 0},
        "end": {"line": line, "character": 0},
    }


def _find_action(actions, title_fragment: str):
    for action in actions:
        if title_fragment.lower() in action.get("title", "").lower():
            return action
    return None


def test_parser_quick_fix_adds_missing_end():
    provider = _provider()
    uri = "file:///missing_end.nxl"
    code = "if true\n    print text \"ok\"\n"
    diagnostic = {
        "range": {"start": {"line": 1, "character": 0}, "end": {"line": 2, "character": 0}},
        "severity": 1,
        "message": "Syntax Error: Expected 'end' before EOF",
        "source": "nlpl",
        "code": "E001",
    }

    actions = provider.get_code_actions(uri, code, _range(1), [diagnostic])
    action = _find_action(actions, "Add missing end")
    assert action is not None
    edit = action["edit"]["changes"][uri][0]
    assert edit["newText"] == "end\n"


def test_parser_quick_fix_adds_closing_paren():
    provider = _provider()
    uri = "file:///missing_paren.nxl"
    code = "print text (value\n"
    diagnostic = {
        "range": {"start": {"line": 0, "character": 0}, "end": {"line": 0, "character": 17}},
        "severity": 1,
        "message": "Syntax Error: expected ')'",
        "source": "nlpl",
        "code": "E001",
    }

    actions = provider.get_code_actions(uri, code, _range(0), [diagnostic])
    action = _find_action(actions, "Add closing )")
    assert action is not None
    edit = action["edit"]["changes"][uri][0]
    assert edit["newText"] == ")"


def test_type_quick_fix_adds_annotation_without_structured_fixes():
    provider = _provider()
    uri = "file:///type_annot.nxl"
    code = "set count to 1\n"
    diagnostic = {
        "range": {"start": {"line": 0, "character": 0}, "end": {"line": 0, "character": 10}},
        "severity": 1,
        "message": "Type error: expected 'Integer', got 'String'",
        "source": "nlpl",
        "code": "E201",
    }

    actions = provider.get_code_actions(uri, code, _range(0), [diagnostic])
    action = _find_action(actions, "Add type annotation: Integer")
    assert action is not None
    edit = action["edit"]["changes"][uri][0]
    assert "as Integer" in edit["newText"]


def test_boolean_quick_fix_for_if_condition():
    provider = _provider()
    uri = "file:///bool_fix.nxl"
    code = "if count\n    print text \"ok\"\nend\n"
    diagnostic = {
        "range": {"start": {"line": 0, "character": 0}, "end": {"line": 0, "character": 8}},
        "severity": 1,
        "message": "Type error: if condition must be a boolean, got 'Integer'",
        "source": "nlpl",
        "code": "E201",
    }

    actions = provider.get_code_actions(uri, code, _range(0), [diagnostic])
    action = _find_action(actions, "explicit boolean check")
    assert action is not None
    edit = action["edit"]["changes"][uri][0]
    assert edit["newText"] == "if count is true"
