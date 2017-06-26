import constants as const
from cluster import Cluster
import numpy as np


class WatchPoint:
    def __init__(self,
                 watch_bits: tuple,  # input bit indices
                 output_bit: int,    # output bit index
                 cluster_make_threshold: int,
                 cluster_activate_threshold: int):
        self.watch_bits = watch_bits
        self.watch_bit_set = set(watch_bits)
        self.output_bit = output_bit
        self.cluster_make_threshold = cluster_make_threshold
        self.cluster_activate_threshold = cluster_activate_threshold
        self._state = const.STATE_LEARN

        # must have the synchronous indexation
        self.cluster_objects = []
        self.cluster_masks = np.empty(shape=(0, len(watch_bits)), dtype=np.int8)

    def process_input(self, input_bits: set):
        active_bits = input_bits & self.watch_bit_set
        if len(active_bits) >= self.cluster_activate_threshold:
            cluster_mask = np.array([1 if bit_idx in active_bits else 0
                                     for bit_idx in self.watch_bits], dtype=np.int8)
            clusterwise_bit_counts = np.count_nonzero(self.cluster_masks & cluster_mask, axis=1)
            if self._state == const.STATE_LEARN and len(active_bits) >= self.cluster_make_threshold:
                self.add_cluster(active_bits, cluster_mask, clusterwise_bit_counts)
            if self._state != const.STATE_RECOGNIZE:
                self.update_clusters(active_bits, clusterwise_bit_counts)

    def add_cluster(self, bits: set, cluster_mask: np.array, clusterwise_bit_counts: np.array):
        if len(clusterwise_bit_counts) > 0:
            is_subset = np.count_nonzero(cluster_mask) == np.max(clusterwise_bit_counts)
        else:
            is_subset = False
        if not is_subset:
            new_cluster = Cluster(bits=bits,
                                  activate_threshold=self.cluster_activate_threshold)
            self.cluster_objects.append(new_cluster)
            self.cluster_masks = np.vstack((self.cluster_masks, cluster_mask))

    def update_clusters(self, bits: set, clusterwise_bit_counts: np.array):
        if len(clusterwise_bit_counts) > 0:
            active_clusters = np.where(clusterwise_bit_counts >= self.cluster_activate_threshold)
            for idx in active_clusters[0]:
                cluster = self.cluster_objects[idx]
                cluster.activate(bits & cluster.bits)

    def cluster_count(self) -> int:
        return len(self.cluster_objects)






