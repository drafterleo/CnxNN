from bitarray import bitarray


class Cluster:
    def __init__(self,
                 bits: tuple,
                 bit_mask: bitarray,
                 activate_threshold: int):
        self.bits = bits
        self.bit_set = set(bits)
        self.bit_mask = bit_mask
        self.activate_threshold = activate_threshold
        self.stats = dict()

    def activate(self, bits: set):
        key = tuple(sorted(bits))
        self.stats[key] = self.stats.get(key, 0) + 1

    def stat_parts(self) -> dict:
        parts = {}
        total_activations = sum(self.stats.values())
        for key, activations in self.stats.items():
            parts[key] = activations / total_activations
        return parts

