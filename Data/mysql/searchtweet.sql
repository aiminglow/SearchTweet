create table stockinfo (
id int(13) primary key not null auto_increment comment '主键，自增',
keywords varchar(50) not null comment '查询这条tweet时使用的关键词和时间区间的组合',
tweet_id char(20) not null comment 'tweet的唯一id',
url varchar(40) not null comment 'tweet对应的url的suf部分，twitter.com+url 即可访问对应的tweet',
`datetime` timestamp comment 'tweet发出时间',
`text` varchar(280) comment 'tweet文字内容',
user_id varchar(25) comment '本条tweet的用户id，对应tweet_user表里的主键。之后不会使用到联合查询，为了插入效率，不设置外键，减少插入过程的约束检查时间',
nbr_retweet int(6) comment '转发数',
nbr_favorite int(6) comment '点赞数',
nbr_reply int(6) comment '回复数',
is_reply boolean comment '本条tweet是不是一条回复',
is_retweet boolean comment '本条tweet是不是一条转发',
images varchar(120) comment '包含的图片的tweet的图片的url',
sumfullcard varchar(80) comment 'twitter.com将tweet中包含的summary card单独存成一个html，他们都有一个自己的url，这里存的是summary card的html的url，这个html包括summary card的标题，summary，图片，domain等信息',
sumurl varchar(80) comment '点击summary card跳转到的url',
unique index `tweet_id_unique_index` (`tweet_id`) comment 'tweet_id的唯一索引，用来查重')
engine=InnoDB DEFAULT CHARSET=utf8mb4;
