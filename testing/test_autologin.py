from pytest import MonkeyPatch
from pytest_mock import MockerFixture

from spyrit.network.autologin import Autologin
from spyrit.network.connection import Status
from spyrit.network.fragments import NetworkFragment, TextFragment
from spyrit.settings.scrambled_text import ScrambledText
from spyrit.settings.spyrit_settings import LoginStyle, SpyritSettings


class TestAutologin:
    def test_login_sent_when_conditions_are_met(
        self, mocker: MockerFixture, monkeypatch: MonkeyPatch
    ) -> None:
        settings = SpyritSettings.Login()
        settings.name.set(name := "test")
        settings.password.set(password := ScrambledText("test"))
        settings.login_style.set(style := LoginStyle.CONNECT_NAME_PASSWORD_CR)

        monkeypatch.setattr(
            Autologin, "_sendLogin", send_login := mocker.Mock()
        )

        autologin = Autologin(settings, mocker.Mock())

        autologin.awaitLoginPrecondition([])
        send_login.assert_not_called()

        autologin.awaitLoginPrecondition([NetworkFragment(Status.DISCONNECTED)])
        send_login.assert_not_called()

        autologin.awaitLoginPrecondition([TextFragment("Some text.")])
        send_login.assert_not_called()

        autologin.awaitLoginPrecondition([NetworkFragment(Status.RESOLVING)])
        send_login.assert_not_called()

        autologin.awaitLoginPrecondition([NetworkFragment(Status.CONNECTED)])
        send_login.assert_not_called()

        autologin.awaitLoginPrecondition([TextFragment("Some text again.")])
        send_login.assert_called_once_with(name, password, style)
        send_login.reset_mock()

        autologin.awaitLoginPrecondition([TextFragment("More text now.")])
        send_login.assert_not_called()

        autologin.awaitLoginPrecondition([NetworkFragment(Status.DISCONNECTED)])
        send_login.assert_not_called()

        autologin.awaitLoginPrecondition([NetworkFragment(Status.CONNECTED)])
        send_login.assert_not_called()

        autologin.awaitLoginPrecondition([TextFragment("And more text now.")])
        send_login.assert_called_once_with(name, password, style)
        send_login.reset_mock()

    def test_login_not_send_if_name_or_password_empty(
        self, mocker: MockerFixture, monkeypatch: MonkeyPatch
    ) -> None:
        settings = SpyritSettings.Login()
        settings.name.set("test")
        settings.password.set(ScrambledText("test"))
        settings.login_style.set(LoginStyle.CONNECT_NAME_PASSWORD_CR)

        monkeypatch.setattr(
            Autologin, "_sendLogin", send_login := mocker.Mock()
        )

        autologin = Autologin(settings, mocker.Mock())

        autologin.awaitLoginPrecondition(
            [
                NetworkFragment(Status.DISCONNECTED),
                NetworkFragment(Status.CONNECTED),
                TextFragment("Some text."),
            ]
        )
        send_login.assert_called_once()
        send_login.reset_mock()

        settings.name.set("")
        settings.password.set(ScrambledText("test"))

        autologin.awaitLoginPrecondition(
            [
                NetworkFragment(Status.DISCONNECTED),
                NetworkFragment(Status.CONNECTED),
                TextFragment("Some text."),
            ]
        )
        send_login.assert_not_called()

        settings.name.set("test")
        settings.password.set(ScrambledText(""))

        autologin.awaitLoginPrecondition(
            [
                NetworkFragment(Status.DISCONNECTED),
                NetworkFragment(Status.CONNECTED),
                TextFragment("Some text."),
            ]
        )
        send_login.assert_not_called()

    def test_login_string_is_correct(self, mocker: MockerFixture) -> None:
        settings = SpyritSettings.Login()
        autologin = Autologin(settings, send := mocker.Mock())

        autologin._sendLogin(  # pyright: ignore [reportPrivateUsage]
            "test_name",
            ScrambledText("test_password"),
            LoginStyle.CONNECT_NAME_PASSWORD_CR,
        )
        send.assert_called_once_with("connect test_name test_password\n")
        send.reset_mock()

        autologin._sendLogin(  # pyright: ignore [reportPrivateUsage]
            "",
            ScrambledText("test_password"),
            LoginStyle.CONNECT_NAME_PASSWORD_CR,
        )
        send.assert_not_called()

        autologin._sendLogin(  # pyright: ignore [reportPrivateUsage]
            "test_name",
            ScrambledText(""),
            LoginStyle.CONNECT_NAME_PASSWORD_CR,
        )
        send.assert_not_called()
