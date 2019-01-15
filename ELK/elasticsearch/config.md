## 重要
- es不能使用root运行  # 基于安全考虑，因为es可以接受用户输入的script并运行

## 节点配置
```
# 默认值
node.master: true
node.data: true
node.ingest: true
search.remote.connect: true # 只在配置专用ingest节点时改为false

## tribe node
The tribe node is deprecated in favour of Cross Cluster Search and will be removed in Elasticsearch 7.0.
```
#### Master节点(专用)
```
# 为防止脑裂，需要配置discovery.zen.minimum_master_nodes
node.master: true
node.data: false
node.ingest: false
```
#### Data节点(专用)
```
# 多CPU
# 大内存
# 尽量高速磁盘，提高IO，segment合并会消耗大量IO
node.master: false
node.data: true
node.ingest: false
```
#### Ingest节点(专用)
```
# 不是一定需要，根据具体使用场景，大部分情况下不用独立的ingest node，默认每个节点都是ingest
node.master: false
node.data: false
node.ingest: true
search.remote.connect: false # Disable cross-cluster search
```
#### Coordinating节点
```
# 接收查询请求，完成数据汇聚
# 需要大内存
node.master: false
node.data: false
node.ingest: false
```

## 基本配置
- cluster.name: xxxx # 集群名称，唯一值
- node.name: xxx-01 # 每个节点名称
- path.data: # 数据存储路径
- path.logs: # 日志存储路径
- http.port: # http端口
- transport.tcp.port: # 如不设置，则在9300-9400之间取未被占用的端口
- network.host: # 节点所在主机地址绑定
- index.store.type: niofs # 默认值是fs(自动选择)，但是会选择到mmapfs，建议直接设置niofs
- discovery.zen.ping.unicast.hosts: ["IP", "IP:PORT"] # 单播检测，只需配置master节点
- discovery.zen.minimum_master_nodes: 1(默认值) # (master_node_num / 2) + 1


## 其他配置
##### JVM 
- 单个节点的heap size应该<=主机的物理内存 * 50%
- -Xms = -Xmx
- -XX:HeapDumpPath=...
- -XX:ErrorFile=...

##### 操作系统配置
- 关闭swap，使用命令：swapoff -a
- bootstrap.memory_lock: true # 可能需要设置max locked memory为unlimited，否则启动失败
```
# ulimit -l unlimited
# 在/etc/security/limits.conf中设置memlock unlimited
```
- 修改文件打开数
```
# ulimit -n 65536
# 在/etc/security/limits.conf中设置nofile 65536
```
- 修改virtual memory，使用mmapfs时需要修改，否则会造成OOM
```
# sysctl -w vm.max_map_count=262144
# 在/etc/sysctl.conf中修改
```
- 修改最大线程数
```
# ulimit -u 4096
# 在/etc/security/limits.conf中设置nproc 4096
```

##### 和跨域访问相关
- http.cors.enabled: true
- http.cors.allow-origin: "*"
- http.cors.allow-methods: OPTIONS, HEAD, GET, POST, PUT, DELETE
- http.cors.allow-headers: Authorization, X-Requested-With, Content-Length, Content-Type
- http.cors.allow-credentials: true
- 单纯的数据节点可以关闭http.port，使用选项http.enabled: false


###### 其他
- bootstrap.system_call_filter: false # 关闭检查，默认打开，在上述系统配置无法修改时，可以关闭，保证es可以启动，生产环境尽量不要使用
- bootstrap.memory_lock: false # 需要和bootstrap.system_call_filter配合false
