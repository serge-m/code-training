"""
17. Letter Combinations of a Phone Number
Medium

sneaky boundary condition (empty array in itertools.product)
"""

import itertools


class Solution:
    def letterCombinations(self, digits: str) -> List[str]:
        if not digits:
            return []
        d2l = {
            2: 'abc',
            3: 'def',
            4: 'ghi',
            5: 'jkl',
            6: 'mno',
            7: 'pqrs',
            8: 'tuv',
            9: 'wxyz'
        }
        d2l = {str(k): v for k, v in d2l.items()}
        letters = [d2l[d] for d in digits]

        return [''.join(word) for word in itertools.product(*letters)]
