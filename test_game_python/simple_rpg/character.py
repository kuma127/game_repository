"""キャラクタークラスの定義"""

from equipment_manager import EquipmentSlots, get_equipment_manager
from status_manager import StatusEffectHolder, get_status_manager


class Character:
    """ゲームキャラクター（プレイヤー・敵）を表すクラス"""

    def __init__(self, name, hp, max_hp, mp, max_mp, attack, defense, level=1):
        self.name = name
        # 基礎ステータス（装備なしの値）
        self.base_hp = hp
        self.base_max_hp = max_hp
        self.base_mp = mp
        self.base_max_mp = max_mp
        self.base_attack = attack
        self.base_defense = defense

        # 現在のステータス
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

        # 装備スロット
        self.equipment = EquipmentSlots()
        # 装備インベントリ
        self.equipment_inventory = []  # Equipment オブジェクトのリスト
        # ゴールド
        self.gold = 100
        # 状態異常管理
        self.status_effects = StatusEffectHolder()

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
            "defense_gain": defense_gain,
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
        player = cls(
            name=save_data["name"],
            hp=save_data["base_hp"],  # 基礎ステータスを使用
            max_hp=save_data["base_max_hp"],
            mp=save_data["base_mp"],
            max_mp=save_data["base_max_mp"],
            attack=save_data["base_attack"],
            defense=save_data["base_defense"],
            level=save_data["level"],
        )

        # 追加の属性を復元
        player.hp = save_data["hp"]  # 現在のHPを復元
        player.mp = save_data["mp"]
        player.exp = save_data["exp"]
        player.exp_to_next = save_data["exp_to_next"]
        player.items = save_data["items"]
        player.total_battles = save_data["total_battles"]
        player.total_victories = save_data["total_victories"]
        player.gold = save_data.get("gold", 0)

        # 装備を復元
        equipment_manager = get_equipment_manager()
        player.equipment = EquipmentSlots.from_dict(
            save_data.get("equipment", {}), equipment_manager
        )

        # 装備インベントリを復元
        inventory_ids = save_data.get("equipment_inventory", [])
        player.equipment_inventory = [
            equipment_manager.get_equipment(eq_id)
            for eq_id in inventory_ids
            if equipment_manager.get_equipment(eq_id)
        ]

        # ステータス再計算
        player.recalculate_stats()

        # 状態異常を復元
        status_manager = get_status_manager()
        player.status_effects = StatusEffectHolder.from_dict(
            save_data.get("status_effects", []), status_manager
        )

        return player

    def recalculate_stats(self):
        """装備を含めた最終ステータスを再計算"""
        equipment_stats = self.equipment.get_total_stats()

        # 基礎ステータス + 装備ボーナス
        new_max_hp = self.base_max_hp + equipment_stats.get("max_hp", 0)
        new_max_mp = self.base_max_mp + equipment_stats.get("max_mp", 0)

        # 最大値が変わった場合、現在値の割合を維持
        if new_max_hp != self.max_hp:
            hp_ratio = self.hp / self.max_hp if self.max_hp > 0 else 1.0
            self.max_hp = new_max_hp
            self.hp = min(int(self.max_hp * hp_ratio), self.max_hp)

        if new_max_mp != self.max_mp:
            mp_ratio = self.mp / self.max_mp if self.max_mp > 0 else 1.0
            self.max_mp = new_max_mp
            self.mp = min(int(self.max_mp * mp_ratio), self.max_mp)

        self.attack = self.base_attack + equipment_stats.get("attack", 0)
        self.defense = self.base_defense + equipment_stats.get("defense", 0)

    def add_equipment_to_inventory(self, equipment):
        """装備をインベントリに追加"""
        self.equipment_inventory.append(equipment)

    def remove_equipment_from_inventory(self, equipment):
        """装備をインベントリから削除"""
        if equipment in self.equipment_inventory:
            self.equipment_inventory.remove(equipment)
            return True
        return False

    def get_effective_attack(self) -> int:
        """状態異常を考慮した実効攻撃力を取得"""
        modifier = self.status_effects.get_stat_modifier("attack")
        return int(self.attack * modifier)

    def get_effective_defense(self) -> int:
        """状態異常を考慮した実効防御力を取得"""
        modifier = self.status_effects.get_stat_modifier("defense")
        return int(self.defense * modifier)

    def apply_damage_with_status(self, damage: int) -> int:
        """状態異常によるダメージ軽減を適用"""
        reduction = self.status_effects.get_damage_reduction()
        final_damage = int(damage * (1.0 - reduction))

        # 睡眠状態なら目覚める
        wake_message = self.status_effects.wake_up_if_sleeping(self.name)

        return final_damage, wake_message
