"""
IntelliQ, a highly intelligent and robust quality string parser.
"""

import logging

import regex

PORTION_PARSER = regex.compile(r'(.+?)=(r?)("|\')((?:\\\3|.)*?)\3')
SEGMENT_PARSER = regex.compile('(best|worst|\d+)?(.*)')


def NO_PROCESS(stream): return stream


def get_pair(target, pairs):
    """
    Returns
    ---

    `tuple` pair, `bool` is_initiator
    """
    for f, l in pairs:
        if target in (f, l):
            return (f, l), target == f

    return (None, None), False


def parse_parenthesized_portions(segment):
    match = PORTION_PARSER.search(segment)

    if not match:
        return (segment, None)

    if match.group(2):
        return (match.group(1), regex.compile(match.group(4)))

    return (match.group(1), match.group(4))


def portion_check(portions):

    for key, portion in portions:
        if not portion:
            yield lambda stream, k=key: bool(stream.get(k))
            continue

        if isinstance(portion, regex.Pattern):
            yield lambda stream, k=key, p=portion: bool(p.search(str(stream.get(k, ""))))
            continue

        yield lambda stream, k=key, p=portion: stream.get(k, "") == p


def parenthesized_portions(string, escape='\\', quoters=["'", '"'], parenthesis=[('[', ']'), ('(', ')'), ('{', '}')]):

    initiator, endpoint = min(parenthesis, key=lambda x: (
        string.find(x[0]) + 1) or float('inf'))

    escaping = False
    current_context = ""

    multiquote_context = dict.fromkeys(quoters, False)

    pos = string.find(initiator)

    if pos == -1:
        return

    for current_pos, content in enumerate(string[pos + 1:], pos + 1):

        if not escaping:
            if content in quoters:
                multiquote_context[content] = not multiquote_context[content]

            if content == endpoint and not any(multiquote_context.values()):

                yield parse_parenthesized_portions(current_context.strip())
                yield from parenthesized_portions(string[current_pos:], escape=escape, quoters=quoters, parenthesis=parenthesis)
                return

        current_context += content
        escaping = content in escape


def split_portion(string, splitters=['/'], escape='\\', quoters=["'", '"'], parenthesis=[('[', ']'), ('(', ')'), ('{', '}')]):
    """
    Writing a regex is possible, I just happen to not take pleasure from such things.
    """

    multiquote_context = dict.fromkeys(quoters, False)
    parenthesis_context = dict.fromkeys(parenthesis, False)

    escaping = False
    current_context = ""
    yield_this_loop = False

    for content in string:

        pair, is_initiator = get_pair(content, parenthesis)

        if not escaping:
            if content in quoters:
                multiquote_context[content] = not multiquote_context[content]

            if pair in parenthesis_context:
                if not parenthesis_context[pair]:
                    if is_initiator:
                        parenthesis_context[pair] = True
                else:
                    if not is_initiator:
                        parenthesis_context[pair] = False

            if content in splitters and not any(multiquote_context.values()) and not any(parenthesis_context.values()):
                yield current_context.strip()
                yield_this_loop = True

        if yield_this_loop:
            current_context = ""
        else:
            current_context += content

        escaping = content in escape
        yield_this_loop = False

    yield current_context.strip()


def get_int(key):

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


def parse_quality_only(quality):
    if quality == 'best':
        return lambda streams: [max(streams, key=lambda stream: get_int(stream.get('quality', 0)))]

    if quality == 'worst':
        return lambda streams: [min(streams, key=lambda stream: get_int(stream.get('quality', 0)))]

    if quality and quality.isdigit():
        return NO_PROCESS

    return lambda streams: list(stream for stream in streams if get_int(stream.get('quality', 0)) >= int(quality or 0))


def finalise_check(quality_check, parsed_parenthesized_portions, fallback=parse_quality_only('best')):

    def internal(streams):
        streams = list(stream for stream in streams if all(_(stream)
                       for _ in portion_check(parsed_parenthesized_portions)))

        if not streams:
            return []

        return quality_check(streams)

    return internal


def parse_quality_string(quality_string: str):

    quality_string = quality_string.lower()

    for segment in split_portion(quality_string):
        match = SEGMENT_PARSER.search(segment)
        yield segment, finalise_check(parse_quality_only(match.group(1)), list(parenthesized_portions(match.group(2))))


def filter_quality(streams, quality_string):

    logger = logging.getLogger('utils/intelliq')

    logger.debug("Parsing {!r} in {!r}".format(quality_string, streams))

    for segment, check in parse_quality_string(quality_string):
        filtered = check(streams)

        if filtered:
            logger.info("{} streams fulfill {!r}.".format(
                len(filtered), segment))
            return filtered

        logger.warning("No streams fulfill {!r}.".format(segment))

    logger.warning(
        "Quality checks have failed miserably. Returning everything back.")
    return streams
