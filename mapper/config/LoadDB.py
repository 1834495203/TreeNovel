import os
from pathlib import Path

from dotenv import load_dotenv
from neomodel import config
from peewee import SqliteDatabase


def load_neo4j_config():
    """
    加载neo数据库
    :return:
    """
    load_dotenv()
    username = os.getenv('NEO4J_USERNAME')
    password = os.getenv('NEO4J_PASSWORD')
    host = os.getenv('NEO4J_HOST')
    port = os.getenv('NEO4J_PORT')

    # 格式化数据库连接 URL
    config.DATABASE_URL = f'bolt://{username}:{password}@{host}:{port}'
    config.ENCRYPTED = False


def load_sqlite_config():
    load_dotenv()
    # relative_path = Path("../")
    # absolute_path = relative_path.resolve()

    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    DB_PATH = os.path.join(BASE_DIR, os.getenv('SQLITE_URL'))
    return SqliteDatabase(DB_PATH, pragmas={'foreign_keys': 1})


if __name__ == '__main__':
    pass
