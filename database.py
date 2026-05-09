# from sqlalchemy import create_engine
# from sqlalchemy.orm import sessionmaker, declarative_base
# from dotenv import load_dotenv
# import os
# import logging

# logging.basicConfig(level=logging.INFO)
# logger = logging.getLogger(__name__)


# load_dotenv()

# DATABASE_URL = os.getenv("DATABASE_URL")

# try:
#     engine = create_engine(DATABASE_URL)

#     SessionLocal = sessionmaker(
#         autocommit=False,
#         autoflush=False,
#         bind=engine
#     )
#     Base = declarative_base()

#     logger.info("Database connection established sunceefully.")
# except  Exception as e:
#     logger.error(f"Error connecting to database: {e}")

# def get_db():
#     db = SessionLocal()
#     logger.debug("Database session opened")
#     try:
#         yield db
#     finally:
#         db.close()
#         logger.debug("Databse session closed")


from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv
import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

# ── Guard: fail immediately with a clear message if .env is missing ────────────
if not DATABASE_URL:
    raise RuntimeError(
        "DATABASE_URL is not set. "
        "Make sure your .env file exists in the same folder as database.py "
        "and contains: DATABASE_URL=postgresql://user:password@localhost:5432/dbname"
    )

# ── These are defined at module level so imports always succeed ────────────────
Base = declarative_base()

try:
    engine = create_engine(DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    logger.info("✅ Database connection established successfully.")
except Exception as e:
    logger.error(f"❌ Error connecting to database: {e}")
    raise  # re-raise so the app doesn't start in a broken state


def get_db():
    db = SessionLocal()
    logger.debug("Database session opened")
    try:
        yield db
    finally:
        db.close()
        logger.debug("Database session closed")

