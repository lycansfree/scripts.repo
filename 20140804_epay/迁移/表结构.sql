-- 登记表
create table dbinfo (
	id int not null auto_increment,
	ip varchar(15) not null,
	dbname varchar(10) not null,
	-- operate是操作
	-- 0:不操作,1:更新,2:回退
	operate int not null default 0,
	-- 记录上一次的操作
	lastoperate int not null default 0,
	lastoutput varchar(100),
	lasttime varchar(14),
	-- 备注
	bakcomm varchar(50),
	-- 所有应用账号默认develop组
	-- username varchar(50) not null,
	-- filetype 是文件类型
	-- uncompress:只是文件,compress:修改的是war或jar包内文件
	-- filetype varchar(20) not null,
	filedir varchar(100) not null,
	filename varchar(50) not null,
	pfile varchar(100),
	primary key (id)
);

-- 插入示例
INSERT INTO dbinfo VALUES (1,'192.168.11.211','zfacc',0,0,'','','测试','wzf','compress','/app/wzf/linshi','FinanceZoneService.war','WEB-INF/classes/jdbc.properties');
INSERT INTO dbinfo (ip,dbname,filedir,filename,pfile) VALUES 
('192.168.11.211','zfacc','/app/wzf/linshi/FinanceZoneService/WEB-INF/classes','jdbc.properties','');


-- 对照信息表
create table contrast_info (
	dictname varchar(20) not null,
	dictkey varchar(20) not null,
	dictvalue varchar(100) not null,
	primary key (dictname,dictkey)
);

-- 插入示例

INSERT INTO contrast_info VALUES ('SERVICEON','skmsyq','srvkey');
INSERT INTO contrast_info VALUES ('SERVICEON','bcmc','srvcif');
INSERT INTO contrast_info VALUES ('SERVICEON','zfpay','srvpay');
INSERT INTO contrast_info VALUES ('SERVICEON','zfacc','srvacc');
INSERT INTO contrast_info VALUES ('SERVICEON','zfoms','srvoms');
INSERT INTO contrast_info VALUES ('SERVICEON','zfcif','srvcif');
INSERT INTO contrast_info VALUES ('SERVICEON','zfact','srvact');



-- 健康表
create table healthy (
	ip varchar(15) not null,
	lastacc varchar(14) not null,
	primary key (ip)
);