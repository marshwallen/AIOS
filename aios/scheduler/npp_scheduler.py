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

import traceback
import time
import heapq

class Process:
    # Syscall 的封装
    def __init__(self, syscall, priority=0):
        self.syscall = syscall
        self.priority = priority

    def __lt__(self, other):
        return self.priority < other.priority
    
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

        # 优先级队列
        self.llm_queues = []
        self.mem_queues = []
        self.storage_queues = []
        self.tool_queues = []

    def update_priority_queue(self, p_queue, syscall_func):
        """
        更新优先级队列，并重新按优先级排列
        :param p_queue: 优先级队列
        :param syscall_func: 获取新任务的函数
        :param max_wait_time: 任务提升优先级之前的最大等待时间
        """
        # 抓取新的任务并直接插入到优先级队列中的适当位置
        while True:
            try:
                task = syscall_func()
                task.set_priority(self.max_priority_level)
                heapq.heappush(p_queue, Process(task, task.get_priority()))
            except Empty:
                break

    def run_llm_syscall(self):
        # self.activate: start/stop the scheduler
        while self.active:
            try:
                # 更新任务队列
                self.update_priority_queue(self.llm_queues, self.get_llm_syscall)
                llm_syscall = heapq.heappop(self.llm_queues).syscall

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
                self.update_priority_queue(self.mem_queues, self.get_memory_syscall)
                memory_syscall = heapq.heappop(self.mem_queues).syscall

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
                storage_syscall = heapq.heappop(self.storage_queues).syscall

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
                tool_syscall = heapq.heappop(self.tool_queues).syscall

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
