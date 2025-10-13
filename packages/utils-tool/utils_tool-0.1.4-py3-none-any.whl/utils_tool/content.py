
import time
from contextlib import contextmanager
from sqlalchemy.orm import sessionmaker
import traceback

@contextmanager
def check_time(title:str,logger):
    """ try catch"""
    time1 = time.time()
    yield
    time2 = time.time()
    logger.debug(f"{title}: {time2-time1}")

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


@contextmanager
def safe_operation():
    """
    一个上下文管理器，用于安全地执行代码块并捕获其中的异常。

    当代码块中发生异常时，此上下文管理器会捕获异常，打印详细的错误信息（包括堆栈跟踪），
    并重新抛出一个通用的异常。这有助于在不中断程序流程的情况下处理预期之外的错误，
    并提供统一的错误日志记录机制。

    用法示例:
        >>> with safe_operation():
        >>>     # 可能会抛出异常的代码
        >>>     result = 1 / 0
        >>> # 异常会被捕获并处理
    """
    try:
        yield
    except Exception as e:
        error_info = traceback.format_exc()
        print(e, error_info)  # 详细信息
        raise Exception(" exception!") from e
        # log记录
