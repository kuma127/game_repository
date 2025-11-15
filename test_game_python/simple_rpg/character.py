"""キャラクタークラスの定義"""


class Character:
    """ゲームキャラクター（プレイヤー・敵）を表すクラス"""

    def __init__(self, name, hp, max_hp, mp, max_mp, attack, defense, level=1):
        self.name = name
        self.hp = hp
        self.max_hp = max_hp
        self.mp = mp
        self.max_mp = max_mp
        self.attack = attack
        self.defense = defense
        self.level = level
        self.exp = 0
        self.exp_to_next = self.calculate_exp_to_next()
        self.items = {"回復薬": 3, "魔法の水": 2}
        self.total_battles = 0
        self.total_victories = 0

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

    def calculate_exp_to_next(self):
        """次のレベルまでに必要な経験値を計算"""
        return int(100 * (1.5 ** (self.level - 1)))
    
    def gain_exp(self, amount):
        """経験値を獲得してレベルアップ判定"""
        self.exp += amount
        level_ups = []
        
        while self.exp >= self.exp_to_next:
            self.exp -= self.exp_to_next
            level_ups.append(self.level_up())
        
        return level_ups
    
    def level_up(self):
        """レベルアップ処理"""
        import random
        self.level += 1
        
        # ステータス上昇量
        hp_gain = random.randint(8, 12)
        mp_gain = random.randint(3, 7)
        attack_gain = random.randint(2, 4)
        defense_gain = random.randint(1, 3)
        
        self.max_hp += hp_gain
        self.max_mp += mp_gain
        self.attack += attack_gain
        self.defense += defense_gain
        
        # レベルアップ時は全回復
        self.hp = self.max_hp
        self.mp = self.max_mp
        
        # 次のレベルまでの経験値を再計算
        self.exp_to_next = self.calculate_exp_to_next()
        
        return {
            "level": self.level,
            "hp_gain": hp_gain,
            "mp_gain": mp_gain,
            "attack_gain": attack_gain,
            "defense_gain": defense_gain
        }
    
    @classmethod
    def from_save_data(cls, save_data):
        """
        セーブデータからCharacterオブジェクトを復元
        
        Args:
            save_data: ロードしたプレイヤーデータの辞書
        
        Returns:
            Character: 復元されたプレイヤー
        """
        player: Character = cls(
            name=save_data["name"],
            hp=save_data["hp"],
            max_hp=save_data["max_hp"],
            mp=save_data["mp"],
            max_mp=save_data["max_mp"],
            attack=save_data["attack"],
            defense=save_data["defense"],
            level=save_data["level"]
        )
        
        # 追加の属性を復元
        player.exp = save_data["exp"]
        player.exp_to_next = save_data["exp_to_next"]
        player.items = save_data["items"]
        player.total_battles = save_data["total_battles"]
        player.total_victories = save_data["total_victories"]
        
        return player
