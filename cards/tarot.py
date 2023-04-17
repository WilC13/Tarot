import random

tarot_deck = [
    "愚者",
    "魔術師",
    "女祭司",
    "皇后",
    "皇帝",
    "教皇",
    "戀人",
    "戰車",
    "力量",
    "隱者",
    "命運之輪",
    "正義",
    "倒吊人",
    "死神",
    "節制",
    "惡魔",
    "高塔",
    "星星",
    "月亮",
    "太陽",
    "審判",
    "世界",
    "權杖首牌",
    "權杖二",
    "權杖三",
    "權杖四",
    "權杖五",
    "權杖六",
    "權杖七",
    "權杖八",
    "權杖九",
    "權杖十",
    "權杖侍從",
    "權杖騎士",
    "權杖皇后",
    "權杖國王",
    "聖杯首牌",
    "聖杯二",
    "聖杯三",
    "聖杯四",
    "聖杯五",
    "聖杯六",
    "聖杯七",
    "聖杯八",
    "聖杯九",
    "聖杯十",
    "聖杯侍從",
    "聖杯騎士",
    "聖杯皇后",
    "聖杯國王",
    "寶劍首牌",
    "寶劍二",
    "寶劍三",
    "寶劍四",
    "寶劍五",
    "寶劍六",
    "寶劍七",
    "寶劍八",
    "寶劍九",
    "寶劍十",
    "寶劍侍從",
    "寶劍騎士",
    "寶劍皇后",
    "寶劍國王",
    "錢幣首牌",
    "錢幣二",
    "錢幣三",
    "錢幣四",
    "錢幣五",
    "錢幣六",
    "錢幣七",
    "錢幣八",
    "錢幣九",
    "錢幣十",
    "錢幣侍從",
    "錢幣騎士",
    "錢幣皇后",
    "錢幣國王",
]


class deck:
    def __init__(self) -> None:
        self.deck = tarot_deck
        self.table = [[None, -1] for _ in range(3)]  # [0]: past, [1]: now, [2]: future

    def shuffle(self) -> None:
        random.shuffle(self.deck)

    def __draw(self):
        side = "正位" if random.randint(0, 1) == 0 else "逆位"
        return [side, self.deck.pop()]

    def past(self):
        self.table[0] = self.__draw()

    def now(self):
        self.table[1] = self.__draw()

    def future(self):
        self.table[2] = self.__draw()

    def full(self):
        self.past()
        self.now()
        self.future()

    def open(self):
        if None not in self.table:
            return self.table
        else:
            if self.table[0] == None:
                return "Past not yet draw"
            if self.table[1] == None:
                return "Now not yet draw"
            if self.table[2] == None:
                return "Future not yet draw"
