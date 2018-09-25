create table nasdaqlisted(
    symbol varchar(10) primary key not null,
    security_name varchar(200),
    market_category varchar(2),
    test_issue varchar(2),
    financial_status varchar(2),
    round_lot_size varchar(5),
	ETF varchar(2),
	nextshares varchar(2))
    engine=InnoDB DEFAULT CHARSET=utf8;
    
create table otherlisted(
    act_symbol varchar(10) primary key not null,
    security_name varchar(300),
    `exchange` varchar(2),
    cqs_symbol varchar(10),
    ETF varchar(2),
    round_lot_size varchar(5),
	test_issue varchar(2),
	nasdaq_symbol varchar(10))
    engine=InnoDB DEFAULT CHARSET=utf8;
    
SHOW GLOBAL VARIABLES LIKE 'local_infile';
SHOW VARIABLES LIKE 'local_infile';
SHOW VARIABLES LIKE "secure_file_priv";
SET @@global.sql_mode= 'NO_AUTO_CREATE_USER,NO_ENGINE_SUBSTITUTION';

SET @@global.sql_mode= '';
-- 'secure_file_priv', '/var/lib/mysql-files/'
-- load data infile
use spider_data;
SET GLOBAL local_infile = 1;
SET autocommit=0;
SET unique_checks=0;
SET foreign_key_checks=0;
load data infile '/var/lib/mysql-files/nasdaqlisted_h.txt' into table nasdaqlisted CHARACTER SET utf8 FIELDS TERMINATED BY '|' lines terminated by '\r\n';
load data infile '/var/lib/mysql-files/otherlisted_h.txt' into table otherlisted CHARACTER SET utf8 FIELDS TERMINATED BY '|' lines terminated by '\r\n';
SET foreign_key_checks=1;
SET unique_checks=1;
commit;