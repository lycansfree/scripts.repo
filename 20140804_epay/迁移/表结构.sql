-- �ǼǱ�
create table dbinfo (
	id int not null auto_increment,
	ip varchar(15) not null,
	dbname varchar(10) not null,
	-- operate�ǲ���
	-- 0:������,1:����,2:����
	operate int not null default 0,
	-- ��¼��һ�εĲ���
	lastoperate int not null default 0,
	lastoutput varchar(100),
	lasttime varchar(14),
	-- ��ע
	bakcomm varchar(50),
	-- ����Ӧ���˺�Ĭ��develop��
	-- username varchar(50) not null,
	-- filetype ���ļ�����
	-- uncompress:ֻ���ļ�,compress:�޸ĵ���war��jar�����ļ�
	-- filetype varchar(20) not null,
	filedir varchar(100) not null,
	filename varchar(50) not null,
	pfile varchar(100),
	primary key (id)
);

-- ����ʾ��
INSERT INTO dbinfo VALUES (1,'192.168.11.211','zfacc',0,0,'','','����','wzf','compress','/app/wzf/linshi','FinanceZoneService.war','WEB-INF/classes/jdbc.properties');
INSERT INTO dbinfo (ip,dbname,filedir,filename,pfile) VALUES 
('192.168.11.211','zfacc','/app/wzf/linshi/FinanceZoneService/WEB-INF/classes','jdbc.properties','');


-- ������Ϣ��
create table contrast_info (
	dictname varchar(20) not null,
	dictkey varchar(20) not null,
	dictvalue varchar(100) not null,
	primary key (dictname,dictkey)
);

-- ����ʾ��

INSERT INTO contrast_info VALUES ('SERVICEON','skmsyq','srvkey');
INSERT INTO contrast_info VALUES ('SERVICEON','bcmc','srvcif');
INSERT INTO contrast_info VALUES ('SERVICEON','zfpay','srvpay');
INSERT INTO contrast_info VALUES ('SERVICEON','zfacc','srvacc');
INSERT INTO contrast_info VALUES ('SERVICEON','zfoms','srvoms');
INSERT INTO contrast_info VALUES ('SERVICEON','zfcif','srvcif');
INSERT INTO contrast_info VALUES ('SERVICEON','zfact','srvact');



-- ������
create table healthy (
	ip varchar(15) not null,
	lastacc varchar(14) not null,
	primary key (ip)
);