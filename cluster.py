import numpy as np


class Cluster(object):
    def __init__(self,
                 bit_mask: np.array,
                 activate_threshold: int):
        self.bit_mask = bit_mask
        self.bit_mask_size = bit_mask.size
        self.activate_threshold = activate_threshold
        self.consolidations = 0
        self.stats = dict()

    def activate(self, bits: np.array, weight: int):
        bit_key = bits.tobytes()
        acts = self.stats.get(bit_key, 0) + weight
        if acts > 0:
            self.stats[bit_key] = acts
        else:
            self.stats[bit_key] = 0

    def component_stats(self) -> dict:
        components = {}
        total_activations = sum(self.stats.values())
        if total_activations > 0:
            for str_key, activations in self.stats.items():
                bit_key = tuple(np.fromstring(str_key, dtype=np.uint8))
                components[bit_key] = activations / total_activations  # probability (local frequency)
        return components

    def has_big_component(self, threshold: float, min_activations=10) -> bool:
        if sum(self.stats.values()) < min_activations:
            return False
        components = self.component_stats()
        for comp in components.values():
            if comp >= threshold:
                return True
        return False

    def test_for_strength(self,
                          component_threshold: float,
                          min_activations: int,
                          trim=False,
                          remain_parts=3,
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
            if trim and len(components) > 1:
                # OR(+) n nearest to most active combination
                base = np.array(components[0][0], dtype=np.uint8)
                base_norm = base / np.linalg.norm(base)
                vectors = np.array([bits for bits, _ in components[1:]])
                norm = np.linalg.norm(vectors, axis=1)
                vectors_norm = vectors / norm[:, None]
                sim_idx = np.dot(vectors_norm, base_norm.T).argsort()[::-1]
                remain_bits = base
                if remain_parts > vectors.size:
                    remain_parts = vectors.size
                for idx in sim_idx[:remain_parts]:
                    remain_bits |= vectors[idx]
                self.bit_mask = remain_bits

        if clear_stats:
            self.stats.clear()
        return result

    def activation_count(self):
        return sum(self.stats.values())

    def activity_numerator(self) -> int:
        result = sum(acts # + np.sum(np.fromstring(bits, dtype=np.uint8))
                     for bits, acts in self.stats.items())
        # # print('point', [acts * len(bits) for bits, acts in self.stats.items()])
        return result
        # return sum(self.stats.values())



