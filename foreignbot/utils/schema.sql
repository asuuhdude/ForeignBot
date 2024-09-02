CREATE TABLE IF NOT EXISTS users (
    user_id BIGINT PRIMARY KEY,
    xp INT DEFAULT 0,
    level INT DEFAULT 1,
    name TEXT,
    balance FLOAT DEFAULT 0,
    bank FLOAT DEFAULT 500,
    notis BOOLEAN
);

CREATE TABLE IF NOT EXISTS guilds (
    guild_id BIGINT PRIMARY KEY,
    name TEXT,
    prefix TEXT
);

CREATE TABLE IF NOT EXISTS general_data (
    creation_epoch DATE,
    ping INT,
    users INT,
    guilds INT,
    channels INT,
    version TEXT,
    ds_version INT
);

CREATE TABLE IF NOT EXISTS user_inventories (
    user_id BIGINT PRIMARY KEY,
    inventory TEXT,
    achievements TEXT
)