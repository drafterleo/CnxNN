

class Cluster:
    def __init__(self,
                 bits: tuple,
                 activate_threshold: int):
        self.bits = bits
        self.bit_set = set(bits)
        self.activate_threshold = activate_threshold

    def activate(self, active_bits: set):
        pass

