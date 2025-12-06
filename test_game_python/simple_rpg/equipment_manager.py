"""装備アイテムの管理を行うモジュール"""

import json
import random
from pathlib import Path
from typing import Dict, List, Optional


class Equipment:
    """装備アイテムを表すクラス"""

    def __init__(self, equipment_data: Dict):
        self.id = equipment_data["id"]
        self.name = equipment_data["name"]
        self.description = equipment_data["description"]
        self.type = equipment_data["type"]  # weapon, armor, accessory
        self.rarity = equipment_data["rarity"]
        self.required_level = equipment_data["required_level"]
        self.stats = equipment_data["stats"]
        self.price = equipment_data.get("price", 0)
        self.sell_price = equipment_data.get("sell_price", 0)

    def __str__(self):
        return f"{self.name} ({self.type})"

    def get_stat_bonus(self, stat_name: str) -> int:
        """特定のステータスのボーナス値を取得"""
        return self.stats.get(stat_name, 0)

    def get_all_stats_text(self) -> str:
        """全てのステータスボーナスをテキストで取得"""
        stat_texts = []
        for stat, value in self.stats.items():
            if value > 0:
                stat_texts.append(f"{stat}: +{value}")
        return ", ".join(stat_texts)


class EquipmentManager:
    """装備データの読み込みと管理を行うクラス"""

    def __init__(self, data_file="equipment/equipment_data.json"):
        """
        Args:
            data_file: 装備データJSONファイルのパス
        """
        # 絶対パスで解決
        if not Path(data_file).is_absolute():
            base_dir = Path(__file__).parent
            self.data_file = base_dir / data_file
        else:
            self.data_file = Path(data_file)

        self.equipment_data = {}
        self.drop_tables = {}
        self.load_equipment_data()

    def load_equipment_data(self):
        """JSONファイルから装備データを読み込む"""
        try:
            if not self.data_file.exists():
                raise FileNotFoundError(
                    f"装備データファイルが見つかりません: {self.data_file}"
                )

            with open(self.data_file, "r", encoding="utf-8") as f:
                data = json.load(f)

            # 全ての装備を1つの辞書にまとめる
            all_equipment = []
            all_equipment.extend(data.get("weapons", []))
            all_equipment.extend(data.get("armors", []))
            all_equipment.extend(data.get("accessories", []))

            self.equipment_data = {eq["id"]: eq for eq in all_equipment}
            self.drop_tables = data.get("drop_tables", {})

            print(f"装備データを読み込みました: {len(self.equipment_data)}種類")

        except Exception as e:
            print(f"装備データ読み込みエラー: {e}")
            self.equipment_data = {}

    def get_equipment(self, equipment_id: str) -> Optional[Equipment]:
        """
        IDで装備を取得

        Args:
            equipment_id: 装備のID

        Returns:
            Equipmentオブジェクト（存在しない場合はNone）
        """
        data = self.equipment_data.get(equipment_id)
        if data:
            return Equipment(data)
        return None

    def get_equipment_by_type(self, equipment_type: str) -> List[Equipment]:
        """
        タイプで装備をフィルタリング

        Args:
            equipment_type: 装備タイプ（weapon, armor, accessory）

        Returns:
            該当する装備のリスト
        """
        equipment_list = []
        for eq_data in self.equipment_data.values():
            if eq_data["type"] == equipment_type:
                equipment_list.append(Equipment(eq_data))
        return equipment_list

    def get_equipment_by_level(
        self, player_level: int, equipment_type: Optional[str] = None
    ) -> List[Equipment]:
        """
        プレイヤーレベルで装備可能なアイテムを取得

        Args:
            player_level: プレイヤーのレベル
            equipment_type: 装備タイプでフィルタ（オプション）

        Returns:
            装備可能な装備のリスト
        """
        equipment_list = []
        for eq_data in self.equipment_data.values():
            if eq_data["required_level"] <= player_level:
                if equipment_type is None or eq_data["type"] == equipment_type:
                    equipment_list.append(Equipment(eq_data))
        return equipment_list

    def roll_equipment_drop(self, enemy_rarity: str) -> Optional[Equipment]:
        """
        敵のレアリティに基づいて装備ドロップを抽選

        Args:
            enemy_rarity: 敵のレアリティ

        Returns:
            ドロップした装備（ドロップなしの場合はNone）
        """
        drop_table_key = f"{enemy_rarity}_enemy"
        drop_table = self.drop_tables.get(drop_table_key, [])

        if not drop_table:
            return None

        # ドロップ判定
        for drop_entry in drop_table:
            if random.random() < drop_entry["chance"]:
                equipment_id = drop_entry["item_id"]
                return self.get_equipment(equipment_id)

        return None

    def get_all_equipment(self) -> List[Equipment]:
        """全ての装備を取得"""
        return [Equipment(eq_data) for eq_data in self.equipment_data.values()]


class EquipmentSlots:
    """プレイヤーの装備スロットを管理するクラス"""

    def __init__(self):
        self.weapon: Optional[Equipment] = None
        self.armor: Optional[Equipment] = None
        self.accessory: Optional[Equipment] = None

    def equip(self, equipment: Equipment, player_level: int) -> tuple[bool, str]:
        """
        装備を装着

        Args:
            equipment: 装備するアイテム
            player_level: プレイヤーのレベル

        Returns:
            (成功したか, メッセージ)
        """
        # レベル要件チェック
        if equipment.required_level > player_level:
            return False, f"レベル {equipment.required_level} 以上が必要です"

        # 装備タイプに応じて装着
        old_equipment = None

        if equipment.type == "weapon":
            old_equipment = self.weapon
            self.weapon = equipment
        elif equipment.type == "armor":
            old_equipment = self.armor
            self.armor = equipment
        elif equipment.type == "accessory":
            old_equipment = self.accessory
            self.accessory = equipment
        else:
            return False, "不明な装備タイプです"

        message = f"{equipment.name} を装備しました"
        if old_equipment:
            message += f"（{old_equipment.name} を外しました）"

        return True, message

    def unequip(self, equipment_type: str) -> tuple[bool, Optional[Equipment]]:
        """
        装備を外す

        Args:
            equipment_type: 装備タイプ

        Returns:
            (成功したか, 外した装備)
        """
        removed = None

        if equipment_type == "weapon" and self.weapon:
            removed = self.weapon
            self.weapon = None
        elif equipment_type == "armor" and self.armor:
            removed = self.armor
            self.armor = None
        elif equipment_type == "accessory" and self.accessory:
            removed = self.accessory
            self.accessory = None
        else:
            return False, None

        return True, removed

    def get_total_stats(self) -> Dict[str, int]:
        """装備による合計ステータスボーナスを計算"""
        total_stats = {}

        for equipment in [self.weapon, self.armor, self.accessory]:
            if equipment:
                for stat, value in equipment.stats.items():
                    total_stats[stat] = total_stats.get(stat, 0) + value

        return total_stats

    def get_equipped_list(self) -> List[Equipment]:
        """装備中のアイテムリストを取得"""
        equipped = []
        if self.weapon:
            equipped.append(self.weapon)
        if self.armor:
            equipped.append(self.armor)
        if self.accessory:
            equipped.append(self.accessory)
        return equipped

    def to_dict(self) -> Dict:
        """セーブ用に装備情報を辞書化"""
        return {
            "weapon": self.weapon.id if self.weapon else None,
            "armor": self.armor.id if self.armor else None,
            "accessory": self.accessory.id if self.accessory else None,
        }

    @classmethod
    def from_dict(cls, data: Dict, equipment_manager: EquipmentManager):
        """セーブデータから装備スロットを復元"""
        slots = cls()

        if data.get("weapon"):
            slots.weapon = equipment_manager.get_equipment(data["weapon"])
        if data.get("armor"):
            slots.armor = equipment_manager.get_equipment(data["armor"])
        if data.get("accessory"):
            slots.accessory = equipment_manager.get_equipment(data["accessory"])

        return slots


# グローバルインスタンス（シングルトンパターン）
_equipment_manager_instance = None


def get_equipment_manager() -> EquipmentManager:
    """EquipmentManagerのシングルトンインスタンスを取得"""
    global _equipment_manager_instance
    if _equipment_manager_instance is None:
        _equipment_manager_instance = EquipmentManager()
    return _equipment_manager_instance
