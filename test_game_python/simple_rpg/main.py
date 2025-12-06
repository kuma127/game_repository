"""Python RPG 戦闘システム - メインエントリーポイント"""

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from character import Character
from battle import start_battle
from ui import create_character_panel, show_save_menu, show_load_menu,show_equipment_menu
from equipment_manager import get_equipment_manager
from save_system import SaveSystem
import time

console = Console()
save_system = SaveSystem()

def game_loop():
    """ゲームメインループ"""
    console.clear()
    
    # ゲーム開始メニュー
    console.print(Panel(
        "[bold cyan]Python RPG[/bold cyan]\n\n"
        "1: 新規ゲーム\n"
        "2: ロード\n"
        "3: 終了",
        title="🎮 メインメニュー",
        border_style="bold cyan"
    ))
    
    choice = Prompt.ask(
        "選択してください",
        choices=["1", "2", "3"],
        default="1"
    )
    
    if choice == "3":
        return
    
    player = None
    
    if choice == "1":
        # 新規ゲーム
        console.clear()
        player_name = Prompt.ask("[bold cyan]あなたの名前を入力してください[/bold cyan]", default="勇者")
        player = Character(player_name, 100, 100, 50, 50, 25, 10, level=1)

        # 初期装備を付与
        equipment_manager = get_equipment_manager()

        starter_weapon = equipment_manager.get_equipment("wooden_sword")
        starter_armor = equipment_manager.get_equipment("cloth_armor")
        
        if starter_weapon:
            player.add_equipment_to_inventory(starter_weapon)
            player.equipment.equip(starter_weapon, player.level)
        
        if starter_armor:
            player.add_equipment_to_inventory(starter_armor)
            player.equipment.equip(starter_armor, player.level)
        
        # ステータス再計算
        player.recalculate_stats()
        
        console.print(Panel(
            f"[bold green]ようこそ、{player_name}![/bold green]\n\n"
            f"[white]あなたの冒険が始まります...[/white]\n\n"
            f"[yellow]初期装備を受け取りました:[/yellow]\n"
            f"• {starter_weapon.name}\n"
            f"• {starter_armor.name}",
            title="🎮 冒険の始まり",
            border_style="bold green"
        ))
        time.sleep(3)
    
    elif choice == "2":
        # ロード
        console.clear()
        slot = show_load_menu(save_system)
        
        if slot == 0:
            console.print("[yellow]ロードをキャンセルしました[/yellow]")
            time.sleep(1)
            return
        
        save_data = save_system.load_game(slot)
        
        if save_data:
            player = Character.from_save_data(save_data)
            console.print(Panel(
                f"[bold green]おかえりなさい、{player.name}![/bold green]\n\n"
                f"[white]レベル {player.level} から冒険を再開します[/white]",
                title="📂 ロード完了",
                border_style="bold green"
            ))
            time.sleep(2)
        else:
            console.print("[red]セーブデータの読み込みに失敗しました[/red]")
            time.sleep(2)
            return
    
    # ゲームループ
    while True:
        console.clear()
        
        # ステータス表示
        console.print(Panel(
            create_character_panel(player, True),
            title="📊 現在のステータス",
            border_style="cyan"
        ))
        
        # 戦績表示
        win_rate = (player.total_victories / player.total_battles * 100) if player.total_battles > 0 else 0
        console.print(f"\n[dim]戦闘回数: {player.total_battles} | 勝利: {player.total_victories} | 勝率: {win_rate:.1f}%[/dim]\n")
        
        # メニュー表示
        console.print("[bold yellow]--- メニュー ---[/bold yellow]")
        console.print("1: 戦闘")
        console.print("2: 休憩 (HP/MP全回復)")
        console.print("3: 装備")  # 追加
        console.print("4: セーブ")
        console.print("5: ステータス確認")
        console.print("6: ゲーム終了")

        choice = Prompt.ask(
            "行動を選択してください",
            choices=["1", "2", "3", "4", "5", "6"],
            default="1"
        )
        
        if choice == "1":
            # 戦闘
            result = start_battle(player)
            
            if result == "defeat":
                console.print("\n[bold red]GAME OVER[/bold red]")
                
                # ゲームオーバー時にセーブするか確認
                if Confirm.ask("セーブしますか?"):
                    console.clear()
                    slot = show_save_menu(save_system)
                    if slot > 0:
                        if save_system.save_game(player, slot):
                            console.print(f"[green]スロット {slot} にセーブしました[/green]")
                        else:
                            console.print("[red]セーブに失敗しました[/red]")
                        time.sleep(1)
                
                time.sleep(2)
                break
            
            # 戦闘後、続けるか確認
            console.print()
            if not Prompt.ask("続けますか?", choices=["y", "n"], default="y") == "y":
                # 終了前にセーブするか確認
                if Confirm.ask("セーブしますか?"):
                    console.clear()
                    slot = show_save_menu(save_system)
                    if slot > 0:
                        if save_system.save_game(player, slot):
                            console.print(f"[green]スロット {slot} にセーブしました[/green]")
                        else:
                            console.print("[red]セーブに失敗しました[/red]")
                        time.sleep(1)
                break
        
        elif choice == "2":
            # 休憩
            player.hp = player.max_hp
            player.mp = player.max_mp
            console.print("\n[green]休憩して完全に回復した![/green]")
            time.sleep(1)
        
        elif choice == "3":
          # 装備メニュー（追加）
          show_equipment_menu(player)
        
        elif choice == "4":
            # セーブ
            console.clear()
            slot = show_save_menu(save_system)
            
            if slot > 0:
                # 上書き確認
                existing_save = save_system.get_save_info(slot)
                if existing_save:
                    if not Confirm.ask(f"[yellow]スロット {slot} を上書きしますか?[/yellow]"):
                        console.print("[dim]セーブをキャンセルしました[/dim]")
                        time.sleep(1)
                        continue
                
                if save_system.save_game(player, slot):
                    console.print(f"[green]スロット {slot} にセーブしました![/green]")
                else:
                    console.print("[red]セーブに失敗しました[/red]")
                
                time.sleep(1)
        
        elif choice == "5":
            # ステータス確認
            console.clear()
            console.print(Panel(
                create_character_panel(player, True),
                title="📊 詳細ステータス",
                border_style="cyan"
            ))
            Prompt.ask("\n[dim]Enterキーで戻る[/dim]", default="")
        
        elif choice == "6":
            # ゲーム終了
            if Confirm.ask("セーブして終了しますか?"):
                console.clear()
                slot = show_save_menu(save_system)
                if slot > 0:
                    if save_system.save_game(player, slot):
                        console.print(f"[green]スロット {slot} にセーブしました[/green]")
                    else:
                        console.print("[red]セーブに失敗しました[/red]")
                    time.sleep(1)
            break
    
    # ゲーム終了時の統計表示
    console.clear()
    console.print(Panel(
        f"[bold cyan]冒険の記録[/bold cyan]\n\n"
        f"最終レベル: [yellow]{player.level}[/yellow]\n"
        f"総戦闘回数: [cyan]{player.total_battles}[/cyan]\n"
        f"勝利回数: [green]{player.total_victories}[/green]\n"
        f"勝率: [magenta]{win_rate:.1f}%[/magenta]",
        title="📜 エンディング",
        border_style="bold yellow"
    ))


if __name__ == "__main__":
    console.print(Panel(
        "[bold cyan]Python RPG - Save/Load System[/bold cyan]\n\n"
        "[white]セーブ/ロード機能が追加されました!\n"
        "最大3つのセーブスロットが利用可能です[/white]",
        title="🎮 ゲームスタート",
        border_style="bold cyan"
    ))
    time.sleep(2)
    
    game_loop()
    
    console.print("\n[dim]ゲームを終了します...[/dim]")