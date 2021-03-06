from watch_point import WatchPoint
from bitnotes import BitNotes
import constants as const
import numpy as np


class ContextNN(object):
    def __init__(self,
                 input_bit_count: int,
                 output_bit_count: int,
                 watch_point_count: int,
                 watch_bit_count: int,
                 cluster_make_threshold: int,
                 cluster_activate_threshold: int,
                 bit_notes: BitNotes = None,
                 data_marks: dict = None):
        self.input_bit_count = input_bit_count
        self.output_bit_count = output_bit_count
        self.watch_point_count = watch_point_count
        self.watch_bit_count = watch_bit_count
        self.cluster_make_threshold = cluster_make_threshold
        self.cluster_activate_threshold = cluster_activate_threshold
        self.bit_notes = bit_notes
        self.data_marks = data_marks
        self._state = const.STATE_ACCUMULATE
        self.vectors_received = 0
        self.watch_points = dict()  # {(watch_bits): WatchPoint}

        # must have the synchronous indexation (axis 0)
        self.point_objects = []
        self.point_masks = np.empty(shape=(0, input_bit_count), dtype=np.int8)

        self.gen_watch_points()

    @property
    def state(self):
        return self._state

    @state.setter
    def state(self, value):
        if self._state != value:
            self._state = value
            for point in self.point_objects:
                point.state = value

    def gen_watch_points(self):
        self.watch_points.clear()
        self.point_objects.clear()
        self.point_masks = np.empty(shape=(0, self.input_bit_count), dtype=np.int8)
        output_bits = np.append(np.repeat(np.arange(self.output_bit_count),
                                          self.watch_point_count // self.output_bit_count),
                                np.arange(self.watch_point_count % self.output_bit_count))
        np.random.shuffle(output_bits)
        for i in range(self.watch_point_count):
            watch_bits = np.random.choice(self.input_bit_count, self.watch_bit_count, replace=False)
            # watch_bits.sort()
            output_bit = output_bits[i]
            point_mask = np.zeros(self.input_bit_count, dtype=np.uint8)
            point_mask[watch_bits] = 1
            watch_point = WatchPoint(watch_bits=watch_bits,
                                     output_bit=output_bit,
                                     bit_mask=point_mask,
                                     cluster_make_threshold=self.cluster_make_threshold,
                                     cluster_activate_threshold=self.cluster_activate_threshold)
            self.point_objects.append(watch_point)
            self.point_masks = np.vstack((self.point_masks, point_mask))

    def receive_bits(self, input_bits: np.array, output_bits: set):
        self.vectors_received += 1

        # filter active points
        intersections = np.sum(self.point_masks & input_bits, axis=1)
        active_point_indices = np.where(intersections > self.cluster_activate_threshold)[0]
        for idx in active_point_indices:
            if self.point_objects[idx].output_bit in output_bits:
                self.point_objects[idx].process_input(input_bits, weight=+1)
            elif self._state == const.STATE_CONSOLIDATE:
                # suppress out-of-bit clusters
                self.point_objects[idx].process_input(input_bits, weight=-1)

    def cluster_count(self) -> int:
        return sum(wp.cluster_count() for wp in self.point_objects)

    def reduce_clusters(self,
                        min_component=0.1,
                        min_activations=10,
                        trim=True,
                        remain_parts=3,
                        clear_stats=True,
                        consolidate=True,
                        amnesty=True):
        for point in self.point_objects:
            point.reduce_clusters(min_component=min_component,
                                  min_activations=min_activations,
                                  trim=trim,
                                  remain_parts=remain_parts,
                                  clear_stats=clear_stats,
                                  consolidate=consolidate,
                                  amnesty=amnesty)
            point.pack_subsets()

    def start_detection(self):
        self.state = const.STATE_DETECT
        self.clear_cluster_activity()
        self.vectors_received = 0

    def detect_bits(self, input_bits: np.array):
        self.vectors_received += 1
        for point in self.point_objects:
            point.process_input(input_bits, weight=+1)

    def summarize_detection(self) -> np.array:  # output bits
        result = [0] * self.output_bit_count
        for output_bit in range(self.output_bit_count):
            bit_points = [point for point in self.point_objects
                          if point.cluster_count() > 0 and point.output_bit == output_bit]
            points_vote = sum([point.output_vote(self.vectors_received) / (point.cluster_count() * len(bit_points))
                               for point in bit_points if point.cluster_count() > 0])
            print(output_bit, points_vote)
            result[output_bit] = points_vote

        return np.array(result)

    def clear_cluster_activity(self):
        for point in self.point_objects:
            for cluster in point.cluster_objects:
                cluster.stats.clear()

    def point_stats(self) -> list:
        """
            [(output bit, cluster count), ...]
        """
        return [(wp.output_bit, wp.cluster_count())
                for wp in self.point_objects]

    def cluster_len_stats(self) -> dict:
        """
            {cluster len: cluster count, ...}
        """
        cluster_lens = dict()
        for wp in self.point_objects:
            for cluster in wp.cluster_objects:
                ones = np.sum(cluster.bit_mask)
                cluster_lens[ones] = cluster_lens.get(ones, 0) + 1
        return cluster_lens

    def cluster_activity_stats(self) -> dict:
        """
            {activity: cluster count, ...}
        """
        cluster_acts = dict()
        for wp in self.point_objects:
            for cluster in wp.cluster_objects:
                key = sum(cluster.stats.values())
                cluster_acts[key] = cluster_acts.get(key, 0) + 1
        return cluster_acts

    def cluster_consolidated_stats(self) -> dict:
        """
            {consolidations: cluster count, ...}
        """
        stats = dict()
        for wp in self.point_objects:
            for cluster in wp.cluster_objects:
                stats[cluster.consolidations] = stats.get(cluster.consolidations, 0) + 1
        return stats

    def cluster_max_component_stats(self):
        pass
