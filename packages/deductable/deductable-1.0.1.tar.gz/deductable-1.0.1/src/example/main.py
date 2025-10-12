from typing import Optional
from loguru import logger

import duckdb
from deductable.core import Deductable


with duckdb.connect(':memory:') as con:
    # Create sequence and table
    con.execute("CREATE SEQUENCE IF NOT EXISTS animal_id_seq START 1")
    con.execute("""
                CREATE TABLE IF NOT EXISTS animals
                (
                    id      INTEGER PRIMARY KEY DEFAULT nextval('animal_id_seq'),
                    species VARCHAR
                )
                """)
    con.execute("""
                INSERT INTO animals (species)
                VALUES ('Cow'),
                       ('Pig'),
                       ('Chicken'),
                       ('Sheep'),
                       ('Goat'),
                       ('Horse'),
                       ('Duck'),
                       ('Turkey')
                """)

    dt = Deductable(con, table_name="animals", )

    @dt.column
    def weight(species: str) -> Optional[float]:
        logger.info(f"Calculating weight for {species}")
        return {"Cow": 700, "Cat": 6.2, "Dog": 20.5, "Horse": 30000}.get(species, None)

    dt.materialize()
    print(dt.df())

