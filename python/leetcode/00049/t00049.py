"""
49. Group Anagrams
Medium

t = 3
"""

from typing import List
from collections import defaultdict

class Solution:
    def groupAnagrams(self, strs: List[str]) -> List[List[str]]:
        groups = defaultdict(list)
        for w in strs:
            groups[''.join(sorted(w))].append(w)
        return list(groups.values())
