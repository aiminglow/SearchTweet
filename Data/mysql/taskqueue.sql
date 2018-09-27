create table taskqueue (
id int(5) primary key not null auto_increment comment 'auto increase',
keywords varchar(50) not null comment '查询关键字',
`table_name` varchar(30) not null comment '对应关键字的表名,表名结构：pretablename_begintime_endtime',
begintime timestamp default '2006-01-01 00:00:00' comment '查询的开始时间',
endtime timestamp default current_timestamp comment '查询的结束时间',
`now` timestamp default '1980-01-01 00:00:00' comment '爬虫当前爬到了什么地方',
`status` int(3) not null default '-1' comment '本条任务状态：-1-未爬，0-已爬，但是now没有爬到endtime，1-已爬完，即now等于endtime，2-其他爬虫正在使用',
index `taskqueue_status_index` (`status`) comment '对任务状态做索引，方便查找')
engine=InnoDB DEFAULT CHARSET=utf8mb4;