from logging import debug, info, warning
from shutil import copyfile

from subword_nmt.learn_bpe import learn_bpe
from subword_nmt.apply_bpe import BPE, read_vocabulary

from .Plugin import Filter, Fixer

class BPESpotter(Fixer):
    """Trains and calculates the code words for a BytePairEncoding
    """

    def __init__(self, options, code_files, min_frequency=2, verbose=False, n_symbols=10000):
        debug(f"Creating instance of [{self.__class__.__name__}]")
        self.runtime_config = options
        self.min_frequency = min_frequency
        self.n_symbols = n_symbols
        self.code_files = code_files
        self.verbose = verbose

    def fix_file(self, pair, locale_code, src_file, target_file, action):
        """learn and apply BPE on the whole file
        this will never change the actual file and always return an empty set
        """
        debug(f"  -[{pair}/{locale_code}]: processing {src_file} now!")
        learn_bpe(
            infile=open(src_file), outfile=open(self.code_files[pair][locale_code], "w"),
            verbose=self.verbose,
            num_symbols=self.n_symbols, min_frequency=self.min_frequency)
        copyfile(src_file, target_file)

        return set()

class BPESplitter(Fixer):
    def __init__(self, options, code_files, merges=1, separator="@@", vocabularies={}, glossaries={}):
        """BPE splitter plugin; takes the following args:
        merges: use this many merge operations
        code_files: path to code file in dict form {"pair/locale_code":code}
        separator: which seq to split the BPE tokens
        vocabulary: vocab file build by subword_nmt/get_vocab to exclude special words
        glossaries: all words that match that pattern will not be affected by transformation
        """
        debug(f"Creating instance of [{self.__class__.__name__}]")
        self.runtime_config = options
        self.bpes = {}
        for pair in code_files:
            if pair not in self.bpes:
                self.bpes[pair] = {}
            for locale in code_files.get(pair, {}):
                debug(f"  -Loading up BytePairEncoder for [{pair}/{locale}]")
                vocabulary = None
                try:
                    vocabulary_info = vocabularies.get(pair, {}).get(locale, {})
                    with open(vocabulary_info["path"]) as vocab_file:
                        vocabulary = read_vocabulary(vocab_file, vocabulary_info.get("threshold"))
                except Exception as err:
                    debug(f"  -Adding vocabulary caused an error: [{err}]... Ignoring it!")

                try:
                    glossary = glossaries.get(pair, {}).get(locale)
                    bpe = BPE(
                        codes=open(code_files[pair][locale]),
                        merges=merges, separator=separator,
                        vocab=vocabulary, glossaries=glossary)
                except Exception as err:
                    warning(err)
                    warning("Could not create BPE for locale! Skipping it...")
                else:
                    self.bpes[pair][locale] = bpe


    def match(self, pair, code, line):
        assert isinstance(line, str), "Line has to be a string"
        assert pair in self.bpes, "Locale pair not found!"
        assert code in self.bpes[pair], "Locale code for pair not found!"

        return True

    def fix_line(self, pair, code, line_number, line):
        """Apply BPE on all lines
        """
        assert pair in self.bpes, "Locale pair not found!"
        assert code in self.bpes[pair], "Locale code for pair not found!"

        return self.bpes[pair][code].process_line(line)


