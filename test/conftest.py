import os
import pytest
from _pytest.monkeypatch import MonkeyPatch
@pytest.fixture(autouse=True)
def set_env(monkeypatch: MonkeyPatch):
    """
    Conftest is really useful for setup/teardown of pytest fixtures, but it can also be used
    to override or manage env settings. EG in my work repo, we have set_env_default and set_env_new
    where set_env_new overrides several env variables. Then pytest can be set to automatically run all
    tests with both sets of configs. Demoing a basic override of the strip env variable.
    """
    monkeypatch.setenv("STRIPE_PUBLIC_KEY", "1234_PUBLIC")
    monkeypatch.setenv("STRIPE_SECRET_KEY", "1234_SECRET")
