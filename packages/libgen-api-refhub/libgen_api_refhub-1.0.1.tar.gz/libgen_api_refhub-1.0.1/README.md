<div align="center">

![logo](logo.png)

![PyPI - Downloads](https://img.shields.io/pypi/dm/libgen-api-refhub?style=plastic)
![GitHub](https://img.shields.io/github/license/Merkousha/libgen-api-refhub?style=plastic)
![PyPI](https://img.shields.io/pypi/v/libgen-api-refhub?style=plastic)
![GitHub Repo stars](https://img.shields.io/github/stars/Merkousha/libgen-api-refhub?style=plastic)

</div>

Search Library Genesis programmatically using a simple Python library.

Allows you to search Library Genesis by title or author, filter results, resolve download links, and get book cover images.

## Acknowledgments

This project is a fork of the original [libgen-api](https://github.com/harrison-broadbent/libgen-api) library created by [Harrison Broadbent](https://github.com/harrison-broadbent). We extend our sincere gratitude to the original author for creating this excellent library and making it open source. This fork builds upon the original work with additional features and improvements.

## New Features
- **Dynamic Domain Selection**: Automatically finds and uses the fastest working LibGen mirror
- **Book Cover Images**: Added ability to fetch book cover images
- **Improved Reliability**: Better error handling and domain fallback
- **Browser Simulation**: Added realistic browser headers to prevent blocking
- **Better Title Extraction**: Improved accuracy in extracting book titles from search results
- **Concurrent Domain Testing**: Tests multiple domains simultaneously to find the fastest one
- **Enhanced Error Handling**: Better timeout and error management for domain testing
- **Realistic Browser Headers**: Comprehensive browser simulation to avoid detection
- **Image Resolution**: New method to extract book cover images from search results

## Contents

- [Getting Started](#getting-started)
- [Basic Searching](#basic-searching)
- [Filtered Searching](#filtered-searching)
  - [Filtered Title Searching](#filtered-title-searching)
  - [Filtered Author Searching](#filtered-author-searching)
  - [Non-exact Filtered Searching](#non-exact-filtered-searching)
  - [Filter Fields](#filter-fields)
- [Resolving mirror links](#resolving-mirror-links)
- [More Examples](#more-examples)
- [Further Information](#further-information)
- [Testing](#testing)

---

Please ⭐ if you find this useful!

---

## Getting Started

Install the package -

```
pip install libgen-api-refhub
```

Perform a basic search -

```python
# search_title()

from libgen_api_refhub import LibgenSearch
s = LibgenSearch()
domains = [
    "https://libgen.bz",
    "https://libgen.li", 
    "https://libgen.la",
    "https://libgen.vg",
    "https://libgen.gs",
    "https://libgen.gl",
]

fastest_domain = s.find_fastest_domain(domains)
results = s.search_title("Pride and Prejudice")
print(results)
```

Check out the [results layout](#results-layout) to see how the results data is formatted.

## Basic Searching:

**_NOTE_**: All queries must be at least 3 characters long. This is to avoid any errors on the LibGen end (different mirrors have different requirements, but a minimum of 3 characters is the official limit).

Search by title or author:

### Title:

```python
# search_title()

from libgen_api_refhub import LibgenSearch
s = LibgenSearch()
domains = [
    "https://libgen.bz",
    "https://libgen.li", 
    "https://libgen.la",
    "https://libgen.vg",
    "https://libgen.gs",
    "https://libgen.gl",
]

fastest_domain = s.find_fastest_domain(domains)
results = s.search_title("Pride and Prejudice")
print(results)
```

### Author:

```python
# search_author()

from libgen_api_refhub import LibgenSearch
s = LibgenSearch()
domains = [
    "https://libgen.bz",
    "https://libgen.li", 
    "https://libgen.la",
    "https://libgen.vg",
    "https://libgen.gs",
    "https://libgen.gl",
]

fastest_domain = s.find_fastest_domain(domains)
results = s.search_author("Jane Austen")
print(results)
```

## Filtered Searching

Skip to the [Examples](#filtered-title-searching)

- You can define a set of filters, and then use them to filter the search results that get returned.
- By default, filtering will remove results that do not match the filters exactly (case-sensitive) -
  - This can be adjusted by setting `exact_match=False` when calling one of the filter methods, which allows for case-insensitive and substring filtering.

### Filtered Title Searching

```python
# search_title_filtered()

from libgen_api_refhub import LibgenSearch

tf = LibgenSearch()
domains = [
    "https://libgen.bz",
    "https://libgen.li", 
    "https://libgen.la",
    "https://libgen.vg",
    "https://libgen.gs",
    "https://libgen.gl",
]

fastest_domain = s.find_fastest_domain(domains)
title_filters = {"Year": "2007", "Extension": "epub"}
titles = tf.search_title_filtered("Pride and Prejudice", title_filters, exact_match=True)
print(titles)
```

### Filtered Author Searching

```python
# search_author_filtered()

from libgen_api_refhub import LibgenSearch

af = LibgenSearch()
domains = [
    "https://libgen.bz",
    "https://libgen.li", 
    "https://libgen.la",
    "https://libgen.vg",
    "https://libgen.gs",
    "https://libgen.gl",
]

fastest_domain = s.find_fastest_domain(domains)
author_filters = {"Language": "German", "Year": "2009"}
titles = af.search_author_filtered("Agatha Christie", author_filters, exact_match=True)
print(titles)
```

### Non-exact Filtered Searching

```python
# search_author_filtered(exact_match = False)

from libgen_api_refhub import LibgenSearch

ne_af = LibgenSearch()
domains = [
    "https://libgen.bz",
    "https://libgen.li", 
    "https://libgen.la",
    "https://libgen.vg",
    "https://libgen.gs",
    "https://libgen.gl",
]

fastest_domain = s.find_fastest_domain(domains)
partial_filters = {"Year": "200"}
titles = ne_af.search_author_filtered("Agatha Christie", partial_filters, exact_match=False)
print(titles)

```

### Filter Fields

You can filter against any of the Library Genesis column names, which are given as -

```python
col_names = [
        "ID",
        "Author",
        "Title",
        "Publisher",
        "Year",
        "Pages",
        "Language",
        "Size",
        "Extension",
        "Mirror_1",
        "Mirror_2",
        "Mirror_3",
        "Mirror_4",
        "Mirror_5",
        "Edit",
    ]
```

## Resolving mirror links

The mirror links returned in the results (ie. by running search_author() or search_title()) are not direct download links and do not resolve to a downloadable URL without further parsing.

An additional method, `resolve_download_links()`, can be to resolve the mirror links of a search item into direct download links.

The `Mirror_1` field is used by `resolve_download_links()` as the results generally contain the most useful URLs.

This method accepts a single result (type: dictionary) from the array of searched results, and
returns a dictionary of all the download links for `Mirror_1` (each mirror link has up to 4 download links):

```python
# resolve_download_links()

from libgen_api_refhub import LibgenSearch

s = LibgenSearch()
domains = [
    "https://libgen.bz",
    "https://libgen.li", 
    "https://libgen.la",
    "https://libgen.vg",
    "https://libgen.gs",
    "https://libgen.gl",
]

fastest_domain = s.find_fastest_domain(domains)
results = s.search_author("Jane Austen")
item_to_download = results[0]
download_links = s.resolve_download_links(item_to_download)
print(download_links)
```

Example output:

```json
{
  "GET": "http://example.com/file.epub",
  "Cloudflare": "http://example.com/file.epub",
  "IPFS.io": "http://example.com/file.epub",
  "Infura": "http://example.com/file.epub"
}
```

## Resolving book cover images

You can also extract book cover images from search results using the `resolve_image()` method.

This method accepts a single result (type: dictionary) from the array of searched results, and
returns the URL of the book cover image if available:

```python
# resolve_image()

from libgen_api_refhub import LibgenSearch

s = LibgenSearch()
results = s.search_author("Jane Austen")
item_to_get_image = results[0]
image_url = s.resolve_image(item_to_get_image)
print(image_url)
```

Example output:
```
http://example.com/covers/book_cover.jpg
```

## Dynamic domain selection

The library now includes a method to automatically find the fastest working LibGen mirror from a list of domains:

```python
# find_fastest_domain()

from libgen_api_refhub import LibgenSearch

s = LibgenSearch()
domains = [
    "https://libgen.bz",
    "https://libgen.li", 
    "https://libgen.la",
    "https://libgen.vg",
    "https://libgen.gs",
    "https://libgen.gl",
]

fastest_domain = s.find_fastest_domain(domains)
print(f"Using fastest domain: {fastest_domain}")
```

This method tests all domains concurrently and automatically sets the fastest responding domain for future requests.

## Enhanced browser simulation

The library now includes comprehensive browser simulation to avoid detection and blocking:

- **Realistic User-Agent**: Uses Firefox browser headers
- **Complete HTTP Headers**: Includes Accept, Accept-Language, Accept-Encoding, and other standard headers
- **Security Headers**: Implements DNT, Sec-Fetch-* headers for modern browser compatibility
- **Connection Management**: Proper keep-alive and cache control headers

This ensures better compatibility with LibGen mirrors and reduces the likelihood of being blocked.

## More Examples

See the [testing file](test/manualtesting.py) for more examples.

## Results Layout

Results are returned as a list of dictionaries:

```json
[
  {
    "Author": "John Smith",
    "Edit": "http://example.com",
    "Extension": "epub",
    "ID": "00000",
    "Language": "German",
    "Mirror_1": "http://example.com",
    "Mirror_2": "http://example.com",
    "Mirror_3": "http://example.com",
    "Mirror_4": "http://example.com",
    "Mirror_5": "http://example.com",
    "Pages": "410",
    "Publisher": "Publisher",
    "Size": "1005 Kb",
    "Title": "Title",
    "Year": "2021"
  }
]
```

## Further information

- If there are no results, the library will return an empty array.
- All fields are strings.
- If a value is not present, the field will contain an empty string.
- Some listings will have page count listed in the form of "count[secondary-count]" as this is how they appear on Library Genesis.
- Only the first page of results (max. 25) will be returned.

## Testing

libgen-api-refhub uses Pytest to run unit tests.

To run the tests -

- ## Clone this repo -
  ```
  git clone https://github.com/Merkousha/libgen-api-refhub.git && cd libgen-api-refhub
  ```
- ## Install dependencies with -
  ```
  pip install .
  ```
- ## Run tests with -
  ```
  pytest
  ```

## Contributors

A massive thank you to those that have contributed to this project!

Please don't hesitate to raise an issue, or fork this project and improve on it.

Thanks to the following contributors -

- [calmoo](https://github.com/calmoo)
- [HENRYMARTIN5](https://github.com/HENRYMARTIN5)

## New Distribution

(for my own reference)

1. python3 -m pip install --user --upgrade setuptools wheel
2. python3 -m pip install --user --upgrade twine
3. python3 setup.py sdist bdist_wheel
4. python3 -m twine upload dist/\*
