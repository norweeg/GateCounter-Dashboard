create table if not exists PIRSTATS (
datetime DATETIME not NULL,
gatecount INT,
PRIMARY KEY (datetime)
);

create table if not exists ULTRASTATS (
datetime DATETIME not NULL,
gatecount INT,
PRIMARY KEY (datetime)
);

create table if not exists LDRSTATS (
datetime DATETIME not NULL,
gatecount INT,
PRIMARY KEY (datetime)
);