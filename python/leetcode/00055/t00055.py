"""
55. Jump Game
Medium


Runtime: 516 ms, faster than 50.16% of Python3 online submissions for Jump Game.
Memory Usage: 15.3 MB, less than 71.73% of Python3 online submissions for Jump Game.
"""
"""
t0

0
true

0 1
false

1 0
true
"""


class Solution:
    def canJump(self, nums: List[int]) -> bool:
        max_pos = 0
        for i, x in enumerate(nums):
            if max_pos < i:
                return False
            max_pos = max(max_pos, i + x)
        return True
