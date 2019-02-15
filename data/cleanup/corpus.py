"""Wrapper to access corpora and their files in a easy manner
"""

from os.path import isfile, isdir, join
from os import listdir
from re import compile as build_regex
from logging import warning, info, debug

class Corpus:
    def __init__(self, name, base_path, name_pattern):
        self.name = name

        if isdir(base_path):
            debug(f"Found base directory for {name}")
        else:
            raise FileNotFoundError
        
        name_regex = build_regex(name_pattern)
        self.files = {}
        debug("Found the following files:")
        debug(listdir(base_path))

        for sub_corpus in listdir(base_path):
            debug(f"Checking [{sub_corpus}]")

            if not isfile(join(base_path, sub_corpus)):
                debug("  Skipping entry, not a fIle!")
                continue

            debug(f"Using [{name_pattern}] to split up file name")
            match = name_regex.match(sub_corpus)
            try:
                matches = match.groupdict()
                debug(f"  Found: {matches}")
                pair = matches["pair"]
                locale = matches["locale"]

                if not pair in self.files:
                    self.files[pair] = {}

                self.files[pair][locale] = join(base_path, sub_corpus)
            except AttributeError:
                debug("  Skipping entry, does not match pattern!")
                continue
            except KeyError as err:
                debug("  Skipping entry, missing group:")
                debug(err)
                continue
            else:
                info(f"  Found {locale} for {pair}")
                self.files[pair][locale] = join(base_path, sub_corpus)

    def load_file(self, pair, locale, mode="r", encoding=None):
        """Loads file into memory and caches it for next run
        """
        assert pair in self.files, "Language Pair not found!"
        assert locale in self.files[pair], "Locale Code not found!"

        raw_file = self.files[pair][locale]

        if isinstance(raw_file, str):
            debug("File not loaded!")
            try:
                if encoding is None:
                    file_handle = open(raw_file, mode)
                else:
                    file_handle = open(raw_file, mode, encoding)
            except Exception as err:
                warning("Could not load file!")
                raise err
            else:
                self.files[pair][locale] = file_handle
                debug("Loade file and registered for later use!")
            return file_handle
        debug("File already loaded! Checking options...")
        if ((raw_file.mode == mode) and
                (raw_file.encoding == encoding)
           ):
            debug("All options are correct!")
            debug("Resetting file view...")
            raw_file.seek(0)
        else:
            debug("Reopening file...")
            path = raw_file.name
            raw_file.close()
            raw_file = open(path, mode=mode, encoding=encoding)
            self.files[pair][locale] = raw_file
            debug("Loaded file and registered for later use!")
        return raw_file
