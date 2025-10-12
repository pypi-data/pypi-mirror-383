import pytest
from prompt_toolkit.document import Document
from prompt_toolkit.completion import Completion
from prompt_toolkit.formatted_text import to_plain_text

# This import will only work if prompt_toolkit is installed
pytest.importorskip("prompt_toolkit")

from patchllm.tui.completer import PatchLLMCompleter

@pytest.fixture
def completer():
    """Provides a PatchLLMCompleter instance with mock data."""
    mock_scopes = {"base": {}, "js_files": {}}
    return PatchLLMCompleter(mock_scopes)

def test_initial_state_completions(completer):
    """Tests that only valid initial commands are shown when no goal or plan exists."""
    completer.set_session_state(has_goal=False, has_plan=False, has_pending_changes=False, can_revert=False, has_context=False)
    doc = Document("/")
    completions = list(completer.get_completions(doc, None))
    
    completion_displays = {to_plain_text(c.display) for c in completions}
    
    assert "task - set goal" in completion_displays
    assert "context - set context" in completion_displays
    assert "menu - help" in completion_displays
    # These should NOT be present in the initial state
    assert "plan - generate or manage" not in completion_displays
    assert "agent - run step" not in completion_displays
    assert "agent - approve changes" not in completion_displays
    assert "agent - revert last approval" not in completion_displays
    assert "agent - ask question" not in completion_displays

def test_has_context_state_completions(completer):
    """Tests that /ask is available when only context is set."""
    completer.set_session_state(has_goal=False, has_plan=False, has_pending_changes=False, can_revert=False, has_context=True)
    doc = Document("/")
    completions = list(completer.get_completions(doc, None))

    completion_displays = {to_plain_text(c.display) for c in completions}

    # These should be available
    assert "task - set goal" in completion_displays
    assert "context - set context" in completion_displays
    assert "agent - ask question" in completion_displays

    # These should NOT be present
    assert "plan - generate or manage" not in completion_displays
    assert "agent - run step" not in completion_displays

def test_has_goal_state_completions(completer):
    """Tests that plan generation is available once a goal is set."""
    completer.set_session_state(has_goal=True, has_plan=False, has_pending_changes=False, can_revert=False, has_context=False)
    doc = Document("/")
    completions = list(completer.get_completions(doc, None))
    
    completion_displays = {to_plain_text(c.display) for c in completions}
    
    assert "task - set goal" in completion_displays
    assert "plan - generate or manage" in completion_displays
    assert "agent - ask question" in completion_displays
    # These should NOT be present yet
    assert "agent - run step" not in completion_displays

def test_has_plan_state_completions(completer):
    """Tests that plan-related and execution commands are available once a plan exists."""
    completer.set_session_state(has_goal=True, has_plan=True, has_pending_changes=False, can_revert=False, has_context=False)
    doc = Document("/")
    completions = list(completer.get_completions(doc, None))
    
    completion_displays = {to_plain_text(c.display) for c in completions}
    
    assert "agent - run step" in completion_displays
    assert "agent - skip step" in completion_displays
    assert "agent - ask question" in completion_displays
    assert "plan - refine with feedback" in completion_displays
    # This should NOT be present
    assert "agent - approve changes" not in completion_displays

def test_pending_changes_state_completions(completer):
    """Tests that approval/diff commands are available only after a run."""
    completer.set_session_state(has_goal=True, has_plan=True, has_pending_changes=True, can_revert=False, has_context=False)
    doc = Document("/")
    completions = list(completer.get_completions(doc, None))
    
    completion_displays = {to_plain_text(c.display) for c in completions}
    
    # All previous commands should still be there
    assert "agent - run step" in completion_displays
    # The new commands should now be available
    assert "agent - approve changes" in completion_displays
    assert "agent - view diff" in completion_displays
    assert "agent - retry with feedback" in completion_displays

def test_can_revert_state_completions(completer):
    """Tests that the revert command is available after an approval."""
    # This state occurs right after an approval, where there are no *pending* changes, but there is something to revert.
    completer.set_session_state(has_goal=True, has_plan=True, has_pending_changes=False, can_revert=True, has_context=False)
    doc = Document("/")
    completions = list(completer.get_completions(doc, None))
    
    completion_displays = {to_plain_text(c.display) for c in completions}

    assert "agent - revert last approval" in completion_displays
    # Approve should not be available, as there are no pending (un-approved) changes
    assert "agent - approve changes" not in completion_displays


def test_completion_object_structure(completer):
    """Tests that the completion object has the correct text, display, and meta."""
    completer.set_session_state(has_goal=False, has_plan=False, has_pending_changes=False, can_revert=False, has_context=False)
    doc = Document("/task")
    completions = list(completer.get_completions(doc, None))
    
    task_completion = next((c for c in completions if c.text == '/task'), None)
    
    assert task_completion is not None
    assert task_completion.text == "/task"
    assert to_plain_text(task_completion.display) == "task - set goal"
    assert to_plain_text(task_completion.display_meta) == "Sets the high-level goal for the agent."