# Bug found
import tkinter as tk
import random


class App(tk.Tk):
    def __init__(self):
        super(App, self).__init__()
        self.title("はさみ将棋")
        self.geometry("{}x{}+{}+{}".format(400, 400, 300, 100))
        self.resizable(width=0, height=0)
        self.iconbitmap("hasami.ico")

        self.flag = False
        self.turn = 1
        self.unpressed = 1
        self.previous_tag = None
        self.current_tag = None
        self.tmp = []
        self.candidates = []
        self.retrieves = []
        self.rtmp = []
        self.rflag = False
        self.result = [0, 0]
        self.lock = 0
        self.enlock = 0

        # Canvasの設定
        self.set_widgets()

    def set_widgets(self):
        ### 将棋盤を作る ###
        self.board = tk.Canvas(self, width=400, height=400, bg="Peach Puff3")
        self.board.pack()

        ### 長方形を作る ###
        # 将棋盤の情報
        # -1 -> 盤の外, 0 -> 空白
        self.board2info = [-1] * 11 + [[0, -1][i in [0, 10]] for i in range(11)] * 9 + [-1] * 11
        # {tag: position}
        self.tag2pos = {}
        # 座標からtagの変換
        self.z2tag = {}
        # 符号
        self.numstr = "123456789"
        self.kanstr = "一二三四五六七八九"
        for i, y in zip(self.kanstr, range(20, 380, 40)):
            for j, x in zip(self.numstr[::-1], range(20, 380, 40)):
                pos = (x, y, x+40, y+40)
                tag = j + i
                self.tag2pos[tag] = pos[:2]
                self.board.create_rectangle(*pos, fill="Peach Puff3", tags=tag)
                self.z2tag[self.z_coordinate(tag)] = tag

        ### 文字を描く ###
        # 初期配置
        for turn, i in zip([0, 1], ["一", "九"]):
            for j in self.numstr[::-1]:
                tag = j + i
                self.draw_text(tag, turn)
                self.board2info[self.z_coordinate(tag)] = [1, 2][turn]
        # self.get_board_info()
        # バインディングの設定
        self.binding()

    def get_board_info(self, a=None, b=None):
        tags = "" if a is None else "\n{} -> {}".format(a, b)
        board_format = " {:2d} " * 11
        print("\n{}の手番\n(相手, 自分)({}, {})".format(\
                                ["相手", "自分"][self.turn], *self.result))
        print(tags, *[board_format.format(*self.board2info[i:i+11]) \
                                    for i in range(0, 121, 11)], sep='\n')

    def draw_text(self, tag, turn):
        x, y = self.tag2pos[tag]
        self.board.create_text(x+20, y+20,
                               font=("Helvetica", 10, "bold"),
                               angle=[180, 0][turn],
                               text=["と", "歩"][turn],
                               tags=tag)

    def z_coordinate(self, tag):
        x, y = self.numstr[::-1].index(tag[0])+1, self.kanstr.index(tag[1])+1
        return y*11 + x

    def binding(self):
        for tag in self.tag2pos.keys():
            self.board.tag_bind(tag, "<ButtonPress-1>", self.board_pressed)

    def board_pressed(self, event):
        # 自分のターンでなければ何もしない
        if self.lock:
            return
        _id = self.board.find_closest(event.x, event.y)
        tag = self.board.gettags(_id[0])[0]
        #print("Tag {} pressed".format(tag))
        #print("Z {} pressed".format(self.z_coordinate(tag)))

        # クリックされた長方形のtagから１次元の座標に変換し、
        # それをもとに盤面の情報を手に入れる。
        state = self.board2info[self.z_coordinate(tag)]
        # クリックされたのが自分の歩ならば色を変える
        # かつ、自分の歩が他に選択されていないとき
        if state == 2 and self.unpressed:
            self.board.itemconfig(tag, fill="Peach Puff2")
            # 文字が消えるので再度文字を書く
            self.draw_text(tag, 1)
            # クリックされた状態
            self.unpressed = 0
            self.previous_tag = tag
            # 候補手の探索と表示
            self.show(tag)
        elif state == 2:
            # 既に自分の歩が選択されていて、
            # 自分の他の歩を選択したとき、
            # 既に選択されているものを元に戻す。
            # その後、新しく選択した歩の色を変える。
            self.board.itemconfig(self.previous_tag, fill="Peach Puff3")
            # 文字が消えるので再度文字を書く
            self.draw_text(self.previous_tag, 1)
            self.board.itemconfig(tag, fill="Peach Puff2")
            self.draw_text(tag, 1)
            self.previous_tag = tag
            # 候補手の表示の前に、先の候補手の色を元に戻す。
            for z in self.candidates:
                ctag = self.z2tag[z]
                self.board.itemconfig(ctag, fill="Peach Puff3")
            # 候補手の探索と表示
            self.show(tag)
        elif state == 1 or self.unpressed:
            # とが選択されたとき, もしくは歩が選択されていない
            return
        else:
            # 歩が選択されていて、かつ空白をクリックしたときの処理
            # クリックされたところが、候補手にあるかどうか確認
            flag = self.click_is_valid(tag)
            if flag == 0:
                return
            self.current_tag = tag
            # クリックされたところが、候補手にあるので盤面の更新。
            self.update_board(tag)

    def update_board(self, tag):
        if self.turn:
            self.lock = 1
        # 候補手の色を元に戻す
        for z in self.candidates:
            ctag = self.z2tag[z]
            self.board.itemconfig(ctag, fill='Peach Puff3')
        self.draw_text(tag, self.turn)
        # 盤面の更新
        self.board2info[self.z_coordinate(tag)] = self.turn + 1
        self.board2info[self.z_coordinate(self.previous_tag)] = 0
        self.board.itemconfig(self.previous_tag, fill="Peach Puff3")
        self.get_board_info(self.previous_tag, tag)
        self.unpressed = 1
        self.previous_tag = None
        self.candidates = []
        # 挟まれているかの確認
        self.after(1000, self.check)

    def show(self, tag):
        # 候補手の表示
        self.candidates = []
        z = self.z_coordinate(tag)
        self.search(z)
        for z in self.candidates:
            ctag = self.z2tag[z]
            self.board.itemconfig(ctag, fill="Peach Puff1")

    def search(self, z):
        # 候補手の探索
        for num in [-11, 11, 1, -1]:
            self.tmp = []
            self.run_search(z+num, num)
            if self.tmp:
                self.candidates += self.tmp

    def run_search(self, z, num):
        v = self.board2info[z]
        if v == 0:
            self.tmp.append(z)
            self.run_search(z+num, num)
        return -1

    def click_is_valid(self, tag):
        # クリックされたところが、候補手にあるかどうか確認
        ans = self.z_coordinate(tag)
        return 1 if ans in self.candidates else 0

    def check(self):
        self.retrieves = []
        z = self.z_coordinate(self.current_tag)
        # 挟んでるかの確認
        self.is_hasami(z)

        # とる
        for z in set(self.retrieves):
            tag = self.z2tag[z]
            self.board.itemconfig(tag, fill="skyblue")
            self.draw_text(tag, self.board2info[z]-1)
        if len(self.retrieves) > 0:
            self.after(500, self.get_koma)

        # 手番を変える
        if self.turn:
            self.after(1000, self.AI)
        else:
            self.after(1000, self.YOU)

    def AI(self):
        if self.enlock:
            return
        self.turn = 0
        self.candidates = []
        while True:
            z = random.choice([i for i, v in enumerate(self.board2info) if v == 1])
            # 動かす駒の符号
            self.previous_tag = self.z2tag[z]
            self.search(z)
            if self.candidates:
                break

        # 候補手からランダムに選択
        z = random.choice(self.candidates)
        # 動かした後の符号
        self.current_tag = self.z2tag[z]
        self.update_board(self.current_tag)

    def YOU(self):
            self.turn = 1
            self.lock = 0

    def is_hasami(self, z):
        # 横と縦のチェック
        for num in [-11, 11, 1, -1]:
            self.rflag = False
            self.rtmp = [z]
            self.hasami_search(z+num, num)
            if self.rflag:
                self.retrieves += self.rtmp

        # 端の探索
        for edge in [(12, 100, 1, 11), (20, 108, -1, 11), (100, 12, 1, -11), (108, 20, -1, -11)]:
            flag = self.edge_check(*edge)
            if flag:
                break

    def edge_check(self, start, end, interval_0, interval_1):
        source = [2, 1][self.turn]
        target = [1, 2][self.turn]
        tmp = []
        cnt = interval_0
        if self.board2info[start] != source:
            return
        i = start + interval_0
        while self.board2info[i] == source:
            cnt = cnt + interval_0
            i = i + interval_0
        if self.board2info[i] in [-1, 0]:
            return
        tmp += [j for j in range(start, start+cnt+interval_0, interval_0)]
        start = start + interval_1
        while True:
            flag_0 = \
                all([1 if self.board2info[j] == source else 0 for j in range(start, start+cnt, interval_0)])
            if flag_0:
                tmp += [j for j in range(start, start+cnt+interval_0, interval_0)]
                start = start + interval_1
                continue
            flag_1 = \
                all([1 if self.board2info[j] == target else 0 for j in range(start, start+cnt, interval_0)])
            if flag_1:
                tmp += [j for j in range(start, start+cnt, interval_0)]
            break
        if flag_1:
            self.retrieves += tmp
        return flag_1

    def get_koma(self):
        for z in set(self.retrieves):
            tag = self.z2tag[z]
            self.board.itemconfig(tag, fill="Peach Puff3")
            if self.board2info[z] == [1, 2][self.turn]:
                self.draw_text(tag, self.board2info[z]-1)
            else:
                self.board2info[z] = 0
                self.result[self.turn] += 1
        # 結果の確認
        if self.result[self.turn] >= 3:
            self.enlock = 1
            self.end_game()

    def hasami_search(self, z, num):
        v = self.board2info[z]
        if v == [2, 1][self.turn]:
            self.rtmp.append(z)
            self.hasami_search(z+num ,num)
        if v == [1, 2][self.turn] and len(self.rtmp) > 1:
            self.rtmp.append(z)
            self.rflag = True
        return

    def end_game(self):
        self.board.unbind("<ButtonPress-1>")
        result = self.result[0] < self.result[1]
        print("Result: {} Win".format(["相手", "あなた"][result]))

    def run(self):
        self.mainloop()


if __name__ == "__main__":
    app = App()
    app.run()
