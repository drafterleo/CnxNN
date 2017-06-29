from watch_point import WatchPoint
import constants as const
import numpy as np
import random
from multiprocessing import Process


class ContextNN:
    def __init__(self,
                 input_bit_count: int,
                 output_bit_count: int,
                 watch_point_count: int,
                 watch_bit_count: int,
                 cluster_make_threshold: int,
                 cluster_activate_threshold: int):
        self.input_bit_count = input_bit_count
        self.output_bit_count = output_bit_count
        self.watch_point_count = watch_point_count
        self.watch_bit_count = watch_bit_count
        self.cluster_make_threshold = cluster_make_threshold
        self.cluster_activate_threshold = cluster_activate_threshold
        self._state = const.STATE_LEARN
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
            for point in self.watch_points.values():
                point._state = value

    def gen_watch_points(self):
        self.watch_points.clear()
        self.point_objects.clear()
        self.point_masks = np.empty(shape=(0, self.input_bit_count), dtype=np.int8)
        for i in range(self.watch_point_count):
            watch_bits = np.random.choice(self.input_bit_count, self.watch_bit_count, replace=False)
            watch_bits.sort()
            watch_bits_key = tuple(watch_bits)
            output_bit = random.randrange(self.output_bit_count)
            point_mask = np.array([1 if bit_idx in watch_bits else 0
                                   for bit_idx in range(self.input_bit_count)], dtype=np.int8)
            watch_point = WatchPoint(watch_bits=watch_bits_key,
                                     output_bit=output_bit,
                                     bit_mask=point_mask,
                                     cluster_make_threshold=self.cluster_make_threshold,
                                     cluster_activate_threshold=self.cluster_activate_threshold)
            self.watch_points[watch_bits_key] = watch_point
            self.point_objects.append(watch_point)
            self.point_masks = np.vstack((self.point_masks, point_mask))

    def receive_bits(self, input_bits: set, output_bits: set):
        # filter active points
        bit_mask = np.array([1 if bit_idx in input_bits else 0
                             for bit_idx in range(self.input_bit_count)], dtype=np.int8)
        intersections = np.count_nonzero(self.point_masks & bit_mask, axis=1)
        active_point_indices = np.where(intersections > 0)

        for idx in active_point_indices[0]:
            if self.point_objects[idx].output_bit in output_bits:
                self.point_objects[idx].process_input(input_bits)

    def cluster_count(self) -> int:
        return sum(wp.cluster_count() for wp in self.point_objects)

    def reduce_clusters(self, min_component=0.1, min_activations=10):
        for point in self.point_objects:
            point.reduce_clusters(min_component, min_activations)

