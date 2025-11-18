from conn import llms
from langgraph.prebuilt import create_react_agent
from langchain.tools import tool
import requests
from env import langsmith_env
import os
os.environ["LANGCHAIN_PROJECT"] = "frontend-generator-fastapi"

@ tool
def save_html(html_path,html_content):
    """保存html的工具"""
    with open(html_path, "w+", encoding="utf-8") as f:
        f.write(html_content)

@ tool
#获取接口文档
def get_api_doc(api_url):
    """获取接口文档"""
    return requests.get(api_url).text


def gen_front_end_files(api_url,dir_path, description):
    agent = create_react_agent(
        model=llms.get_deepseek(),
        prompt='''
        1. 先根据传入的接口文档url获取接口文档信息。
        2. 根据接口文档创建基于vue合适的前端html文件并保存。
        ''',
        tools=[get_api_doc,save_html],
    )
    message = {
        "messages": [
            {
                "role": "user",
                "content": f'''
                接口文档url：{api_url}
                前端文件目录地址：{dir_path}
                说明：{description}'''
            }
        ]
    }
    r = agent.invoke(message)
    return r['messages'][-1].content


if __name__ == '__main__':
    dir_path = r'D:\workspace\pythonworkspace\chuanzhi\rag_project\frontend'
    api_url = 'http://127.0.0.1:8000/openapi.json'
    description = '''
                1. 这是一个聊天展示框
                2. 注意聊天要流式输出
                '''
    r = gen_front_end_files(api_url,dir_path,description)
    print(r)