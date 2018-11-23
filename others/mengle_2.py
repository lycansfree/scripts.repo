#!/usr/bin/env python
# coding:utf-8

# 孟乐的算法题
# 计算能挣到最多的钱
# n是可以工作的总天数
# jjjj

import json
import copy

def calculateProfit(n, earning, cost, e):
    pass

def main():
    global beauty, max_t, costTimes

    # 路线时间
    costTimes = {}

    allData = {
        '测试数据集-1': {
            'beauty': [0, 32, 10, 43],
            'n': 4,
            'm': 3,
            'max_t': 49,
            'u': [0, 2, 0],
            'v': [1, 0, 3],
            't': [10, 13, 17]
        },
        '测试数据集-2': {
            'beauty': [5, 10, 15, 20],
            'n': 4,
            'm': 3,
            'max_t': 30,
            'u': [0, 1, 0],
            'v': [1, 2, 3],
            't': [6, 7, 10]
        },
        '测试数据集-3': {
            'beauty': [5, 7, 17, 8, 21, 15],
            'n': 6,
            'm': 7,
            'max_t': 30,
            'u': [0, 0, 0, 0, 1, 2, 3],
            'v': [1, 2, 4, 5, 3, 4, 5],
            't': [3, 6, 12, 13, 7, 8, 5]
        },
    }
    # 执行
    testData = allData['测试数据集-2']
    beauty = testData['beauty']
    max_t = testData['max_t']
    findBestPath(**testData)

if __name__ == '__main__':
    main()

