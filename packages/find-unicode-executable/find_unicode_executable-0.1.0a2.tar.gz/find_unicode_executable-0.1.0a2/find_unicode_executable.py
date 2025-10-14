# coding=utf-8
import itertools
import ntpath
import posixpath

from posix_or_nt import posix_or_nt
from read_unicode_environment_variables_dictionary import read_unicode_environment_variables_dictionary
from typing import Container, Iterator, Text


def seqtok(string, separators):
    # type: (Text, Container[Text]) -> Iterator[Text]
    """Mimics the behavior of C's strtok() function:

    - Consecutive separators are treated as a single separator
    - Leading/trailing separators are ignored (no empty tokens)
    - Returns tokens one at a time via iteration

    But with crucial differences:

    - State is encapsulated in the generator instance (no global state)
        - No thread safety concerns from global state
    - Each iterator maintains independent state (safe for separate instances)
        - Multiple tokenizers can operate simultaneously

    Example: splitting u'a::b::::c:' by u':' yields [u'a', u'b', u'c'] instead of [u'a', u'', u'b', u'', u'', u'', u'c', u'']
    """
    last_char_is_separator = True
    char_buffer = []

    for char in string:
        if last_char_is_separator:
            if char not in separators:
                # State transition
                last_char_is_separator = False
                char_buffer.append(char)
        else:
            if char not in separators:
                char_buffer.append(char)
            else:
                # State transition
                last_char_is_separator = True
                yield u''.join(char_buffer)
                char_buffer = []

    if char_buffer:
        yield u''.join(char_buffer)


if posix_or_nt() == 'nt':
    UNICODE_ENVIRONMENT_VARIABLES_DICTIONARY = read_unicode_environment_variables_dictionary()

    UNICODE_PATH_ENTRIES = [
        entry
        for entry in seqtok(UNICODE_ENVIRONMENT_VARIABLES_DICTIONARY[u'PATH'], {u';'})
    ]

    UNICODE_PATH_EXTENSIONS = [
        ext
        for ext in seqtok(UNICODE_ENVIRONMENT_VARIABLES_DICTIONARY[u'PATHEXT'], {u';'})
    ]


    def find_unicode_executable(executable_name):
        # type: (Text) -> Iterator[Text]
        """Yield full Unicode paths for all executables matching the given name."""
        candidate_executable_names_with_extensions = set()

        # Does `string_executable_name` include an extension?
        _, extension = ntpath.splitext(executable_name)
        if extension:
            # Is it already a path?
            if ntpath.exists(executable_name):
                yield ntpath.abspath(executable_name)
            else:
                candidate_executable_names_with_extensions.add(executable_name)
        else:
            for path_extension in UNICODE_PATH_EXTENSIONS:
                candidate_executable_names_with_extensions.add(executable_name + path_extension)

        # Look in the current directory first, then directories in PATH
        for directory in itertools.chain((u'.',), UNICODE_PATH_ENTRIES):
            for candidate_executable_name_with_extension in candidate_executable_names_with_extensions:
                candidate_executable_path = ntpath.join(directory, candidate_executable_name_with_extension)
                if ntpath.exists(candidate_executable_path):
                    yield ntpath.abspath(candidate_executable_path)
else:
    UNICODE_ENVIRONMENT_VARIABLES_DICTIONARY = read_unicode_environment_variables_dictionary()

    UNICODE_PATH_ENTRIES = [
        entry
        for entry in seqtok(UNICODE_ENVIRONMENT_VARIABLES_DICTIONARY[u'PATH'], {u':'})
    ]


    def find_unicode_executable(executable_name):
        # type: (Text) -> Iterator[Text]
        # Does `string_executable_name` contain a slash?
        # Then we treat `string_executable_name` as the path to an executable
        if u'/' in executable_name:
            if posixpath.exists(executable_name):
                yield posixpath.abspath(executable_name)
        # Elsewise, we do a path lookup
        else:
            for path_entry in UNICODE_PATH_ENTRIES:
                potential_executable_path = posixpath.join(path_entry, executable_name)
                if posixpath.exists(potential_executable_path):
                    yield posixpath.abspath(potential_executable_path)
