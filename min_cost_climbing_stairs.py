from typing import List


class Solution:
    def minCostClimbingStairs(self, cost: List[int]) -> int:
        dp = [0] * len(cost)
        for i in range(len(cost) - 2)[::-1]:
            dp[i] = min(dp[i + 1] + cost[i + 1], dp[i + 2] + cost[i + 2])

        return min(dp[0] + cost[0], dp[1] + cost[1])


sol = Solution()
print(sol.minCostClimbingStairs([10, 15, 20]))
print(sol.minCostClimbingStairs([1, 100, 1, 1, 1, 100, 1, 1, 100, 1]))
