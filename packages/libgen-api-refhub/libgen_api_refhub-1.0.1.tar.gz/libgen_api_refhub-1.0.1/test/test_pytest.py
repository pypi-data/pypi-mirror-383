import pytest
from pathlib import Path

from libgen_api_refhub.libgen_search import LibgenSearch
from libgen_api_refhub.search_request import SearchRequest


title = "Pride and Prejudice"
author = "Agatha Christie"

FIXTURES = Path(__file__).parent / "fixtures"


class _FakeResponse:
    def __init__(self, text: str, status_code: int = 200):
        self.text = text
        self.status_code = status_code


def _load_fixture(name: str) -> str:
    return (FIXTURES / name).read_text(encoding="utf-8")


@pytest.fixture(autouse=True)
def mock_requests(monkeypatch):
    title_html = _load_fixture("title_search.html")
    author_html = _load_fixture("author_search.html")
    download_html = _load_fixture("download_page.html")

    def fake_get(url, *args, **kwargs):
        if "column=title" in url:
            return _FakeResponse(title_html)
        if "column=author" in url:
            return _FakeResponse(author_html)
        if "ads.php" in url:
            return _FakeResponse(download_html)
        raise AssertionError(f"Unexpected URL requested: {url}")

    monkeypatch.setattr("libgen_api_refhub.search_request.requests.get", fake_get)
    monkeypatch.setattr("libgen_api_refhub.libgen_search.requests.get", fake_get)
    SearchRequest.domain = "https://libgen.li"


@pytest.fixture
def search_client():
    return LibgenSearch()


class TestBasicSearching:
    def test_title_search(self, search_client):
        titles = search_client.search_title(title)
        first_result = titles[0]

        assert title in first_result["Title"]

    def test_author_search(self, search_client):
        titles = search_client.search_author(author)
        first_result = titles[0]

        assert author in first_result["Author"]

    def test_title_filtering(self, search_client):
        title_filters = {"Year": "2007", "Extension": "epub"}
        titles = search_client.search_title_filtered(title, title_filters, exact_match=True)
        first_result = titles[0]

        assert (title in first_result["Title"]) & fields_match(
            title_filters, first_result
        )

    def test_author_filtering(self, search_client):
        author_filters = {"Language": "German", "Year": "2009"}
        titles = search_client.search_author_filtered(author, author_filters, exact_match=True)
        first_result = titles[0]

        assert (author in first_result["Author"]) & fields_match(
            author_filters, first_result
        )

    # explicit test of exact filtering
    # should return no results as they will all get filtered out
    def test_exact_filtering(self, search_client):
        exact_filters = {"Extension": "PDF"}
        titles = search_client.search_author_filtered(author, exact_filters, exact_match=True)

        assert len(titles) == 0

    def test_non_exact_filtering(self, search_client):
        non_exact_filters = {"Extension": "PDF"}
        titles = search_client.search_author_filtered(author, non_exact_filters, exact_match=False)
        first_result = titles[0]

        assert (author in first_result["Author"]) & fields_match(
            non_exact_filters, first_result, exact=False
        )

    def test_non_exact_partial_filtering(self, search_client):
        partial_filters = {"Extension": "p", "Year": "200"}
        titles = search_client.search_title_filtered(title, partial_filters, exact_match=False)
        first_result = titles[0]

        assert (title in first_result["Title"]) & fields_match(
            partial_filters, first_result, exact=False
        )

    def test_exact_partial_filtering(self, search_client):
        exact_partial_filters = {"Extension": "p"}
        titles = search_client.search_title_filtered(
            title, exact_partial_filters, exact_match=True
        )

        assert len(titles) == 0

    def test_resolve_download_links(self, search_client):
        titles = search_client.search_author(author)
        title_to_download = titles[0]
        dl_links = search_client.resolve_download_links(title_to_download)

        assert list(dl_links.keys()) == ["GET", "Cloudflare", "IPFS.io", "Infura"]
        assert all(dl_links[key] for key in dl_links)

    # should return an error if search query is less than 3 characters long
    def test_raise_error_on_short_search(self, search_client):
        with pytest.raises(Exception):
            search_client.search_title(title[0:2])

####################
# Helper Functions #
####################

# Check object fields for equality -
# -> Returns True if they match.
# -> Returns False otherwise.
#
# when exact-True, fields are checked strictly (==).
#
# when exact=False, fields are normalized to lower case,
# and checked whether filter value is a subset of the response.
def fields_match(filter_obj, response_obj, exact=True):
    for key, value in filter_obj.items():

        if exact is False:
            value = value.lower()
            response_obj[key] = response_obj[key].lower()
            if value not in response_obj[key]:
                return False

        elif response_obj[key] != value:
            return False
    return True
