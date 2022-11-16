This utility is based on commands available in the .17 and .18 version of bitcoin-cli
This utility is intended to be run from the coin/src/util folder where your coin-cli is in coin/src.
Your coind daemon must be running and fully synced.
You should create a directory named data.
You'll want to edit the code to supply your destination wallet and/or passphrase for the consolidated transactions.
The utility will leave .json data in the data directory.  For good house keeping you may want to remove these files when finished with the utility.
Be absolutely certain you're using correct wallets.  If you send mainnet coin to a testnet wallet it will be lost forever!
Messing with your input transactions is risky and will cost you fees to transact.  Use this tool at your own risk!

Usage:
python3 iconsolidate.py


If using the config/config_example.json:
Working with windows paths and escape characters has been overly complicated.  For now the simple work around is:
A. If your dimecoin path has any spaces in it, ie C:\Program Files  you'll need to put the path info in the iconsolidate_windows.py (not in the .json)
B. If your dimecoin path does NOT have spaces in it, feel free to retain all paths in the .json.  You'll also need to comment out lines 26 and 28 and uncomment lines 27 and 29.

{
    "testnet": true,                            <--- Change this to false if using mainnet
    "passphrase": "",                           <--- If your wallet is already unlocked for staking, you can leave this blank.  If you want to periodically unlock for consolidation, put your passphrase here.
    "dest_wallet": "",                          <--- The wallet you want consolidated inputs to be sent to.  Very important you have this 100% accurate!
    "datadir": "",                              <--- If you're storing the blockchain in a custom dir, you'd specify it here i.e -datadir=C:\SomeFolder\Dimecoin\Blockchain
    "defaultCliPath": "",                       <--- The path to your cli exe, ie C:\SomeFolder\Dimecoin\Daemon
    "defaultCliExe": "dimecoin-cli.exe",        <--- The executable file for the cli goes here.
    "minInputAmount": 10000,                    <--- The max input amount to consolidate.  I.e If you want to consolidate all inputs under 1,000,000 you'd put 1000000 here (no quotations or commas)
    "eternalLoop": true,                        <--- If you want the program to loop forever periodically checking for inputs to consolidate leave this as true.  Set to false for single use.
    "checkfrequency": 240                       <--- Time in minutes of how often you want the program to loop looking for the max number of transactions to consolidate (22 for windows)
}
