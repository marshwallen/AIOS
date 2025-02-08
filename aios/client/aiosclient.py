# 创建 AIOS Client 类以使用 AIOS SDK

# AIOS SDK: https://docs.aios.foundation/aios-docs/aios-sdk/overview
# All queries from these modules are ultimately channeled through a central send_request(Query) function in the AIOS-Agent SDK, 
# which then communicates with the AIOS kernel via HTTP requests (either to localhost or a remote URL).

from cerebrum import config
from cerebrum.client import Cerebrum
from cerebrum.llm.layer import LLMLayer
from cerebrum.memory.layer import MemoryLayer
from cerebrum.overrides.layer import OverridesLayer
from cerebrum.storage.layer import StorageLayer
from cerebrum.tool.layer import ToolLayer

class AIOSClient:
    def __init__(self, args):
        self.base_url = args.base_url

        # Initialize Client
        self.client = Cerebrum(args.base_url)
        config.global_client = self.client
        self.agents = {}

        # Add Functionality Layers
        # The AIOS-Agent SDK offers five router APIs to initialize and setup the following essential modules in the AIOS kernel.
        # LLM, Memory, Storage, Tools, Scheduler

        self.client.add_llm_layer(
            LLMLayer(
                llm_name=args.llm_name, 
                llm_backend=args.llm_backend,
                max_new_tokens=args.max_new_tokens,
                )  # Configure your LLM
        ).add_storage_layer(
            StorageLayer(root_dir=args.root_dir)  # Set storage directory
        ).add_memory_layer(
            MemoryLayer(memory_limit=args.memory_limit)  # Set memory per agent
        ).add_tool_layer(
            ToolLayer()  # Add tool capabilities
        ).override_scheduler(
            OverridesLayer(max_workers=args.max_workers)  # Configure scheduling
        )

    def run_agents(self, agent_path, task_desc, timeout=10.0):
        """
        Run agents and get their results
        :param agent_path: Your agent's name or path. Name can be seen at https://app.aios.foundation/agenthub
        :param task_desc: Your task description
        """
        try:
            # Connect to the client
            self.client.connect()
            
            # Execute agent
            result = self.client.execute(agent_path, {"task": task_desc})
            
            # Get the results
            final_result = self.client.poll_agent(
                result["execution_id"],
                timeout=timeout
            )

            print("📋 Task result:", final_result)
            print("✅ Task completed")

            return final_result

        except TimeoutError:
            print("❌ Task timed out")
            return None
        except Exception as e:
            print(f"❌ Failed to execute task: {str(e)}")
            return None
        finally:
            self.client.cleanup()








