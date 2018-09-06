-- 查询最大连接数配置
show variables like 'max_connections';
select * from information_schema.global_variables where variable_name = 'max_connections';
-- 查看 查询语句的数量
select count(1) from INFORMATION_SCHEMA.PROCESSLIST where command = 'Query';
