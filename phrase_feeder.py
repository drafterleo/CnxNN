import random
import numpy as np


class PhraseFeeder:
    """
        phrase_base - {bit_key: [phrases(notated notes)]}
    """
    def __init__(self,
                 phrase_base: dict,
                 marks: dict):
        self.phrase_base = phrase_base
        self.marks = marks
        self.bit_keys = list(phrase_base.keys())
        self.curr_key_idx = 0
        self.counters = dict()  # {bit_key: int}
        self.random_indices = np.array([], dtype=int)
        for key in phrase_base.keys():
            self.counters[key] = 0

    def take_phrase_batch(self,
                          count=100,
                          random_bit_key=False) -> (list, tuple):
        """
            return: phrases, bit_key
        """
        if random_bit_key:
            if self.random_indices.size == 0:
                self.random_indices = np.arange(len(self.bit_keys), dtype=np.int)
                np.random.shuffle(self.random_indices)
            key_idx = self.random_indices[0]
            self.random_indices = np.delete(self.random_indices, 0)
        else:
            key_idx = self.curr_key_idx
            self.curr_key_idx += 1
            if self.curr_key_idx >= len(self.bit_keys):
                self.curr_key_idx = 0
        curr_bit_key = self.bit_keys[key_idx]
        curr_counter = self.counters[curr_bit_key]
        self.counters[curr_bit_key] += count
        curr_phrase_list = self.phrase_base[curr_bit_key]
        if curr_phrase_list:
            if curr_counter + count < len(curr_phrase_list):
                return curr_phrase_list[curr_counter:curr_counter + count], curr_bit_key
            else:
                self.counters[curr_bit_key] = 0
                print('counter ends')
                return curr_phrase_list[curr_counter:], curr_bit_key
        else:
            return [], ()

