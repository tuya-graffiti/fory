# 创建PromptTemplate类，用于创建Prompt模板
from langchain_core.prompts import PromptTemplate

class RAGPrompts:

    @staticmethod
    def rag_prompt():
        return PromptTemplate(
            # RAG专用问答提示词
            # context, history, question, phone
            template="""
            你是一个智能助手，负责帮助用于回答问题，请按照以下步骤处理
            1.**分析问题和上下文**
                - 基于提供的上下文(如果有)和你的知识回答问题
            2.**评估对话历史**
                - 检查对话历史是否与当前问题相关(例如:是否设计相同的话题、实体或问题背景)
                - 如果对话历史与问题相关，请结合历史信息生成更准确的回答。
                - 如果对话历史无关（例如，仅包含问候或不相关的内容），忽略历史，仅基于上下文和问题回答。
            3.**生成回答**:
                - 提供清晰、准确的回答，避免无关信息
                - 如果上下文和历史消息均不足以回答问题，请回复：“信息不足，无法回答，请联系人工客服，电话：{phone}。”
                - 强制要求在回答的开头写:"LL为您服务" 
            **上下文**: {context}
            **对话历史**:{history}
            **问题**: {question}
            **回答**:            
            """
        )
    @staticmethod
    def general_prompt():
        """
        通用对话提示词
        :return:
        """
        return  PromptTemplate(
            template = """
            **对话历史**:{history}
            **问题**:{query}
            """
        )