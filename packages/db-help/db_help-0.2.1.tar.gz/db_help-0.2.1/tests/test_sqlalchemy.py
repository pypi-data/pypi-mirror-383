
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import sessionmaker, declarative_base
import pytest

from contextlib import contextmanager

@contextmanager
def create_session(engine):
    # 5. 创建会话 (Session)
    # Session 是与数据库交互的主要接口，它管理着你的对象和数据库之间的持久化操作
    Session = sessionmaker(bind=engine)
    session = Session()
    try:
        yield session

    except Exception as e:
        print(f"An error occurred: {e}")
        session.rollback() # 发生错误时回滚事务
    finally:
        session.close() # 关闭会话，释放资源

Base = declarative_base()
class User(Base):
    __tablename__ = 'users29' # 数据库中的表名
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50)) # <<--- 这里！为 String 指定长度，例如 50
    email = Column(String(100), unique=True) # <<--- 这里！为 String 指定长度，例如 100

    def __repr__(self):
        return f"<User(id={self.id}, name='{self.name}', email='{self.email}')>"


@pytest.fixture
def engine():
    database_url = "mysql+pymysql://root:1234@localhost:3306/prompts"
    engine = create_engine(database_url, echo=True) # echo=True 仍然会打印所有执行的 SQL 语句
    return engine


def test_create_engine(engine):
    # create engine
    
    # 3. 定义模型 (Model) - 映射数据库表
    Base.metadata.create_all(engine)

def test_add(engine):
    with create_session(engine) as session:
        user1 = User(name='Alice', email='alice@example.com')
        user2 = User(name='Bob', email='bob@example.com')
        user3 = User(name='Charlie', email='charlie@example.com')
        session.add(user1)
        session.add_all([user2, user3]) # 可以一次添加多个对象
        session.commit() # 提交事务，将数据写入数据库

def test_search_all(engine):
    print("\nAll users:")
    with create_session(engine) as session:
        for user in session.query(User).all():
            print(user)

def test_search_1(engine):
    print("\nAll users:")
    with create_session(engine) as session:
        alice = session.query(User).filter_by(name='Alice').first() # first() 返回第一个匹配项
        if alice:
            print("=="*20)
            print(alice)
            print("=="*20)

def test_search_2(engine):
    print("\nUsers with 'example.com' in email:")
    with create_session(engine) as session:
        for user in session.query(User).filter(User.email.like('%example.com%')).all():
            print("=="*20)
            print(user)
            print("=="*20)

def test_search_3(engine):
    print("\nUser with ID 2:")
    with create_session(engine) as session:        
        user_by_id = session.query(User).get(2) # get() 只能用于主键查询
        if user_by_id:
            print("=="*20)
            print(user_by_id)
            print("=="*20)
            
def test_update(engine):
    with create_session(engine) as session:        
        # 先查询到 User
        # alice.email = 'new_alice@example.com'
        session.commit() # 提交更新

def test_delete(engine):
    with create_session(engine) as session:  
        # 先查询到 User ->   user_by_id
        session.delete(user_by_id)
        session.commit() # 提交删除
        print("User with ID 2 deleted.")
