import math
import random
from bisect import bisect_right


class ChuckSort:
    def __init__(self, nums, viz=False):
        self.nums = nums
        self.bin_size = int(math.sqrt(len(self.nums)))
        self.min = min(nums)
        self.max = max(nums)
        self.bounds2bins = self.setup_bins()
        self.bins2bounds = {v: k for k, v in self.bounds2bins.items()}
        self.lower_bounds = list(self.bounds2bins.keys())

        self.been_bin_sorted = set()

        self.viz = viz

    def setup_bins(self):
        """Map the range of values in nums to grouped indices of nums."""
        width = int((self.max - self.min) / self.bin_size)
        bins = {
            i * width + self.min: (idx, idx + self.bin_size)
            for i, idx in enumerate(range(0, len(self.nums), self.bin_size))
        }
        return bins

    def predecessor(self, n, lower, upper):
        """Find index of the value _just_ smaller than n."""
        pred = -math.inf
        pos = None
        for i, ele in enumerate(self.nums[lower: upper], start=lower):
            if pred < ele < n:
                pred = ele
                pos = i
        return pos

    @staticmethod
    def find_le(a, x):
        """Binary search. Find rightmost value less than or equal to x"""
        i = bisect_right(a, x)
        if i:
            return a[i - 1]
        raise ValueError

    def insert(self, n, bin_):
        """Find the correct location to place a number and add it back to the list."""
        pred_pos = self.predecessor(n, bin_[0], bin_[1])
        insert_pos = pred_pos + 1 if pred_pos is not None else bin_[0]
        self.nums.insert(insert_pos, n)

    def check_bad_bin(self, bin_):
        """Return a number from the current bin that doesn't belong there."""
        low = self.bins2bounds[bin_]
        for n in self.nums[bin_[0]: bin_[1]]:
            if n not in self.been_bin_sorted:
                self.been_bin_sorted.add(n)
                if self.find_le(self.lower_bounds, n) != low:
                    return n
        return None

    def sort_to_bin(self, n):
        """Move a number to it's correct bin."""
        self.been_bin_sorted.add(n)
        self.nums.remove(n)
        bin_ = self.bounds2bins[self.find_le(self.lower_bounds, n)]
        self.insert(n, bin_)
        return self.check_bad_bin(bin_), bin_

    def get_new_n(self, bin_):
        """Clearly this is over-complicated, but we tended to continue from where we started."""
        def get_from(array):
            for possible_new_n in array:
                if possible_new_n not in self.been_bin_sorted:
                    return possible_new_n
            return None
        new_n = get_from(self.nums[bin_[1]:])
        if new_n is None:
            new_n = get_from(self.nums[0: bin_[0]])
        return new_n

    def first_unsorted(self, start):
        """Clearly this is over-complicated, but we tended to continue from where we started."""
        def get_from(start, stop):
            for i in range(start, stop):
                if self.nums[i] > self.nums[i+1]:
                    return i+1
            return None
        if start == len(self.nums):
            start = 0
        new_n = get_from(start, len(self.nums)-1)
        if new_n is None:
            new_n = get_from(0, start)
        return new_n

    def nearby_sort(self, idx):
        """This is the best way to describe what happened at this stage. There was no consistent algo."""
        start = max(0, idx - int(self.bin_size / 2))
        stop = min(idx + int(self.bin_size / 2), len(self.nums))
        self.nums[start: stop] = sorted(self.nums[start: stop])
        return stop

    def stage1(self):
        """Roughly sort all numbers into their approximate locations."""
        n = self.min
        while True:
            n, bin_ = self.sort_to_bin(n)
            if n is None:
                n = self.get_new_n(bin_)
                if n is None:
                    break
            if self.viz:
                yield

    def stage2(self):
        """Find numbers that are still unsorted and sort their nearby areas."""
        start = 0
        while True:
            idx = self.first_unsorted(start)
            if idx is None:
                break
            start = self.nearby_sort(idx)
            if self.viz:
                yield

    def sort(self):
        """This setup allows me to do the visualizations on each step."""
        for _ in self.stage1():
            yield
        for _ in self.stage2():
            yield
