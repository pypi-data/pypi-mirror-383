from memokit.db import MemoryPoolConnector
class MemoryPool:
    def __init__(self, db_connector=None):
        if db_connector is None or db_connector == "pickle":
            self.db_connector = MemoryPoolConnector()
        else:
            raise ValueError("Unsupported db_connector type")

    def create_pool(self, uids):

        pool_id = self.db_connector.create_pool(uids)
        return pool_id

    def delete_pool(self, pool_id):
        self.db_connector.delete_pool(pool_id)

    def get_pool(self, pool_id):
        return self.db_connector.get_pool(pool_id)

    def add_memory(self, pool_id, memory, uid, shared_with=[]):
        self.db_connector.add_memory(pool_id, memory, uid, shared_with)

    def clear_memories(self, pool_id):
        self.db_connector.clear_memories(pool_id)

    def get_memories(self, pool_id):
        return self.db_connector.get_memories(pool_id)

    def get_shared_memories(self, pool_id, uid):
        return self.db_connector.get_shared_memories(pool_id, uid)

    def get_created_memories(self, pool_id, uid):
        return self.db_connector.get_created_memories(pool_id, uid)

    def get_context(self, pool_id, uid):
        shared_memories = self.get_shared_memories(pool_id, uid)
        context = f"""
        You have the following shared memories:
        """
        for memory in shared_memories:
            context += f"""
            Memory: {memory['memory']}
            Shared with: {memory["shared_with"]}
            """

        return context
