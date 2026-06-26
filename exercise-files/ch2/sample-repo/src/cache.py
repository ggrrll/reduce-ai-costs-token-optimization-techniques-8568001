_STORE, _TTL = {}, 60
def get_status(tx_id): return _STORE.get(tx_id)
def set_status(tx_id, val): _STORE[tx_id] = val
