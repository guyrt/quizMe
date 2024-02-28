from pymilvus import Collection, connections


class _MilvusWrapperSingleton:
    def __init__(self) -> None:
        connections.connect(
            alias="default",  # database
            user="username",  # get from setting
            password="password",  # get from setting
            host="localhost",  # get from setting
            port="19530",
        )
        Collection()


milvus_wrapper = _MilvusWrapperSingleton()
