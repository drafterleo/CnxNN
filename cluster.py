from bitarray import bitarray
import numpy as np
import utils


class Cluster:
    def __init__(self,
                 bit_mask: bitarray,
                 activate_threshold: int):
        self.bit_mask = bit_mask
        self.activate_threshold = activate_threshold
        self.stats = dict()

    def activate(self, bit_mask: bitarray):
        key = bit_mask.to01()  # tuple(sorted(bits))
        self.stats[key] = self.stats.get(key, 0) + 1

    def component_stats(self) -> dict:
        components = {}
        total_activations = sum(self.stats.values())
        if total_activations > 0:
            for bit_key, activations in self.stats.items():
                components[bit_key] = activations / total_activations  # probability (local frequency)
        return components

    def has_big_component(self, threshold: float, min_activations=10) -> bool:
        if len(self.stats.keys()) < min_activations:
            return False
        components = self.component_stats()
        for comp in components.values():
            if comp >= threshold:
                return True
        return False

    def bit_rate(self) -> (np.array, list):
        bit_map = sorted(utils.extract_bit_indices(self.bit_mask))
        vectors = [[activity if bit in bit_key else 0 for bit in bit_map]
                   for bit_key, activity in self.stats.items()]
        vec_sum = np.sum(vectors, axis=0)
        norm = np.max(vec_sum) # np.linalg.norm(vec_sum)
        return vec_sum / norm, bit_map


