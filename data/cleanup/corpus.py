"""Wrapper to access corpora and their files in a easy manner
"""

from os.path import isfile, isdir, join
from os import listdir
from re import compile as build_regex
from logging import warning, info, debug

class Corpus:
    def __str__(self):
        return self.base_path

    def __init__(self, name, base_path, name_pattern, options=None):
        self.name = name
        self.base_path = base_path
        self.options = options

        self.path_regex = build_regex(name_pattern)
        self.files = {}

    def load_filelist(self):
        """Loadup the file list as described by the init pattern
        """
        if isdir(self.base_path):
            debug(f"Found base directory for {self.name}")
        else:
            raise FileNotFoundError

        debug("Found the following files:")
        debug(listdir(self.base_path))
        debug(f"  -Using [{self.path_regex.pattern}] to split up file name")

        for sub_corpus in listdir(self.base_path):
            debug(f"Checking [{sub_corpus}]")

            if not isfile(join(self.base_path, sub_corpus)):
                debug("  -Skipping entry, not a fIle!")
                continue

            match = self.path_regex.match(sub_corpus)
            try:
                matches = match.groupdict()
                debug(f"  -Found: {matches}")
                pair = matches["pair"]
                locale = matches["locale"]

                if not pair in self.files:
                    self.files[pair] = {}

                self.files[pair][locale] = join(self.base_path, sub_corpus)
            except AttributeError:
                debug("  -Skipping entry, does not match pattern!")
                continue
            except KeyError as err:
                debug("  -Skipping entry, missing group:")
                debug(err)
                continue
            else:
                info(f"  -Using locale '{locale}' for pair '{pair}'")
                self.files[pair][locale] = join(self.base_path, sub_corpus)

    def load_file(self, pair, locale, mode="r", encoding=None):
        """Loads file into memory and caches it for next run
        """
        assert pair in self.files, f"Language Pair 'pair' not found!"
        assert locale in self.files[pair], f"Locale Code '{locale}' not found!"

        raw_file = self.files[pair][locale]

        if isinstance(raw_file, str):
            debug("File not cached... Loading it now")
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
                debug("Loaded file succesful into memory")
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
            debug("Loaded file succesful into memory")
        return raw_file
