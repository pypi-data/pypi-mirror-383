"""Accessing and preparing arxiv data for the xv project.

The data was found at https://alex.macrocosm.so/download

At the point of writing this, my attempts enable `graze` to automatically confirm
download in the googledrive downloads (which, when downloading too-big files,
will tell the user it can't scan the file and ask the user to confirm the download).

Therefore, the following files need to be downloaded manually:
* **titles**: https://drive.google.com/file/d/1Ul5mPePtoPKHZkH5Rm6dWKAO11dG98GN/view?usp=share_link
* **abstracts**: https://drive.google.com/file/d/1g3K-wlixFxklTSUQNZKpEgN4WNTFTPIZ/view?usp=share_link

(If those urls don't work, perhaps they were updated: See here: https://alex.macrocosm.so/download .)

You can then copy them over to the place graze will look for by doing:

```python
from pathlib import Path
from imbed.util import Graze
from imbed.mdat.arxiv import urls

g[urls['titles']] = Path('TITLES_DATA_LOCAL_FILEPATH').read_bytes()
g[urls['abstracts']] = Path('ABSTRACTS_DATA_LOCAL_FILEPATH').read_bytes()
```

"""

import re
from typing import Mapping, Literal, Iterable, KT, Union, Optional, Callable
from functools import partial, lru_cache
import io
from itertools import chain
from dol import (
    FilesOfZip,
    remove_mac_junk_from_zip,
    add_ipython_key_completions,
    Pipe,
    cached_keys,
    wrap_kvs,
    KeyCodecs,
    FuncReader,
    KeyTemplate,
)
from dol.kv_codecs import common_prefix_keys_wrap
import pandas as pd
from xv.util import grazed_path

# from tabled import ColumnOrientedMapping

_raw_store = Pipe(
    grazed_path,
    FilesOfZip,
    remove_mac_junk_from_zip,
    common_prefix_keys_wrap,
    add_ipython_key_completions,
)

urls = {
    "titles": "https://drive.google.com/file/d/1Ul5mPePtoPKHZkH5Rm6dWKAO11dG98GN/view?usp=share_link",
    "abstracts": "https://drive.google.com/file/d/1g3K-wlixFxklTSUQNZKpEgN4WNTFTPIZ/view?usp=share_link",
}
raw_sources = FuncReader({name: partial(_raw_store, url) for name, url in urls.items()})

# --------------------------------------------------------------------------------------
# The data-specific part
# TODO: Ugly and unclean. Maybe just do with wrap_kvs and lambdas?

import pandas as pd

_key_template_kwargs = dict(
    field_patterns=dict(
        kind=r"\w+", number=r"\d+"  # the pattern to match is an integer
    ),
    from_str_funcs=dict(number=int),  # transform integer string into actual integer
)
_parquet_codec_end_pipe = (
    wrap_kvs(obj_of_data=Pipe(io.BytesIO, pd.read_parquet)),  # get a dataframe
    cached_keys(keys_cache=sorted),  # sort the keys when iterating
)

titles_key_template = KeyTemplate(
    "titles_{number:d}.parquet",  # this is the template/pattern for the keys
    **_key_template_kwargs,
)
titles_parquet_codec = Pipe(
    titles_key_template.filt_iter("str"),  # filter in only keys that match the pattern
    titles_key_template.key_codec("single"),  # just get a single integer as the key
    *_parquet_codec_end_pipe,
)
abstracts_key_template = KeyTemplate(
    "abstracts_{number:d}.parquet",  # this is the template/pattern for the keys
    **_key_template_kwargs,
)
abstracts_parquet_codec = Pipe(
    abstracts_key_template.filt_iter(
        "str"
    ),  # filter in only keys that match the pattern
    abstracts_key_template.key_codec("single"),  # just get a single integer as the key
    *_parquet_codec_end_pipe,
)


def _kind_router(k, v):
    if k.startswith("titles"):
        return titles_parquet_codec(v)
    elif k.startswith("abstracts"):
        return abstracts_parquet_codec(v)
    raise KeyError(f"Invalid key: {k}")


# --------------------------------------------------------------------------------------
# url manipulations

sources = wrap_kvs(raw_sources, postget=_kind_router)

arxiv_url_template = "https://arxiv.org/{resource}/{doi}"

ArxivResource = Literal["abs", "pdf", "format", "src", "cits", "html"]

resource_descriptions = {
    "abs": "Main page of article. Contains links to all other relevant information.",
    "pdf": "Direct link to article pdf",
    "format": "Page giving access to other formats",
    "src": "Access to the original source files submitted by the authors.",
    "cits": "Tracks citations of the article across various platforms and databases.",
    "html": "Link to the ar5iv html page for the article.",
}


# --------------------------------------------------------------------------------------
# TODO: Redo this compile and parsing with dol.StrTupleDict

# There's an official DOI, as defined by the International DOI Foundation (IDF).
# See https://www.doi.org/doi_handbook/2_Numbering.html
# This is what we're recording underneath, but the arXiv also has its own DOI system.
# See https://arxiv.org/help/doi
OFFICIAL_DOI_PATTERN = re.compile(
    r"^(?:doi:|doi://)?"  # Optional DOI protocol prefix
    r"(10\.\d{4,9}/"  # DOI prefix: "10." followed by 4–9 digits and a slash
    r"[-._;()/:A-Za-z0-9]+)"  # DOI suffix: one or more allowed characters
    r"$",
    re.IGNORECASE,
)


def extract_doi(s: str) -> Optional[str]:
    """
    Extracts and returns a valid DOI from the input string if present,
    otherwise returns None. Supports strings of the form:
      - "10.1234/abcd"
      - "doi:10.1234/abcd"
      - "doi://10.1234/abcd"

    :param s: Input string potentially containing a DOI.
    :return: The DOI without any protocol prefix, or None if not a valid DOI.

    >>> extract_doi("10.1000/182")
    '10.1000/182'
    >>> extract_doi("doi:10.1234/ABC-123")
    '10.1234/ABC-123'
    >>> extract_doi("random string") is None
    True
    """
    s = s.strip()
    match = OFFICIAL_DOI_PATTERN.match(s)
    if match:
        return match.group(1)
    return None


# arXiv DOI
ARXIV_DOI_PATTERN = re.compile(
    r"^(?:doi:|doi://)?"  # Optional DOI protocol prefix
    r"(10\.48550/arXiv\."  # DOI prefix and literal "arXiv."
    r"\d{4}\.\d{4,5})"  # YYMM.number (4 or 5 digits), no version
    r"$",
    re.IGNORECASE,
)


def extract_arxiv_doi(s: str) -> Optional[str]:
    """
    Extracts and returns a valid arXiv-assigned DOI from the input string if present,
    otherwise returns None. Supports DOIs of the form:
      - "10.48550/arXiv.2202.01037"
      - "doi:10.48550/arXiv.2202.01037"
      - "doi://10.48550/arXiv.2202.01037"

    The DOI always uses the prefix 10.48550 and the base arXiv identifier (no version).

    >>> extract_arxiv_doi("10.48550/arXiv.2505.07987")
    '10.48550/arXiv.2505.07987'
    >>> extract_arxiv_doi("doi:10.48550/arXiv.2302.11894")
    '10.48550/arXiv.2302.11894'
    >>> extract_arxiv_doi("doi://10.48550/arXiv.1234.56789")
    '10.48550/arXiv.1234.56789'
    >>> extract_arxiv_doi("10.48550/arXiv.2202.01037v2") is None
    True
    >>> extract_arxiv_doi("arXiv:2202.01037") is None
    True
    """
    s = s.strip()
    match = ARXIV_DOI_PATTERN.match(s)
    if match:
        return match.group(1)
    return None


# Add helper functions
def parse_arxiv_uri(uri: str) -> dict:
    # Parses a DOI or a full URL into a dict with 'doi' and optionally 'resource'
    if uri.startswith("http"):
        if uri.startswith("https://arxiv.org/"):
            parts = uri[len("https://arxiv.org/") :].split("/", 1)
            if len(parts) == 2:
                return {"resource": parts[0], "doi": parts[1]}
        if uri.startswith("https://ar5iv.labs.arxiv.org/html/"):
            doi = uri[len("https://ar5iv.labs.arxiv.org/html/") :]
            return {"resource": "html", "doi": doi}
    elif doi := extract_doi(uri):
        return {"doi": doi}
    return None


def compile_arxiv_uri(data: dict) -> str:
    # Compiles a URI from a dict containing 'doi' and a 'resource'
    doi = data.get("doi", None)
    if doi is None:
        raise ValueError("Missing DOI in the data dictionary.")
    resource = data.get("resource", None)
    if resource is None:
        return f"{doi}"
    elif resource == "html":
        return f"https://ar5iv.labs.arxiv.org/html/{doi}"
    else:
        return f"https://arxiv.org/{resource}/{doi}"


def return_input(x):
    return x


def return_none(x):
    return None


def arxiv_url(
    uri: str,
    resource: ArxivResource = "abs",
    *,
    if_unparsable: Optional[Callable] = return_input,
) -> str:
    """
    Return the URL for the given URI translated to the specified resource.

    Args:
        uri (str): The URI to be parsed ({doi}, https://arxiv.org/{resource}/{doi}, or https://ar5iv.labs.arxiv.org/html/{doi})
        resource (ArxivResource): The desired resource type.
        if_unparsable (Optional[Callable]): Function to call if the URI cannot be parsed.
            If None, it will raise a ValueError.

    Returns:
        str: The compiled URL for the specified resource.

    >>> arxiv_url('https://arxiv.org/abs/10.3233', 'pdf')
    'https://arxiv.org/pdf/10.3233'
    >>> arxiv_url('https://arxiv.org/abs/10.3233', 'html')
    'https://ar5iv.labs.arxiv.org/html/10.3233'
    >>> arxiv_url('10.3233', 'abs')
    '10.3233'

    """
    parsed = parse_arxiv_uri(uri)
    if parsed:
        parsed["resource"] = resource  # override or add the desired resource
        return compile_arxiv_uri(parsed)
    else:
        if not if_unparsable:
            raise ValueError(f"This is not arxiv-parsable: {uri}")
        return if_unparsable(uri)
