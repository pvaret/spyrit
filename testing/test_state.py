from spyrit.settings.spyrit_settings import SpyritSettings
from spyrit.settings.spyrit_state import SpyritState


def test_state_hierarchy_copy() -> None:
    state = SpyritState()
    settings = SpyritSettings()
    assert settings.id.get() == ""

    state = state.getOrCreateSection("dummy")

    level1 = settings.getOrCreateSection("depth_1")
    assert level1.id.get() != ""

    level2 = level1.getOrCreateSection("depth_2")
    assert level2.id.get() != ""

    level2_state = state.getStateSectionForSettingsSection(level2)

    assert level2_state.sectionName() == level2.id.get()
    assert (level1_state := level2_state.parent()) is not None
    assert level1_state.parent() is state
    assert level1_state.sectionName() == level1.id.get()
    assert state.getStateSectionForSettingsSection(level2) is level2_state
