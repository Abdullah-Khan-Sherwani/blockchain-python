"""
The wallet page.

Flask talks to the two shared dictionaries created by the blockchain process
(unspent outputs and the memory pool), so a transaction signed here is picked
up by the miner on its next block.
"""
from flask import Flask, render_template, request

from Blockchain.Backend.util.config import WEB_PORT
from Blockchain.client.sendBTC import SendBTC
from Blockchain.Backend.core.Tx import Tx

app = Flask(__name__)


@app.route("/", methods=["GET", "POST"])
def wallet():
    message = ""

    if request.method == "POST":
        FromAddress = request.form.get("fromAddress")
        ToAddress = request.form.get("toAddress")
        Amount = request.form.get("Amount", type=int)

        try:
            sendCoin = SendBTC(FromAddress, ToAddress, Amount, UTXOS)
            TxObj = sendCoin.prepareTransaction()

            scriptPubKey = sendCoin.scriptPubKey(FromAddress)
            verified = True

            if not TxObj:
                message = "Invalid Transaction"
            else:
                for index, tx in enumerate(TxObj.tx_ins):
                    if not TxObj.verify_input(index, scriptPubKey):
                        verified = False

                if verified:
                    MEMPOOL[TxObj.TxId] = TxObj
                    message = "Transaction added in memory Pool"
                else:
                    message = "Signature verification failed"
        except Exception as error:
            message = f"Error: {error}"

    return render_template("wallet.html", message=message)


def main(utxos, MemPool):
    global UTXOS
    global MEMPOOL
    UTXOS = utxos
    MEMPOOL = MemPool
    app.run(host="127.0.0.1", port=WEB_PORT, debug=False, use_reloader=False)
