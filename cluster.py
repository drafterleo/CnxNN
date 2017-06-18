

class Cluster:
    def __init__(self,
                 bits: tuple,
                 bit_threshold: int):
        self.bits = bits
        self.bit_set = set(bits)
        self.bit_threshold = bit_threshold

    def activate(self, active_bits: set):
        pass

