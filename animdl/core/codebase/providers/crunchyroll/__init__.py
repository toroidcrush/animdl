import json
import regex
from collections import defaultdict
from functools import partial

import lxml.html as htmlparser

from ....config import CRUNCHYROLL
from ...helper import construct_site_based_regex
from .geobypass import geobypass_response

REGEX = construct_site_based_regex(
    CRUNCHYROLL, extra_regex=r'/([^?/&]+)')

CONTENT_METADATA = regex.compile(r"vilos\.config\.media = (\{.+\})")


def get_subtitle(subtitles, lang='enUS'):
    for sub in subtitles:
        if sub.get('language') == lang:
            yield sub.get('url')


def get_stream_urls(episode_data):
    for episode_page, title in episode_data:
        json_content = json.loads(CONTENT_METADATA.search(
            geobypass_response(episode_page).text).group(1))
        metadata = json_content.get('metadata')

        for stream in json_content.get('streams'):
            if stream.get('format') in ['adaptive_dash', 'adaptive_hls', 'multitrack_adaptive_hls_v2',
                                        'vo_adaptive_dash', 'vo_adaptive_hls'] and stream.get('hardsub_lang') in [None, 'enUS']:
                yield_content = {
                    'stream_url': stream.get('url'),
                    'title': "{} ({})".format(metadata.get('title'), title) if title else metadata.get('title')}

                if stream.get('hardsub_lang') is None:
                    yield_content.update(
                        {'subtitle': [*get_subtitle(json_content.get('subtitles'))], 'download': False})

                yield yield_content


def group_content(slug, html_element):

    episodes = defaultdict(list)

    for element in html_element.cssselect('a.episode')[::-1]:
        episode_match = (regex.search(
            '^/{}/episode-(\d+)'.format(regex.escape(slug)), element.get('href')))
        episodes[int(episode_match.group(1)) if episode_match else 0].append(
            (CRUNCHYROLL + element.get('href', '').strip('/'), element.get('title')))

    return episodes


def fetcher(session, url, check, match):

    slug = match.group(1)
    url = CRUNCHYROLL + slug

    for episode_number, episode_data in sorted(group_content(slug, htmlparser.fromstring(geobypass_response(url).text)).items()):
        if check(episode_number):
            yield partial((lambda e: [*get_stream_urls(e)]), episode_data), episode_number
