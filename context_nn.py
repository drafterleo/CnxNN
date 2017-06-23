from watch_point import WatchPoint
import numpy as np
import random

STATE_LEARN = 1
STATE_CONSOLIDATE = 2
STATE_RECOGNIZE = 3


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
        self.state = STATE_LEARN
        self.watch_points = dict()  # {(watch_bits): WatchPoint}
        self.gen_watch_points()

    def gen_watch_points(self):
        for i in range(self.watch_point_count):
            watch_bits = np.random.choice(self.input_bit_count, self.watch_bit_count, replace=False)
            watch_bits.sort()
            watch_bits_key = tuple(watch_bits)
            output_bit = random.randrange(self.output_bit_count)
            watch_point = WatchPoint(watch_bits=watch_bits_key,
                                     output_bit=output_bit,
                                     cluster_make_threshold=self.cluster_make_threshold,
                                     cluster_activate_threshold=self.cluster_activate_threshold)
            self.watch_points[watch_bits_key] = watch_point

    def receive_bits(self, input_bits: set, output_bits: set):
        for watch_point in self.watch_points.values():
            if watch_point.output_bit in output_bits:
                watch_point.process_input(input_bits)

