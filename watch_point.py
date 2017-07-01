import constants as const
from cluster import Cluster
import numpy as np


class WatchPoint(object):
    def __init__(self,
                 watch_bits: tuple,  # input bit indices
                 output_bit: int,    # output bit index
                 bit_mask: np.array,
                 cluster_make_threshold: int,
                 cluster_activate_threshold: int):
        self.watch_bits = watch_bits
        self.watch_bit_set = set(watch_bits)
        self.bit_mask = bit_mask
        self.output_bit = output_bit
        self.cluster_make_threshold = cluster_make_threshold
        self.cluster_activate_threshold = cluster_activate_threshold
        self._state = const.STATE_ACCUMULATE

        # must have the synchronous indexation
        self.cluster_objects = []
        self.cluster_masks = np.empty(shape=(0, len(watch_bits)), dtype=np.int8)

    def process_input(self, input_bits: set):
        active_bits = input_bits & self.watch_bit_set
        if len(active_bits) >= self.cluster_activate_threshold:
            cluster_mask = np.array([1 if bit_idx in active_bits else 0
                                     for bit_idx in self.watch_bits], dtype=np.int8)
            clusterwise_intersections = np.count_nonzero(self.cluster_masks & cluster_mask, axis=1)
            if self._state == const.STATE_ACCUMULATE and len(active_bits) >= self.cluster_make_threshold:
                self.add_cluster(active_bits, cluster_mask, clusterwise_intersections)
            if self._state != const.STATE_DETECT:
                self.update_clusters(active_bits, clusterwise_intersections)

    def add_cluster(self, bits: set, cluster_mask: np.array, clusterwise_intersections: np.array):
        if len(clusterwise_intersections) > 0:
            is_subset = np.count_nonzero(cluster_mask) == np.max(clusterwise_intersections)
        else:
            is_subset = False
        if not is_subset:
            new_cluster = Cluster(bits=bits,
                                  bit_mask=cluster_mask,
                                  activate_threshold=self.cluster_activate_threshold)
            self.cluster_objects.append(new_cluster)
            self.cluster_masks = np.vstack((self.cluster_masks, cluster_mask))

    def update_clusters(self, bits: set, clusterwise_intersections: np.array):
        if len(clusterwise_intersections) > 0:
            active_clusters = np.where(clusterwise_intersections >= self.cluster_activate_threshold)
            for idx in active_clusters[0]:
                cluster = self.cluster_objects[idx]
                cluster.activate(bits & cluster.bits)

    def cluster_count(self) -> int:
        return len(self.cluster_objects)

    def remove_cluster(self, index: int):
        del self.cluster_objects[index]
        self.cluster_masks = np.delete(self.cluster_masks, (index,), axis=0)

    def remove_clusters(self, indices: list):
        for rm_idx in sorted(indices, reverse=True):
            del self.cluster_objects[rm_idx]
        self.cluster_masks = np.delete(self.cluster_masks, indices, axis=0)

    def pack_subsets(self):
        remove_indices = []
        for idx, cluster in enumerate(self.cluster_objects):
            intersections = np.count_nonzero(self.cluster_masks & cluster.bit_mask, axis=1)
            supersets = np.where(intersections == len(cluster.bits))
            if len(supersets) > 1:
                remove_indices.append(idx)
        self.remove_clusters(remove_indices)

    def reduce_clusters(self,
                        min_component=0.1,
                        min_activations=10,
                        trim=True,
                        remain_part=0.3,
                        clear_stats=True,
                        consolidate=True,
                        amnesty=True):
        remove_indices = []
        for idx, cluster in enumerate(self.cluster_objects):
            if not cluster.test_for_strength(component_threshold=min_component,
                                             min_activations=min_activations,
                                             trim=trim,
                                             remain_part=remain_part,
                                             clear_stats=clear_stats,
                                             consolidate=consolidate,
                                             amnesty=amnesty):
                remove_indices.append(idx)
            else:
                new_bit_mask = np.array([1 if bit_idx in cluster.bits else 0
                                         for bit_idx in self.watch_bits], dtype=np.int8)
                cluster.bit_mask = new_bit_mask
                self.cluster_masks[idx] = new_bit_mask  # if cluster was trimmed

        self.remove_clusters(remove_indices)

    def output_vote(self, received_vectors: int) -> float:  # 0 or 1
        max_cluster_len = max(len(cluster.bits) for cluster in self.cluster_objects)
        max_cluster_consld = max(cluster.consolidations for cluster in self.cluster_objects)
        activity_norm = received_vectors * self.cluster_count() * max_cluster_len * max_cluster_consld
        cluster_contribs = sum(cluster.activity_numerator()/activity_norm for cluster in self.cluster_objects)
        return cluster_contribs







