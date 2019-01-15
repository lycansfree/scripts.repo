### 下载 + 编译
> 官网 - http://redis.io 下载源码包

```
1. 解压并进入对应目录
# 如果编译出错，大部分情况可能是没有指定内存池
# 由于redis没有自己实现内存池，所以编译时可以额外指定
# jemalloc 是 facebook推出，编译参数默认值
# tcmalloc 是 google推出
# libc 是标准内存分配库malloc
2. 编译 - make MALLOC=libc
3. 安装 - make PREFIX=${redis_dir} install
```

#### 创建集群
##### 版本5.0+
> ./redis-cli --cluster create host1:port1 ... hostN:portN --cluster-replicas 1

##### 版本3.x 4.x
> 需要使用ruby环境与脚本，gem安装redis后方可


### 使用
> 查看集群信息和节点信息

```
redis-cli -h 172.20.17.73 -p 7001 cluster info

redis-cli -h 172.20.17.73 -p 7001 cluster nodes

redis-cli --cluster check 172.20.17.71:7000
```

> 总共拥有16384个slot

```
# 重新分配slot
redis-cli --cluster reshard 172.20.17.72:7001


```
