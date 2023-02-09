#########################################################################
##  DIMECOIN input consolidator v0.0.3                                 ##
##  Created by Dalamar 2/8/2023                                        ##
##  This utility is intended for consolidating input                   ##
##  transactions.                                                      ##
##  Calculations are delicate and can result in the loss of coin       ##
##  use this at your own risk!                                         ##
#########################################################################

import os, sys
import json
import time, datetime
import iconfig as _config

class DimeConsolidator:
    def __init__(self):
        self._config_dict = _config.Config().config_dict
        self.dest_wallet = self._config_dict.get('dest_wallet')
        self.num_of_txns = 66  # don't change this number
        self.max_txns = 0
        self.fee = 0
        self.txn_id = ""
        self.hexoutput = ""
        self.eternalLoop = self._config_dict.get('eternalLoop')
        self.passphrase = self._config_dict.get('passphrase')  # If you want you can hard code your passphrase.  Not recomended.  However it's useful for a large number of transactions.
        #self.defaultCliPath = "/home/pi/dimecoin/src"  # Path where your cli.exe is located
        self.defaultCliPath = self._config_dict.get('defaultCliPath')
        self.datadir = self._config_dict.get('datadir')  # Leave this blank if you're not using the -datadir argument. i.e -datadir=C:\Program Files\Dimecoin\Blockchain
        self.defaultCliExe = self._config_dict.get('defaultCliExe')  # the cli executable file
        self.pathandCli = self.defaultCliPath + "/" + self.defaultCliExe
        self.testnet = self._config_dict.get("testnet")
        self.unencrypted = False
        self.wstatus = False

    def log_output(self,fname, data, method):
        #Store API results in a file
        filepath = self.defaultCliPath + "/data/" + fname
        if os.path.isfile(filepath):
            pass
        try:
            file = open(filepath, method)
            file.close()
            fd = os.open(filepath, os.O_RDWR)
            line = str.encode(data)
            numBytes = os.write(fd, line)
            print(f"Creating {filepath} bytes:{numBytes}")
            os.close(fd)

        except:
            print("Failed to write to /data")


    def read_json(self,filename):
        try:
            with open(filename) as data_file:
                file_dict = json.load(data_file)
                return file_dict
        except Exception as e:
            print(f"There was a problem reading from: {filename}")

    def get_wallet_info(self):
        if self.testnet != False:
            command = f"{self.pathandCli} -testnet {self.datadir} getwalletinfo"
        else:
            command = f"{self.pathandCli} {self.datadir} getwalletinfo"
        print(f"executing: {command}")    
        winfo = os.popen(command)
        wallet_info = winfo.read()
        self.log_output("winfo.json", wallet_info)
        walletinfofile = self.defaultCliPath + "/data/winfo.json"
        winfo_jdata = self.read_json(walletinfofile)
        #wstatus = winfo_jdata["unlocked_until"]
        try:
             self.wstatus = winfo_jdata["unlocked_until"]
        except KeyError: 
             print("Error unlocking wallet.  Is your wallet encrypted?")
             print("Proceeding with unencrypted wallet...")
             self.unencrypted = True
             self.wstatus = 1

        #print(wallet_info)
        if self.wstatus > 0:
            print("Wallet unlocked: TRUE")
            return True
        else:
            print("Wallet unlocked: FALSE")
            return False

    def consolidate_txns(self,jdata,num_of_txns):
        if len(jdata) > num_of_txns:
            txn_list_amnt = []
            txn_list_noamnt = []
            for i in range(num_of_txns):
                #print(jdata[i])
                txn_summary_amnt = {"txid":str(jdata[i]['txid']),"vout":int(jdata[i]['vout']),"scriptPubKey":str(jdata[i]['scriptPubKey']),"amount":float(jdata[i]['amount'])}
                txn_summary_noamnt = {"txid":str(jdata[i]['txid']),"vout":int(jdata[i]['vout']),"scriptPubKey":str(jdata[i]['scriptPubKey'])}
                txn_list_amnt.append(txn_summary_amnt)
                txn_list_noamnt.append(txn_summary_noamnt)
            print(json.dumps(txn_list_amnt, indent=4))
            return txn_list_amnt, txn_list_noamnt
        else:
            print(f"Less than {num_of_txns} unspent transactions available")

    def total_txn_amnts(self,txn_list_amnt, fee):
        sum = 0
        for i in range(len(txn_list_amnt)):
            #print(txn_list[i]["amount"])
            sum = sum + txn_list_amnt[i]["amount"]
        total = float(sum) - float(fee)
        print(f"total amount(s) {sum} minus {str(fee)} fee = {str(total)}")
        return total


    def create_txn(self,txn_list_noamnt, totalamnt):
        wallet_amnt = {self.dest_wallet:totalamnt}
        txn_list_noamnt = json.dumps(txn_list_noamnt)
        wallet_amnt = json.dumps(wallet_amnt)
        if self.testnet != False:
            command = f"{self.pathandCli} -testnet {self.datadir} createrawtransaction '{txn_list_noamnt}' '{wallet_amnt}'"
        else:
            command = f"{self.pathandCli} {self.datadir} createrawtransaction '{txn_list_noamnt}' '{wallet_amnt}'"
        print(command)
        createtxn = os.popen(command)
        txn_hex_code = createtxn.read()
        return txn_hex_code

    def unlock_wallet(self,passphrase, unlocktime):
        # Unlock the wallet so transactions can be sent
        if self.testnet != False:
            command = f"{self.pathandCli} -testnet {self.datadir} walletpassphrase {passphrase} {unlocktime}"
        else:
            command = f"{self.pathandCli} {self.datadir} walletpassphrase {passphrase} {unlocktime}"
        unlock = os.popen(command)
        print(f"Unlocking wallet for {str(unlocktime)} seconds...")

    def sign_txn(self,txn_hex_code):
        # Sign the transaction
        if self.testnet != False:
            command = f"{self.pathandCli} -testnet {self.datadir} signrawtransactionwithwallet {txn_hex_code}"
        else:
            command = f"{self.pathandCli} {self.datadir} signrawtransactionwithwallet {txn_hex_code}"
        signtxn = os.popen(command)
        print("Signing transaction...")
        hexoutput =  signtxn.read()
        self.log_output("txnhexcode.json", hexoutput, 'w+')
        hexcodefile = self.defaultCliPath + "/data/txnhexcode.json"
        hexoutput_jdata = self.read_json(hexcodefile)
        return hexoutput_jdata

    def send_txn(self,signed_hex):
        # Send the signed transaction
        if self.testnet != False:
            command = f"{self.pathandCli} -testnet {self.datadir} sendrawtransaction {signed_hex}"
        else:
            command = f"{self.pathandCli} {self.datadir} sendrawtransaction {signed_hex}"
        print("Sending transaction...")
        txn = os.popen(command)
        txn_id = txn.read()
        return txn_id

    def view_txn(self, txn_id):
        # Optional feature to view the transaction after it's been sent.
        if self.testnet != False:
            command = f"{self.pathandCli} -testnet {self.datadir} gettransaction {txn_id}"
        else:
            command = f"{self.pathandCli} {self.datadir} gettransaction {txn_id}"
        print(f"executing: {command}")
        txn = os.popen(command)
        txn_output = txn.read()
        print(txn_output)

    def getbalance(self):
        # Query the wallet balance
        if self.testnet != False:
            command = f"{self.pathandCli} -testnet {self.datadir} getbalance"
        else:
            command = f"{self.pathandCli} {self.datadir} getbalance"
        print(f"executing: {command}")
        bal = os.popen(command)
        balance = bal.read()
        return balance

    def getunspent(self, maxinput):
        # Locate all unspent and unlocked transactions for consolidation
        if self.testnet != False:
            command = f"{self.pathandCli} -testnet {self.datadir} listunspent"
        else:
            command = f"{self.pathandCli} {self.datadir} listunspent"
        print(f"executing: {command}")
        unspent = os.popen(command)
        # convert the stream to a list
        list_unspent = unspent.read()
        self.log_output('unspent.json', list_unspent, 'w+')

        low_amount_list = []
        unspentfile = self.defaultCliPath + "/data/unspent.json"
        jdata = self.read_json(unspentfile)
        # parse the list of unspent transactions keeping only those under the requested amount
        print(jdata)
        for i in range(len(jdata)):
            if jdata[i]['amount'] <= int(maxinput):
                low_amount_list.append(jdata[i])
        if low_amount_list != "":
            lowamountjson = json.dumps(low_amount_list)
            self.log_output("unspent.json", lowamountjson, 'w+')
            jdata = self.read_json(unspentfile)
            if len(jdata) <= 0 and self.eternalLoop == False:
                print(f"Failed to find any inputs with an amount below: {str(maxinput)}")
                sys.exit(0)
        else:
            if self.eternalLoop == False:
                print(f"Not enough inputs with an amount below: {str(maxinput)}.  Waiting to try again later.")
            else:
                print(f"Failed to find any inputs with an amount below: {str(maxinput)}")
                sys.exit(0)
        return jdata

    def confirmation(self, info):
        confirm = input(f"Are you absolutely sure this {info} is correct? (Y/N) :")
        if confirm.upper() == "Y":
            return True
        else:
            return False

    def startup(self):
        unlocktime = 60
        cliPath = self._config_dict.get('defaultCliPath')
        cliPath = self.defaultCliPath
        if cliPath == None:
            cliPath = input("\nEnter the full path to your coin cli. i.e. C:\Program Files\Dimecoin\daemon (leave blank for default install path): ")
            if cliPath == "":
                cliPath = self.defaultCliPath
            else:
                self.defaultCliPath = cliPath
        print(f"using cli path: {self.defaultCliPath}")

        cliExe = self._config_dict.get('defaultCliExe')
        cliExe = self.defaultCliExe
        if cliExe == None:
            cliExe = input("Enter your cli .exe file name. i.e. dimecoin-cli.exe (leave blank for default exe file): ")
            if cliExe == "":
                cliExe = self.defaultCliExe
            else:
                self.defaultCliExe = cliExe
        print(f"using cli exe: {self.defaultCliExe}")

        testnetEnabled = self._config_dict.get('testnet')
        if testnetEnabled == True:
            print(f"using: -testnet")
        if testnetEnabled == False:
            print("*** WARNING *** USING PRODUCTION!!!")
        if testnetEnabled == None:
            testnetEnabled = input("Will you be using testnet? (leave blank for Y): ")
            if (testnetEnabled.upper() == "" or testnetEnabled.upper() == "Y"):
                self.testnet = True
                print(f"using: -testnet")
            else:
                self.testnet = False
                print("*** WARNING *** USING PRODUCTION!!!")

        rcv_wallet = self._config_dict.get('dest_wallet')
        rcv_wallet = self.dest_wallet
        if rcv_wallet == None:
            rcv_wallet = input(f"Enter the destination wallet address.  When inputs are consolidated they'll need to be sent to yourself to a valid receiving address. Pres enter to use {self.dest_wallet}: ")
            if rcv_wallet == "":
                rcv_wallet = self.dest_wallet
                if self.dest_wallet == "":
                    print("Error! No wallet provided.  Closing app!")
                    sys.exit(0)
            else:
                conf = self.confirmation(self.dest_wallet)
                if conf == True:
                    print(f"using destination wallet: {self.dest_wallet}")
                    pass
                else:
                    self.dest_wallet = input("Enter the destination wallet address again. :")
                    conf = self.confirmation(self.dest_wallet)
                    if conf == True:
                        pass
                    else:
                        print("Error! Bad or no wallet provided.  Closing app!")
                        sys.exit(0)
        print(f"using destination wallet: {self.dest_wallet}")
        
        dataFolder = self.defaultCliPath + "/data"
        os.popen(f"mkdir {dataFolder}")

        try:
            balance = self.getbalance()
            print(f"Current wallet balance is: {balance}")
        except Exception as e:
            print("*** ERROR ***")
            print("Is your daemon running?")
            print(f"{e}")
            sys.exit(0)

        maxinput = self._config_dict.get('minInputAmount')
        if maxinput == None or maxinput == "":
            maxinput = input("What is the max input amount you'd like me to select for consolidation? (i.e. 10000): ")
            if maxinput == "":
                print("No input size prefrence provided, defaulting to include inputs up to 1 billion in size")
                maxinput = 999999999
            jdata = self.getunspent(maxinput)
            self.max_txns = int(len(jdata))
            txncount = len(jdata) - 1
            print(f"You have {txncount} unspent transactions.")
            if (len(jdata) - 1) == 0:
                sys.exit(0)
            if txncount > self.num_of_txns:    
                wanttoloop = input("Do you want the program to loop using the info you've provided? (y/n): ")
                wanttoloop = wanttoloop.upper()
            else:
                wanttoloop = "N"
            
            if wanttoloop == "Y":
                loopmax = int(txncount/self.num_of_txns)          
                loopqty = input(f"How many times would you like to loop this consolidation activity? (Max is {loopmax}): ")
                if int(loopqty) <= 0 or int(loopqty) > int(loopmax) or int(loopqty) == "":
                    print("ERROR! Something is wrong with the loop number provided.")
                    sys.exit(0)
                else: 
                    print(f"Okay, looping {loopqty} times!")
                    if self.passphrase == "":
                        wstatus = self.get_wallet_info()
                    else:
                        # Using unlocktime to scale how long to unlock the wallet based on number of inputs being consolidated.
                        # The wallet needs to remain unlocked for the duration of the consolidation cycle.
                        unlocktime = int(loopqty) * 60
                        self.unlock_wallet(self.passphrase, unlocktime)
                        wstatus = True
                    
                    for x in range(int(loopqty)):
                        print(f"Starting loop number {x+1} of {str(loopqty)}")
                        self.num_of_txns = 22
                        self.main(jdata, wstatus, maxinput)
                        self.txn_id = self.send_txn(str(self.hexoutput['hex']))
                        if self.txn_id != "":
                            print(f"********** SUCCESS! **********\nTransaction id: {self.txn_id}")
                            timestamp = datetime.datetime.now()
                            print(timestamp)
                            self.log_output("transaction.log", str(timestamp) + ", " + self.txn_id, 'a')
                            time.sleep(1)
                
                    print("Finished!")
            else:
                unlocktime = 60
                # Windows command line has a 8191 character limitation so we cap combinable inputs at 22.
                if txncount >= self.num_of_txns:
                    maxtxns = self.num_of_txns
                else:
                    maxtxns = txncount
            
                self.num_of_txns = input(f"How many transactions would you like to combine? (max {str(maxtxns)}): ")
                if self.num_of_txns == "" or int(self.num_of_txns) <= 0 or int(self.num_of_txns) > maxtxns:
                    print("Invalid number of transactions provided!")
                    sys.exit(0)

                if self.unencrypted == True:
                    self.wstatus = True
                elif self.passphrase == "" and self.wstatus == False:
                    self.wstatus = self.get_wallet_info()
                else:
                    self.unlock_wallet(self.passphrase, unlocktime)
                    self.wstatus = True

                self.main(jdata, self.wstatus, maxinput)

                go = input("Make sure everything looks correct.\nProceed? y/n: ")
                if go.lower() == "y":
                    self.txn_id = self.send_txn(str(self.hexoutput['hex']))
                if self.txn_id != "":
                    print(f"********** SUCCESS! **********\nTransaction id: {self.txn_id}")
                    timestamp = datetime.datetime.now()
                    print(timestamp)
                    self.log_output("transaction.log", str(timestamp) + ", " + self.txn_id, 'a')
                    view = input("View this transactions y/n: ")
                    if view.lower() == "y":
                        self.view_txn(self.txn_id)
                    else:
                        sys.exit(0)
                else:
                    print("Error something is wrong with this transaction. Fee too small? Wallet unlock time expired? Try combining fewer inputs?  Please try again.")
                    sys.exit(0)
        else:
            # Loop whenever input quantity reaches maxinputs
            if self.eternalLoop == True:
                while True:
                    jdata = self.getunspent(maxinput)
                    self.max_txns = int(len(jdata))
                    txncount = len(jdata) - 1
                    if txncount == -1:
                        print(f"You have NO unspent transactions less than {maxinput}. Try increasing your minInputAmount in the config_example.json")
                    else:
                        print(f"You have {txncount} unspent transactions less than {maxinput}.")

                    if txncount >= 22:
                        # unlock wallet
                        if self.unencrypted == True:
                            self.wstatus = True
                        elif self.passphrase == "" and self.wstatus == False:
                            self.wstatus = self.get_wallet_info()
                        else:
                            self.unlock_wallet(self.passphrase, unlocktime)
                            self.wstatus = True
                 
                        self.main(jdata, self.wstatus, maxinput)
                        self.txn_id = self.send_txn(str(self.hexoutput['hex']))
                        if self.txn_id != "":
                            print(f"********** SUCCESS! **********\nTransaction id: {self.txn_id}")
                            timestamp = datetime.datetime.now()
                            print(timestamp)
                            self.log_output("transaction.log", str(timestamp) + ", " + self.txn_id, 'a')
                            time.sleep(.25)
                    else:
                        waittime = self._config_dict.get('checkfrequency')
                        waittime = int(waittime) * 60
                        print(datetime.datetime.now())
                        print(f"Waiting {(waittime / 60)} minute(s) until there are at least {self.num_of_txns} unspent transactions before checking again.")
                        time.sleep(int(waittime))
            else:
                print("ERROR! There is a config problem.  Did you fill out the config.json?  Is eternalLoop set to true?")
                sys.exit(0)


    def main(self,jdata, wstatus, maxinput):
        unlocktime = 60
        jdata = self.getunspent(maxinput)
        print(f"You have {len(jdata) - 1} unspent transactions.")
        if int(self.num_of_txns) < 10:
            self.fee = 0.01
        else:
            self.fee = int(self.num_of_txns) * 0.0015

        if int(self.num_of_txns) > 0 and int(self.num_of_txns) <= self.max_txns:
            txn_list_amnt, txn_list_noamnt = self.consolidate_txns(jdata,int(self.num_of_txns))
        else:
            print("Invalid number of transactions!")
            sys.exit(0)

        totalamnt = self.total_txn_amnts(txn_list_amnt, float(self.fee))
        txn_hex_code = self.create_txn(txn_list_noamnt, totalamnt)
        print(f"Generating Transaction Hex Code...")

        # Need to unlock wallet before txn can be signed
        if self.passphrase == "" or wstatus == False:
            print("We must unlock your wallet to sign the transaction.")
            self.passphrase = input("Enter your wallet passphrase:")
            self.unlock_wallet(self.passphrase, unlocktime)

        print("Building transaction...")
        self.hexoutput = self.sign_txn(txn_hex_code)
        #print(self.hexoutput)
        print("Generating your Signed Hex Output...")


if __name__ == '__main__':
    _dc = DimeConsolidator()
    welcome = f"""************************************************************************************************************
*   Welcome to the cli input consolidation tool.  This tool can combine inputs into single transactions.   * 
*   Changing coin inputs can be delicate and if not done correctly can result in coin loss.                *
*   Use this utility at your own risk!                                                                     *
************************************************************************************************************"""
    print(welcome)
    _dc.startup()
