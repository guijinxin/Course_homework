from pymilvus import connections, FieldSchema, CollectionSchema, DataType, Collection, utility
from sentence_transformers import SentenceTransformer
import pandas as pd
import json
# 1. 连接到 Milvus 数据库
connections.connect(host="10.58.0.2", port="19530")

# 2. 定义集合的 Schema
fields = [
    FieldSchema(name="id", dtype=DataType.VARCHAR, max_length=50, is_primary=True),  # 论文的唯一标识符
    FieldSchema(name="vector", dtype=DataType.FLOAT_VECTOR, dim=384),  # 向量维度（与嵌入模型匹配）
    FieldSchema(name="title", dtype=DataType.VARCHAR, max_length=500),  # 论文标题
    FieldSchema(name="authors", dtype=DataType.VARCHAR, max_length=500),  # 论文作者
    FieldSchema(name="categories", dtype=DataType.VARCHAR, max_length=200),  # 论文分类
    FieldSchema(name="doi", dtype=DataType.VARCHAR, max_length=200),  # 论文 DOI
    FieldSchema(name="journal_ref", dtype=DataType.VARCHAR, max_length=500),  # 期刊引用
    FieldSchema(name="comments", dtype=DataType.VARCHAR, max_length=500),  # 论文评论
    FieldSchema(name="text", dtype=DataType.VARCHAR, max_length=5000),  # 论文摘要（必须命名为 text）
]

schema = CollectionSchema(fields, "arXiv 数据集")

# 3. 创建集合（如果集合不存在）
collection_name = "arXiv"
if collection_name not in utility.list_collections():
    collection = Collection(name=collection_name, schema=schema)
    print(f"集合 {collection_name} 创建成功！")
else:
    # Drop the existing collection
    collection = Collection(name=collection_name)
    collection.drop()
    print(f"集合 {collection_name} 已删除！")
    collection = Collection(name=collection_name, schema=schema)
    print(f"集合 {collection_name} 创建成功！")

# 4. 加载嵌入模型
embedding_model = SentenceTransformer("sentence-transformers/all-MiniLM-L12-v2")

# 5. 加载 arXiv 数据集
with open("arxiv-metadata-oai-snapshot.json", "r") as read_file:
    data = [json.loads(line) for line in read_file]


# 6. 数据预处理
vectors = []
ids = []
titles = []
authors = []
categories = []
dois = []
journal_refs = []
comments = []
texts = []
print(len(data))
new = 0
for item in data:
    abstract = item.get("abstract", "N/A")  # 论文摘要
    if len(abstract) > 5000:
        print(f"Abstract length exceeds 5000 characters: {len(abstract)}")
        abstract = abstract[:5000]  # 截断到最大长度

    title = item.get("title", "N/A")
    if len(title) > 500:
        print(f"Title length exceeds 500 characters: {len(title)}")
        title = title[:500]  # 截断到最大长度

    author_list = ", ".join([", ".join(author) for author in item.get("authors_parsed", [])])
    if len(author_list) > 500:
        print(f"Authors length exceeds 500 characters: {len(author_list)}")
        author_list = author_list[:500]  # 截断到最大长度

    category_list = item.get("categories", "N/A")
    if len(category_list) > 200:
        print(f"Categories length exceeds 200 characters: {len(category_list)}")
        category_list = category_list[:200]  # 截断到最大长度

    doi = item.get("doi", "N/A")
    if len(doi) > 200:
        print(f"DOI length exceeds 200 characters: {len(doi)}")
        doi = doi[:200]  # 截断到最大长度

    journal_ref = item.get("journal-ref", "N/A")
    if len(journal_ref) > 500:
        print(f"Journal Ref length exceeds 500 characters: {len(journal_ref)}")
        journal_ref = journal_ref[:500]  # 截断到最大长度

    comment_list = item.get("comments", "N/A")
    if len(comment_list) > 500:
        print(f"Comments length exceeds 500 characters: {len(comment_list)}")
        comment_list = comment_list[:500]  # 截断到最大长度
    vector = embedding_model.encode(abstract).tolist()  # 生成向量
    vectors.append(vector)
    ids.append(item.get("id", "N/A"))
    titles.append(title)
    authors.append(author_list)
    categories.append(category_list)
    dois.append(doi)
    journal_refs.append(journal_ref)
    comments.append(comment_list)
    texts.append(abstract)
    new += 1
    if new % 1000 == 0:
        entities = [
            ids,  # 论文 ID
            vectors,  # 向量
            titles,  # 论文标题
            authors,  # 论文作者
            categories,  # 论文分类
            dois,  # 论文 DOI
            journal_refs,  # 期刊引用
            comments,  # 论文评论
            texts,  # 论文摘要
        ]
        collection.insert(entities)
        print(f"数据已成功插入到集合 {collection_name} 中！")
        vectors = []
        ids = []
        titles = []
        authors = []
        categories = []
        dois = []
        journal_refs = []
        comments = []
        texts = []



# # 7. 插入数据到 Milvus
# entities = [
#     ids,  # 论文 ID
#     vectors,  # 向量
#     titles,  # 论文标题
#     authors,  # 论文作者
#     categories,  # 论文分类
#     dois,  # 论文 DOI
#     journal_refs,  # 期刊引用
#     comments,  # 论文评论
#     texts,  # 论文摘要
# ]
# collection.insert(entities)
# print(f"数据已成功插入到集合 {collection_name} 中！")

# 8. 创建索引（加速查询）
index_params = {
    "index_type": "IVF_FLAT",
    "metric_type": "L2",
    "params": {"nlist": 128},
}
collection.create_index("vector", index_params)
print("索引创建成功！")

# 9. 持久化数据
collection.load()
print("集合已加载到内存中！")