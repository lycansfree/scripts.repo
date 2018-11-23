#!/usr/bin/env python
# coding:utf-8

# 孟乐的算法题
# 计算在给定时间范围内能获取到的最大魅力值
# n是景点数量,m是路线数量,max_t是最大允许用时
# beauty是景点的魅力值-list
# u和v是index对照关系,生成路线图
# t是每条路线的单程耗时

import json
import copy

def calBeauty(currPoint, prevPoint, oldRoads, totalBeauty, totalTime, roads):
    # 递归函数,计算路线和魅力值
    # 总时长大于max_t时则return
    # 回到0点且加上下一步时长大于max_t时则return
    # 无路可走则return
    # currPoint是当前节点
    # prevPoint是上一个节点
    # oldRoads是已经走过的节点
    # totalBeauty是已经拿到的魅力值总和

    # 先判断是否到最终态
    # 回到0点且无法再走
    if prevPoint == '0':
        tmpTotalTime = totalTime + 2 * costTimes[prevPoint + '-' + currPoint]
        if tmpTotalTime > max_t:
            return [[totalTime, totalBeauty, oldRoads]]
    else:
        tmpTotalTime = totalTime + costTimes[prevPoint + '-' + currPoint]
        if tmpTotalTime > max_t:
            return [[totalTime, totalBeauty, oldRoads]]

    # 走过的路不再走
    roads[prevPoint].pop(roads[prevPoint].index(currPoint))

    # 计算totalBeauty, 重复走过的不计算
    if currPoint not in oldRoads:
        totalBeauty += beauty[int(currPoint)]

    # 记录走过的路
    oldRoads.append(currPoint)

    # 计算消耗时间
    totalTime += costTimes[prevPoint + '-' + currPoint]

    # 再计算下一步
    if len(roads[currPoint]) == 0:
        # 无下一步可走
        return [[totalTime, totalBeauty, oldRoads]]
    else:
        # 有下一步,且任何方向都包括
        ret = []
        for x in roads[currPoint]:
            tmpRoads = copy.deepcopy(roads)
            tmpOldRoads = copy.deepcopy(oldRoads)
            ret += calBeauty(currPoint = x, prevPoint = currPoint, oldRoads = tmpOldRoads, totalBeauty = totalBeauty, totalTime = totalTime, roads = tmpRoads)
        return ret
        

def findBestPath(n, m, max_t, beauty, u, v, t):
    # 定义所有结果集
    allRoads = {
        'maxBeauty': 0,
        'maxRoad': '',
        'maxTime': 0
    }

    # 先遍历出路线图
    roads = {}
    for idx in xrange(m):
        uidx = str(u[idx])
        vidx = str(v[idx])
        if uidx not in roads:
            roads[uidx] = []
        if vidx not in roads:
            roads[vidx] = []

        roads[uidx].append(vidx)
        roads[vidx].append(uidx)

        costTimes[uidx + '-' + vidx] = t[idx]
        costTimes[vidx + '-' + uidx] = t[idx]
        
    # print json.dumps(costTimes, indent = 4)
    # print json.dumps(roads, indent = 4)
    # 开始计算路线,从0点开始
    ret = []
    for x in roads['0']:
        # 对路线图做深拷贝,单独开辟内存空间,用于每一条路线实例
        tmpRoads = copy.deepcopy(roads)
        # 传递下一个节点,做当前节点
        ret += calBeauty(currPoint = x, prevPoint = '0', oldRoads = ['0'], totalBeauty = beauty[0], totalTime = 0, roads = tmpRoads)
        
    for _t, _b, _r in ret:
        # if _t > max_t:
        #     continue

        # 最后未回到起点的路线,pass
        if _r[-1] != '0':
            continue

        # 记录所有走过的路线,耗时与魅力值,可以不要
        allRoads['-'.join(_r)] = [_t, _b]

        # 判断魅力值最大的路线,存储下来,并在循环结束后输出
        if _b > allRoads['maxBeauty']:
            allRoads['maxBeauty'] = _b
            allRoads['maxRoad'] = '-'.join(_r)
            allRoads['maxTime'] = _t

    # print json.dumps(allRoads, indent = 4)
    print "最佳路线:%s,最佳路线获得的魅力值:%d,最佳路线耗时:%d" % (allRoads['maxRoad'], allRoads['maxBeauty'], allRoads['maxTime'])

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

