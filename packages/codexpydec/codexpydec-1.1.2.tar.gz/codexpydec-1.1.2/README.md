# Codex

Codex is an archive format for storing and distributing large-scale
collections of articles. It was designed for the
[Omnipedia app](https://recursive.ink/omnipedia/), an offline Wikipedia reader
for iOS.

The Codex format has four notable features:

1. **Block compression.** Articles are grouped together and compressed
in "blocks" to balance compression ratio with random access speed.
2. **File sharding.** Archives can be split across many shards (separate files)
to allow for partial downloading over unstable connections.
3. **Isolated title index.** Article titles are stored separately from
articles to allow for rapid title searches without decompressing the articles
themselves.
4. **Incremental updates.** Infrastructure is in place to permit
incremental updates to articles.

This repository provides a reference implementation of the Codex decoder
(in Python) and describes the Codex format.


## CodexPyDec

CodexPyDec requires Python 3.10 or greater. It has no required dependencies
unless you want to access an archive compressed with LZFSE, in which case
[pyliblzfse](https://github.com/ydkhatri/pyliblzfse) is required.


### Installation

[CodexPyDec is available on the Python Package Index](https://pypi.org/project/codexpydec/)
and can be installed using pip:

```bash
pip install codexpydec
```

To install alongside pyliblzfse for LZFSE compression support, use:

```bash
pip install codexpydec[lzfse]
```

### Usage example

In your script or Python shell, import `CodexDecoder` from the `codexpydec`
package:

```python
from codexpydec import CodexDecoder
```

Load an archive by specifying the path to the Codex archive on your machine.
Do not include a shard number or file extension – these are appended
automatically.

```python
my_archive = CodexDecoder("path/to/my_archive")
```

If the archive loaded successfully, you will be able to read the library
metadata:

```python
print(my_archive.library_id)
print(my_archive.library_name)
print(my_archive.library_license)
print(my_archive.library_version)
print(my_archive.n_catalog_entries)
print(my_archive.n_library_entries)
```

#### Catalog search

Use the `search_catalog()` method to perform a search of the article titles:

```python
search_results = my_archive.search_catalog("united nations")
print(search_results)
```

`search_catalog()` returns a list of tuples. Each tuple holds the catalog
entry title (which may include redirect information) and an entry number that
points to the article content. For example:

```python
[
	('United Nations', 1231),
	('United nations\x00United Nations', 1231),
	...
	('United Nations Trusteeship Council', 135068)
]
```

The results above tell us that there is an article titled "United Nations"
located at entry number 1231, an article titled "United Nations Trusteeship
Council" located at entry number 135068, and a catalog redirect for "United
nations" (with a lowercase N) that redirects to the "United Nations" article.

Optionally, you can cap the number of results and remove redirects using the
`max_results` and `include_redirects` arguments:

```python
search_results = my_archive.search_catalog("united nations", max_results=10, include_redirects=False)
print(search_results)
```

#### Retrieving articles

There are three methods to retrieve an article, and your choice of which
method to use will depend on what information you have in advance. If you
only know the title, you can use the `get_article_by_title()` method:

```python
article = my_archive.get_article_by_title("United Nations")
print(article)
```

If you only know the entry number, you can use the
`get_article_by_entry_number()` method:

```python
article = my_archive.get_article_by_entry_number(1231)
print(article)
```

If you know both the title and entry number, you can use the
`get_article()` method:

```python
article = get_article("United Nations", 1231)
print(article)
```

`get_article()` and `get_article_by_title()` return the full article including
title and footer. `get_article_by_entry_number()` only returns the main
article body (without title and footer). `get_article_by_title()` is slower
because it needs to perform a catalog search to establish the entry number.
`get_article_by_entry_number()` is faster but does not include the title and
footer. `get_article()` provides the full article but you need to
know both title and entry number in advance.

#### Exporting articles

Once you've extracted an article, you can save it as a Markdown file like so:

```python
with open("output_directory/article.md", "w") as file:
	file.write(article)
```

To extract all articles from the archive, you can iterate over the archive
and save each article like so:

```python
for entry_number, article in my_archive:
	with open(f"output_directory/{entry_number}.md", "w") as file:
		file.write(article)
```

The complete set of decompressed articles will typically be around three times
larger than the compressed archive. Extracting millions of articles is likely
to take multiple hours.

To extract all articles based on some search query, you can use a script such
as the following:

```python
search_results = my_archive.search_catalog("united nations", max_results=10, include_redirects=False)
for (article_title, entry_number) in search_results:
	article = my_archive.get_article(article_title, entry_number)
	if article is not None:
		with open(f"output_directory/{entry_number}.md", "w") as file:
			file.write(article)
```


## The Codex Format

A Codex archive consists of three main parts: the **header**, the **catalog**,
and the **library**. The header can be further broken down into four parts:
the **header proper**, the **inventory**, the **catalog index**, and the
**library index**. The catalog and library consist of some number of **catalog
blocks** and **library blocks**. Each catalog and library block is comprised of
a **block index** and a **block payload**.

Archives can be split across multiple files and each file must be named with
its shard number (e.g. `my_archive.017.codex`). Shard numbers (as presented
in the filename) are always three digits and left-padded with zeros. Shard
`000` is always the "header shard" – the shard that contains the header.
Optionally, the catalog and library can also be placed in the header shard
resulting in a single file.


### Header

The header contains general metadata about the contents of the archive as well
as various counts, pointers, and indexes for navigating the rest of the
archive.

The header proper is 256 bytes in length and consists of a mix of strings and
integers as described in the table below. Strings are always UTF-8 encoded
and right-padded with null bytes. Integers are always unsigned and
little-endian, but they vary in bit-length. The ranges and lengths in the
following table are expressed in bytes.

| Field                 | Length | Range   | Notes |
| :-------------------- | :----- | :------ | :---- |
| File signature        | 4      | 0–4     | String. Always set to `CODX` (hex: `43 4f 44 58`). |
| Major schema version  | 1      | 4–5     | 8-bit integer. Major schema versions indicate breaking changes to the schema.|
| Minor schema version  | 1      | 5–6     | 8-bit integer. Minor schema versions indicate backward-compatible changes to the schema. |
| Compression algorithm | 4      | 6–10    | String. Compression algorithm used to compress blocks, typically set to `ZLIB`, `LZ4`, `LZMA`, `LZFS`. Codex does not mandate any particular compression format; however, the Python decoder only decodes ZLIB compressed archives. |
| Library ID            | 8      | 10–18   | String. Unique identifier for the library that remains fixed across library versions. |
| Library name          | 64     | 18–82   | String. Descriptive library name. |
| Library license       | 128    | 82–210  | String. Copyright and licensing information. |
| Library version       | 4      | 210–214 | 32-bit integer. Library version number, typically set to the snapshot date in YYYYMMDD format. |
| Patched version      | 4      | 214–218 | 32-bit integer. If set to 0, the archive is a regular archive with full articles. If greater than 0, the archive contains diffs patching the specified version number. |
| *N* catalog entries   | 4      | 218–222 | 32-bit integer. Number of entries contained in the catalog. Must be > 0 and is limited to ~4.29 billion. |
| *N* library entries   | 4      | 222–226 | 32-bit integer. Number of articles contained in the library. Must be > 0 and is limited to ~4.29 billion. |
| *N* catalog blocks    | 2      | 226–228 | 16-bit integer. Number of compression blocks that the catalog is divided into. Must be > 0 and is limited to 65,535. |
| *N* library blocks    | 2      | 228–230 | 16-bit integer. Number of compression blocks that the library is divided into. Must be > 0 and is limited to 65,535. |
| *N* catalog shards    | 1      | 230–231 | 8-bit integer. Number of shards that the catalog blocks are distributed over. If 0, the catalog is contained in the header shard. Otherwise, the decoder expects to find additional files with with a zero-padded shard number at the end of the file name (e.g. `my_archive.001.codex`). Catalog shards (if any) are numbered from 001 to 00N in the filename (since 000 is reserved for the header shard). |
| *N* library shards    | 1      | 231–232 | 8-bit integer. Number of shards that the library blocks are distributed over. If 0, the library is contained in the header shard. Otherwise, the decoder expects to find additional files with with a zero-padded shard number at the end of the file name (e.g. `my_archive.002.codex`). Library shards (if any) are numbered sequentially after the catalog shard numbers. The total number of shards – header plus catalog plus library – cannot exceed 256. |
| Inventory pointer     | 8      | 232–240 | 32-bit integer. Byte offset of the inventory. |
| Catalog index pointer | 8      | 240–248 | 32-bit integer. Byte offset of the catalog index |
| Library index pointer | 8      | 248–256 | 32-bit integer. Byte offset of the library index |


### Inventory

The inventory is a chunk of compressed data of variable length stored in the
header shard immediately after the 256 bytes described above. It holds a list
of persistent article IDs (32-bit integers) that are only used during archive
updates. The inventory is immediately followed by the catalog index.


### Catalog index

The catalog index is a chunk of uncompressed data stored in the header shard
immediately after the inventory. It specifies the location of each catalog
block using 5 bytes. The first byte is the shard number (8-bit integer) and
the remaining 4 bytes is the file offset within the shard (32-bit integer).
The catalog index consists of *N* + 1 items, where *N* is the number of
catalog blocks, and is therefore (*N* + 1) × 5 bytes in length. The extra
item at the end of the catalog index specifies the byte position of the *end*
of the last catalog block. Thus, any two consecutive index items specify the
start and end position of a catalog block.


### Library index

The library index has the same format as the catalog index, with *N* = the
number of library blocks.


### Catalog and catalog blocks

The catalog is a concatenation of *N* catalog blocks, which may be spread
across multiple shards. Splitting across shards always occurs at block
boundaries.

Each catalog block is a chunk of compressed data of variable length. Once
decompressed, the catalog block consists of two parts: the block index and
the block payload. The first 4 bytes of the block index state how many
entries are contained in the block – the entry count, *N*. The remainder of
the index, which will be *N* × 4 bytes in length, gives the start position of
each block entry.

A catalog entry, which is variable in length, consists of two parts. The first
4 bytes is a 32-bit integer (the "entry number"). This entry number can be
translated into a shard–block–article address for lookup of the associated
article. The remainder of the catalog entry is a UTF-8 encoded string
(typically an article title). If the string contains a null byte, the entry
is a "redirection entry." The string should be split at the null byte to
yield two substrings: a redirect-from title and a redirect-to title.
Redirections make it possible for multiple catalog entries (e.g. "UN" and
"United Nations") to point to the same article.

Catalog entries are arranged in case-insensitive lexicographic order.


### Library and library blocks

The library has the same basic structure as the catalog, except that the
payload of each library block is a concatenation of articles. Articles are
arranged in arbitrary order. Article 0 – the first article in the first block
of the first shard – is special. It is the **footer text** that is
automatically appended to the bottom of each article.


## License

© 2025 Recursive Ink Ltd. CodexPyDec is licensed under the terms of the GNU
General Public License version 3 (GPLv3). By submitting a pull request you
represent that your contribution can be licensed under GPLv3.
