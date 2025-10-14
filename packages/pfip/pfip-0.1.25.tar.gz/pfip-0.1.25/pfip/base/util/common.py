import re


def min_edit_distance(word1, word2):
    """
    最小编辑距离计算
    :param word1:
    :param word2:
    :return:
    """
    m = len(word1)
    n = len(word2)
    # 初始化二维数组，dp[i][j]表示将word1的前i个字符转换为word2的前j个字符所需的最小编辑距离
    dp = [[0] * (n + 1) for _ in range(m + 1)]
    # 初始化第一行和第一列
    for i in range(m + 1):
        dp[i][0] = i
    for j in range(n + 1):
        dp[0][j] = j
    # 动态规划填表
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if word1[i - 1] == word2[j - 1]:
                dp[i][j] = dp[i - 1][j - 1]  # 相同字符，不需要操作
            else:
                dp[i][j] = min(
                    dp[i - 1][j] + 1,  # 删除操作
                    dp[i][j - 1] + 1,  # 插入操作
                    dp[i - 1][j - 1] + 1
                )  # 替换操作
    # 返回右下角的值，即word1转换为word2的最小编辑距离
    return dp[m][n]


def remove_whitespace(text: str):
    """使用正则表达式去除所有空格和不可见字符"""
    return re.sub(r'\s+', '', text)
