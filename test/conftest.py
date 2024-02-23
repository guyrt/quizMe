import os
import pytest
from _pytest.monkeypatch import MonkeyPatch
@pytest.fixture(autouse=True)
def set_env(monkeypatch: MonkeyPatch):
    monkeypatch.setenv("STRIPE_PUBLIC_KEY", "1234")
    monkeypatch.setenv("STRIPE_PUBLIC_KEY", "1234")
