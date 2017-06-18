from cluster import Cluster


class WatchPoint:
    def __init__(self,
                 input_bits: tuple,  # input bit indices
                 output_bit: int,    # output bit index
                 cluster_make_threshold: int,
                 cluster_activate_threshold: int):
        self.input_bits = input_bits
        self.input_bit_set = set(input_bits)
        self.output_bit = output_bit
        self.cluster_make_threshold = cluster_make_threshold
        self.cluster_activate_threshold = cluster_activate_threshold
        self.clusters = dict()

    def process_input(self, input_bits: set):
        active_bits = set.intersection(input_bits, self.input_bit_set)
        if len(active_bits) >= self.cluster_make_threshold:
            self.add_cluster(tuple(sorted(active_bits)))
        if len(active_bits) >= self.cluster_activate_threshold:
            self.update_clusters()

    def add_cluster(self, bit_key: tuple):
        if bit_key not in self.clusters:
            self.clusters[bit_key] = Cluster

    def update_clusters(self, active_bits: set):
        for key, cluster in self.clusters:
            intersection = active_bits & cluster.bit_set
            if len(intersection) >= self.cluster_activate_threshold:
                cluster.activate(intersection)








