import base64
import re


def parse_string(string, separators, converter=None):
    r"""
    Split a string by separators (recursively) and convert each substring using the given converter (if provided).

    The string will be split by the given separators. The amount of separators will determine the dimension of the resulting list.
    For example, if separators = ("\\n", ","), the string will be split by newline and each resulting substring will be
    split by comma, forming a two-dimensional list.
    The substrings will then be converted using the given converter and returned.
    The function can handle any number of separators/dimensions, but since recursive typing is not widely supported,
    its type hinting is limited to five dimensions.

    :param string: The string to parse.
    :param separators: The separators to split the string by.
    :param converter: A callable that converts each split string.
    :return: The result of the parsing and conversion.
    """
    processed_data = string

    if not separators:
        if converter is not None:
            processed_data = converter(processed_data)
        return processed_data

    if separators[0] == "":
        processed_data = list(processed_data)
    elif isinstance(separators[0], str):
        processed_data = processed_data.split(separators[0])
    elif isinstance(separators[0], re.Pattern):
        processed_data = separators[0].split(processed_data)
    else:
        raise TypeError("Separators must be of type str or re.Pattern")

    return [
        parse_string(substr, separators=separators[1:], converter=converter)
        for substr in processed_data
    ]


def parse_file_content(filepath, separators, converter=None):
    r"""
    Read file content, split it by separators (recursively) and convert each substring using the given converter (if provided).

    The string will be read from the file at the given filepath.
    The string will be split by the given separators. The amount of separators will determine the dimension of the resulting list.
    For example, if separators = ("\\n", ","), the string will be split by newline and each resulting substring will be
    split by comma, forming a two-dimensional list.
    The substrings will then be converted using the given converter and returned.
    The function can handle any number of separators/dimensions, but since recursive typing is not widely supported,
    its type hinting is limited to five dimensions.

    :param filepath: The path to the file to read.
    :param separators: The separators to split the string by.
    :param converter: A callable that converts each split string.
    :return: The result of the parsing and conversion.
    """
    with open(filepath) as file:
        file_content = file.read()

    return parse_string(file_content, separators, converter)


def b64encode(text, times_to_encode=1):
    """
    Encode the given text using base64 encoding.
    :param text: The text to encode.
    :param times_to_encode: The number of times to encode the text.
    :return: The encoded text.
    """
    for _ in range(times_to_encode):
        text = base64.b64encode(text.encode("utf-8")).decode("utf-8")

    return text


def b64decode(text, times_to_decode=1):
    """
    Decode the given text using base64 encoding.
    :param text: The text to decode.
    :param times_to_decode: The number of times to decode the text.
    :return: The decoded text.
    """
    for _ in range(times_to_decode):
        text = base64.b64decode(text).decode("utf-8")

    return text
