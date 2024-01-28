from spyrit.settings.spyrit_settings import SpyritSettings


class TestSettings:
    def test_title(self) -> None:
        settings = SpyritSettings()

        assert settings.title() == "Unnamed world"

        settings.net.server.set("some.game.org")
        settings.net.port.set(1234)

        assert settings.title() == "Unnamed world (some.game.org:1234)"

        settings.name.set("Some game")

        assert settings.title() == "Some game"

    def test_section_name(self) -> None:
        settings = SpyritSettings()

        world = settings.newSection()
        assert world.sectionName() == ""

        world.name.set("Test!")
        assert world.sectionName() == "test"

        world.name.clear()
        assert world.sectionName() == ""
