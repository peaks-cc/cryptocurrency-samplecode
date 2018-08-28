import threading


class EdgeNodeList:

    def __init__(self):
        self.lock = threading.Lock()
        self.list = set()

    def add(self, edge):
        """
        Edgeノードをリストに追加する。

        param:
            edge : Edgeノードとして格納されるノードの接続情報（IPアドレスとポート番号）
        """
        with self.lock:
            print('Adding edge: ', edge)
            self.list.add((edge))
            print('Current Edge List: ', self.list)

    def remove(self, edge):
        """
        離脱したと判断されるEdgeノードをリストから削除する。

        param:
            edge : 削除するノードの接続先情報（IPアドレスとポート番号）
        """
        with self.lock:
            if edge in self.list:
                print('Removing edge: ', edge)
                self.list.remove(edge)
                print('Current Edge list: ', self.list)

    def overwrite(self, new_list):
        """
        複数のEdgeノードの生存確認を行った後で一括での上書き処理をしたいような場合はこちら
        """
        with self.lock:
            print('edge node list will be going to overwrite')
            self.list = new_list
            print('Current Edge list: ', self.list)

    def get_list(self):
        """
        現在接続状態にあるEdgeノードの一覧を返却する
        """
        return self.list
