from bitarray import bitarray
import numpy as np


class Cluster(object):
    def __init__(self,
                 bits: set,
                 bit_mask: np.array,
                 activate_threshold: int):
        self.bits = bits
        self.bit_mask = bit_mask
        self.bit_mask_size = bit_mask.size
        self.activate_threshold = activate_threshold
        self.consolidations = 0
        self.stats = dict()

    def activate(self, bits: set):
        bit_key = tuple(sorted(bits))
        self.stats[bit_key] = self.stats.get(bit_key, 0) + 1

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
        bit_map = sorted(self.bits)
        vectors = [[activity if bit in bit_key else 0 for bit in bit_map]
                   for bit_key, activity in self.stats.items()]
        vec_sum = np.sum(vectors, axis=0)
        norm = np.max(vec_sum) # np.linalg.norm(vec_sum)
        return vec_sum / norm, bit_map

    def test_for_strength(self,
                          component_threshold: float,
                          min_activations: int,
                          trim=False,
                          remain_part=0.3,
                          clear_stats=False,
                          consolidate=False,
                          amnesty=False) -> bool:
        # [0] - component bits, [1] - component part
        components = sorted(self.component_stats().items(), key=lambda x: x[1], reverse=True)
        result = False
        if self.stats and sum(self.stats.values()) >= min_activations:
            for bits, part in components:
                if part >= component_threshold:
                    result = True
                    break
        if consolidate:
            if result:
                self.consolidations += 1
            else:
                self.consolidations -= 1
                # amnesty for the previous consolidations
                if amnesty and self.consolidations >= 0:
                    result = True
        if result:
            if trim:
                component_sum = 0.0
                remain_bits = set()
                for bits, part in components:
                    component_sum += part
                    remain_bits |= set(bits)
                    if component_sum > remain_part:
                        break
                self.bits = remain_bits
        if clear_stats:
            self.stats.clear()
        return result

    def activity_numerator(self) -> int:
        result = sum(acts + len(bits) * 0.2 for bits, acts in self.stats.items())
        # # print('point', [acts * len(bits) for bits, acts in self.stats.items()])
        return result * self.consolidations
        # return sum(self.stats.values())



