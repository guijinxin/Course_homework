from pymilvus import connections, utility

# 连接到 Milvus 数据库
connections.connect(host="10.58.0.2", port="19530")

# 获取数据库信息
info = utility.get_server_version()
print("Milvus Server Version:", info)

# 获取当前连接的 Milvus 实例信息
instance_info = utility.get_query_segment_info('arxiv')
print("Milvus Server Type:", instance_info)

