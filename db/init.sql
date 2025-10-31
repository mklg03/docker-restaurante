CREATE TABLE orders (
    id SERIAL PRIMARY KEY,
    item VARCHAR(255),
    status VARCHAR(100)
);

CREATE TABLE deliveries (
    id SERIAL PRIMARY KEY,
    customer VARCHAR(255),
    address VARCHAR(255),
    item VARCHAR(255),
    status VARCHAR(100)
);
