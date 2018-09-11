create table rec_file (
	host varchar(15) not null,
	
	ID number(3) primary key,
	caName varchar(50),
	endtime varchar(8),
	description varchar(50),
	checkflag number(1),
	rsField varchar(50)
);

comment on column rec_file.ID
is 'ID号,主键';

comment on column rec_file.caName
is '证书名';

comment on column rec_file.endtime
is '到期日';

comment on column rec_file.description
is '备注描述';

comment on column rec_file.checkflag
is '检查标志:0-不检查,1-检查';

comment on column rec_file.rsField
is '预留字段';

