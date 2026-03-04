create schema oltp;


create table oltp.deployments(
    id PRIMARY KEY,
    db_name VARCHAR(50),
    status BIT,
    username VARCHAR(50),
    creation_time TIMESTAMP
)