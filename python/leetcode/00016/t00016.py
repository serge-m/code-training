"""
16. 3Sum Closest
Medium

O(n^2)

Runtime: 164 ms, faster than 44.27% of Python3 online submissions for 3Sum Closest.
Memory Usage: 14.4 MB, less than 11.77% of Python3 online submissions for 3Sum Closest.
"""
import math


def find2(nums, i2, i3, target, mindiff):
    while i2 < i3:

        s = nums[i2] + nums[i3]
        # print(f"find2 {i2} {i3} {mindiff} s {s} target {target}" )
        diff = target - s
        if abs(diff) < abs(mindiff):
            mindiff = diff
        if target > s:
            i2 += 1  # increase sum
        elif target < s:
            i3 -= 1  # decrease sum
        else:
            break  # sum == 0, no need to continue
    # print(f"find2 {i2} {i3} {mindiff}")
    return mindiff


class Solution:
    def threeSumClosest(self, nums: List[int], target: int) -> int:
        nums.sort()
        # print(nums)
        mindiff = math.inf

        n = len(nums)
        for i1 in range(n - 2):
            x1 = nums[i1]
            # print(f"min {mindiff} x1 {x1}")

            mindiff = find2(nums, i1 + 1, n - 1, target - x1, mindiff)
            if x1 * 3 - target > abs(mindiff):
                break
        # print(mindiff)
        return target - mindiff
