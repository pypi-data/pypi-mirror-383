import pytest
from db_help.mysql import MySQLManager, MySQLManagerWithVersionControler
from dotenv import load_dotenv
import os
from datetime import datetime

load_dotenv()

table_name = os.environ.get("MySQL_DB_Table_Name")

class Test_MySQLManager():

    @pytest.fixture
    def db_manager(self):
        return MySQLManager(
            host = os.environ.get("MySQL_DB_HOST"),
            user = os.environ.get("MySQL_DB_USER"),
            password = os.environ.get("MySQL_DB_PASSWORD"),
            database =  os.environ.get("MySQL_DB_NAME"),
        )
        

    def test_create_table(self,db_manager):
        """

        """
        # db_manager_no_db = MySQLManager(DB_HOST, DB_USER, DB_PASSWORD)
        # db_manager_no_db.create_database(DB_NAME)
        table_name = "prompts_data"
        columns_def = """
            id INT AUTO_INCREMENT PRIMARY KEY,
            prompt_id VARCHAR(255) NOT NULL,
            version VARCHAR(50) NOT NULL,
            timestamp DATETIME NOT NULL,
            prompt TEXT NOT NULL,
            UNIQUE (prompt_id, version) -- 复合唯一索引定义在这里
        """
        db_manager.create_table(table_name, columns_def)
        db_manager.close()

    def test_insert(self,db_manager):
        table_name = "prompts_data"
        user1_id = db_manager.insert(table_name, {'prompt_id': '1234134', 'version': '1.0', 'timestamp': datetime.now(),"prompt":"你好"})
        user2_id = db_manager.insert(table_name, {'prompt_id': '2345234234', 'version': '1.0', 'timestamp': datetime.now(),"prompt":"你好22"})
        user3_id = db_manager.insert(table_name, {'prompt_id': '3456653456', 'version': '1.0', 'timestamp': datetime.now(),"prompt":"你好33"})
        user3_id = db_manager.insert(table_name, {'prompt_id': '34566534562', 'version': '1.1', 'timestamp': datetime.now(),"prompt":"你好33545"})
        user3_id = db_manager.insert(table_name, {'prompt_id': '34566534562', 'version': '1.2', 'timestamp': datetime.now(),"prompt":"你好3354523"})
        db_manager.close()

    def test_bulk_insert(self,db_manager):
        # # 批量插入
        bulk_data = [
            ('2345234234', '1.0', datetime.now(),"你好22"),
            ('2345234234', '1.1', datetime.now(),"你好2s")
        ]
        db_manager.bulk_insert(table_name, ['prompt_id', 'version', 'timestamp','prompt'], bulk_data)
        db_manager.close()

    def test_search_all(self,db_manager):
        table_name = "prompts_data"

        all_users = db_manager.select(table_name, fetch_all=True)

        if all_users:
            for user in all_users:
                print(user)
        db_manager.close()

    def test_search_1(self,db_manager):
        table_name = "prompts_data"

        older_users = db_manager.select(table_name, conditions="age > %s", params=(30,), order_by="age DESC")
        if older_users:
            for user in older_users:
                print(user)
 
        print("\n--- 查询 ID 为 1 的用户 ---")
        user_by_id_1 = db_manager.select(table_name, conditions="id = %s", params=(1,), fetch_all=False)
        if user_by_id_1:
            print(user_by_id_1)

        db_manager.close()

    def test_update(self,db_manager):
        db_manager.update(table_name, {'age': 31, 'name': 'Alice Smith'}, conditions="id = %s", params=(user1_id,))


class Test_MySQLManagerWithVersionControler():
    @pytest.fixture
    def db_manager(self):
        return MySQLManagerWithVersionControler(
            host = os.environ.get("MySQL_DB_HOST"),
            user = os.environ.get("MySQL_DB_USER"),
            password = os.environ.get("MySQL_DB_PASSWORD"),
            database =  os.environ.get("MySQL_DB_NAME"),
        )
    
    def test_get_content(self,db_manager):
        result =db_manager.get_content_by_version(
            target_name = "db_help_test_001",
            table_name = "test",
        )
        print(result,'result')
        db_manager.close()

    def test_save_content(self,db_manager):
        result =db_manager.save_content(
            table_name = "test",
            data = {'name': "db_help_test_001", 
                    'timestamp': datetime.now(),
                    "prompt":"你好33545"}
        )
        print(result,'result')
        db_manager.close()