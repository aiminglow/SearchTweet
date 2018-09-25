show databases;

use spider_data;
select * from taskqueue;

insert into taskqueue(keywords,`table_name`) values("JPM","JPM_20060101");
commit;

-- 查询没有被search完!=1&没有正在被使用的!=2 的keyword来使用。
select id,keywords,`table_name`,begintime,endtime,`now`,`status`
from taskqueue
where id=(select min(id) from taskqueue where status!=1 and status!=2);

select min(id) from taskqueue where status!=1 and status!=2;

-- 使用之前将状态置为2：正在使用。起到锁的作用
update taskqueue
set status=2
where id=#id#

-- 使用完成后更新状态字段为1：使用完了。
update taskqueue
set status=1
where id=#id#

-- 如果进行手动停止，那么要把now时间写入，把状态写成0：使用了，但是没有查完
update taskqueue
set status=0,now=#nowdate#
where id=#id#;
;

SELECT table_name FROM information_schema.TABLES WHERE table_name ='taskqueue';

use spider_data;
-- insert form nasdaqlisted and otherlisted
insert into taskqueue(keywords,`table_name`) select symbol,"STOCK_SYMBOL_20060101" from spider_data.nasdaqlisted;
insert into taskqueue(keywords,`table_name`) select nasdaq_symbol,"STOCK_SYMBOL_20060101" from spider_data.otherlisted;
commit;




