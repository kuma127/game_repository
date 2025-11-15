"""キャラクタークラスの定義"""


class Character:
    """ゲームキャラクター（プレイヤー・敵）を表すクラス"""

    def __init__(self, name, hp, max_hp, mp, max_mp, attack, defense):
        self.name = name
        self.hp = hp
        self.max_hp = max_hp
        self.mp = mp
        self.max_mp = max_mp
        self.attack = attack
        self.defense = defense
        self.items = {"回復薬": 3, "魔法の水": 2}

    def is_alive(self):
        """キャラクターが生存しているかチェック"""
        return self.hp > 0

    def take_damage(self, damage):
        """ダメージを受ける"""
        self.hp = max(0, self.hp - damage)

    def heal(self, amount):
        """HPを回復する"""
        self.hp = min(self.max_hp, self.hp + amount)

    def use_mp(self, amount):
        """MPを消費する（成功/失敗を返す）"""
        if self.mp >= amount:
            self.mp -= amount
            return True
        return False

    def restore_mp(self, amount):
        """MPを回復する"""
        self.mp = min(self.max_mp, self.mp + amount)
