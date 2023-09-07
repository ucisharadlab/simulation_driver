CREATE TABLE care_facility (
    id SERIAL PRIMARY KEY,
    name VARCHAR(250),
    location TEXT,
    max_occupancy INTEGER
);

CREATE TABLE person (
    id SERIAL PRIMARY KEY,
    name VARCHAR(250),
    birthdate date
);

CREATE TABLE disease (
    id SERIAL PRIMARY KEY,
    name VARCHAR(250),
    affected_area text
);

CREATE TABLE hospital (
    id SERIAL PRIMARY KEY,
    name VARCHAR(250),
    max_occupancy INTEGER
);

CREATE TABLE pollutant_concentration (
    id SERIAL PRIMARY KEY,
    timestamp date,
    location text,
    name VARCHAR(250),
    concentration FLOAT
);

