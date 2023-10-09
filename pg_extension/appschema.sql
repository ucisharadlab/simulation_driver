CREATE TABLE care_facility (
    id SERIAL PRIMARY KEY,
    name VARCHAR(250),
    location TEXT,
    max_occupancy INTEGER
);

CREATE TABLE person (
    id SERIAL PRIMARY KEY,
    name VARCHAR(250),
    birthdate date,
    lives_at INTEGER
);

CREATE TABLE disease (
    id SERIAL PRIMARY KEY,
    name VARCHAR(250),
    affected_organ text
);

CREATE TABLE hospital (
    id SERIAL PRIMARY KEY,
    name VARCHAR(250),
    max_occupancy INTEGER
);

CREATE TABLE pollutant_spread (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP,
    location text,
    name VARCHAR(250),
    concentration FLOAT
);

CREATE TABLE admission (
    hospital_id INTEGER,
    person_id INTEGER,
    start_time TIMESTAMP,
    end_time TIMESTAMP
);

CREATE TABLE sickness (
    disease_id INTEGER,
    person_id INTEGER,
    start_time TIMESTAMP,
    end_time TIMESTAMP
);

create table hysplit_test_data (
	parameters TEXT,
	cost DECIMAL,
	quality DECIMAL
);

