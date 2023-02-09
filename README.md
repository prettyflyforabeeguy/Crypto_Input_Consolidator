# Crypto_Input_Consolidator
Consolidate transaction inputs from a wallet.<br>
<br>
This utility is based on commands available in the .17 and .18 version of bitcoin-cli<br>
Before running this program, your coind daemon must be running and fully synced.<br>

You'll need to edit the config.json to supply your destination wallet, passphrase, and required paths. See the config_example files for more details.<br>
If using windows you may need to edit the iconsolidate_windows.py lines 26 and 28 to speficy specfic paths.  
The utility will leave .json data in the data directory.  For good house keeping you may want to remove these files when finished with the utility.<br>
Be absolutely certain you're using correct wallets.  If you send mainnet coin to a testnet wallet it will be lost forever!<br>
Messing with your input transactions is risky and will cost you fees to transact.  Use this tool at your own risk!<br>
<br>
Usage:<br>
python3 iconsolidate_windows.py
or
python3 iconsolidate_linux.py