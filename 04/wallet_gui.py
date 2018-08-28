from tkinter import *
from tkinter import messagebox
from tkinter.ttk import Button, Style


class SimpleBC_Gui(Frame):

  
    def __init__(self, parent):
        Frame.__init__(self, parent)
        self.parent = parent
        self.parent.protocol('WM_DELETE_WINDOW', self.quit)
        self.coin_balance = StringVar(self.parent, '0')
        self.status_message = StringVar(self.parent, 'No coin to be sent')
        self.initApp()
        self.setupGUI()

    def quit(self, event=None):
        """
        アプリの終了
        """
        self.parent.destroy()


    def initApp(self):
        """
        ClientCoreとの接続含めて必要な初期化処理はここで実行する
        """
        print('SimpleBitcoin is now activating ...: ')
      

    def display_info(self, info):
        """
        ダイアログボックスを使ったメッセージの表示
        """
        pass


    def update_status(self, info):
        """
        画面下部のステータス表示内容を変更する
        """  
        self.status_message.set(info)


    def update_balance(self):
        """
        総額表示の内容を最新のブロックチェーンに合わせて変更する
        """
        pass


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
        self.subMenu.add_command(label='Load my Keys', command=self.load_my_keys)
        self.subMenu.add_command(label='Update Blockchain', command=self.update_block_chain)
        self.subMenu.add_separator()
        self.subMenu.add_command(label='Quit', command=self.quit)

        self.subMenu2 = Menu(self.menuBar, tearoff=0)
        self.menuBar.add_cascade(label='Settings', menu=self.subMenu2)
        self.subMenu2.add_command(label='Renew my Keys', command=self.renew_my_keypairs)
        self.subMenu2.add_command(label='Connection Info', command=self.edit_conn_info)

        self.subMenu3 = Menu(self.menuBar, tearoff=0)
        self.menuBar.add_cascade(label='Advance', menu=self.subMenu3)
        self.subMenu3.add_command(label='Show logs', command=self.open_log_window)
        self.subMenu3.add_command(label='Show Blockchain', command=self.show_my_block_chain)

    
    def show_my_address(self):
        pass

    
    def load_my_keys(self):
        pass    


    def update_block_chain(self):
        pass

        
    def renew_my_keypairs(self):
        """
        利用する鍵ペアを更新する。
        TODO: 新規アドレスになるので所有コインを0に戻すことを忘れずに
        """
        pass

        
    def edit_conn_info(self):
        """
        Coreノードへの接続情報の編集
        """
        pass


    def open_log_window(self):
        """
        別ウィンドウでログ情報を表示する。デバッグ用
        """
        pass

        
    def show_my_block_chain(self):
        """
        自分が保持しているブロックチェーンの中身を確認する
        """
        pass

  
    def setupGUI(self):
        """
        画面に必要なパーツを並べる
        """

        self.parent.bind('<Control-q>', self.quit)
        self.parent.title("SimpleBitcoin GUI")
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
    
        self.amountBox2 = Entry(lf2, bd=2)
        self.amountBox2.grid(row=2, column=1, pady=5, sticky='NSEW')

        # 間隔の開け方がよくわからんので空文字で場所確保
        self.label4 = Label(lf2, text='')
        self.label4.grid(row=3, pady=5)

        # 送金実行ボタン
        self.sendBtn = Button(lf2, text='\nSend Coin(s)\n', command=self.sendCoins)
        self.sendBtn.grid(row=4, column=1, sticky='NSEW')

        # 下部に表示するステータスバー
        stbar = Label(self.winfo_toplevel(), textvariable=self.status_message, bd=1, relief=SUNKEN, anchor=W)
        stbar.pack(side=BOTTOM, fill=X)

  
    # 送金実行ボタン押下時の処理実体
    def sendCoins(self):
        pass

 
def main():
  
    root = Tk()
    app = SimpleBC_Gui(root)
    root.mainloop()


if __name__ == '__main__':
    main()