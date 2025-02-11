# 非抢占式优先级调度算法 (Non-preemptive Priority Scheduling Algorithm)

from aios.hooks.types.llm import LLMRequestQueueGetMessage
from aios.hooks.types.memory import MemoryRequestQueueGetMessage
from aios.hooks.types.tool import ToolRequestQueueGetMessage
from aios.hooks.types.storage import StorageRequestQueueGetMessage

from aios.memory.manager import MemoryManager
from aios.storage.storage import StorageManager
from aios.llm_core.adapter import LLMAdapter
from aios.tool.manager import ToolManager

from .base import Scheduler

from queue import Empty
from collections import deque

import traceback
import time

class NPPScheduler(Scheduler):
    def __init__(
        self,
        llm: LLMAdapter,
        memory_manager: MemoryManager,
        storage_manager: StorageManager,
        tool_manager: ToolManager,
        log_mode,
        get_llm_syscall: LLMRequestQueueGetMessage,
        get_memory_syscall: MemoryRequestQueueGetMessage,
        get_storage_syscall: StorageRequestQueueGetMessage,
        get_tool_syscall: ToolRequestQueueGetMessage,
        scheduler_type: str
    ):
        super().__init__(
            llm,
            memory_manager,
            storage_manager,
            tool_manager,
            log_mode,
            get_llm_syscall,
            get_memory_syscall,
            get_storage_syscall,
            get_tool_syscall,
        )

        # 优先级设置
        self.max_priority_level = 5 # 最大优先级的级数
        self.max_wait_time=10 # 任务经过多少等待时间后提升优先级

        # 优先级队列
        self.llm_queues = deque()
        self.mem_queues = deque()
        self.storage_queues = deque()
        self.tool_queues = deque()

    def insert_task(self, p_queue: deque, task):
        """
        将任务插入到优先级队列中的适当位置
        :param p_queue: 优先级队列
        :param task: 要插入的任务
        """
        inserted = False
        for i in range(len(p_queue)):
            if task.get_priority() < p_queue[i].get_priority():
                p_queue.insert(i, task)
                inserted = True
                break
        if not inserted:
            p_queue.append(task)

    def update_priority_queue(self, p_queue: deque, syscall_func):
        """
        更新优先级队列，并重新按优先级排列
        :param p_queue: 优先级队列
        :param syscall_func: 获取新任务的函数
        :param max_wait_time: 任务提升优先级之前的最大等待时间
        """
        curr_time = time.time()

        # 抓取新的任务并直接插入到优先级队列中的适当位置
        while True:
            try:
                task = syscall_func()
                task.set_priority(self.max_priority_level)
                self.insert_task(p_queue, task)
            except Empty:
                break

        # 检查任务队列，提升等待时间过长的任务的优先级
        for task in list(p_queue):  # 将 deque 转换为列表以避免在迭代时修改
            if curr_time - task.get_created_time() > self.max_wait_time:
                new_priority = min(0, task.get_priority() - 1)
                task.set_priority(new_priority)
                p_queue.remove(task)  # 从原队列中移除任务
                self.insert_task(p_queue, task)  # 重新插入到适当位置

    def run_llm_syscall(self):
        # self.activate: start/stop the scheduler
        while self.active:
            try:
                # 更新任务队列
                self.update_priority_queue(self.llm_queues, self.get_llm_syscall)
                llm_syscall = self.llm_queues.popleft()

                llm_syscall.set_status("executing")
                self.logger.log(
                    f"{llm_syscall.agent_name} is executing. \n", "execute"
                )
                llm_syscall.set_start_time(time.time())

                response = self.llm.address_syscall(llm_syscall)
                llm_syscall.set_response(response)

                llm_syscall.event.set()
                llm_syscall.set_status("done")
                llm_syscall.set_end_time(time.time())

            except IndexError:
                pass
            except Empty:
                pass
            except Exception:
                traceback.print_exc()

    def run_memory_syscall(self):
        while self.active:
            try:
                # wait at a fixed time interval, if there is nothing received in the time interval, it will raise Empty
                # 新来的任务，按最高优先级加入队列
                self.update_priority_queue(self.mem_queues, self.get_memory_syscall)
                memory_syscall = self.mem_queues.popleft()

                memory_syscall.set_status("executing")
                self.logger.log(
                    f"{memory_syscall.agent_name} is executing. \n", "execute"
                )
                memory_syscall.set_start_time(time.time())

                response = self.memory_manager.address_request(memory_syscall)
                memory_syscall.set_response(response)

                memory_syscall.event.set()
                memory_syscall.set_status("done")
                memory_syscall.set_end_time(time.time())

            except IndexError:
                pass
            except Empty:
                pass
            except Exception:
                traceback.print_exc()

    def run_storage_syscall(self):
        while self.active:
            try:
                self.update_priority_queue(self.storage_queues, self.get_storage_syscall)
                storage_syscall = self.storage_queues.popleft()

                storage_syscall.set_status("executing")
                self.logger.log(
                    f"{storage_syscall.agent_name} is executing. \n", "execute"
                )
                storage_syscall.set_start_time(time.time())

                response = self.storage_manager.address_request(storage_syscall)
                storage_syscall.set_response(response)

                storage_syscall.event.set()
                storage_syscall.set_status("done")
                storage_syscall.set_end_time(time.time())

                self.logger.log(
                    f"Current request of {storage_syscall.agent_name} is done. Thread ID is {storage_syscall.get_pid()}\n",
                    "done"
                )

            except IndexError:
                pass
            except Empty:
                pass
            except Exception:
                traceback.print_exc()

    def run_tool_syscall(self):
        while self.active:
            try:
                self.update_priority_queue(self.tool_queues, self.get_tool_syscall)
                tool_syscall = self.tool_queues.popleft()

                tool_syscall.set_status("executing")

                tool_syscall.set_start_time(time.time())

                response = self.tool_manager.address_request(tool_syscall)
                tool_syscall.set_response(response)

                tool_syscall.event.set()
                tool_syscall.set_status("done")
                tool_syscall.set_end_time(time.time())
                
            except IndexError:
                pass
            except Empty:
                pass
            except Exception:
                traceback.print_exc()
