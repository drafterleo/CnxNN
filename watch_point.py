import constants as const
import utils
from cluster import Cluster
from bitarray import bitarray


class WatchPoint:
    def __init__(self,
                 watch_bits: tuple,  # input bit indices (sorted)
                 input_size: int,
                 output_bit: int,    # output bit index
                 cluster_make_threshold: int,
                 cluster_activate_threshold: int):
        self.watch_bits = watch_bits
        self.watch_bit_set = set(watch_bits)
        self.input_size = input_size
        self.bit_mask = utils.shape_bit_mask(input_size, watch_bits)
        self.output_bit = output_bit
        self.cluster_make_threshold = cluster_make_threshold
        self.cluster_activate_threshold = cluster_activate_threshold
        self._state = const.STATE_LEARN
        self.clusters = dict()

    def process_input(self, input_bits: set):
        active_bits = input_bits & self.watch_bit_set
        bit_idx_map = [1 if bit_idx in active_bits else 0
                       for idx, bit_idx in enumerate(self.watch_bits)]
        mapped_bit_mask = bitarray(bit_idx_map) # utils.shape_bit_mask(len(self.watch_bits), bit_idx_map)
        if len(active_bits) >= self.cluster_activate_threshold:
            if self._state == const.STATE_LEARN and len(active_bits) >= self.cluster_make_threshold:
                self.add_cluster(mapped_bit_mask)
            if self._state != const.STATE_RECOGNIZE:
                self.update_clusters(mapped_bit_mask)

    def add_cluster(self, bit_mask: bitarray):
        is_subset = False
        bit_mask_count = bit_mask.count()
        for cluster in self.clusters.values():
            intersection = bit_mask & cluster.bit_mask
            if intersection.count() == bit_mask_count:
                is_subset = True
                break
        if not is_subset:
            key = bit_mask.tobytes() # tuple(sorted(bits))
            self.clusters[key] = Cluster(bit_mask=bit_mask,
                                         activate_threshold=self.cluster_activate_threshold)

    def update_clusters(self, bit_mask):
        for cluster in self.clusters.values():
            intersection = bit_mask & cluster.bit_mask
            if intersection.count() >= self.cluster_activate_threshold:
                cluster.activate(intersection)

    def cluster_count(self) -> int:
        return len(self.clusters)






