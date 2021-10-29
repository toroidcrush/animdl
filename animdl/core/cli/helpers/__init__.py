import logging
from re import I
import regex

from click import prompt

from ...codebase import downloader, extractors
from .fun import (bannerify, choice, create_random_titles, stream_judiciary,
                  to_stdout)
from .player import *
from .processors import get_searcher, process_query

def inherit_stream_meta(parent, streams, *, exempt=['headers', 'stream_url']):
    for stream in streams:
        stream.update({_: __ for _, __ in parent.items() if _ not in exempt})
        yield stream

def further_extraction(session, stream):
    extractor, options = stream.pop('further_extraction', (None, None))
    fe_logger = logging.getLogger("further-extraction")

    for ext_module, ext in extractors.iter_extractors():
        if ext == extractor:
            try:
                return list(inherit_stream_meta(stream, ext_module.extract(session, stream.get('stream_url'), **options)))
            except Exception as e:
                fe_logger.error("Extraction from {!r} failed due to: {!r}.".format(ext, e))
    return []

def ensure_extraction(session, stream_uri_caller):
    for stream in stream_uri_caller():
        if 'further_extraction' in stream:
            yield from further_extraction(session, stream)
        else:
            yield stream


def get_quality(the_dict):
    key = the_dict.get('quality')

    if not key:
        return 0

    if isinstance(key, int):
        return key

    if isinstance(key, str) and key.isdigit():
        return int(key)

    digits = regex.search(key, r'[0-9]+')
    if digits:
        return int(digits.group(0))
    
    return 0


def filter_urls(stream_urls, *, download=False):
    for _ in sorted(stream_urls, reverse=True, key=get_quality):
        if (download and  (_.get('download') or _.get('download') is None)):
            yield _, get_quality(_) 


def filter_quality(stream_urls, preferred_quality, *, download=False):
    for _, quality in filter_urls(stream_urls, download=download):
        if preferred_quality >= quality:
            yield _, quality

def get_range_conditions(range_string):
    for matches in regex.finditer(r"(?:([0-9]*)[:\-.]([0-9]*)|([0-9]+))", range_string):
        start, end, singular = matches.groups()
        if ((start or '').isdigit() and (end or '').isdigit()) and int(start) > int(end):
            start, end = end, start
        yield (lambda x, s=singular: int(s) == x) if singular else (lambda x: True) if not (start or end) else (lambda x, s=start: x >= int(s)) if start and not end else (lambda x, e=end: x <= int(e)) if not start and end else (lambda x, s=start, e=end: int(s) <= x <= int(e))

def get_check(range_string):
    if not range_string:
        return lambda *args, **kwargs: True
    return lambda x: any(condition(x) for condition in get_range_conditions(range_string))

def ask(log_level, **prompt_kwargs):

    if log_level < 20:
        return prompt_kwargs.get('default')

    return prompt(**prompt_kwargs)

def download(session, logger, content_dir, outfile_name, stream_urls, quality, **kwargs):
    downloadable_content = [*filter_quality(stream_urls, quality, download=True)] or \
        [*filter_urls(stream_urls, download=True)]

    if not downloadable_content:
        return False, "No downloadable content found."

    iter_downloads = iter(downloadable_content)

    for download_data in iter_downloads:
        dl, q = download_data
        if "further_extraction" in dl:
            try:
                return download(session, logger, content_dir, outfile_name, further_extraction(session, dl), quality, **kwargs)
            except Exception as e:
                logger.critical("Could not extract from the stream due to {!r}. falling back to other streams.".format(e))
                continue

        content_url = dl.get('stream_url')
        content_headers = dl.get('headers')
        try:
            return True, downloader.handle_download(session, content_url, content_headers, content_dir, outfile_name, preferred_quality=quality, **kwargs)
        except Exception as e:
            logger.critical("Could not download a stream, due to: {!r}, falling back to other streams.".format(e))
    
    return False, "All stream links were undownloadable."