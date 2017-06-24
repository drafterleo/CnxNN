from cluster import Cluster
from bitarray import bitarray


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
        self.clusters = dict()

    def process_input(self, input_bits: set):
        active_bits = input_bits & self.watch_bit_set
        if len(active_bits) >= self.cluster_activate_threshold:
            bits = [1 if bit_idx in active_bits else 0
                    for bit_idx in self.watch_bits]
            bit_mask = bitarray(bits)
            if len(active_bits) >= self.cluster_make_threshold:
                self.add_cluster(tuple(sorted(active_bits)), bit_mask)
            self.update_clusters(active_bits, bit_mask)

    def add_cluster(self, bit_key: tuple, bit_mask: bitarray):
        if bit_key not in self.clusters:
            self.clusters[bit_key] = Cluster(bits=bit_key,
                                             bit_mask=bit_mask,
                                             activate_threshold=self.cluster_activate_threshold)

    def update_clusters(self, bits: set, bit_mask: bitarray):
        for cluster in self.clusters.values():
            intersection = bits & cluster.bit_set
            if len(intersection) >= self.cluster_activate_threshold:
                cluster.activate(intersection)
        # for cluster in self.clusters.values():
        #     intersection = bit_mask & cluster.bit_mask
        #     if intersection.count(1) >= self.cluster_activate_threshold:
        #         cluster.activate(intersection)








