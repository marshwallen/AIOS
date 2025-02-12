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
- 本 repo 的 LLM 后端使用的是 Ollama，其安装和配置方法在此不作赘述，可以参考：https://github.com/marshwallen/llm-deploy-playground
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
python client/tasktest.py --llm_name erwan2/DeepSeek-Janus-Pro-7B --llm_backend ollama

# 📋 Task result: {'agent_name': 'example/tech_support_agent', 'result': "Than ... Have you tried either of these solutions?", 'rounds': 3}
# ✅ Task completed
# Concurrent run time: 37.9095573425293s
```
- AIOS 支持的 Backend 列表写在 [README_OFFCIAL.md](https://github.com/marshwallen/AIOS/blob/main/README_OFFCIAL.md) 的 Supported LLM Cores 项中

## 调度算法
AIOS 支持多个 Agent 的同时请求，因此需要调度算法合理规划每一个 task
1. **先来先服务 (First-In, First-Out, FIFO)**
- 一种简单的调度策略，任务按照它们到达的顺序进行处理。每个任务在前一个任务完成后才开始执行。这种策略适用于任务之间没有优先级差异的场景
- 该调度算法为本 AIOS 的默认调度算法，具体使用线程和队列实现了一个 FIFO 任务队列，类似于轮询调度程序。但是，超时时间是 1 秒而不是 0.05 秒
- 具体实现见：```aios/scheduler/fifo_scheduler.py```
```sh
# 要启用 FIFO 调度，请在 runtime/kernel.py 中修改如下项
scheduler_type = "FIFO"
```

2. **非抢占式优先级调度 (Non-preemptive Priority Scheduling)**
- 任务按照其优先级进行处理，但一旦一个任务开始执行，它将不会被中断，直到完成或自愿让出处理器。这种策略适用于需要确保高优先级任务最终得到执行的场景，同时保持系统的稳定性和可预测性
- 本 forked repo 实现了该调度算法，主要方法有：
    - **任务队列**：使用优先级队列实现，每个任务都有一个优先级，优先级高的任务会优先被调度
    - **优先级队列管理**：任务根据优先级插入和重新排列
    - **等待时间监控**：长时间等待的任务优先级会被提升，以防止饥饿现象（计算任务队列中每个任务的等待时间，使用其90百分位作为阈值，当任务等待时间超过阈值时，提升其优先级）
    - **新任务动态插入**：从系统调用函数中动态获取新任务并插入到队列中
- 具体实现见：```aios/scheduler/npp_scheduler.py```
```sh
# 要启用非抢占式优先级调度，请在 runtime/kernel.py 中修改如下项
scheduler_type = "NPPS"
```
