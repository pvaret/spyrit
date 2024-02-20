from spyrit.settings.spyrit_settings import SpyritSettings
from spyrit.settings.spyrit_state import SpyritState


def test_state_hierarchy_copy() -> None:
    state = SpyritState()
    settings = SpyritSettings()

    refs = [settings, state]

    state = state.getOrCreateSection("dummy")

    settings = settings.getOrCreateSection("depth_1")
    settings = settings.getOrCreateSection("depth_2")

    state = state.getStateSectionForSettingsSection(settings)

    assert state.meta().path() == settings.meta().path()
    assert state.sectionName() == "depth_2"
    assert (parent := state.parent()) is not None
    assert parent.sectionName() == "depth_1"

    del refs
