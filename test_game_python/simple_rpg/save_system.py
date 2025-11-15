import json
from datetime import datetime
from pathlib import Path


class SaveSystem:
    """セーブ/ロードを管理するクラス"""
    
    def __init__(self, save_dir="saves"):
        """
        Args:
            save_dir: セーブファイルを保存するディレクトリ
        """
        self.save_dir = Path(save_dir)
        self.save_dir.mkdir(exist_ok=True)
    
    def save_game(self, player, slot=1):
        """
        ゲームをセーブする
        
        Args:
            player: Characterオブジェクト
            slot: セーブスロット番号（デフォルト: 1）
        
        Returns:
            bool: 保存成功時True
        """
        try:
            filename = self.save_dir / f"save_slot_{slot}.json"
            
            # プレイヤーデータを辞書化
            save_data = {
                "version": "1.0",  # セーブデータのバージョン
                "save_date": datetime.now().isoformat(),
                "player": {
                    "name": player.name,
                    "level": player.level,
                    "exp": player.exp,
                    "exp_to_next": player.exp_to_next,
                    "hp": player.hp,
                    "max_hp": player.max_hp,
                    "mp": player.mp,
                    "max_mp": player.max_mp,
                    "attack": player.attack,
                    "defense": player.defense,
                    "items": player.items,
                    "total_battles": player.total_battles,
                    "total_victories": player.total_victories
                }
            }
            
            # JSONファイルに保存
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(save_data, f, indent=2, ensure_ascii=False)
            
            return True
        
        except Exception as e:
            print(f"セーブエラー: {e}")
            return False
    
    def load_game(self, slot=1):
        """
        セーブデータを読み込む
        
        Args:
            slot: セーブスロット番号
        
        Returns:
            dict: プレイヤーデータ（失敗時はNone）
        """
        try:
            filename = self.save_dir / f"save_slot_{slot}.json"
            
            if not filename.exists():
                return None
            
            with open(filename, 'r', encoding='utf-8') as f:
                save_data = json.load(f)
            
            return save_data["player"]
        
        except Exception as e:
            print(f"ロードエラー: {e}")
            return None
    
    def get_save_info(self, slot=1):
        """
        セーブデータの情報を取得（セーブ選択画面用）
        
        Args:
            slot: セーブスロット番号
        
        Returns:
            dict: セーブ情報（存在しない場合はNone）
        """
        try:
            filename = self.save_dir / f"save_slot_{slot}.json"
            
            if not filename.exists():
                return None
            
            with open(filename, 'r', encoding='utf-8') as f:
                save_data = json.load(f)
            
            player_data = save_data["player"]
            
            return {
                "slot": slot,
                "name": player_data["name"],
                "level": player_data["level"],
                "save_date": save_data["save_date"],
                "total_battles": player_data["total_battles"],
                "total_victories": player_data["total_victories"]
            }
        
        except Exception as e:
            print(f"セーブ情報取得エラー: {e}")
            return None
    
    def list_saves(self, max_slots=3):
        """
        全てのセーブスロットの情報を取得
        
        Args:
            max_slots: 最大スロット数
        
        Returns:
            list: セーブ情報のリスト
        """
        saves = []
        for slot in range(1, max_slots + 1):
            info = self.get_save_info(slot)
            saves.append(info)
        return saves
    
    def delete_save(self, slot=1):
        """
        セーブデータを削除
        
        Args:
            slot: セーブスロット番号
        
        Returns:
            bool: 削除成功時True
        """
        try:
            filename = self.save_dir / f"save_slot_{slot}.json"
            
            if filename.exists():
                filename.unlink()
                return True
            return False
        
        except Exception as e:
            print(f"削除エラー: {e}")
            return False
    
    def create_player_from_save(self, save_data):
        """
        セーブデータからCharacterオブジェクトを復元
        （character.pyからCharacterクラスをインポートして使用）
        
        Args:
            save_data: ロードしたプレイヤーデータ
        
        Returns:
            Character: 復元されたプレイヤーオブジェクト
        """
        # このメソッドはmain.pyなど、Characterクラスにアクセスできる場所で使用
        # または、character.pyでこのロジックを実装する方が良い
        pass


def format_datetime(iso_string):
    """
    ISO形式の日時文字列を読みやすい形式に変換
    
    Args:
        iso_string: ISO形式の日時文字列
    
    Returns:
        str: フォーマットされた日時文字列
    """
    try:
        dt = datetime.fromisoformat(iso_string)
        return dt.strftime("%Y/%m/%d %H:%M:%S")
    except:  # noqa: E722
        return iso_string
