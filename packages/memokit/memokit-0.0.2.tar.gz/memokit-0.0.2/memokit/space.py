from memokit.db import SpaceConnector
import json


class Space:
    def __init__(self, db_connector=None):
        if db_connector is None or db_connector == "pickle":
            self.db_connector = SpaceConnector()
        else:
            raise ValueError("Unsupported db_connector type")

    def create_space(self, uid, name, description, data=[]):
        self.db_connector.create_space(
            uid, name, description, data)

    def get_space(self, uid, name):
        return self.db_connector.get_space(uid, name)

    def get_spaces(self, uid):
        return self.db_connector.get_spaces(uid)

    def add_memory(self, uid, memory):
        self.db_connector.add_memory(uid, memory)

    def get_memories(self, uid):
        return self.db_connector.get_memories(uid)

    def update_space(self, uid, name, data):
        self.db_connector.update_space(uid, name, data)

    def clear_memories(self, uid):
        self.db_connector.clear_memories(uid)

    def get_space_context(self, uid, space_name):
        space = self.get_space(uid, space_name)
        context = f"""
        You have the following memories:
        {space['data']}
        """
        return context

    def get_spaces_context(self, uid):
        spaces = self.get_spaces(uid)

        context = "You have the following memories:"
        for space in spaces:
            space = self.get_space(uid, space['name'])
            context += f"""
            {space['data']}
            """

        return context

    def summarize_memories(self, uid, call_openai):
        try:
            spaces = self.get_spaces(uid)
            memories = self.get_memories(uid)
            memory_list = "\n".join(
                [f"{i+1}. {memory}" for i, memory in enumerate(memories)])
            spaces_list = "\n".join(
                [f"{i+1}. {space['name']}: {space['description']}" for i, space in enumerate(spaces)])
            prompt = f"""
            You have the following spaces:
            {spaces_list}

            You have the following memories:
            {memory_list}

            Your Tasks:
            
            1. Shorten the memories to key words.
            2. Analyze the memories and organize them into the appropriate spaces.
            3. IMPORTANT: You must respond with ONLY a JSON(double quotes) array in exactly this format, no additional text or formatting:
            {[{
                "space": "space_name1",
                "data": [
                    "memory1",
                    "memory2"
                ]
            }, {
                "space": "space_name2",
                "data": [
                    "memory3",
                    "memory4"
                ]
            }]}
            
            Replace "space_name" with actual space names from the list above.
            """

            response = call_openai(prompt)

            response_json = json.loads(response)

            for item in response_json:
                self.update_space(uid, item['space'], item['data'])

            self.clear_memories(uid)
        except Exception as e:
            print(e)
