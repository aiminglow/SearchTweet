use spider_data;

insert into taskqueue(keywords)
select concat('$', symbol) from nasdaqlisted;

insert into taskqueue(keywords)
select concat('$', act_symbol) from otherlisted;

commit;