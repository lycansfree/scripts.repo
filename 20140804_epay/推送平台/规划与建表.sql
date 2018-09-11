--����ƽ̨���幦��
--��from��������ȡ�ļ�������
--�ٴӱ��������ļ���to����
--���ش���������ΪĿ¼�ṹ���ı�
--��IDΪ�ļ���
--�滮Ϊ2��python�ű�
--initialize.py�����ʼ���������ݣ��Լ������ļ��У���ɾ��3��ǰ
--transfer.py����ÿ��Ĵ��乤���������滮��5���߳�ͬʱ����
--master.py������ȣ������������������������ٸ�transfer.py����

--����registerע���
create table register (
	ID number(1),
	host varchar(15),
	port number(5),
	primary key(ID)
);

comment on column register.ID
is '����ID,�����0��ʼ';

comment on column register.host
is '����IP';

comment on column register.port
is '�����Ķ˿�';

--����template������

CREATE SEQUENCE template_id
INCREMENT BY 1
START WITH 1
MAXVALUE 10000
NOCYCLE 
NOCACHE ;

--����template��
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

--���ע��
comment on column template.ID
is 'ģ����ÿ���ļ���Ψһ��ʶ,����';

comment on column template.fromtype
is '��ȡ��ʽ:ftp/sftp';

comment on column template.fromhost
is '��ȡ��������ַ';

comment on column template.fromuser
is '��ȡ�������û�';

comment on column template.frompass
is '��ȡ���û�����';

comment on column template.fromdir
is '��ȡ���ļ�·��';

comment on column template.totype
is '���ͷ�ʽ:ftp/sftp';

comment on column template.tohost
is '���͵�������ַ';

comment on column template.touser
is '���͵������û�';

comment on column template.topass
is '���͵��û�����';

comment on column template.todir
is '���͵��ļ�·��';

comment on column template.filename
is '�ļ���ģ��';

comment on column template.daytype
is '�ļ���������ģ��:%Y%m%d��';

comment on column template.offset
is '�ļ���������ƫ����';

comment on column template.transtamp
is 'ÿ���ļ�����ʱ��';

comment on column template.remark
is '�����ļ���������ע';

--����ִ�б�transfer
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
is 'ִ�б����ļ�ID,��today�ֶ�Ϊ��������';

comment on column transfer.today
is '��������';

comment on column transfer.filename
is 'ÿ����ļ���';

comment on column transfer.transtamp
is '�����ļ�����ʱ��';

comment on column transfer.fromtype
is '��ȡ��ʽ:ftp/sftp';

comment on column transfer.fromhost
is '��ȡ��������ַ';

comment on column transfer.fromuser
is '��ȡ�������û�';

comment on column transfer.frompass
is '��ȡ���û�����';

comment on column transfer.fromdir
is '��ȡ���ļ�·��';

comment on column transfer.totype
is '���ͷ�ʽ:ftp/sftp';

comment on column transfer.tohost
is '���͵�������ַ';

comment on column transfer.touser
is '���͵������û�';

comment on column transfer.topass
is '���͵��û�����';

comment on column transfer.todir
is '���͵��ļ�·��';

comment on column transfer.laststatus
is '��һ�ε�ִ��״̬:0-ʧ��,1-�ɹ�';

comment on column transfer.exec_times
is 'ִ�����͵Ĵ���:3�κ�״̬��ʧ�ܵ�,����ִ������';

comment on column transfer.localdir
is '���ش洢·������basedir + today + ID���';

--ִ�б�transfer��laststatus��exec_timesӦ����Ҫ��������
create index laststatus_index on transfer(laststatus);
create index exec_times_index on transfer(exec_times);

commit;

