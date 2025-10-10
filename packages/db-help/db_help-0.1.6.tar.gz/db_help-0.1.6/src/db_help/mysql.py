import mysql.connector
from mysql.connector import Error
import os
from datetime import datetime
from dotenv import load_dotenv, find_dotenv
dotenv_path = find_dotenv()
load_dotenv(dotenv_path, override=True)

from db_help.log import Log
logger = Log.logger
editing_logger = logger.info

class MySQLManager:
    """
    一个用于与 MySQL 数据库交互的通用工具包。
    提供了连接管理、增删改查 (CRUD) 操作和错误处理。
    """

    def __init__(self, 
                 host=None, 
                 user=None, 
                 password=None, 
                 database=None, port=3306):
        """
        初始化数据库管理器。
        :param host: 数据库主机名或 IP 地址。
        :param user: 数据库用户名。
        :param password: 数据库密码。
        :param database: 默认数据库名称 (可选，如果只连接到服务器而不指定数据库)。
        :param port: 数据库端口 (默认为 3306)。
        """
        self.host = host or os.getenv("MySQL_DB_HOST")
        self.user = user or os.getenv("MySQL_DB_USER")
        self.password = password or os.getenv("MySQL_DB_PASSWORD")
        self.database = database or os.getenv("MySQL_DB_NAME")
        self.port = port
        self.connection = None

    def _connect(self):
        """
        建立数据库连接。
        """
        if self.connection is None or not self.connection.is_connected():
            try:
                self.connection = mysql.connector.connect(
                    host=self.host,
                    user=self.user,
                    password=self.password,
                    database=self.database,
                    port=self.port,
                )
                if self.connection.is_connected():
                    editing_logger(
                        f"成功连接到 MySQL 数据库: {self.database if self.database else self.host}"
                    )
                return self.connection
            except Error as e:
                logger.error(f"连接数据库时发生错误: {e}")
                self.connection = None
                return None
        return self.connection

    def close(self):
        """
        关闭数据库连接。
        """
        if self.connection and self.connection.is_connected():
            self.connection.close()
            editing_logger("数据库连接已关闭。")
            self.connection = None

    def execute_query(
        self, query, params=None, fetch_one=False, fetch_all=False, commit=False
    ):
        """
        执行 SQL 查询 (用于 SELECT, INSERT, UPDATE, DELETE, DDL)。
        :param query: 要执行的 SQL 查询字符串。
        :param params: 查询参数 (元组或列表)，用于参数化查询。
        :param fetch_one: 如果为 True，则获取单行结果 (用于 SELECT)。
        :param fetch_all: 如果为 True，则获取所有结果 (用于 SELECT)。
        :param commit: 如果为 True，则提交事务 (用于 INSERT, UPDATE, DELETE, DDL)。
        :return: 查询结果 (如果是 SELECT)，或 None。
        """
        conn = self._connect()
        if not conn:
            return None

        cursor = None
        result = None
        try:
            cursor = conn.cursor(
                dictionary=True
            )  # 使用 dictionary=True 返回字典形式的结果
            cursor.execute(query, params)

            if commit:
                conn.commit()
                editing_logger(f"Query committed. Affected rows: {cursor.rowcount}")
                result = (
                    cursor.lastrowid
                    if query.strip().upper().startswith("INSERT")
                    else cursor.rowcount
                )
            elif fetch_one:
                result = cursor.fetchone()
            elif fetch_all:
                result = cursor.fetchall()

        except Error as e:
            logger.error(f"执行查询时-发生错误: {e}")
            if conn:
                conn.rollback()  # 发生错误时回滚事务
            result = None
        finally:
            if cursor:
                cursor.close()
        return result

    # --- CRUD 操作封装 ---

    def create_database(self, db_name):
        """
        创建新的数据库。
        :param db_name: 要创建的数据库名称。
        :return: True 如果成功，False 如果失败。
        """
        # 注意：创建数据库时，需要连接到服务器但不能指定database参数
        # 所以这里需要一个临时的连接器或者修改self.database
        # 更安全的做法是，连接到一个默认的数据库（如'mysql'）来执行此操作
        # 或者在初始化时就不指定database
        temp_manager = MySQLManager(
            self.host, self.user, self.password, database=None, port=self.port
        )
        conn = temp_manager._connect()
        if not conn:
            return False

        cursor = None
        try:
            cursor = conn.cursor()
            query = f"CREATE DATABASE IF NOT EXISTS {db_name}"
            cursor.execute(query)
            conn.commit()
            editing_logger(f"数据库 '{db_name}' 已成功创建或已存在。")
            self.database = db_name  # 如果成功，更新当前管理器指向新数据库
            return True
        except Error as e:
            logger.error(f"创建数据库 '{db_name}' 时发生错误: {e}")
            return False
        finally:
            if cursor:
                cursor.close()
            if conn:
                temp_manager.close()  # 关闭临时连接

    def create_table(self, table_name, columns_definition):
        """
        创建表。
        :param table_name: 要创建的表名。
        :param columns_definition: 列定义字符串，例如 "id INT AUTO_INCREMENT PRIMARY KEY, name VARCHAR(255), age INT"。
        :return: True 如果成功，False 如果失败。
        """
        if not self.database:
            logger.error("错误：未指定数据库，无法创建表。")
            return False
        query = f"CREATE TABLE IF NOT EXISTS {table_name} ({columns_definition})"
        result = self.execute_query(query, commit=True)
        if result is not None:
            editing_logger(f"表 '{table_name}' 已成功创建或已存在。")
            return True
        return False

    def insert(self, table_name, data):
        """
        插入单条数据。
        :param table_name: 表名。
        :param data: 字典，键为列名，值为要插入的数据。
                     例如: {'name': 'Alice', 'age': 30, 'email': 'alice@example.com'}
        :return: 新插入记录的 ID (如果表有自增主键)，否则返回 None。
        """
        if not data:
            logger.warning("错误：插入数据为空。")
            return None

        columns = ", ".join(data.keys())
        placeholders = ", ".join(["%s"] * len(data))
        query = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"
        params = tuple(data.values())

        last_row_id = self.execute_query(query, params=params, commit=True)
        if last_row_id is not None:
            editing_logger(f"数据已成功插入到 '{table_name}'，ID: {last_row_id}")
        return last_row_id

    def bulk_insert(self, table_name, columns, data_list):
        """
        批量插入数据。
        :param table_name: 表名。
        :param columns: 列名列表，例如 ['name', 'age', 'email']。
        :param data_list: 包含元组或列表的列表，每个元组/列表代表一行数据。
                          例如: [('Alice', 30, 'alice@example.com'), ('Bob', 25, 'bob@example.com')]
        :return: 影响的行数，或 None。
        """
        if not data_list:
            logger.warning("错误：批量插入数据为空。")
            return None

        cols_str = ", ".join(columns)
        placeholders = ", ".join(["%s"] * len(columns))
        query = f"INSERT INTO {table_name} ({cols_str}) VALUES ({placeholders})"

        conn = self._connect()
        if not conn:
            return None

        cursor = None
        try:
            cursor = conn.cursor()
            cursor.executemany(query, data_list)
            conn.commit()
            editing_logger(f"批量插入 {cursor.rowcount} 条数据到 '{table_name}'。")
            return cursor.rowcount
        except Error as e:
            editing_logger(f"批量插入数据时发生错误: {e}")
            conn.rollback()
            return None
        finally:
            if cursor:
                cursor.close()

    def select(
        self,
        table_name,
        columns="*",
        conditions=None,
        params=None,
        order_by=None,
        limit=None,
        fetch_all=True,
    ):
        """
        查询数据。
        :param table_name: 表名。
        :param columns: 要查询的列名，可以是字符串 "col1, col2" 或列表 ["col1", "col2"]，默认为 "*"。
        :param conditions: WHERE 子句的条件字符串，例如 "age > %s AND name LIKE %s"。
        :param params: 条件对应的参数 (元组或列表)。
        :param order_by: ORDER BY 子句字符串，例如 "age DESC"。
        :param limit: LIMIT 子句整数，例如 10。
        :param fetch_all: 如果为 True，获取所有匹配的行；如果为 False，获取第一行。
        :return: 查询结果 (列表或字典)，或 None。
        """
        if isinstance(columns, list):
            columns = ", ".join(columns)

        query = f"SELECT {columns} FROM {table_name}"
        if conditions:
            query += f" WHERE {conditions}"
        if order_by:
            query += f" ORDER BY {order_by}"
        if limit is not None:
            query += f" LIMIT {limit}"

        result = self.execute_query(
            query, params=params, fetch_all=fetch_all, fetch_one=not fetch_all
        )
        return result


    def update(self, table_name, data, conditions, params=None):
        """
        更新数据。
        :param table_name: 表名。
        :param data: 字典，键为要更新的列名，值为新数据。
                     例如: {'age': 31, 'email': 'new_alice@example.com'}
        :param conditions: WHERE 子句的条件字符串，例如 "id = %s"。
        :param params: 条件对应的参数 (元组或列表)。
        :return: 影响的行数，或 None。
        """
        if not data:
            editing_logger("错误：更新数据为空。")
            return None
        if not conditions:
            editing_logger("错误：更新操作必须包含 WHERE 条件，以避免全表更新。")
            return None

        set_clauses = [f"{key} = %s" for key in data.keys()]
        set_str = ", ".join(set_clauses)

        query = f"UPDATE {table_name} SET {set_str} WHERE {conditions}"
        update_params = tuple(data.values())

        # 将更新参数和条件参数合并
        if params:
            final_params = update_params + tuple(params)
        else:
            final_params = update_params

        affected_rows = self.execute_query(query, params=final_params, commit=True)
        if affected_rows is not None:
            editing_logger(f"'{table_name}' 中 {affected_rows} 条数据已更新。")
        return affected_rows

    def delete(self, table_name, conditions, params=None):
        """
        删除数据。
        :param table_name: 表名。
        :param conditions: WHERE 子句的条件字符串，例如 "id = %s"。
        :param params: 条件对应的参数 (元组或列表)。
        :return: 影响的行数，或 None。
        """
        if not conditions:
            editing_logger("错误：删除操作必须包含 WHERE 条件，以避免全表删除。")
            return None

        query = f"DELETE FROM {table_name} WHERE {conditions}"
        affected_rows = self.execute_query(query, params=params, commit=True)
        if affected_rows is not None:
            editing_logger(f"'{table_name}' 中 {affected_rows} 条数据已删除。")
        return affected_rows



class MySQLManagerWithVersionControler(MySQLManager):

    def __init__(self, host=None, user=None, password=None, database=None, port=3306):
        super().__init__(host, user, password, database, port)
        """

        要求sql   首位 id int 自增
                 二位 name
                 包含 id name version 
        """
        #assert 特定要求的数据库
        self.select = ["name", "version", "timestamp", "prompt", "use_case"]

    def _search_by_version(self,target_name,target_version,table_name,
                          ):
        """
        1 有值  指定version => 指定
        有值 无指定version = > 最高
        无值, 有,无指定version => 无值
        """
        name_id = self.select[0]
        _select = ", ".join(self.select)
        base_query = f"""
            SELECT id, {_select}
            FROM {table_name}
            WHERE {name_id} = %s
        """
        params = [target_name] # 初始化参数列表

        if target_version is not None:
            # 如果指定了版本，添加版本条件
            query = f"{base_query} AND version = %s LIMIT 1"
            params.append(target_version)
        else:
            # 如果没有指定版本，获取最新版本
            query = f"{base_query} ORDER BY timestamp DESC, version DESC LIMIT 1"
            # 注意：这里params只需要target_name，因为ORDER BY和LIMIT不依赖额外的参数

        result = self.execute_query(query, params=tuple(params), fetch_one=True)
        return result

    def get_content_by_version(self,
                             target_name,
                             table_name,
                             target_version = None,
                             ) -> tuple[str, int]:
        
        """
        从sql获取提示词
        """
        result = self._search_by_version(
                target_name = target_name,
                target_version = target_version,
                table_name = table_name,
            )
        if not result:
            result = self._search_by_version(
                target_name = target_name,
                target_version = target_version,
                table_name = table_name,
            )
        return result

    def save_content(self,table_name,data):
        target_name = data['name']
        latest_version = self.get_content_by_version(
                             target_name,
                             table_name,
                             target_version = None)
        if latest_version:
            # 如果存在版本加1
            version_ori = latest_version.get("version")
            _, version = version_ori.split(".")
            version = int(version)
            version += 1
            version_ = f"1.{version}"
        else:
            # 如果不存在版本为1.0
            version_ = '1.0'
        data.update({"version":version_})
        self.insert(table_name, data)



        

    def search_by_time(self, start_time: datetime, end_time: datetime = None):
        """
        #TODO 
        根据时间范围获取指定内容。

        Args:
            start_time (datetime): 查询的起始时间。
            end_time (datetime, optional): 查询的结束时间。如果未提供，则只查询大于等于 start_time 的内容。

        Returns:
            list[dict] or None: 如果找到，返回包含 new_id, name, version, timestamp, content 字段的字典列表；
                                否则返回 None。
        """
        table_name = "content"
        if end_time:
            query = f"""
                SELECT new_id, name, version, timestamp, content
                FROM {table_name}
                WHERE timestamp BETWEEN %s AND %s
                ORDER BY timestamp DESC
            """
            params = (start_time, end_time)
        else:
            query = f"""
                SELECT new_id, name, version, timestamp, content
                FROM {table_name}
                WHERE timestamp >= %s
                ORDER BY timestamp DESC
            """
            params = (start_time,)
        
        result = self.mysql.execute_query(query, params=params, fetch_one=False)
        if result:
            print(f"找到时间范围从 '{start_time}' 到 '{end_time or '现在'}' 的内容数据。")
        else:
            print(f"未找到时间范围从 '{start_time}' 到 '{end_time or '现在'}' 的内容数据。")
        return result