"""Access to arxiv resources

>>> from xv import raw_sources
>>> list(raw_sources)  # doctest: +SKIP
['titles', 'abstracts']
>>> from xv import sources  # raw store + wrapper. See parquet_codec code.
>>> titles_tables = sources['titles']  # doctest: +SKIP
abstract_tables = sources['abstracts']  # doctest: +SKIP
>>> print(list(titles_tables))  # doctest: +SKIP
[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23]
>>> titles_df = titles_tables[1]  # doctest: +SKIP

etc.

"""

from xv.data_access import raw_sources, sources, arxiv_url
