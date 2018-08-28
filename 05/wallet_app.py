from tkinter import *
from tkinter import messagebox
from tkinter import filedialog
from tkinter.ttk import Button, Style
from tkinter import ttk
import binascii
import os
import json
import sys
import base64
import datetime
import pprint
import copy

from core.client_core import ClientCore as Core
from transaction.transactions import Transaction
from transaction.transactions import CoinbaseTransaction
from transaction.transactions import TransactionInput
from transaction.transactions import TransactionOutput
from transaction.utxo_manager import UTXOManager as UTXM
from utils.key_manager import KeyManager
from utils.rsa_util import RSAUtil
from p2p.message_manager import (

    MSG_NEW_TRANSACTION,
    MSG_ENHANCED,
)


class SimpleBC_Gui(Frame):

  
    def __init__(self, parent, my_port, c_host, c_port):
        Frame.__init__(self, parent)
        self.parent = parent
        self.parent.protocol('WM_DELETE_WINDOW', self.quit)
        self.coin_balance = StringVar(self.parent, '0')
        self.status_message = StringVar(self.parent, 'Ready')
        self.c_core = None
        self.initApp(my_port, c_host, c_port)
        self.setupGUI()

    def quit(self, event=None):
        """
        アプリの終了
        """
        self.c_core.shutdown()
        self.parent.destroy()


    def initApp(self, my_port, c_host, c_port):
        """
        ClientCoreとの接続含めて必要な初期化処理はここで実行する
        """
        print('SimpleBitcoin client is now activating ...: ')

        self.km = KeyManager() 
        self.um = UTXM(self.km.my_address())
        self.rsa_util = RSAUtil()

        self.c_core = Core(my_port, c_host, c_port, self.update_callback)
        self.c_core.start()

        # テスト用途（本来はこんな処理しない）
        t1 = CoinbaseTransaction(self.km.my_address())
        t2 = CoinbaseTransaction(self.km.my_address())
        t3 = CoinbaseTransaction(self.km.my_address())

        transactions = []
        transactions.append(t1.to_dict())
        transactions.append(t2.to_dict())
        transactions.append(t3.to_dict())
        self.um.extract_utxos(transactions)

        self.update_balance()
      

    def display_info(self, title, info):
        """
        ダイアログボックスを使ったメッセージの表示
        """
        f = Tk()
        label = Label(f, text=title)
        label.pack()
        info_area = Text(f, width=70, height=50)
        info_area.insert(INSERT, info)
        info_area.pack()
          

    def update_callback(self):
        print('update_callback was called!')
        s_transactions = self.c_core.get_stored_transactions_from_bc()
        print(s_transactions)
        self.um.extract_utxos(s_transactions)
        self.update_balance()


    def update_status(self, info):
        """
        画面下部のステータス表示内容を変更する
        """  
        self.status_message.set(info)


    def update_balance(self):
        """
        総額表示の内容を最新状態に合わせて変更する
        """
        bal = str(self.um.my_balance)
        self.coin_balance.set(bal)


    def create_menu(self):
        """
        メニューバーに表示するメニューを定義する
        """
        top = self.winfo_toplevel()
        self.menuBar = Menu(top)
        top['menu'] = self.menuBar

        self.subMenu = Menu(self.menuBar, tearoff=0)
        self.menuBar.add_cascade(label='Menu', menu=self.subMenu)
        self.subMenu.add_command(label='Show My Address', command=self.show_my_address)
        self.subMenu.add_command(label='Load my Keys', command=self.show_input_dialog_for_key_loading)
        self.subMenu.add_command(label='Update Blockchain', command=self.update_block_chain)
        self.subMenu.add_separator()
        self.subMenu.add_command(label='Quit', command=self.quit)

        self.subMenu2 = Menu(self.menuBar, tearoff=0)
        self.menuBar.add_cascade(label='Settings', menu=self.subMenu2)
        self.subMenu2.add_command(label='Renew my Keys', command=self.renew_my_keypairs)

        self.subMenu3 = Menu(self.menuBar, tearoff=0)
        self.menuBar.add_cascade(label='Advance', menu=self.subMenu3)
        self.subMenu3.add_command(label='Show Blockchain', command=self.show_my_block_chain)


    
    def show_my_address(self):
        f = Tk()
        label = Label(f, text='My Address')
        label.pack()
        key_info = Text(f, width=70, height=10)
        my_address = self.km.my_address()
        key_info.insert(INSERT, my_address)
        key_info.pack()


    def show_input_dialog_for_key_loading(self):
    
        def load_my_keys():
            # ファイル選択ダイアログの表示
            f2 = Tk()
            f2.withdraw()
            fTyp = [('','*.pem')]
            iDir = os.path.abspath(os.path.dirname(__file__))
            messagebox.showinfo('Load key pair','please choose your key file')
            f_name = filedialog.askopenfilename(filetypes = fTyp,initialdir = iDir)
            
            try:
                file = open(f_name)
                data = file.read()
                target = binascii.unhexlify(data)
                # TODO: 本来は鍵ペアのファイルが不正などの異常系処理を考えるべき
                self.km.import_key_pair(target, p_phrase.get())
            except Exception as e:
                print(e)
            finally:
                # TODO: 所有コインの再確認処理を入れる必要あり
                file.close()
                f.destroy()
                f2.destroy()
                self.um = UTXM(self.km.my_address())
                self.um.my_balance = 0
                self.update_balance()
    
        f = Tk()
        label0 = Label(f, text='Please enter pass phrase for your key pair')
        frame1 = ttk.Frame(f)
        label1 = ttk.Label(frame1, text='Pass Phrase:')

        p_phrase = StringVar()

        entry1 = ttk.Entry(frame1, textvariable=p_phrase) 
        button1 = ttk.Button(frame1, text='Load', command=load_my_keys)

        label0.grid(row=0,column=0,sticky=(N,E,S,W))
        frame1.grid(row=1,column=0,sticky=(N,E,S,W))
        label1.grid(row=2,column=0,sticky=E)
        entry1.grid(row=2,column=1,sticky=W)
        button1.grid(row=3,column=1,sticky=W)


    def update_block_chain(self):
        self.c_core.send_req_full_chain_to_my_core_node()

    def renew_my_keypairs(self):
        """
        利用する鍵ペアを更新する。
        """
        def save_my_pem():
            self.km = KeyManager()
            my_pem = self.km.export_key_pair(p_phrase)
            my_pem_hex = binascii.hexlify(my_pem).decode('ascii')
            # とりあえずファイル名は固定
            path = 'my_key_pair.pem'
            f1 = open(path,'a')
            f1.write(my_pem_hex)
            f1.close()

            f.destroy()
            self.um = UTXM(self.km.my_address())
            self.um.my_balance = 0
            self.update_balance()
            
        f = Tk()
        f.title('New Key Gene')
        label0 = Label(f, text='Please enter pass phrase for your new key pair')
        frame1 = ttk.Frame(f)
        label1 = ttk.Label(frame1, text='Pass Phrase:')

        p_phrase = StringVar()

        entry1 = ttk.Entry(frame1, textvariable=p_phrase) 
        button1 = ttk.Button(frame1, text='Generate', command=save_my_pem)

        label0.grid(row=0,column=0,sticky=(N,E,S,W))
        frame1.grid(row=1,column=0,sticky=(N,E,S,W))
        label1.grid(row=2,column=0,sticky=E)
        entry1.grid(row=2,column=1,sticky=W)
        button1.grid(row=3,column=1,sticky=W)


    def show_my_block_chain(self):
        """
        自分が保持しているブロックチェーンの中身を確認する
        """
        mychain = self.c_core.get_my_blockchain()
        if mychain is not None:
            mychain_str = pprint.pformat(mychain, indent=2)
            self.display_info('Current Blockchain', mychain_str)
        else:
            self.display_info('Warning', 'Currently Blockchain is empty...')


  
    def setupGUI(self):
        """
        画面に必要なパーツを並べる
        """

        self.parent.bind('<Control-q>', self.quit)
        self.parent.title('SimpleBitcoin GUI')
        self.pack(fill=BOTH, expand=1)

        self.create_menu()

        lf = LabelFrame(self, text='Current Balance')
        lf.pack(side=TOP, fill='both', expand='yes', padx=7, pady=7)

        lf2 = LabelFrame(self, text='')
        lf2.pack(side=BOTTOM, fill='both', expand='yes', padx=7, pady=7)
    
        #所持コインの総額表示領域のラベル
        self.balance = Label(lf, textvariable=self.coin_balance, font='Helvetica 20')
        self.balance.pack()

        #受信者となる相手の公開鍵
        self.label = Label(lf2, text='Recipient Address:')
        self.label.grid(row=0, pady=5)

        self.recipient_pubkey = Entry(lf2, bd=2)
        self.recipient_pubkey.grid(row=0, column=1, pady=5)

        # 送金額
        self.label2 = Label(lf2, text='Amount to pay :')
        self.label2.grid(row=1, pady=5)
    
        self.amountBox = Entry(lf2, bd=2)
        self.amountBox.grid(row=1, column=1, pady=5, sticky='NSEW')

        # 手数料
        self.label3 = Label(lf2, text='Fee (Optional) :')
        self.label3.grid(row=2, pady=5)
    
        self.feeBox = Entry(lf2, bd=2)
        self.feeBox.grid(row=2, column=1, pady=5, sticky='NSEW')

        # 間隔の開け方がよくわからんので空文字で場所確保
        self.label4 = Label(lf2, text='')
        self.label4.grid(row=5, pady=5)

        # 送金実行ボタン
        self.sendBtn = Button(lf2, text='\nSend Coin(s)\n', command=self.sendCoins)
        self.sendBtn.grid(row=6, column=1, sticky='NSEW')

        # 下部に表示するステータスバー
        stbar = Label(self.winfo_toplevel(), textvariable=self.status_message, bd=1, relief=SUNKEN, anchor=W)
        stbar.pack(side=BOTTOM, fill=X)

  
    # 送金実行ボタン押下時の処理実体
    def sendCoins(self):
        sendAtp = self.amountBox.get()
        recipientKey = self.recipient_pubkey.get()
        sendFee = self.feeBox.get()

        utxo_len = len(self.um.utxo_txs)

        if not sendAtp:
            messagebox.showwarning('Warning', 'Please enter the Amount to pay.')
            return
        elif len(recipientKey) <= 1:
            messagebox.showwarning('Warning', 'Please enter the Recipient Address.')
            return
        else:
            result = messagebox.askyesno('Confirmation', 'Sending {} SimpleBitcoins to :\n {}'.format(sendAtp, recipientKey))

        if not sendFee:
            sendFee = 0


        if result:
            if 0 < utxo_len:
                print('Sending {} SimpleBitcoins to reciever:\n {}'.format(sendAtp, recipientKey))
            else:
                messagebox.showwarning('Short of Coin.', 'Not enough coin to be sent...')
                return

            utxo, idx = self.um.get_utxo_tx(0)

            t = Transaction(
                [TransactionInput(utxo, idx)],
                [TransactionOutput(recipientKey, int(sendAtp))]
            )

            counter = 1
            # TransactionInputが送信額を超えるまで繰り返して取得しTransactionとして完成させる
            if type(sendFee) is not str:
                sendFee = int(sendFee)
            while t.is_enough_inputs(sendFee) is not True:
                new_utxo, new_idx = self.um.get_utxo_tx(counter)
                t.inputs.append(TransactionInput(new_utxo, new_idx))
                counter += 1
                if counter > utxo_len:
                    messagebox.showwarning('Short of Coin.', 'Not enough coin to be sent...')
                    break

            # 正常なTransactionが生成できた時だけ秘密鍵で署名を実行する
            if t.is_enough_inputs(sendFee) is True:
                # まずお釣り用Transactionを作る
                change = t.compute_change(sendFee)
                t.outputs.append(TransactionOutput(self.km.my_address(), change))
                to_be_signed = json.dumps(t.to_dict(), sort_keys=True)
                signed = self.km.compute_digital_signature(to_be_signed)
                new_tx = json.loads(to_be_signed)
                new_tx['signature'] = signed
                # TransactionをP2P Networkに送信
                tx_strings = json.dumps(new_tx)
                self.c_core.send_message_to_my_core_node(MSG_NEW_TRANSACTION, tx_strings)
                print('signed new_tx:', tx_strings)
                # 実験的にお釣り分の勘定のため新しく生成したTransactionをUTXOとして追加しておくが
                # 本来はブロックチェーンの更新に合わせて再計算した方が適切
                self.um.put_utxo_tx(t.to_dict())
                to_be_deleted = 0
                del_list = []
                while to_be_deleted < counter:
                    del_tx = self.um.get_utxo_tx(to_be_deleted)
                    del_list.append(del_tx)
                    to_be_deleted += 1

                for dx in del_list:
                    self.um.remove_utxo_tx(dx)

        self.amountBox.delete(0,END)
        self.feeBox.delete(0,END)
        self.recipient_pubkey.delete(0,END)
        self.update_balance()

 
def main(my_port, c_host, c_port):
  
    root = Tk()
    app = SimpleBC_Gui(root, my_port, c_host, c_port)
    root.mainloop()


if __name__ == '__main__':

    args = sys.argv
 
    if len(args) == 4:
        my_port = int(args[1])
        c_host = args[2]
        c_port = int(args[3])
    else:
        print('Param Error')
        print('$ Wallet_App.py <my_port> <core_node_ip_address> <core_node_port_num>')
        quit()

    main(my_port, c_host, c_port)
