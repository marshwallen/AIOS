# 创建客户端使用 AIOSClient，并提交并发请求观察其运行时间
from aiosclient import AIOSClient
import argparse
import time
import concurrent.futures

parser = argparse.ArgumentParser()
parser.add_argument("--base_url", type=str, default="http://0.0.0.0:8000")
parser.add_argument("--llm_name", type=str, default="erwan2/DeepSeek-Janus-Pro-7B", help="Ollama model name")
parser.add_argument("--llm_backend", type=str, default="ollama")
parser.add_argument("--root_dir", type=str, default="data")
parser.add_argument("--memory_limit", type=int, default=8*1024*1024)
parser.add_argument("--max_workers", type=int, default=16)
parser.add_argument("--max_new_tokens", type=int, default=256)
args = parser.parse_args()

def run_client(args, agent_path, task_desc):
    client = AIOSClient(args)
    result = client.run_agents(agent_path=agent_path, task_desc=task_desc)
    return result

def concurrent_run(args, tasks):
    """
    同时提交多个 Agent 任务，观察其运行时间
    """
    results = {}
    start_time = time.time()

    with concurrent.futures.ThreadPoolExecutor(max_workers=len(tasks)) as executor:
        # 提交所有任务
        future_to_client = {executor.submit(run_client, args, item["agent_name"], item["query"]): item for i, item in enumerate(tasks)}
        
        # 收集结果
        for future in concurrent.futures.as_completed(future_to_client):
            future_to_client[future]

    end_time = time.time()
    total_time = end_time - start_time
    print(f"Concurrent run time: {total_time}s")

# 并发测试
if __name__ == "__main__":
    tasks = [
        {"agent_name": "example/tech_support_agent", "query": "For what reason is my memory not working?"},
        {"agent_name": "example/tech_support_agent", "query": "For what reason is my graphics card not working?"},
        {"agent_name": "example/tech_support_agent", "query": "For what reason is my monitor not working?"},
        {"agent_name": "example/story_teller", "query": "Tell me a story."},
        {"agent_name": "example/story_teller", "query": "Tell me a funny story."},
    ]

    concurrent_run(args, tasks)
    
