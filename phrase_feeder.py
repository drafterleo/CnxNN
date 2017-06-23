import random


class PhraseFeeder:
    """
        phrase_base - {bit_key: [phrases(notated notes)]}
    """
    def __init__(self, phrase_base: dict, marks: dict):
        self.phrase_base = phrase_base
        self.marks = marks
        self.bit_keys = list(phrase_base.keys())
        self.curr_key_idx = 0
        self.counters = dict()  # {bit_key: int}
        for key in phrase_base.keys():
            self.counters[key] = 0

    def take_phrase_bunch(self, count=100, random_bit_key=True) -> (list, tuple):
        """
            return: phrases, bit_key
        """
        key_idx = self.curr_key_idx
        if random_bit_key:
            key_idx = random.randrange(len(self.bit_keys))
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
            if curr_counter >= len(curr_phrase_list):
                curr_counter = 0
            if curr_counter + count < len(curr_phrase_list):
                return curr_phrase_list[curr_counter:curr_counter + count], curr_bit_key
            else:
                return curr_phrase_list[curr_counter:], curr_bit_key
        else:
            return [], ()

