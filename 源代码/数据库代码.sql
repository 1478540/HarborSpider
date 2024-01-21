use Port_information;
show tables;
set SQL_safe_updates=0;

create table Basic_information(
Port_Code varchar(10) primary key,
City varchar(100),
Port_Chinese varchar(100),
Port_English varchar(100),
Country varchar(100),
Region varchar(100),
Route_Chinese varchar(100),
Route_English varchar(100),
Anchorage varchar(100),
Type varchar(50)
);

create table Port_Introduce(
Port_Code varchar(10),
introduce TEXT,
foreign key(Port_Code) references Basic_information(Port_Code)
);

create table City_Coordinates(
City_name varchar(100) primary key,
Latitude double,
longitude double
);

create view Coordinate_view as
select Basic_information.Port_Chinese,City_Coordinates.City_name,City_Coordinates.Latitude,City_Coordinates.Longitude,Basic_information.Port_Code 
from Basic_information join City_Coordinates on Basic_information.City like concat('%',City_Coordinates.City_name,'%');


desc Basic_information;
desc Port_Introduce;
desc City_Coordinates;

select * from Basic_information;
select * from Port_Introduce;

delete from Basic_information;
delete from Port_Introduce;
delete from City_Coordinates;

select * from City_Coordinates;
select * from Basic_information where Region="东南亚";
select * from Port_Introduce where port_Code="KRKPO";

SELECT SUM(data_length + index_length)
FROM information_schema.TABLES
WHERE table_schema = 'port_information';

select distinct City from Basic_information;

select * from Basic_information natural join Port_Introduce;


select * from Coordinate_view where Port_Code="AuALH";


show tables;
select * from basic_information;