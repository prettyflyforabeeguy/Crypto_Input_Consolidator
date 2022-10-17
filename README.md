# Crypto_Input_Consolidator
Consolidate transaction inputs from a wallet.<br>
<br>
This utility is based on commands available in the .17 and .18 version of bitcoin-cli<br>
This utility is intended to be run from the coin/src/util folder where your coin-cli is in coin/src.<br>
Your coind daemon must be running and fully synced.<br>
You should create a directory named data.<br>
You'll want to edit the code to supply your destination wallet and/or passphrase for the consolidated transactions.<br>
The utility will leave .json data in the data directory.  For good house keeping you may want to remove these files when finished with the utility.<br>
Be absolutely certain you're using correct wallets.  If you send mainnet coin to a testnet wallet it will be lost forever!<br>
Messing with your input transactions is risky and will cost you fees to transact.  Use this tool at your own risk!<br>
<br>
Usage:<br>
python3 iconsolidate.py
