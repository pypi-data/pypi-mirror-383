from pickledb import PickleDB
import time
import os


class SpaceConnector:
    def __init__(self, space_db='./data/pickle/space.db', memory_db='./data/pickle/space_memory.db'):

        os.makedirs(os.path.dirname(space_db), exist_ok=True)
        os.makedirs(os.path.dirname(memory_db), exist_ok=True)

        self.space_db = PickleDB(space_db)
        self.memory_db = PickleDB(memory_db)

    def create_space(self, uid, name, description, data=[]):
        space = {
            'uid': str(uid),
            'name': name,
            'description': description,
            'data': data
        }
        self.space_db.set(f'{uid}:{name}', space)
        self.space_db.save()

    def delete_space(self, uid, name):
        self.space_db.remove(f'{uid}:{name}')

    def update_space(self, uid, name, data):

        space = self.get_space(uid, name)

        if space:

            space['data'] = space['data']+data

            self.space_db.set(f'{uid}:{name}', space)

            self.space_db.save()

    def get_space(self, uid, name):
        return self.space_db.get(f'{uid}:{name}')

    def get_spaces(self, uid):
        keys = self.get_namespace_keys(self.space_db, f'{uid}')
        return [self.space_db.get(key) for key in keys]

    def add_memory(self, uid, memory):
        timestamp = int(time.time() * 1_000_000)
        self.memory_db.set(f'{str(uid)}:{timestamp}', memory)
        self.memory_db.save()

    def get_memories(self, uid):
        keys = self.get_namespace_keys(self.memory_db, f'{str(uid)}')
        return [self.memory_db.get(key) for key in keys]

    def clear_memories(self, uid):
        keys = self.get_namespace_keys(self.memory_db, f'{str(uid)}')
        for key in keys:
            self.memory_db.remove(key)
        self.memory_db.save()

    def get_namespace_keys(self, db_instance, namespace):
        return [key for key in db_instance.all() if key.startswith(f"{namespace}:")]


class MemoryPoolConnector:
    def __init__(self, memory_pool_db='./data/pickle/memory_pool.db'):
        os.makedirs(os.path.dirname(memory_pool_db), exist_ok=True)
        self.memory_pool_db = PickleDB(memory_pool_db)

    def create_pool(self, uids):
        pool_id = len(self.memory_pool_db.all())
        pool = {
            'id': str(pool_id),
            'uids': uids,
            'memories': []
        }
        self.memory_pool_db.set(f'{pool_id}', pool)
        self.memory_pool_db.save()
        return pool_id

    def delete_pool(self, pool_id):
        self.memory_pool_db.remove(f'{pool_id}')
        self.memory_pool_db.save()

    def get_pool(self, pool_id):
        return self.memory_pool_db.get(f'{pool_id}')

    def add_memory(self, pool_id, memory, uid, shared_with=[]):
        pool = self.memory_pool_db.get(str(pool_id))

        if pool:

            if str(uid) in pool['uids']:

                if len(shared_with) == 0:
                    shared_with = pool['uids']
                pool['memories'].append({
                    'uid': str(uid),
                    'memory': memory,
                    'shared_with': shared_with
                })

                self.memory_pool_db.set(f'{pool_id}', pool)
                self.memory_pool_db.save()

    def get_memories(self, pool_id):
        pool = self.memory_pool_db.get(f'{pool_id}')
        if pool:
            return pool['memories']
        return None

    def get_shared_memories(self, pool_id, uid):
        pool = self.memory_pool_db.get(f'{pool_id}')
        if pool:
            return [mem for mem in pool['memories'] if uid in mem['shared_with']]
        return []

    def get_created_memories(self, pool_id, uid):
        pool = self.memory_pool_db.get(f'{pool_id}')
        if pool:
            return [mem for mem in pool['memories'] if mem['uid'] == uid]
        return []

    def clear_memories(self, pool_id):
        pool = self.memory_pool_db.get(f'{pool_id}')
        if pool:
            pool['memories'] = []
            self.memory_pool_db.set(f'{pool_id}', pool)
            self.memory_pool_db.save()
