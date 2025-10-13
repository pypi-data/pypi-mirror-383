from qdrant_client import QdrantClient, models

class QdrantManager:
    """
    一个用于与 MySQL 数据库交互的通用工具包。
    提供了连接管理、增删改查 (CRUD) 操作和错误处理。
    """

    def __init__(self, host, port=6333):
        """
        初始化数据库管理器。
        :param host: 数据库主机名或 IP 地址。
        :param user: 数据库用户名。
        :param password: 数据库密码。
        :param database: 默认数据库名称 (可选，如果只连接到服务器而不指定数据库)。
        :param port: 数据库端口 (默认为 3306)。
        """
        self.host = host
        self.port = port
        self.connection = QdrantClient(host=host, port=port)

    # --- CRUD 操作封装 ---

    def create_collection(self, collection_name: str, vector_dimension = 4):
        """
        创建表。
        注意： recreate_collection 会在集合存在时先删除再创建。如果你只想在集合不存在时创建，可以使用 create_collection。
        :param table_name: 要创建的表名。
        :param columns_definition: 列定义字符串，例如 "id INT AUTO_INCREMENT PRIMARY KEY, name VARCHAR(255), age INT"。
        :return: True 如果成功，False 如果失败。
        """

        self.connection.recreate_collection(
            collection_name=collection_name,
            vectors_config=models.VectorParams(size=vector_dimension, distance=models.Distance.COSINE),
            # 可以选择配置 payload_m_config 来优化存储
            # payload_m_config=models.PayloadMConfig(
            #     enable_m=True,
            #     m=16, # 默认 16，越大索引构建越慢，但查询越快，内存占用越多
            # )
        )
        print('创建成功')
        return True
    
    def insert(self, collection_name, data):
        """
        插入单条数据。
        :param table_name: 表名。
        :param data: 字典，键为列名，值为要插入的数据。
                     例如: {'name': 'Alice', 'age': 30, 'email': 'alice@example.com'}
        :return: 新插入记录的 ID (如果表有自增主键)，否则返回 None。
        """
        if not data:
            print("错误：插入数据为空。")
            return None
        points = [
                models.PointStruct(
                    **data
                )
            ]
        self.connection.upsert(
            collection_name=collection_name,
            wait=True,
            points=points
        )

        return True

    def bulk_insert(self, collection_name, data_list):
        """
        批量插入数据。
        :param table_name: 表名。
        :param columns: 列名列表，例如 ['name', 'age', 'email']。
        :param data_list: 包含元组或列表的列表，每个元组/列表代表一行数据。
                          例如: [('Alice', 30, 'alice@example.com'), ('Bob', 25, 'bob@example.com')]
        :return: 影响的行数，或 None。
        """

        if not data_list:
            print("错误：批量插入数据为空。")
            return None

        points_to_insert = [models.PointStruct(**data) for data in data_list]        

        self.connection.upsert(
            collection_name=collection_name,
            wait=True,  # 等待操作完成
            points=points_to_insert
        )
        print(f"Inserted/Upserted {len(points_to_insert)} points into '{collection_name}'.")


    def select_by_id(self,collection_name,ids =[1, 3] ):
            
        retrieved_points = self.connection.retrieve(
            collection_name=collection_name,
            ids=ids,
            with_vectors=True,  # 是否返回向量数据
            with_payload=True   # 是否返回负载数据
        )
        return retrieved_points
    
    def select_by_vector(self,query_vector = [0.12, 0.22, 0.32, 0.42],
                            collection_name = "",
                                limit = 2 # 返回最相似的 2 个点
                         ):
        """
        # 查找城市为 "New York" 的点中，与查询向量最相似的
        query_filter=models.Filter(
                must=[
                    models.FieldCondition(
                        key="city",
                        match=models.MatchValue(value="New York")
                    )
                ]
            ),

        # 查找年龄大于 30 的点
        query_filter=models.Filter(
                must=[
                    models.Range(
                        key="age",
                        gte=30 # Great than or Equal to 30
                    )
                ]
            ),
        """

        search_results = self.connection.search(
            query_vector=query_vector,
            collection_name=collection_name,
            query_filter = None,
            limit=limit,
            with_payload=True,
            with_vectors=False # 通常搜索结果不需要返回向量本身
        )
        return search_results
    
    def scroll(self,collection_name):

        """
        # 带过滤条件的滚动
        scroll_filter=models.Filter(
                must=[
                    models.FieldCondition(
                        key="city",
                        match=models.MatchValue(value="London")
                    )
                ]
            ),
        """
        # 获取集合中所有点 # 分页查询
        all_points = self.connection.scroll(
            collection_name=collection_name,
            scroll_filter = None,
            limit=10, # 每次请求返回的最大点数
            with_payload=True,
            with_vectors=False
        )
        return all_points

    def update(self, collection_name, data_list):
        """
        更新数据。
        :param table_name: 表名。
        :param data: 字典，键为要更新的列名，值为新数据。
                     例如: {'age': 31, 'email': 'new_alice@example.com'}
        :param conditions: WHERE 子句的条件字符串，例如 "id = %s"。
        :param params: 条件对应的参数 (元组或列表)。
        :return: 影响的行数，或 None。
        """


        if not data_list:
            print("错误：批量插入数据为空。")
            return None

        points_to_insert = [models.PointStruct(**data) for data in data_list]        

        # 更新 ID 为 1 的点的年龄
        self.connection.upsert(
            collection_name=collection_name,
            wait=True,
            points=points_to_insert
        )

    def set_payload_by_id(self,collection_name,payload:dict,ids = []):
        # 为 ID 2 的点设置一个新的字段 "occupation"
        self.connection.set_payload(
            collection_name=collection_name,
            payload=payload,
            points=ids, # 指定要更新的点 ID
            wait=True
        )
   
    def delete(self, collection_name, conditions, params=None):
        """
        删除数据。
        :param table_name: 表名。
        :param conditions: WHERE 子句的条件字符串，例如 "id = %s"。
        :param params: 条件对应的参数 (元组或列表)。
        :return: 影响的行数，或 None。
        """

        # 清除 ID 1 的点的 'status' 字段
        self.connection.clear_payload(
            collection_name=collection_name,
            points_selector=models.PointIdsList(points=[1]), # 也可以使用 query_filter
            keys=["status"],
            wait=True
        )
