"""敵データの読み込みと生成を管理するモジュール"""

import json
import random
from pathlib import Path
from typing import Dict, List, Optional


class EnemyManager:
    """敵データの読み込みと生成を管理するクラス"""

    def __init__(self, data_file="enemies/enemy_data.json"):
        """
        Args:
            data_file: 敵データJSONファイルのパス
        """
        # 絶対パスで解決（enemy_manager.pyと同じディレクトリ基準）
        if not Path(data_file).is_absolute():
            # このファイル（enemy_manager.py）の場所を基準にパスを解決
            base_dir = Path(__file__).parent
            self.data_file = base_dir / data_file
        else:
            self.data_file = Path(data_file)

        self.enemy_data = {}
        self.ai_patterns = {}
        self.rarity_weights = {}
        self.load_enemy_data()

    def load_enemy_data(self):
        """JSONファイルから敵データを読み込む"""
        try:
            if not self.data_file.exists():
                raise FileNotFoundError(f"敵データファイルが見つかりません: {self.data_file}")

            with open(self.data_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # 敵データを辞書化（IDで検索しやすく）
            self.enemy_data = {enemy['id']: enemy for enemy in data['enemies']}
            self.ai_patterns = data.get('ai_patterns', {})
            self.rarity_weights = data.get('rarity_weights', {})

            print(f"敵データを読み込みました: {len(self.enemy_data)}種類")

        except Exception as e:
            print(f"敵データ読み込みエラー: {e}")
            # デフォルトデータで初期化
            self._load_default_data()

    def _load_default_data(self):
        """データ読み込み失敗時のフォールバック"""
        self.enemy_data = {
            "goblin": {
                "id": "goblin",
                "name": "ゴブリン",
                "level_range": [1, 10],
                "base_stats": {"hp": 50, "mp": 0, "attack": 15, "defense": 5},
                "exp_reward": 40,
                "gold_reward": 20,
                "ai_pattern": "balanced",
                "rarity": "common"
            }
        }

    def get_enemies_for_level(self, player_level: int) -> List[Dict]:
        """
        プレイヤーレベルに適した敵のリストを取得

        Args:
            player_level: プレイヤーのレベル

        Returns:
            該当する敵データのリスト
        """
        suitable_enemies = []

        for _, enemy_data in self.enemy_data.items():
            level_range = enemy_data['level_range']
            min_level, max_level = level_range

            # プレイヤーレベルが敵のレベル範囲内かチェック
            if min_level <= player_level <= max_level:
                suitable_enemies.append(enemy_data)

        return suitable_enemies

    def create_enemy(self, player_level: int, force_enemy_id: Optional[str] = None):
        """
        プレイヤーレベルに応じた敵を生成

        Args:
            player_level: プレイヤーのレベル
            force_enemy_id: 特定の敵IDを指定（デバッグ用）

        Returns:
            dict: 敵の情報（Character生成用）
        """
        # 特定の敵を指定された場合
        if force_enemy_id and force_enemy_id in self.enemy_data:
            enemy_template = self.enemy_data[force_enemy_id]
        else:
            # レベルに適した敵を抽選
            suitable_enemies = self.get_enemies_for_level(player_level)

            if not suitable_enemies:
                # 該当する敵がいない場合は全敵から選択
                suitable_enemies = list(self.enemy_data.values())

            # レアリティに基づいて抽選
            enemy_template = self._select_enemy_by_rarity(suitable_enemies)

        # 敵の基本ステータスを取得
        base_stats = enemy_template['base_stats']
        level_range = enemy_template['level_range']

        # 敵のレベルを決定（プレイヤーレベル±1の範囲）
        min_enemy_level = max(level_range[0], player_level - 1)
        max_enemy_level = min(level_range[1], player_level + 1)
        enemy_level = random.randint(min_enemy_level, max_enemy_level)

        # レベルに応じてステータスを調整
        level_modifier = 1 + (enemy_level - level_range[0]) * 0.15

        # 敵情報を返す
        enemy_info = {
            "id": enemy_template['id'],
            "name": enemy_template['name'],
            "level": enemy_level,
            "hp": int(base_stats['hp'] * level_modifier),
            "max_hp": int(base_stats['hp'] * level_modifier),
            "mp": int(base_stats.get('mp', 0) * level_modifier),
            "max_mp": int(base_stats.get('mp', 0) * level_modifier),
            "attack": int(base_stats['attack'] * level_modifier),
            "defense": int(base_stats['defense'] * level_modifier),
            "exp_reward": int(enemy_template['exp_reward'] * level_modifier),
            "gold_reward": int(enemy_template.get('gold_reward', 0) * level_modifier),
            "ai_pattern": enemy_template.get('ai_pattern', 'simple_attack'),
            "special_abilities": enemy_template.get('special_abilities', []),
            "rarity": enemy_template.get('rarity', 'common'),
            "description": enemy_template.get('description', '')
        }

        return enemy_info

    def _select_enemy_by_rarity(self, enemies: List[Dict]) -> Dict:
        """
        レアリティに基づいて敵を抽選

        Args:
            enemies: 候補となる敵のリスト

        Returns:
            選択された敵データ
        """
        if not enemies:
            return list(self.enemy_data.values())[0]

        # レアリティごとに敵を分類
        enemies_by_rarity = {}
        for enemy in enemies:
            rarity = enemy.get('rarity', 'common')
            if rarity not in enemies_by_rarity:
                enemies_by_rarity[rarity] = []
            enemies_by_rarity[rarity].append(enemy)

        # レアリティを抽選
        rarities = list(enemies_by_rarity.keys())
        weights = [self.rarity_weights.get(r, 0.25) for r in rarities]

        selected_rarity = random.choices(rarities, weights=weights)[0]

        # 選択されたレアリティの敵からランダムに選択
        return random.choice(enemies_by_rarity[selected_rarity])

    def get_enemy_by_id(self, enemy_id: str) -> Optional[Dict]:
        """
        IDで敵データを取得

        Args:
            enemy_id: 敵のID

        Returns:
            敵データ（存在しない場合はNone）
        """
        return self.enemy_data.get(enemy_id)

    def get_ai_pattern(self, pattern_name: str) -> Dict:
        """
        AIパターンを取得

        Args:
            pattern_name: AIパターン名

        Returns:
            AIパターンのデータ
        """
        return self.ai_patterns.get(pattern_name, self.ai_patterns.get('simple_attack', {}))

    def get_all_enemies(self) -> List[Dict]:
        """全ての敵データを取得"""
        return list(self.enemy_data.values())

    def get_enemies_by_rarity(self, rarity: str) -> List[Dict]:
        """
        レアリティで敵をフィルタリング

        Args:
            rarity: レアリティ（common, uncommon, rare, legendary）

        Returns:
            該当する敵のリスト
        """
        return [e for e in self.enemy_data.values() if e.get('rarity') == rarity]


# グローバルインスタンス（シングルトンパターン）
_enemy_manager_instance = None


def get_enemy_manager() -> EnemyManager:
    """EnemyManagerのシングルトンインスタンスを取得"""
    global _enemy_manager_instance
    if _enemy_manager_instance is None:
        _enemy_manager_instance = EnemyManager()
    return _enemy_manager_instance