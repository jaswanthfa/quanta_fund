from sqlalchemy import create_engine, text

# Database Configuration
DATABASE_URL = "postgresql://postgres:example@localhost:5432/postgres"

# Create SQLAlchemy engine
engine = create_engine(DATABASE_URL)

# Test Connection and Query
try:
    with engine.connect() as connection:
        print("Connection successful!")
        # Run a basic query
        result = connection.execute(text("SELECT * FROM filings WHERE LOWER(filer_name) = 'berkshire hathaway inc'"))
        for row in result:
            print(row)
except Exception as e:
    print(f"Error connecting to the database: {e}")