import time
from typing import List, Dict

from pydantic import BaseModel, Field

try:
    import pymysql
    from pymysql import OperationalError
except ImportError:
    raise ValueError("pymysql is not installed. Please install it with `poetry add pymysql`")

try:
    from dbutils.pooled_db import PooledDB
except ImportError:
    raise ValueError("dbutils is not installed. Please install it with `poetry add dbutils`")
from loguru import logger


class MysqlConf(BaseModel):
    host: str = Field(default="localhost", description="mysql ip地址")
    port: int = Field(default=3306, description="端口号")
    user: str = Field(default="root", description="用户名")
    password: str = Field(default="root", description="密码")
    db: str = Field(description="schema名")


class MysqlComponent:
    __instance = None
    config: Dict = None

    def __init__(self, config: Dict):
        self.config = config
        db_config = {
            **self.config,
            'creator': pymysql,
            'maxconnections': 10,  # 连接池最大连接数量
            'cursorclass': pymysql.cursors.DictCursor
        }
        self.pool = PooledDB(**db_config)
        wait_for_llm_db(self.pool)

    @classmethod
    def from_conf(cls, conf: MysqlConf):
        return cls(conf.model_dump())

    def get_connection(self):
        conn = self.pool.connection()
        cursor = conn.cursor()
        return conn, cursor

    def insert(self, sql, value) -> bool:
        """
        插入数据库
        """
        conn, cursor = self.get_connection()
        try:
            cursor.execute(sql, value)
            conn.commit()
            return True
        except Exception as e:
            logger.exception(e)
            return False
        finally:
            cursor.close()
            conn.close()

    def insert_batch(self, sql: str, data: List[Dict]) -> bool:
        """
            批量插入数据库
        """
        conn, cursor = self.get_connection()
        try:
            cursor.executemany(sql, data)
            conn.commit()
            return True
        except Exception as e:
            logger.exception(e)
            return False
        finally:
            cursor.close()
            conn.close()

    def update(self, sql):
        """
        更新数据库
        """
        conn, cursor = self.get_connection()
        try:
            cursor.execute(sql)
            conn.commit()
            return 1
        except Exception as e:
            logger.exception(e)
            return 0
        finally:
            cursor.close()
            conn.close()

    def delete(self, sql, values) -> bool:
        """
        执行删除语句
        """
        conn, cursor = self.get_connection()
        try:
            cursor.execute(sql, values)
            conn.commit()
            return True
        except Exception as e:
            logger.exception(e)
            return False
        finally:
            cursor.close()
            conn.close()

    def fetch(self, sql):
        """
        查询数据库
        """
        conn, cursor = self.get_connection()
        try:
            cursor.execute(sql)
            info = cursor.fetchall()
            return info
        except Exception as e:
            logger.exception(e)
            return None
        finally:
            cursor.close()
            conn.close()

    def fetch_condition(self, sql: str, values):
        """
        根据条件获取结果
        :param sql:
        :param values:
        :return:
        """
        conn, cursor = self.get_connection()
        try:
            with cursor:
                # 执行查询语句
                cursor.execute(sql, values)
                # 获取结果
                result = cursor.fetchall()
                # 处理结果
                return result
        finally:
            conn.close()

    def close(self):
        self.pool.close()

    def fetch_one_condition(self, sql: str, values):
        """
        根据条件查询，只有一个结果
        :param sql:
        :param values:
        :return:
        """
        conn, cursor = self.get_connection()
        try:
            with cursor:
                # 执行查询语句
                cursor.execute(sql, values)
                # 获取结果
                result = cursor.fetchone()
                # 处理结果
                return result
        finally:
            conn.close()


def wait_for_llm_db(pool, max_attempts=10, retry_interval=30):
    attempts = 0
    while attempts < max_attempts:
        try:
            conn = pool.connection()
            conn.close()
            logger.info("连接数据库成功")
            break
        except OperationalError:
            attempts += 1
            time.sleep(retry_interval)
            logger.warning("第{}次尝试连接数据库", attempts)
    else:
        raise Exception(f"Failed to connect to llm-db after {max_attempts} attempts")
