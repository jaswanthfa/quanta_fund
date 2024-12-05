import psycopg2

# connect to database
try:
    conn = psycopg2.connect(
        host="localhost",
        database="postgres",
        user="postgres",  # default user is 'postgres' in the official PostgreSQL image
        password="example",
        port="5432"  # explicitly specify the port
    )
    print("Database connection successful")
except psycopg2.Error as e:
    print(f"Error connecting to database: {e}")
    exit(1)

def create_tables():
    try:
        # create a cursor
        cur = conn.cursor()

        # create tables
        create_table_commands = (
            """
            CREATE TABLE IF NOT EXISTS filings (
                filing_id varchar(255) PRIMARY KEY,
                cik bigint,
                filer_name varchar(255),
                period_of_report date
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS holdings (
                filing_id varchar(255),
                name_of_issuer varchar(255),
                cusip varchar(255),
                title_of_class varchar(255),
                value bigint,
                shares bigint,
                put_call varchar(255)
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS holding_infos (
                cusip varchar(255),
                security_name varchar(255),
                ticker varchar(50),
                exchange_code varchar(10),
                security_type varchar(50)
            )
            """
        )

        # create table one by one
        for command in create_table_commands:
            cur.execute(command)
        
        # make the changes to the database persistent
        conn.commit()
        print("Tables created successfully")
        
    except psycopg2.Error as e:
        print(f"Error creating tables: {e}")
        conn.rollback()
    finally:
        # close cursor
        cur.close()

if __name__ == "__main__":
    create_tables()
    conn.close()