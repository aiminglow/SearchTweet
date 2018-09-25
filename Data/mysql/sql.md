# create tables

当前问题：

1. 是否在插入时查重？
2. 使用自增数字作为主键还是tweet_id作为主键？
3. 使用哪种mysql引擎？

思考：

InnoDB 采用聚集索引，所以主键的索引在data域存储的是表的数据，而辅助索引的data域存储的是主键索引的值。所以使用辅助索引查询时，需要查询两次才能查到数据。

所以主索引不能太大，不然辅助索引的data域会变得很大，不利于存储更多的数据。

InnoDB的数据本身就是在索引上面，所以使用非单调的主键，在插入数据时，会频繁的因为维持B+Tree的平衡而插入到原来的数据中去，这样的插入效率非常低！所以，InnoDB使用自增主键非常重要。

关于外键：

对于InnoDB支持外键，保证了数据的一致性！也有利于说明各种数据中的业务逻辑。每次插入外键都会扫描他是否符合要求，所以安全性很高。

但是每次存储时，都会检验外键是否是否合格，这样会耗费很多时间。

所以，如果不是很注重数据的一致性，而是很看重数据插入和查询效率，最好使用MyISAM，如果需要限制，使用触发器。

MyISAM的主键是否需要自增：

MyISAM的索引的data域存储的是数据的地址，而不是数据，所以它不需要像InnoDB那样考虑使用自增主键来避免insert过程中需要平衡B+Tree而挪动数据的操作。所以说，MyISAM其实可以不用自增字段了？因为后面在去重的时候还是在使用tweet_id来进行去重。

__\*\*\*__一个关于数据挖掘或者NLP的问题：

数据挖掘工作或者训练NLP的AI时，是需要在数据库存储的文本中查找特定的关键字的那一条，然后取出来进行分析呢？还是说把所有数据一条一条取出来，都要进行处理呢？

如果说是需要先进行特定关键字的筛选的话，那么效率真的挺低的，在mysql中使用like匹配效率很低吧？（如果匹配的是文本的开头的话，那么是可以用到索引的）

mysql的memory存储是一种内存存储，只有这一种支持哈希索引。

数据去重：

[数据去重的方法也找到了](https://www.jianshu.com/p/74a85208f29f)

```mysql
DELETE FROM `table`
WHERE
`去重字段名` IN (
    SELECT x FROM
    (
        SELECT `去重字段名` AS x 
        FROM `table` 
        GROUP BY `去重字段名` 
        HAVING COUNT(`去重字段名`) > 1
    ) tmp0
)
AND 
`递增主键名` NOT IN (
    SELECT y FROM
    (
        SELECT min(`递增主键名`) AS y 
        FROM `table` 
        GROUP BY `去重字段名` 
        HAVING COUNT(`去重字段名`) > 1
    ) tmp1
)
```



### 数据库设计

1. 直接将所有关键字的记录存在一张表里面？然后用一个数字的字段代表关键字的ID？然后后面查询的时候也可以存储为索引？既然都要存储成索引了，那么干脆直接存储关键字就行了，也不用维护一个新的keyword表，并且在插入的时候维护他了！我的mysql表也用不了多少时间，就要换成hbase了，所以也存储不了多长数据！
2. 是否查重呢？不查重的话效率很高吧？特别是数据越来越多之后！查重的工作就留到以后再说吧！
3. 既然不查重，到时候导出是一个接一个到处，使用InnoDB+自增ID真的不错。





表设计：

table_name : searchtweet

time_schema: yyyyMMdd

sql:

```mysql
create table tweet_keywords_begintime_endtime (
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
```



| col           | type and length | description |
| ------------- | --------------- | ----------- |
| keywords      | varchar(50)     |             |
| tweet_id      |                 |             |
| url           |                 |             |
| datetime      |                 |             |
| text          |                 |             |
| user_id       |                 |             |
| usernameTweet |                 |             |
| nbr_retweet   |                 |             |
| nbr_favorite  |                 |             |
| nbr_reply     |                 |             |
| is_reply      |                 |             |
| is_retweet    |                 |             |
| images        |                 |             |
| sumfullcard   |                 |             |
| sumurl        |                 |             |
|               |                 |             |

table_name : tweetuser

sql:

```mysql
create table tweetuser(
id int(11) primary key not null auto_increment comment '主键，自增',
user_id varchar(25) not null comment '用户的唯一id',
name varchar(25) comment '用户发推时@后面显示的名字',
screen_name varchar(25) comment '用户发tweet时粗体显示的名字',
avatar varchar(80) comment '用户的头像url',
unique index `user_id_unique_index` (`user_id`) comment 'user_id的唯一索引，方便查重')
engine=InnoDB DEFAULT CHARSET=utf8mb4;
```



| col  | type and length | description |
| ---- | --------------- | ----------- |
|      |                 |             |



table_name : taskqueue

```mysql
create table taskqueue (
id int(5) primary key not null auto_increment comment 'auto increase',
keywords varchar(50) not null comment '查询关键字',
`table_name` varchar(30) not null comment '对应关键字的表名,表名结构：pretablename_begintime_endtime',
begintime timestamp default '2006-01-01 00:00:00' comment '查询的开始时间',
endtime timestamp default current_timestamp comment '查询的结束时间',
`now` timestamp default '2006-01-01 00:00:00' comment '爬虫当前爬到了什么地方',
`status` int(3) not null default '-1' comment '本条任务状态：-1-未爬，0-已爬，但是now没有爬到endtime，1-已爬完，即now等于endtime，2-其他爬虫正在使用',
index `taskqueue_status_index` (`status`) comment '对任务状态做索引，方便查找')
engine=InnoDB DEFAULT CHARSET=utf8mb4;
```



| col       | type and length                            | description                                                  |
| --------- | ------------------------------------------ | ------------------------------------------------------------ |
| id        | int(5) auto_increment primary key not null |                                                              |
| keywords  | varchar(50) not null                       |                                                              |
| begintime | varchar(20)                                | default=2016-01-01                                           |
| endtime   | varchar(20)                                | default=2018-09-01                                           |
| now       | varchar(20)                                |                                                              |
| status    | int(3) not null                            | default=-1-未使用,0-使用了，但是没有查完，1-使用了并且查完了 |



关于数据库设计的再次思考：

1. 要提高效率就必须要用索引，不然就算插入的时候不查重，最终使用数据的时候，select要取数据的时候，要把MyISAM的表全部扫描一遍了！所以说**必须要有索引**。
2. 既然必须要有索引，那么在插入的时候进行查重，和数据全部插入完了以后进行查重，效率是一样的。
3. 如果按照查询关键词进行分表，那么一个表的数据不会特别多，B+Tree的深度不大，查重效率会很高，所以**可以进行查重**。
4. mysql的表名一定要自己起，不规范的表名会出现很多问题，爬虫会直接中断。
5. searchtweet表的keywords字段还要加时间区间吗？还是**要有时间区间的**，有的话题可能会有很多tweet，必须要设置时间限制，那么自己在定义表名称的时候应该有一个规范，**表名里面要加上开始时间和结束时间**。

结果：

1. tweet_keywords_begintime_endtime表，使用InnoDB，主键索引，添加keywords字段上面的辅助索引，自增id，
2. taskqueue表，InnoDB，主键索引，添加keywords上面的辅助索引，自增id
3. tweetuser表，InnoDB，主键索引，添加user_id上面的辅助索引，user表就这一个