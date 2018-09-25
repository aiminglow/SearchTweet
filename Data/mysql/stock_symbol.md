#### NASDAQ

| **File Name:**     | nasdaqlisted.txt                                             |
| ------------------ | ------------------------------------------------------------ |
| **FTP Directory:** | [ftp://ftp.nasdaqtrader.com/symboldirectory](ftp://ftp.nasdaqtrader.com/symboldirectory/) |

| **Field Name**      | **Definition**                                               |
| ------------------- | ------------------------------------------------------------ |
| Symbol              | The one to four or five character identifier for each NASDAQ-listed security. |
| Security Name       | Company issuing the security.                                |
| Market Category     | The category assigned to the issue by NASDAQ based on Listing Requirements. Values:Q = NASDAQ Global Select MarketSMG = NASDAQ Global MarketSMS = NASDAQ Capital Market |
| Test Issue          | Indicates whether or not the security is a test security. Values: Y = yes, it is a test issue. N = no, it is **not** a test issue. |
| Financial Status    | Indicates when an issuer has failed to submit its regulatory filings on a timely basis, has failed to meet NASDAQ's continuing listing standards, and/or has filed for bankruptcy. Values include:D = Deficient: Issuer Failed to Meet NASDAQ Continued Listing RequirementsE = Delinquent: Issuer Missed Regulatory Filing DeadlineQ = Bankrupt: Issuer Has Filed for BankruptcyN = Normal (Default): Issuer Is NOT Deficient, Delinquent, or Bankrupt.G = Deficient and BankruptH = Deficient and DelinquentJ = Delinquent and BankruptK = Deficient, Delinquent, and Bankrupt |
| Round Lot           | Indicates the number of shares that make up a round lot for the given security. |
| File Creation Time: | The last row of each Symbol Directory text file contains a timestamp that reports the File Creation Time. The file creation time is based on when NASDAQ Trader generates the file and can be used to determine the timeliness of the associated data. The row contains the words File Creation Time followed by mmddyyyyhhmm as the first field, followed by all delimiters to round out the row. An example: File Creation Time: 1217200717:03\|\|\|\|\| |

MYSQL:

分析：某个字段的值每一行都相同不建立索引。

其实只需要主键索引就够了，因为我们要这个表是以后抓到的某个symbol经常涉及某个话题，所以我们需要查一下这家公司叫什么名字。

HEAD:Symbol|Security Name|Market Category|Test Issue|Financial Status|Round Lot Size|ETF|NextShares

END:File Creation Time: 0911201808:15|||||||

vim

:%s/^/\"

:%s/$/\"

```mysql
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
    
-- load data infile
SHOW GLOBAL VARIABLES LIKE 'local_infile';
SHOW VARIABLES LIKE 'local_infile';
SHOW VARIABLES LIKE "secure_file_priv";
SET @@global.sql_mode= 'NO_AUTO_CREATE_USER,NO_ENGINE_SUBSTITUTION';
-- 'secure_file_priv', '/var/lib/mysql-files/'
-- load data infile
use spider_data;
SET GLOBAL local_infile = 1;
SET autocommit=0;
SET unique_checks=0;
SET foreign_key_checks=0;
load data infile '/var/lib/mysql-files/nasdaqlisted_h.txt' into table nasdaqlisted CHARACTER SET utf8 FIELDS TERMINATED BY '|' lines terminated by '\r\n';
SET foreign_key_checks=1;
SET unique_checks=1;
commit;
```







### other listed securities

| **File Name:**     | otherlisted.txt                                              |
| ------------------ | ------------------------------------------------------------ |
| **FTP Directory:** | [ftp://ftp.nasdaqtrader.com/symboldirectory](ftp://ftp.nasdaqtrader.com/symboldirectory/) |

| **Field Name**                                  | **Definition**                                               |
| ----------------------------------------------- | ------------------------------------------------------------ |
| ACT SymbolField Name Change effective 2/12/2010 | Identifier for each security used in [ACT](http://www.nasdaqtrader.com/Trader.aspx?id=ACT) and [CTCI connectivity protocol](http://www.nasdaqtrader.com/Trader.aspx?id=CTCI). Typical identifiers have 1-5 character root symbol and then 1-3 characters for suffixes. Allow up to 14 characters.More information regarding the symbology convention can be found on this [website](http://www.nasdaqtrader.com/trader.aspx?id=CQSsymbolconvention). |
| Security Name                                   | The name of the security including additional information, if applicable. Examples are security type (common stock, preferred stock, etc.) or class (class A or B, etc.). Allow up to 255 characters. |
| Exchange                                        | The listing stock exchange or market of a security.Allowed values are:A = NYSE MKTN = New York Stock Exchange (NYSE)P = NYSE ARCAZ = BATS Global Markets (BATS)V = Investors' Exchange, LLC (IEXG) |
| CQS Symbol                                      | Identifier of the security used to disseminate data via the SIAC Consolidated Quotation System (CQS) and Consolidated Tape System (CTS) data feeds. Typical identifiers have 1-5 character root symbol and then 1-3 characters for suffixes. Allow up to 14 characters.More information regarding the symbology convention can be found on this [website](http://www.nasdaqtrader.com/trader.aspx?id=CQSsymbolconvention). |
| ETF                                             | Identifies whether the security is an exchange traded fund (ETF). Possible values:Y = Yes, security is an ETFN = No, security is not an ETFFor new ETFs added to the file, the ETF field for the record will be updated to a value of "Y". |
| Round Lot Size                                  | Indicates the number of shares that make up a round lot for the given security. Allow up to 6 digits. |
| Test Issue                                      | Indicates whether the security is a test security.Y = Yes, it is a test issue.N = No, it is **not** a test issue. |
| NASDAQ SymbolNew field effective 2/12/2010      | Identifier of the security used to in various NASDAQ connectivity protocols and NASDAQ market data feeds. Typical identifiers have 1-5 character root symbol and then 1-3 characters for suffixes. Allow up to 14 characters.More information regarding the symbology convention can be found on this [website](http://www.nasdaqtrader.com/trader.aspx?id=CQSsymbolconvention) |
| File Creation Time:                             | The last row of each Symbol Directory text file contains a timestamp that reports the File Creation Time. The file creation time is based on when NASDAQ Trader generates the file and can be used to determine the timeliness of the associated data. The row contains the words File Creation Time followed by mmddyyyyhhmm as the first field, followed by all delimiters to round out the row. An example: File Creation Time: File Creation Time: 1217200717:03\|\|\|\|\|\| |

ACT Symbol|Security Name|Exchange|CQS Symbol|ETF|Round Lot Size|Test Issue|NASDAQ Symbol

ZYME|Zymeworks Inc. Common Shares|N|ZYME|N|100|N|ZYME

```mysql
create table otherlisted(
    act_symbol varchar(10) primary key not null,
    security_name varchar(200),
    `exchange` varchar(2),
    cqs_symbol varchar(10),
    ETF varchar(2),
    round_lot_size varchar(5),
	test_issue varchar(2),
	nasdaq_symbol varchar(10))
    engine=InnoDB DEFAULT CHARSET=utf8;
    
    
load data infile '/var/lib/mysql-files/otherlisted_h.txt' into table otherlisted CHARACTER SET utf8 FIELDS TERMINATED BY '|' lines terminated by '\r\n';
```

