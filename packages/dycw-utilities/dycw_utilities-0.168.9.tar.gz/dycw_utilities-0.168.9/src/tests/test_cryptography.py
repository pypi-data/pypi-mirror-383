from __future__ import annotations

from cryptography.fernet import Fernet
from hypothesis import given
from hypothesis.strategies import text
from pytest import raises

from utilities.cryptography import (
    _ENV_VAR,
    GetFernetError,
    decrypt,
    encrypt,
    get_fernet,
)
from utilities.os import temp_environ


class TestEncryptAndDecrypt:
    @given(text=text())
    def test_round_trip(self, text: str) -> None:
        key = Fernet.generate_key()
        with temp_environ({_ENV_VAR: key.decode()}):
            assert decrypt(encrypt(text)) == text


class TestGetFernet:
    def test_main(self) -> None:
        key = Fernet.generate_key()
        with temp_environ({_ENV_VAR: key.decode()}):
            fernet = get_fernet()
        assert isinstance(fernet, Fernet)

    def test_error(self) -> None:
        with (
            temp_environ({_ENV_VAR: None}),
            raises(GetFernetError, match=r"Environment variable 'FERNET_KEY' is None"),
        ):
            _ = get_fernet()
