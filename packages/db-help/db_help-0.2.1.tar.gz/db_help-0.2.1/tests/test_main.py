import pytest
import os
from datetime import datetime
from db_help.qdrant import QdrantManager
from dotenv import load_dotenv
load_dotenv()

table_name = os.environ.get("MySQL_DB_Table_Name")

class Test_Qdrant():

    @pytest.fixture
    def db_manager(self):
        return QdrantManager(
            host = "localhost",
        )
        

    def test_create_collection(self,db_manager):
        """
        """
        collection_name = "content"
        db_manager.create_collection(collection_name)


    def test_insert(self,db_manager):
        collection_name = "content"
        data = {
            "id": 974849725,
            "vector":[0.05, 0.15, 0.25, 0.35],
            "payload":{"name": "Eve", 'version': '1.0',
                       'timestamp': datetime.now(),
                        "content": "你好"}
        }
        user1_id = db_manager.insert(collection_name, data)


    def test_bulk_insert(self,db_manager):
        # # 批量插入
        collection_name = "content"
        data_list = [
                {
                    "id":3,
                    "vector":[0.05, 0.15, 0.25, 0.34],
                    "payload":{"name": "Eve", 'version': '1.2',
                            'timestamp': datetime.now(),
                                "content": "你好2"}
                },
                {
                    "id":2,
                    "vector":[0.05, 0.15, 0.25, 0.32],
                    "payload":{"name": "Eve", 'version': '1.1',
                            'timestamp': datetime.now(),
                                "content": "你好1"}
                },
                {
                    "id":1,
                    "vector":[0.05, 0.15, 0.25, 0.31],
                    "payload":{"name": "Eve", 'version': '1.0',
                            'timestamp': datetime.now(),
                                "content": "你好"}
                },
                {
                    "id":0,
                    "vector":[0.05, 0.15, 0.25, 0.39],
                    "payload":{"name": "Eve", 'version': '1.0',
                            'timestamp': datetime.now(),
                                "content": "你好"}
                },
        ]


        db_manager.bulk_insert(collection_name, data_list)


    def test_select_by_id(self,db_manager):
        collection_name = "content"
        x = db_manager.select_by_id(collection_name,[1,3])
        print(x)

    def test_select_by_vector(self,db_manager):
        collection_name = "content"
        x = db_manager.select_by_vector(query_vector = [0.12, 0.22, 0.32, 0.42],
                                        collection_name = collection_name,
                                        limit = 2)
        print(x)

    def test_scroll(self,db_manager):
        collection_name = "content"

        x = db_manager.scroll(collection_name)
        print(x )


    def test_update(self,db_manager):
        collection_name = "content"
        data_list = [
                {
                    "id":3,
                    "vector":[0.05, 0.15, 0.25, 0.34],
                    "payload":{"name": "Eve", 'version': '1.2',
                            'timestamp': datetime.now(),
                                "content": "你好2"}
                },
                {
                    "id":2,
                    "vector":[0.05, 0.15, 0.25, 0.32],
                    "payload":{"name": "Eve", 'version': '1.1',
                            'timestamp': datetime.now(),
                                "content": "你好1"}
                },
                {
                    "id":1,
                    "vector":[0.05, 0.15, 0.25, 0.31],
                    "payload":{"name": "Eve", 'version': '1.0',
                            'timestamp': datetime.now(),
                                "content": "你好"}
                },
                {
                    "id":0,
                    "vector":[0.05, 0.15, 0.25, 0.39],
                    "payload":{"name": "Eve", 'version': '1.0',
                            'timestamp': datetime.now(),
                                "content": "你好"}
                },
        ]
        db_manager.update(collection_name, data_list)

    def test_set_payload_by_id(self,db_manager):
        collection_name = "content"
        payload = {"work":234}
        db_manager.set_payload_by_id(collection_name, payload ,ids = [2,3])

    def test_delete(self,db_manager):
        collection_name = "content"
        data_list = [
                {
                    "id":3,
                    "vector":[0.05, 0.15, 0.25, 0.34],
                    "payload":{"name": "Eve", 'version': '1.2',
                            'timestamp': datetime.now(),
                                "content": "你好2"}
                },
                {
                    "id":2,
                    "vector":[0.05, 0.15, 0.25, 0.32],
                    "payload":{"name": "Eve", 'version': '1.1',
                            'timestamp': datetime.now(),
                                "content": "你好1"}
                },
                {
                    "id":1,
                    "vector":[0.05, 0.15, 0.25, 0.31],
                    "payload":{"name": "Eve", 'version': '1.0',
                            'timestamp': datetime.now(),
                                "content": "你好"}
                },
                {
                    "id":0,
                    "vector":[0.05, 0.15, 0.25, 0.39],
                    "payload":{"name": "Eve", 'version': '1.0',
                            'timestamp': datetime.now(),
                                "content": "你好"}
                },
        ]
        db_manager.update(collection_name, data_list)
