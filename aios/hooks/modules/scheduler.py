from typing import Any, Tuple, Callable, Dict
from random import randint

from aios.hooks.types.scheduler import (
    # AgentSubmitDeclaration,
    # FactoryParams,
    # LLMParams,
    SchedulerParams,
    # LLMRequestQueue,
    # QueueGetMessage,
    # QueueAddMessage,
    # QueueCheckEmpty,
)

from contextlib import contextmanager

from aios.hooks.utils.validate import validate
from aios.hooks.stores import queue as QueueStore, processes as ProcessStore
from aios.scheduler.fifo_scheduler import FIFOScheduler
from aios.scheduler.npp_scheduler import NPPScheduler


@validate(SchedulerParams)
def useScheduler(
    params: SchedulerParams,
) -> Tuple[Callable[[], None], Callable[[], None]]:
    """
    Initialize and return a scheduler with start and stop functions.

    Args:
        params (SchedulerParams): Parameters required for the scheduler.

    Returns:
        Tuple: A tuple containing the start and stop functions for the scheduler.
    """
    if params.get_llm_syscall is None:
        from aios.hooks.stores._global import global_llm_req_queue_get_message
        params.get_llm_syscall = global_llm_req_queue_get_message
        
    if params.get_memory_syscall is None:
        from aios.hooks.stores._global import global_memory_req_queue_get_message
        params.get_memory_syscall = global_memory_req_queue_get_message
        
    if params.get_storage_syscall is None:
        from aios.hooks.stores._global import global_storage_req_queue_get_message
        params.get_storage_syscall = global_storage_req_queue_get_message
        
    if params.get_tool_syscall is None:
        from aios.hooks.stores._global import global_tool_req_queue_get_message
        params.get_tool_syscall = global_tool_req_queue_get_message

    if params.scheduler_type == "FIFO" or params.scheduler_type is None:
        scheduler = FIFOScheduler(**params.model_dump())
    elif params.scheduler_type == "NPPS":
        scheduler = NPPScheduler(**params.model_dump())
    else:
        raise ValueError(f"Invalid scheduler type: {params.scheduler_type}")

    # Function to start the scheduler
    def startScheduler():
        scheduler.start()

    # Function to stop the scheduler
    def stopScheduler():
        scheduler.stop()

    return startScheduler, stopScheduler


@contextmanager
@validate(SchedulerParams)
def scheduler(params: SchedulerParams):
    """
    A context manager that starts and stops a FIFO scheduler.

    Args:
        params (SchedulerParams): The parameters for the scheduler.
    """
    if params.get_llm_syscall is None:
        from aios.hooks.stores._global import global_llm_req_queue_get_message
        params.get_llm_syscall = global_llm_req_queue_get_message

    if params.get_memory_syscall is None:
        from aios.hooks.stores._global import global_memory_req_queue_get_message
        params.get_memory_syscall = global_memory_req_queue_get_message
    
    if params.get_storage_syscall is None:
        from aios.hooks.stores._global import global_storage_req_queue_get_message
        params.get_storage_syscall = global_storage_req_queue_get_message
        
    if params.get_tool_syscall is None:
        from aios.hooks.stores._global import global_tool_req_queue_get_message
        params.get_tool_syscall = global_tool_req_queue_get_message
    
    if params.scheduler_type == "FIFO" or params.scheduler_type is None:
        scheduler = FIFOScheduler(**params.model_dump())
    elif params.scheduler_type == "NPPS":
        scheduler = NPPScheduler(**params.model_dump())
    else:
        raise ValueError(f"Invalid scheduler type: {params.scheduler_type}")
    
    scheduler.start()
    yield
    scheduler.stop()

@validate(SchedulerParams)
def scheduler_nonblock(params: SchedulerParams):
    """
    A context manager that starts and stops a FIFO scheduler.

    Args:
        params (SchedulerParams): The parameters for the scheduler.
    """
    if params.get_llm_syscall is None:
        from aios.hooks.stores._global import global_llm_req_queue_get_message
        params.get_llm_syscall = global_llm_req_queue_get_message

    if params.get_memory_syscall is None:
        from aios.hooks.stores._global import global_memory_req_queue_get_message
        params.get_memory_syscall = global_memory_req_queue_get_message
    
    if params.get_storage_syscall is None:
        from aios.hooks.stores._global import global_storage_req_queue_get_message
        params.get_storage_syscall = global_storage_req_queue_get_message
        
    if params.get_tool_syscall is None:
        from aios.hooks.stores._global import global_tool_req_queue_get_message
        params.get_tool_syscall = global_tool_req_queue_get_message
    
    if params.scheduler_type is None or params.scheduler_type == "FIFO":
        scheduler = FIFOScheduler(**params.model_dump())
    elif params.scheduler_type == "NPPS":
        scheduler = NPPScheduler(**params.model_dump())
    else:
        raise ValueError(f"Invalid scheduler type: {params.scheduler_type}")

    return scheduler