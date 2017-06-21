from watch_point import WatchPoint

STATE_LEARN = 1
STATE_CONSOLIDATE = 2
STATE_RECOGNIZE = 3


class ContextNN:
    def __init__(self,
                 input_bits_count: int,
                 output_bits_count: int,
                 watch_point_count: int):
        self.input_bits_count = input_bits_count
        self.output_bits_count = output_bits_count
        self.watch_point_count = watch_point_count
        self.state = STATE_LEARN
        self.watch_points = dict()  # {(watch_bits): WatchPoint}
        self.make_watch_points()

    def feed_active_bits(self, input_bits: set, output_bits: set):
        for key, watch_point in self.watch_points:
            if watch_point.output_bit in output_bits:
                watch_point.process_input(input_bits)

    def make_watch_points(self):
        pass
