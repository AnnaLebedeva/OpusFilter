"""Hashing parallel segments"""

import pyhash
import regex


from . import ConfigurationError


class SegmentHasher:
    """Hasher for text segments"""

    not_letter = regex.compile(r'[^\p{L}]')
    join_char = '\n'
    join_char_escaped = r'\n'

    def __init__(self, compare='all', hash='xx_64', hashseed=0, lowercase=False, letters_only=False):
        """Create a hasher for parallel segments

        Keyword arguments:
          compare -- a list of indices for selecting the segments to hash or 'all' (default 'all')
          hash -- hash function from pyhash library, None for no hashing (default 'xx_64')
          hashseed -- integer seed for the hash algorithm (default 0)
          lowercase -- lowercase input strings before hashing
          letters_only -- remove all non-letters from intput strings before hashing

        """
        self.compare = None
        if compare != 'all':
            if not isinstance(compare, list) or not all(isinstance(x, int) for x in compare):
                raise ConfigurationError(
                    "The compare parameter for hashing has to be 'all' or "
                    "a list of input file indices")
            self.compare = sorted(compare)
        hashname = hash
        if hashname and not hasattr(pyhash, hashname):
            raise ConfigurationError(
                "Algorithm '{}' not available from from pyhash".format(hashname))
        self.hashfunc = getattr(pyhash, hashname)(seed=hashseed) if hashname else lambda x: x
        self.lowercase = lowercase
        self.letters_only = letters_only

    def preprocess(self, inputstr):
        """Preprocess string"""
        if self.letters_only:
            inputstr = regex.sub(self.not_letter, '', inputstr)
        if self.lowercase:
            inputstr = inputstr.lower()
        inputstr = inputstr.replace(self.join_char, self.join_char_escaped)
        return inputstr

    def apply(self, segments):
        """Hash a list of segments"""
        if self.compare is None:
            inputstr = self.join_char.join(self.preprocess(seg) for seg in segments)
        else:
            try:
                inputstr = self.join_char.join(self.preprocess(segments[idx]) for idx in self.compare)
            except KeyError:
                raise ConfigurationError(
                    "The input indices {} in the compare parameter do not match input of length {}",
                    self.compare, len(segments))
        return self.hashfunc(inputstr)
