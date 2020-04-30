import copy
import hashlib
import os
import pickle
import time


def hashable(item):
    """Determine whether `item` can be hashed."""
    try:
        hash(item)
    except TypeError:
        return False
    return True


def sha256(filename):
    """
    Digest a file using sha256
    """
    sha256_hash = hashlib.sha256()
    with open(filename, "rb") as f:
        # Read and update hash string value in blocks of 4K
        while chunk := f.read(8192):
            sha256_hash.update(chunk)
    return sha256_hash.hexdigest()


def __not_equal__(a, b):
    return a != b


class Memoizable:
    def __init__(self, cache_file='.cache', expire_in_days=7, hashfunc=None):
        self.__cache_file__ = cache_file
        self.cache = {}
        self.__expire_in__ = expire_in_days * 60 * 60 * 24
        if hashfunc is not None:
            self.__current_stamp__ = hashfunc
            self.__expiration_stamp__ = None
            self.__is_expired__ = __not_equal__
        self.load_cache()

    def __call__(self, *args):
        args = self.__preprocess_args__(*args)
        if not hashable(args):
            print("Uncacheable args.", args)
            return self.fresh(*args)

        cached = self.cache.get(args, None)
        current = self.__current_stamp__(*args)
        if cached is None or self.__is_expired__(cached[1], current):
            value = self.fresh(*args)
            if self.__expiration_stamp__ is not None:
                current = self.__expiration_stamp__(*args)
            self.cache[args] = value, current
            self.save_cache()
            return copy.deepcopy(value)
        else:
            return copy.deepcopy(self.cache[args][0])

    def __preprocess_args__(self, *args):
        return args

    def load_cache(self):
        if os.path.exists(self.__cache_file__):
            with open(self.__cache_file__, 'rb') as fd:
                self.cache = pickle.load(fd)
        else:
            self.cache = {}

    def save_cache(self, cache_file=None):
        if cache_file is None: cache_file = self.__cache_file__
        with open(cache_file, 'wb') as f:
            pickle.dump(self.cache, f)

    def fresh(self, *args):
        raise Exception("Executor not yet defined.")
        return False

    def __is_expired__(self, cached, current):
        return current > cached

    def __current_stamp__(self, *args):
        return time.time()

    def __expiration_stamp__(self, *args):
        return time.time() + self.__expire_in__
