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
is 'ID��,����';

comment on column rec_file.caName
is '֤����';

comment on column rec_file.endtime
is '������';

comment on column rec_file.description
is '��ע����';

comment on column rec_file.checkflag
is '����־:0-�����,1-���';

comment on column rec_file.rsField
is 'Ԥ���ֶ�';

