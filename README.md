# Blockchain Implementation in Python

A working Bitcoin-style blockchain written from scratch, with a wallet page that
can send coins to another address and a miner that keeps adding blocks in the
background.

| | |
|---|---|
| Name | Humayl Zafer |
| Student ID | 24k-5604 |
| Course Section | BS-FT 5C |
| Course | Blockchain |
| Language | Python 3.10 or newer |
| Libraries | Flask, pycryptodome |
| Storage | Plain JSON files in `data/` |

## What it does

The project runs two things at the same time. One is the mining loop, which
builds a new block roughly every second and writes it to disk. The other is a
small Flask page on `http://127.0.0.1:5900/` where you type a sender address, a
receiver address and an amount, and the app builds a signed transaction from
it. Signed transactions go into a memory pool, and the miner picks them up and
puts them in the next block.

Everything is built by hand. The elliptic curve maths, the transaction
serialisation, the scripting system, the merkle root and the proof of work are
all written in this repo. Flask is only used to render the form.

## How to run it

You need Python 3.10 or newer. The code was tested on Python 3.14.

```
pip install -r requirements.txt
python -m Blockchain.Backend.core.blockchain
```

Then open `http://127.0.0.1:5900/`.

Run the command from the project root, the folder that contains `Blockchain/`
and `data/`. If you prefer running the file from an editor, `blockchain.py`
also works, because it adds the project root to `sys.path` on its own.

To create a fresh wallet:

```
python -m Blockchain.client.account
```

That prints a private key and a public address and appends both to
`data/account`.

## Sending coins

The miner is paid at the address `1LYgXwYXw16GJXgDwHV7aCNijnQWYEdc1C`, and the
matching private key is already saved in `data/account` so the wallet works out
of the box.

1. Start the node and wait a few seconds. Blocks 0, 1, 2 and so on get mined,
   and each one pays 50 coins to the miner.
2. Open the wallet page.
3. From address: `1LYgXwYXw16GJXgDwHV7aCNijnQWYEdc1C`
4. To address: any valid address, for example one you generated with
   `account.py`.
5. Amount: 5
6. Press Send. The page should say `Transaction added in memory Pool`.

Now watch the terminal. Within a block or two you will see the block size jump
and the transaction disappear from the pool, which means it was mined.

## Project layout

```
Blockchain/
  Backend/
    core/
      block.py          block container
      blockheader.py    header and proof of work
      blockchain.py     entry point, mining loop, block assembly
      Tx.py             transactions, coinbase, signing and verification
      Script.py         small stack based scripting engine (P2PKH)
      database/
        database.py     JSON storage for chain and accounts
      EllepticCurve/
        EllepticCurve.py  secp256k1 keys, signatures, SEC and base58
        FieldElement.py   modular arithmetic
        Point.py          points on the curve
        op.py             opcodes used by the script engine
    util/
      util.py           hashing, varints, merkle root, difficulty helpers
      config.py         project paths and the web port
  client/
    account.py          creates a new key pair and address
    sendBTC.py          builds and signs a transaction
  Frontend/
    run.py              Flask app
    templates/wallet.html
    static/css/style.css
data/
  blockchain            the chain, one JSON array
  account               stored key pairs
```

## How it works

### Keys and addresses

A private key is just a random 256-bit number. Multiplying it by the secp256k1
generator point gives the public key. I take the x coordinate (32 bytes) and
prefix it with `02` or `03` depending on whether y is even or odd, which is the
compressed form. That gets hashed with SHA-256 and then RIPEMD-160. The result
is prefixed with `00` for a mainnet address, checksummed with the first four
bytes of a double SHA-256, and encoded in base58. The leading zero bytes turn
into the `1` characters at the start of every address.

All of that lives in `EllepticCurve.py`. Field arithmetic is a class that wraps
an integer and a prime, and a point is two field elements. Adding and doubling
points follows the standard chord and tangent formulas.

### Transactions

A transaction has a version, a list of inputs, a list of outputs and a locktime.
Each input points at an earlier transaction id and an output index. Each output
holds an amount in satoshis and a locking script.

The transaction id is the double SHA-256 of the serialised transaction, reversed
so it reads in the usual order.

To sign, the code rebuilds a modified copy of the transaction where the input
being signed carries the previous output's script, hashes it, and signs that
hash with the private key. The signature is DER encoded with a sighash byte
appended, then the public key is attached next to it.

Verification does the same hash and runs the combined script.

### Scripts

`Script.py` implements the small stack machine. The locking script for a normal
payment is `OP_DUP OP_HASH160 <hash160> OP_EQUALVERIFY OP_CHECKSIG`. The
unlocking script pushes the signature and the public key. When both are joined
and evaluated, the stack ends with a true value. Anything else fails.

### Coinbase and rewards

Each block starts with a coinbase transaction. It has one input pointing at a
zero hash and index `0xFFFFFFFF`, and the block height is written into its
script. Its output pays 50 coins to the miner. If the block also contains
normal transactions, the sum of their fees is added to that reward, so the
miner collects both.

### Memory pool and UTXOs

The Flask process and the miner are separate processes, so they share two
dictionaries made with `multiprocessing.Manager`. One holds the memory pool:
transactions that are signed and verified but not mined yet. The other holds the
unspent outputs, keyed by transaction id.

When a transaction arrives, the app checks the signature and drops it in the
pool. On the next block, the miner reads the pool, calculates the fee by
subtracting total outputs from total inputs, adds the coinbase, mines the block,
then removes the spent outputs from the UTXO set and clears those transactions
from the pool.

### Merkle root and block header

The block header is 80 bytes: version, previous block hash, merkle root,
timestamp, difficulty bits and nonce. The merkle root comes from pairing the
transaction ids, hashing each pair, and repeating until one hash is left. If a
level has an odd number of hashes, the last one is duplicated.

### Proof of work

Mining means hashing the header over and over with a different nonce until the
result is numerically smaller than the target. The starting target in
`blockchain.py` is

```
0x0000FFFF00000000000000000000000000000000000000000000000000000000
```

which needs about 16 leading zero bits, so a block takes a fraction of a second
on a normal laptop. `target_to_bits` converts that number into the compact
`bits` field stored in the header.

The block size is 80 bytes for the header plus the serialised size of every
transaction in it.

## Notes

The chain and the accounts are stored in `data/` as plain JSON. Delete
`data/blockchain` if you want to start again from the genesis block. Keep
`data/account`, or run `account.py` again to make a new wallet.

The Flask development server is fine for a local demo. For anything public you
would run it behind a real WSGI server.

This project was built by following the "Build a Blockchain from Scratch in
Python" video course by Codies Alert, and then adapted to run cleanly on
Windows and Linux without the hardcoded paths from the original code.
