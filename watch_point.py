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
        self.cluster_masks = np.empty(shape=(0, len(watch_bits)), dtype=np.uint8)

    def process_input(self, input_bits: np.array):
        cluster_mask = input_bits[self.watch_bits]
        active_bit_count = np.count_nonzero(cluster_mask)
        if active_bit_count >= self.cluster_activate_threshold:
            clusterwise_isects = np.count_nonzero(self.cluster_masks & cluster_mask, axis=1)
            if self._state == const.STATE_ACCUMULATE and \
               active_bit_count >= self.cluster_make_threshold and \
               (len(clusterwise_isects) == 0 or active_bit_count > np.max(clusterwise_isects)):
                    self.add_cluster(cluster_mask)
                    return

            if len(clusterwise_isects) > 0:
                active_cluster_indices = np.where(clusterwise_isects >= self.cluster_activate_threshold)[0]
                self.update_clusters(cluster_mask, active_cluster_indices)

    def add_cluster(self, cluster_mask: np.array):
        new_cluster = Cluster(bit_mask=cluster_mask,
                              activate_threshold=self.cluster_activate_threshold)
        self.cluster_objects.append(new_cluster)
        self.cluster_masks = np.vstack((self.cluster_masks, cluster_mask))
        new_cluster.activate(bits=cluster_mask)

    def update_clusters(self, bits: np.array, active_cluster_indices: list):
        for idx in active_cluster_indices:
            cluster = self.cluster_objects[idx]
            cluster.activate(bits & cluster.bit_mask)

    def cluster_count(self) -> int:
        return len(self.cluster_objects)

    def remove_cluster(self, index: int):
        del self.cluster_objects[index]
        self.cluster_masks = np.delete(self.cluster_masks, (index,), axis=0)

    def remove_clusters(self, indices: list):
        for rm_idx in sorted(indices, reverse=True):
            del self.cluster_objects[rm_idx]
        self.cluster_masks = np.delete(self.cluster_masks, indices, axis=0)

    def remove_duplicates(self):
        unique_clusters = {}
        for cluster in self.cluster_objects:
            key = cluster.bit_mask.tobytes()
            if key in unique_clusters:
                unique_clusters[key].append(cluster)
            else:
                unique_clusters[key] = [cluster]

        self.cluster_objects = []
        self.cluster_masks = np.empty(shape=(0, len(self.watch_bits)), dtype=np.uint8)
        for key, clusters in unique_clusters.items():
            self.cluster_objects.append(clusters[0])
            self.cluster_masks = np.vstack((self.cluster_masks, clusters[0].bit_mask))

    def remove_subsets(self):
        remove_indices = []
        for idx, cluster in enumerate(self.cluster_objects):
            intersections = np.count_nonzero(self.cluster_masks & cluster.bit_mask, axis=1)
            supersets = np.where(intersections == np.count_nonzero(cluster.bit_mask))
            if len(supersets) > 1:
                remove_indices.append(idx)
        self.remove_clusters(remove_indices)

    def pack_subsets(self):
        # self.remove_duplicates()
        self.remove_subsets()

    def reduce_clusters(self,
                        min_component=0.1,
                        min_activations=10,
                        trim=True,
                        remain_parts=3,
                        clear_stats=True,
                        consolidate=True,
                        amnesty=True):
        remove_indices = []
        for idx, cluster in enumerate(self.cluster_objects):
            if not cluster.test_for_strength(component_threshold=min_component,
                                             min_activations=min_activations,
                                             trim=trim,
                                             remain_parts=remain_parts,
                                             clear_stats=clear_stats,
                                             consolidate=consolidate,
                                             amnesty=amnesty):
                remove_indices.append(idx)
            else:
                self.cluster_masks[idx] = cluster.bit_mask # if cluster was trimmed

        self.remove_clusters(remove_indices)

    def output_vote(self, received_vectors: int) -> float:  # 0 or 1
        # max_cluster_len = max(len(cluster.bits) for cluster in self.cluster_objects)
        # max_cluster_consld = max(cluster.consolidations for cluster in self.cluster_objects)
        activity_norm = received_vectors * self.cluster_count()  # * max_cluster_len * max_cluster_consld  * self.cluster_count()
        if activity_norm:
            cluster_contribs = sum(cluster.activity_numerator() * cluster.consolidations
                                   for cluster in self.cluster_objects)
            # print(list(cluster.activity_numerator() for cluster in self.cluster_objects))
            # print(received_vectors, self.cluster_count(), max_cluster_len, max_cluster_consld)
            # print(cluster_contribs)
        else:
            cluster_contribs = 0.0
        return cluster_contribs







