create database photocalorie;
use photocalorie;
create table user(username char(50),password char(150), name char(100));
create table consumption( username char(50) not null, fooditem char(50), calories float, fats float, carbohydrates float, proteins float, date date);
create table chat(username char(50), query text, reply text);
insert into user("saurabhrathi12","qwerty123","Saurabh");