# Memokit 

Memokit is a lightweight AI memory toolkit that helps AI applications manage medium-term memory.

## Installation

**Install from pypi:**

```bash
pip install memokit
```

**Or clone the repository:**

```bash
git clone https://github.com/AmeNetwork/memokit.git
cd memokit
pip install -r requirements.txt
```

## Usage
**Memokit Space:**  
Custom memory spaces, different spaces are used to store different memories, and they will automatically classify and store your memories.

```python
from memokit import Space 
space=Space()
# create space for sport 
space.create_space(uid="alice", space_name="sport", space_description="sport space")
# add memory to sport space 
space.add_memory(uid="alice", memory='I like playing football')
```

Full Example Here: [space_example.py](https://github.com/AmeNetwork/memokit/blob/main/examples/space_example.py)

**Memokit Pool:**   
Memokit Pool is a shared memory pool that allows different users and agents to share the same pool, enabling memory sharing and management.

```python
from memokit.pool import MemoryPool
pool = MemoryPool()

# create a memory pool for alice and bob
pool_id = pool.create_pool(["alice", "bob"])

# add memory to pool
pool.add_memory(
    pool_id=pool_id,
    memory="we will hold a meeting at 10am on Wednesday next week",
    uid="alice"
)
```
Full Example Here: [pool_example.py](https://github.com/AmeNetwork/memokit/blob/main/examples/pool_example.py)

