import json
import random
from pathlib import Path
from typing import Dict, List, Optional


class StatusEffect:
    """状態異常を表すクラス"""

    def __init__(self, status_data: Dict):
        self.id = status_data["id"]
        self.name = status_data["name"]
        self.icon = status_data["icon"]
        self.description = status_data["description"]
        self.type = status_data["type"]  # positive or negative
        self.duration_turns = status_data["duration_turns"]
        self.remaining_turns = status_data["duration_turns"]
        self.effects = status_data["effects"]
        self.can_stack = status_data.get("can_stack", False)
        self.max_stacks = status_data.get("max_stacks", 1)
        self.current_stacks = 1
        self.prevent_actions = status_data.get("prevent_actions", [])

        self.message_on_apply = status_data.get("message_on_apply", "")
        self.message_on_turn = status_data.get("message_on_turn", "")
        self.message_on_expire = status_data.get("message_on_expire", "")

    def advance_turn(self):
        """ターンを進める"""
        self.remaining_turns -= 1
        return self.remaining_turns <= 0

    def add_stack(self):
        """スタックを追加（スタック可能な場合）"""
        if self.can_stack and self.current_stacks < self.max_stacks:
            self.current_stacks += 1
            return True
        return False

    def get_effect_value(self, effect_name: str, default=0):
        """効果の値を取得（スタック数を考慮）"""
        base_value = self.effects.get(effect_name, default)
        if self.can_stack and effect_name in ["damage_per_turn", "heal_per_turn"]:
            return base_value * self.current_stacks
        return base_value


class StatusManager:
    """状態異常データの読み込みと管理を行うクラス"""

    def __init__(self, data_file="statuses/status_data.json"):
        """
        Args:
            data_file: 状態異常データJSONファイルのパス
        """
        # 絶対パスで解決
        if not Path(data_file).is_absolute():
            base_dir = Path(__file__).parent
            self.data_file = base_dir / data_file
        else:
            self.data_file = Path(data_file)

        self.status_data = {}
        self.status_resistances = {}
        self.load_status_data()

    def load_status_data(self):
        """JSONファイルから状態異常データを読み込む"""
        try:
            if not self.data_file.exists():
                raise FileNotFoundError(
                    f"状態異常データファイルが見つかりません: {self.data_file}"
                )

            with open(self.data_file, "r", encoding="utf-8") as f:
                data = json.load(f)

            self.status_data = {status["id"]: status for status in data["statuses"]}
            self.status_resistances = data.get("status_resistances", {})

            print(f"状態異常データを読み込みました: {len(self.status_data)}種類")

        except Exception as e:
            print(f"状態異常データ読み込みエラー: {e}")
            self.status_data = {}

    def create_status(self, status_id: str) -> Optional[StatusEffect]:
        """
        状態異常を生成

        Args:
            status_id: 状態異常のID

        Returns:
            StatusEffectオブジェクト
        """
        data = self.status_data.get(status_id)
        if data:
            return StatusEffect(data)
        return None

    def get_status_data(self, status_id: str) -> Optional[Dict]:
        """状態異常データを取得"""
        return self.status_data.get(status_id)

    def get_all_statuses(self) -> List[Dict]:
        """全ての状態異常データを取得"""
        return list(self.status_data.values())

    def get_resistance(self, status_id: str, equipment_id: str) -> int:
        """装備による状態異常耐性を取得"""
        if status_id in self.status_resistances:
            return self.status_resistances[status_id].get(equipment_id, 0)
        return 0


class StatusEffectHolder:
    """キャラクターの状態異常を管理するクラス"""

    def __init__(self):
        self.active_statuses: Dict[str, StatusEffect] = {}

    def add_status(
        self, status: StatusEffect, target_name: str = "対象"
    ) -> tuple[bool, str]:
        """
        状態異常を追加

        Args:
            status: StatusEffectオブジェクト
            target_name: 対象の名前

        Returns:
            (追加されたか, メッセージ)
        """
        if status.id in self.active_statuses:
            existing = self.active_statuses[status.id]
            if existing.add_stack():
                return (
                    True,
                    f"{target_name}の{status.name}が重なった！（スタック: {existing.current_stacks}）",
                )
            else:
                # スタックできない場合は持続ターンをリセット
                existing.remaining_turns = existing.duration_turns
                return True, f"{target_name}の{status.name}の効果時間が延長された！"
        else:
            self.active_statuses[status.id] = status
            message = status.message_on_apply.replace("{target}", target_name)
            return True, message

    def remove_status(self, status_id: str):
        """状態異常を削除"""
        if status_id in self.active_statuses:
            del self.active_statuses[status_id]

    def has_status(self, status_id: str) -> bool:
        """特定の状態異常を持っているか"""
        return status_id in self.active_statuses

    def get_status(self, status_id: str) -> Optional[StatusEffect]:
        """特定の状態異常を取得"""
        return self.active_statuses.get(status_id)

    def get_all_statuses(self) -> List[StatusEffect]:
        """全ての状態異常を取得"""
        return list(self.active_statuses.values())

    def can_act(self) -> tuple[bool, str]:
        """
        行動可能かチェック

        Returns:
            (行動可能か, 理由)
        """
        for status in self.active_statuses.values():
            action_fail_chance = status.get_effect_value("action_fail_chance", 0)
            if action_fail_chance > 0 and random.random() < action_fail_chance:
                return False, status.message_on_turn

        return True, ""

    def can_perform_action(self, action_type: str) -> bool:
        """
        特定の行動が可能かチェック

        Args:
            action_type: 行動タイプ（attack, magic, item, defend）

        Returns:
            行動可能か
        """
        for status in self.active_statuses.values():
            if action_type in status.prevent_actions:
                return False
        return True

    def process_turn_effects(self, character, target_name: str = "対象") -> List[str]:
        """
        ターン開始/終了時の状態異常効果を処理

        Args:
            character: Characterオブジェクト
            target_name: 対象の名前

        Returns:
            効果メッセージのリスト
        """
        messages = []
        expired_statuses = []

        for status_id, status in list(self.active_statuses.items()):
            # ダメージ効果
            damage_per_turn = status.get_effect_value("damage_per_turn", 0)
            if damage_per_turn > 0:
                damage_type = status.effects.get("damage_type", "percentage")
                if damage_type == "percentage":
                    damage = int(character.max_hp * damage_per_turn)
                else:
                    damage = int(damage_per_turn)

                character.take_damage(damage)
                message = status.message_on_turn.replace("{target}", target_name)
                messages.append(f"{message} ({damage}ダメージ)")

            # 回復効果
            heal_per_turn = status.get_effect_value("heal_per_turn", 0)
            if heal_per_turn > 0:
                heal_type = status.effects.get("heal_type", "percentage")
                if heal_type == "percentage":
                    heal = int(character.max_hp * heal_per_turn)
                else:
                    heal = int(heal_per_turn)

                character.heal(heal)
                message = status.message_on_turn.replace("{target}", target_name)
                messages.append(f"{message} ({heal}回復)")

            # ターン経過
            if status.advance_turn():
                expired_statuses.append(status_id)
                expire_message = status.message_on_expire.replace(
                    "{target}", target_name
                )
                messages.append(expire_message)

        # 期限切れの状態異常を削除
        for status_id in expired_statuses:
            self.remove_status(status_id)

        return messages

    def get_stat_modifier(self, stat_name: str) -> float:
        """
        ステータス補正値を取得

        Args:
            stat_name: ステータス名（attack, defense等）

        Returns:
            補正倍率（1.0が標準、1.5なら+50%、0.7なら-30%）
        """
        modifier = 1.0

        for status in self.active_statuses.values():
            # 攻撃力補正
            if stat_name == "attack":
                boost = status.get_effect_value("attack_boost", 0)
                reduction = status.get_effect_value("attack_reduction", 0)
                modifier *= 1.0 + boost - reduction

            # 防御力補正
            elif stat_name == "defense":
                boost = status.get_effect_value("defense_boost", 0)
                reduction = status.get_effect_value("defense_reduction", 0)
                modifier *= 1.0 + boost - reduction

        return max(0.1, modifier)  # 最低でも10%は残す

    def get_damage_reduction(self) -> float:
        """ダメージ軽減率を取得"""
        reduction = 0.0
        for status in self.active_statuses.values():
            reduction += status.get_effect_value("damage_reduction", 0)
        return min(0.9, reduction)  # 最大90%軽減

    def wake_up_if_sleeping(self, target_name: str = "対象") -> Optional[str]:
        """睡眠状態の場合、攻撃を受けたら目覚める"""
        if "sleep" in self.active_statuses:
            status = self.active_statuses["sleep"]
            if status.effects.get("wake_on_damage", False):
                self.remove_status("sleep")
                return f"{target_name}は攻撃を受けて目を覚ました！"
        return None

    def get_status_display(self) -> str:
        """状態異常の表示用テキストを取得"""
        if not self.active_statuses:
            return ""

        status_icons = []
        for status in self.active_statuses.values():
            stack_text = (
                f"x{status.current_stacks}" if status.current_stacks > 1 else ""
            )
            status_icons.append(
                f"{status.icon}{status.name}({status.remaining_turns}){stack_text}"
            )

        return " ".join(status_icons)

    def to_dict(self) -> List[Dict]:
        """セーブ用に状態異常情報を辞書化"""
        return [
            {
                "id": status.id,
                "remaining_turns": status.remaining_turns,
                "current_stacks": status.current_stacks,
            }
            for status in self.active_statuses.values()
        ]

    @classmethod
    def from_dict(cls, data: List[Dict], status_manager):
        """セーブデータから状態異常を復元"""
        holder = cls()
        for status_data in data:
            status = status_manager.create_status(status_data["id"])
            if status:
                status.remaining_turns = status_data.get(
                    "remaining_turns", status.duration_turns
                )
                status.current_stacks = status_data.get("current_stacks", 1)
                holder.active_statuses[status.id] = status
        return holder


# グローバルインスタンス（シングルトンパターン）
_status_manager_instance = None


def get_status_manager() -> StatusManager:
    """StatusManagerのシングルトンインスタンスを取得"""
    global _status_manager_instance
    if _status_manager_instance is None:
        _status_manager_instance = StatusManager()
    return _status_manager_instance
