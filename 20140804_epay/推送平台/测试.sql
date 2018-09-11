
SELECT * FROM TRANSFER ORDER BY ID

SELECT * FROM TRANSFER WHERE LASTSTATUS = 0
BEGIN
FOR x IN 21..100 LOOP 
	INSERT INTO TRANSFER VALUES (x,'20170110',to_char(x)||'.txt','20170110 08:00:00',
	'sftp','192.168.8.42','nagios','pp85iQTu&','/home/nagios/wobaifu',
	'sftp','192.168.8.41','nagios','pp85iQTu&','/home/nagios/2b',
	0,0,'/app/testftp/platform/storFiles/20170110/'||to_char(x)
	);
END LOOP ;
END;


UPDATE TRANSFER SET LASTSTATUS = 0, exec_times = 0;
COMMIT;



DELETE FROM TRANSFER WHERE ID > 20
COMMIT


UPDATE TRANSFER SET FROMDIR = '/home/nagios/wobaifu' WHERE fromdir = '/home/nagios/wobaidu'