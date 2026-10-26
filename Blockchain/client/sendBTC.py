"""
Builds a signed transaction from one address to another.

It collects enough unspent outputs belonging to the sender, adds a change
output and signs every input with the sender's private key.
"""
from Blockchain.Backend.util.util import decode_base58
from Blockchain.Backend.core.Script import Script
from Blockchain.Backend.core.Tx import TxIn, TxOut, Tx
from Blockchain.Backend.core.database.database import AccountDB
from Blockchain.Backend.core.EllepticCurve.EllepticCurve import PrivateKey
import time


class SendBTC:
    def __init__(self, fromAccount, toAccount, Amount, UTXOS):
        self.COIN = 100000000
        self.FromPublicAddress = fromAccount
        self.toAccount = toAccount
        self.Amount = Amount * self.COIN
        self.utxos = UTXOS

    def scriptPubKey(self, PublicAddress):
        h160 = decode_base58(PublicAddress)
        script_pubkey = Script().p2pkh_script(h160)
        return script_pubkey

    def getPrivateKey(self):
        AllAccounts = AccountDB().read()
        if not AllAccounts:
            return None

        for account in AllAccounts:
            if account["PublicAddress"] == self.FromPublicAddress:
                return account["privateKey"]

    def prepareTxIn(self):
        TxIns = []
        self.Total = 0

        """Convert Public Address into Public Hash to find tx_outs that are locked to this hash"""

        self.From_address_script_pubkey = self.scriptPubKey(self.FromPublicAddress)
        self.fromPubKeyHash = self.From_address_script_pubkey.cmds[2]

        newutxos = {}

        # The miner process keeps filling this shared dictionary. Give it a
        # moment to catch up, but never leave the browser request hanging.
        deadline = time.time() + 15
        try:
            while len(newutxos) < 1 and time.time() < deadline:
                newutxos = dict(self.utxos)
                time.sleep(1)
        except Exception as e:
            print(f"Error in converting the Managed Dict to Normal Dict: {e}")

        for Txbyte in newutxos:
            if self.Total < self.Amount:
                TxObj = newutxos[Txbyte]

                for index, txout in enumerate(TxObj.tx_outs):
                    if txout.script_pubkey.cmds[2] == self.fromPubKeyHash:
                        self.Total += txout.amount
                        prev_tx = bytes.fromhex(TxObj.id())
                        TxIns.append(TxIn(prev_tx, index))
            else:
                break
        self.isBalanceEnough = True
        if self.Total < self.Amount:
            self.isBalanceEnough = False

        return TxIns

    def prepareTxOut(self):
        TxOuts = []
        to_scriptPubkey = self.scriptPubKey(self.toAccount)
        TxOuts.append(TxOut(self.Amount, to_scriptPubkey))

        """ Calculate Fee """
        self.fee = self.COIN
        self.changeAmount = self.Total - self.Amount - self.fee
        TxOuts.append(TxOut(self.changeAmount, self.From_address_script_pubkey))
        return TxOuts

    def signTx(self):
        secret = self.getPrivateKey()
        priv = PrivateKey(secret=secret)

        for index, input in enumerate(self.TxIns):
            self.TxObj.sign_input(index, priv, self.From_address_script_pubkey)

    def prepareTransaction(self):
        self.TxIns = self.prepareTxIn()

        if not self.isBalanceEnough:
            return False

        # Without the private key we cannot sign, so report a bad transaction
        # instead of crashing the wallet page.
        if self.getPrivateKey() is None:
            return False

        self.TxOuts = self.prepareTxOut()
        self.TxObj = Tx(1, self.TxIns, self.TxOuts, 0)
        self.TxObj.TxId = self.TxObj.id()
        self.signTx()
        return self.TxObj
