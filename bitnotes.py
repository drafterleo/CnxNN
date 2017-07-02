import numpy as np


class BitNotes(object):
    def __init__(self,
                 note_count=100,
                 notation_count=10,
                 active_bits=8,
                 bit_count=255):
        self.note_count = note_count
        self.active_bits = active_bits
        self.bit_count = bit_count
        self.notation_count = notation_count
        self._notes = list()  # [note_0_notations, note_1_notations ...]  -> [ [(idx idx ...) ...] ...]
        self.gen_notes()

    def __getitem__(self, idx):
        return self._notes[idx]

    def __iter__(self):
        for note in self._notes:
            yield note

    def __len__(self):
        return len(self._notes)

    def notation_as_bits(self, notation: set) -> np.array:  # [1 0 1 0 0 ...]
        bits = np.zeros(self.bit_count, dtype=np.uint8)
        bits[list(notation)] = 1
        return bits

    def note_notation_as_bits(self, note_idx: int, notation_idx: int) -> np.array:  # [1 0 1 0 0 ...]
        return self.notation_as_bits(self._notes[note_idx][notation_idx])

    def gen_notation(self) -> tuple:
        # just tuple of active bit indices
        notation = np.random.choice(self.bit_count, self.active_bits, replace=False)
        notation.sort()
        return tuple(notation)

    def gen_notations(self) -> list:
        notations = set()
        for i in range(self.note_count * self.notation_count):
            brake = 1000
            while True:
                notation = self.gen_notation()
                if notation not in notations:
                    notations.add(notation)
                    break
                else:
                    brake -= 1
                    if brake == 0:
                        raise Exception("attempt limit overflow")
        return list(notations)

    def gen_notes(self):
        notations = self.gen_notations()
        self._notes = list()
        for i_note in range(self.note_count):
            note_notations = [notations[i_note * self.notation_count + i] for i in range(self.notation_count)]
            self._notes.append(note_notations)

    def phrase_chord(self, phrase: list) -> set:
        """
            phrase: [(note_idx, notation_idx) ...] -> {bit indices}
        """
        bits = set()
        for note_idx, notation_idx in phrase:
            bits = bits.union(self._notes[note_idx][notation_idx])
        return bits

    def phrase_chord_as_bits(self, phrase: list) -> np.array:
        chord = self.phrase_chord(phrase)
        return self.notation_as_bits(chord)

