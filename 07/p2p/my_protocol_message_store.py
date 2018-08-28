import threading


class MessageStore:
    """ 
    拡張メッセージのリストをスレッドセーフに管理する
    """
    def __init__(self):
        self.lock = threading.Lock()
        self.list = []

    def add(self, msg):
        """
        メッセージをリストに追加する。

        param:
            msg : 拡張メッセージとして届けられたもの
        """
        print('Message store added', msg)
        with self.lock:
            self.list.append(msg)


    def remove(self, msg):
        """
        メッセージをリストから削除する。今のところ使うか不明

        param:
            msg : 拡張メッセージとして届けられたもの）
        """
        with self.lock:
            toBeRemoved = None
            for m in self.list:
                if msg == m:
                    toBeRemoved = m
                    break
            if not toBeRemoved:
                return
            self.list.remove(toBeRemoved)


    def overwrite(self, new_list):
        """
        一括での上書き処理をしたいような場合はこちら
        """
        with self.lock:
            self.list = new_list


    def get_list(self):
        """
        現在保存されているメッセージの一覧を返却する
        """
        if len(self.list) > 0:
            return self.list
        else:
        	return None

    def get_length(self):
    	return len(self.list)


    def has_this_msg(self, msg):
        for m in self.list:
            if m == msg:
                return True

        return False,
