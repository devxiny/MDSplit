# MDSplit

# 简介
基于大模型构建知识库，常常需要对文档进行分片，如果不加处理直接对文档分片往往识别效果不好，因此写了个程序来帮助干这件事，首先需要把文档转成markdown格式，然后交由程序处理，程序会根据markdown的标题层级分片，子标题会将父节点标题拼接一起，来优化知识库的效果。
