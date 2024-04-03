from .fixtures import full_github  # noqa

from extensionapis.domain_summary.basic_domain_summary import get_path_root


def test_get_path_root_landing_page():
    path_prefix, url_prefix = get_path_root("https://github.com")
    assert path_prefix == ""
    assert url_prefix == "https://github.com/"


def test_get_path_single_path_component():
    path_prefix, url_prefix = get_path_root("https://nytimes.com/single-path")
    assert path_prefix == "single-path"
    assert url_prefix == "https://nytimes.com/single-path"


def test_get_path_two_path_components():
    path_prefix, url_prefix = get_path_root("https://nytimes.com/first/second")
    assert path_prefix == "first/second"
    assert url_prefix == "https://nytimes.com/first/second"


def test_get_path_three_path_components():
    path_prefix, url_prefix = get_path_root("https://nytimes.com/first/second/third")
    assert path_prefix == "first/second"
    assert url_prefix == "https://nytimes.com/first/second"
