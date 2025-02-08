# 仓库介绍
- 本 forked repo 源于《AIOS：LLM Agent Operating System》的官方代码仓库，仅供学习之用，在其基础上进行二次开发
- 关于本 AIOS 的技术架构和实现笔记参考：[链接](https://zhuanlan.zhihu.com/p/691420682)
- 原 Readme 请参考 [README_OFFCIAL.md](https://github.com/marshwallen/AIOS/blob/main/README_OFFCIAL.md)

## Instruction
1. **AIOS 安装**
- 请参考: https://docs.aios.foundation/aios-docs/getting-started/installation
```sh
# 依赖安装完成后，敲入以下命令启动 AIOS 服务
bash runtime/launch_kernel.sh

# [DEBUG] Using Agent Hub URL: https://app.aios.foundation
# [DEBUG] Using Tool Hub URL: https://app.aios.foundation
# INFO:     Started server process [54037]
# INFO:     Waiting for application startup.
# INFO:     Application startup complete.
# INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

2. **LLM Backend 准备**
- 本 repo 的 LLM 后端使用的是 Ollama，其安装和配置方法在此不作赘述
- 安装完成后，终端输出应当如下所示
```sh
# 1 检查 Ollama 服务是否起来
ollama -v
# 若服务成功起来，会显示 ollama version is x.x.x

# 2 检查 Ollama 模型列表
ollama list
# NAME                                               ID              SIZE      MODIFIED     
# erwan2/DeepSeek-Janus-Pro-7B:latest                e877a212a6a7    4.2 GB    43 hours ago    
# cyberuser42/DeepSeek-R1-Distill-Qwen-14B:latest    fff139a47679    9.0 GB    45 hours ago    
# hengwen/DeepSeek-R1-Distill-Qwen-32B:q4_k_m        4376ba0a1404    19 GB     46 hours ago    
```

3. **通过 Cerebrum 调用 AIOS 服务**
- AIOS SDK 文档: https://docs.aios.foundation/aios-docs/aios-sdk/overview
- 这里使用 ```erwan2/DeepSeek-Janus-Pro-7B``` 作为演示，向 AIOS 服务后端发送多个 Agent 请求
- CPU: 12th Gen Intel(R) Core(TM) i5-12490F
- GPU: NVIDIA GeForce RTX 3060 Ti 8G
- RAM: DDR4 16Gx2 3200Mhz
```sh
# 多实例调用 AIOS 服务
python client/tasktest.py

# 📋 Task result: {'agent_name': 'example/tech_support_agent', 'result': "Than ... Have you tried either of these solutions?", 'rounds': 3}
# ✅ Task completed
# Concurrent run time: 37.9095573425293s
```