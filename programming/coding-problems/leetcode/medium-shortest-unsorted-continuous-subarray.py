from typing import List


class Solution:
    def findUnsortedSubarray(self, nums: List[int]) -> int:
        n = len(nums)

        # 1) Find first inversion from the left.
        left = 0
        while left < n - 1 and nums[left] <= nums[left + 1]:
            left += 1

        # Already sorted.
        if left == n - 1:
            return 0

        # 2) Find first inversion from the right.
        right = n - 1
        while right > 0 and nums[right - 1] <= nums[right]:
            right -= 1

        # 3) Compute min/max inside the rough unsorted window.
        # Derivation intuition:
        # - The first left/right inversions only give a rough window where order is broken.
        # - Sorting just that rough window may still fail if values outside conflict with it.
        # - window_min is the smallest value that must appear before any larger value.
        # - window_max is the largest value that must appear after any smaller value.
        # So we expand boundaries until everything left is <= window_min and
        # everything right is >= window_max.
        window_min = min(nums[left:right + 1])
        window_max = max(nums[left:right + 1])

        # 4) Expand left if elements before it are bigger than window_min.
        while left > 0 and nums[left - 1] > window_min:
            left -= 1

        # 5) Expand right if elements after it are smaller than window_max.
        while right < n - 1 and nums[right + 1] < window_max:
            right += 1

        return right - left + 1


if __name__ == "__main__":
    s = Solution()
    assert s.findUnsortedSubarray([2, 6, 4, 8, 10, 9, 15]) == 5
    assert s.findUnsortedSubarray([1, 2, 3, 4]) == 0
    assert s.findUnsortedSubarray([1]) == 0
    assert s.findUnsortedSubarray([1, 3, 2, 2, 2]) == 4
    print("All tests passed")
