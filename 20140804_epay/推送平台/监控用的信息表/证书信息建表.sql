create table ca_info (
	ID number(3) primary key,
	caName varchar(50),
	endtime varchar(8),
	description varchar(50),
	checkflag number(1),
	rsField varchar(50)
);

comment on column ca_info.ID
is 'ID��,����';

comment on column ca_info.caName
is '֤����';

comment on column ca_info.endtime
is '������';

comment on column ca_info.description
is '��ע����';

comment on column ca_info.checkflag
is '����־:0-�����,1-���';

comment on column ca_info.rsField
is 'Ԥ���ֶ�';


