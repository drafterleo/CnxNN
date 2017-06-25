import constants as const
from cluster import Cluster


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
        self.clusters = dict()

    def process_input(self, input_bits: set):
        active_bits = input_bits & self.watch_bit_set
        if len(active_bits) >= self.cluster_activate_threshold:
            if self._state == const.STATE_LEARN and len(active_bits) >= self.cluster_make_threshold:
                self.add_cluster(active_bits)
            if self._state != const.STATE_RECOGNIZE:
                self.update_clusters(active_bits)

    def add_cluster(self, bits: set):
        is_subset = False
        for cluster in self.clusters.values():
            if bits.issubset(cluster.bits):
                is_subset = True
                break
        # is_subset = [True for cluster in self.clusters.values() if bits.issubset(cluster.bits)]
        if not is_subset:
            bit_key = tuple(sorted(bits))
            self.clusters[bit_key] = Cluster(bits=bits,
                                             activate_threshold=self.cluster_activate_threshold)

    def update_clusters(self, bits: set):
        for cluster in self.clusters.values():
            intersection = bits & cluster.bits
            if len(intersection) >= self.cluster_activate_threshold:
                cluster.activate(intersection)

    def cluster_count(self) -> int:
        return len(self.clusters)






