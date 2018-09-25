create table tweetuser(
id int(11) primary key not null auto_increment comment '主键，自增',
user_id varchar(25) not null comment '用户的唯一id',
name varchar(25) comment '用户发推时@后面显示的名字',
screen_name varchar(25) comment '用户发tweet时粗体显示的名字',
avatar varchar(80) comment '用户的头像url',
unique index `user_id_unique_index` (`user_id`) comment 'user_id的唯一索引，方便查重')
engine=InnoDB DEFAULT CHARSET=utf8mb4;


insert into tweetuser(user_id,`name`,screen_name,avator) 
value(%s,%s,%s,%s);