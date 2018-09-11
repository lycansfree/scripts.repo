create table ca_info (
	ID number(3) primary key,
	caName varchar(50),
	endtime varchar(8),
	description varchar(50),
	checkflag number(1),
	rsField varchar(50)
);

comment on column ca_info.ID
is 'ID号,主键';

comment on column ca_info.caName
is '证书名';

comment on column ca_info.endtime
is '到期日';

comment on column ca_info.description
is '备注描述';

comment on column ca_info.checkflag
is '检查标志:0-不检查,1-检查';

comment on column ca_info.rsField
is '预留字段';


