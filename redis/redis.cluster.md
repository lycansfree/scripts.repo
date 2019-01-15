> redis 5.0.3 cluster config

```
bind IP
port 6379
daemonize yes
pidfile /var/run/redis_6379.pid
logfile ""
always-show-logo yes
cluster-enabled yes
cluster-config-file nodes.conf
cluster-node-timeout 5000
maxmemory 1g


# no upstart systemd auto
supervised no

# debug verbose notice warning
loglevel notice

# 默认开启,防止未经认证的客户端从其他主机进行连接
protected-mode yes
# 配置访问密码
# requirepass RQqyDmr@sH8yEjx!2J89fVq#mSTO7H8V
# 配置主从模式
# slaveof 192.168.80.104 6379
# 如果需要访问密码，则主从时也需要对应配置
# masterauth RQqyDmr@sH8yEjx!2J89fVq#mSTO7H8V
# 主从同步数据配置，默认yes
# slave-serve-stale-data yes

# TCP连接中允许队列的最大值
# 这里的配置和/proc/sys/net/core/somaxconn的值取两者中最小值
# 表现为netstat中的Send-Q
tcp-backlog 511

# 当客户端空闲N秒后关闭链接，0为不断开
timeout 0

# 默认值300，TCP长连接，根据使用场景决定是否开启
# 开启后对server性能有所损耗
tcp-keepalive 0

# 设置数据库的数量，0 TO (${databases} - 1)
databases 16

# 设置RDB持久化的频率
# save ${N秒} ${M个key值发生变化}
# 只配置save "" 时，关闭RDB模式
save 900 1
save 300 10
save 60 10000

# RDB持久化发生失败后，禁止再进行写操作
stop-writes-on-bgsave-error yes

# 启用压缩需要消耗一点CPU性能
rdbcompression yes

# 对RDB数据进行校验，消耗CPU性能
rdbchecksum yes

# RDB文件名和路径
dbfilename dump.rdb
dir ./

# 是否开启AOF模式
appendonly no
# AOF文件名
appendfilename "appendonly.aof"
# AOF策略：always everysec no
appendfsync everysec
# 在执行bgrewriteaof时，是否执行写入磁盘
# 原因是在rewrite AOF文件时，会有大量的磁盘IO，如果此时执行写入磁盘，则可能会有阻塞等待
no-appendfsync-on-rewrite no
auto-aof-rewrite-percentage 100
auto-aof-rewrite-min-size 64mb
aof-load-truncated yes
# AOF和RDB混合模式，在AOF文件中用RDB格式记录已有数据，AOF格式记录近期变化的数据
# redis 4.0后新增功能
aof-use-rdb-preamble yes
# redis内置lua脚本支持，定义脚本的执行时间上限
lua-time-limit 5000
# 定义多长时间的查询为slowlog
# 单位是微秒
slowlog-log-slower-than 10000
slowlog-max-len 128
# 监控大于等于N（毫秒）的操作，N == 0关闭该监控
latency-monitor-threshold 0
# 通知客户端关于keyspace的事件，通常关闭
notify-keyspace-events ""
# 进阶配置
hash-max-ziplist-entries 512
hash-max-ziplist-value 64
list-max-ziplist-size -2
list-compress-depth 0
set-max-intset-entries 512
zset-max-ziplist-entries 128
zset-max-ziplist-value 64
hll-sparse-max-bytes 3000
stream-node-max-bytes 4096
stream-node-max-entries 100
activerehashing yes
client-output-buffer-limit normal 0 0 0
client-output-buffer-limit replica 256mb 64mb 60
client-output-buffer-limit pubsub 32mb 8mb 60
# Redis server执行后台任务的频率（次数/秒）
hz 10
dynamic-hz yes
aof-rewrite-incremental-fsync yes
rdb-save-incremental-fsync yes
```
