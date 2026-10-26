"""
Tiny JSON file store used for the blockchain and for the wallet keys.

Both files live in the project's data/ folder. The path is worked out from the
project root, so starting the app from a different folder no longer breaks it.
"""
import json

from Blockchain.Backend.util.config import DATA_DIR


class BaseDB:
    def __init__(self):
        DATA_DIR.mkdir(exist_ok=True)
        self.filepath = DATA_DIR / self.filename

    def read(self):
        if not self.filepath.exists():
            print(f"File {self.filepath} not available")
            return False

        with open(self.filepath, "r") as file:
            raw = file.readline()

        if len(raw) > 0:
            data = json.loads(raw)
        else:
            data = []
        return data

    def write(self, item):
        data = self.read()
        if data:
            data = data + item
        else:
            data = item

        with open(self.filepath, "w+") as file:
            file.write(json.dumps(data))


class BlockchainDB(BaseDB):
    def __init__(self):
        self.filename = "blockchain"
        super().__init__()

    def lastBlock(self):
        data = self.read()

        if data:
            return data[-1]


class AccountDB(BaseDB):
    def __init__(self):
        self.filename = "account"
        super().__init__()
