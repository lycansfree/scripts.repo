--推送平台主体功能
--从from主机上拉取文件到本地
--再从本地推送文件到to主机
--本地创建以日期为目录结构的文本
--以ID为文件夹
--规划为2个python脚本
--initialize.py负责初始化当天数据，以及创建文件夹，并删除3天前
--transfer.py负责每天的传输工作，初步规划用5个线程同时传输
--master.py负责调度，根据任务量，决定启动多少个transfer.py进程

--创建register注册表
create table register (
	ID number(1),
	host varchar(15),
	port number(5),
	primary key(ID)
);

comment on column register.ID
is '主机ID,必须从0开始';

comment on column register.host
is '主机IP';

comment on column register.port
is '监听的端口';

--创建template的序列

CREATE SEQUENCE template_id
INCREMENT BY 1
START WITH 1
MAXVALUE 10000
NOCYCLE 
NOCACHE ;

--创建template表
create table template (
ID number(5),
fromtype varchar(4),
fromhost varchar(15),
fromuser varchar(20),
frompass varchar(50),
fromdir varchar(100),
totype varchar(4),
tohost varchar(15),
touser varchar(20),
topass varchar(50),
todir varchar(100),
filename varchar(50),
daytype varchar(20),
offset number(1),
transtamp varchar(8),
remark varchar(100),
primary key(ID)
);

--添加注释
comment on column template.ID
is '模板中每个文件的唯一标识,主键';

comment on column template.fromtype
is '拉取方式:ftp/sftp';

comment on column template.fromhost
is '拉取的主机地址';

comment on column template.fromuser
is '拉取的主机用户';

comment on column template.frompass
is '拉取的用户密码';

comment on column template.fromdir
is '拉取的文件路径';

comment on column template.totype
is '推送方式:ftp/sftp';

comment on column template.tohost
is '推送的主机地址';

comment on column template.touser
is '推送的主机用户';

comment on column template.topass
is '推送的用户密码';

comment on column template.todir
is '推送的文件路径';

comment on column template.filename
is '文件名模板';

comment on column template.daytype
is '文件名中日期模板:%Y%m%d等';

comment on column template.offset
is '文件名中日期偏移量';

comment on column template.transtamp
is '每日文件推送时间';

comment on column template.remark
is '推送文件的描述备注';

--创建执行表transfer
create table transfer (
ID number(5),
today varchar(8),
filename varchar(50),
transtamp varchar(17),
fromtype varchar(4),
fromhost varchar(15),
fromuser varchar(20),
frompass varchar(50),
fromdir varchar(100),
totype varchar(4),
tohost varchar(15),
touser varchar(20),
topass varchar(50),
todir varchar(100),
laststatus number(1),
exec_times number(1),
localdir varchar(100),
primary key(ID,today)
);

comment on column transfer.ID
is '执行表中文件ID,和today字段为联合主键';

comment on column transfer.today
is '当天日期';

comment on column transfer.filename
is '每天的文件名';

comment on column transfer.transtamp
is '当天文件推送时间';

comment on column transfer.fromtype
is '拉取方式:ftp/sftp';

comment on column transfer.fromhost
is '拉取的主机地址';

comment on column transfer.fromuser
is '拉取的主机用户';

comment on column transfer.frompass
is '拉取的用户密码';

comment on column transfer.fromdir
is '拉取的文件路径';

comment on column transfer.totype
is '推送方式:ftp/sftp';

comment on column transfer.tohost
is '推送的主机地址';

comment on column transfer.touser
is '推送的主机用户';

comment on column transfer.topass
is '推送的用户密码';

comment on column transfer.todir
is '推送的文件路径';

comment on column transfer.laststatus
is '上一次的执行状态:0-失败,1-成功';

comment on column transfer.exec_times
is '执行推送的次数:3次后状态仍失败的,不再执行推送';

comment on column transfer.localdir
is '本地存储路径，由basedir + today + ID组成';

--执行表transfer上laststatus和exec_times应该需要创建索引
create index laststatus_index on transfer(laststatus);
create index exec_times_index on transfer(exec_times);

commit;

