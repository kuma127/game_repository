"""UI表示関連の関数"""

from rich.console import Console
from rich.panel import Panel
from rich.layout import Layout
from rich.table import Table
from rich.prompt import Prompt

console = Console()


def create_battle_layout():
    """戦闘画面全体のレイアウトを作成"""
    layout = Layout()
    layout.split_column(
        Layout(name="header", size=3),
        Layout(name="main"),
        Layout(name="footer", size=1)
    )

    layout["header"].update(
        Panel("[bold red]⚔️  戦闘中  ⚔️[/bold red]", style="bold white on red")
    )

    layout["main"].split_column(
        Layout(name="status", size=12),
        Layout(name="log")
    )

    return layout


def create_character_panel(character, is_player=True):
    """キャラクターステータスパネルを作成"""
    hp_percentage = (character.hp / character.max_hp) * 100
    hp_color = "green" if hp_percentage > 50 else "yellow" if hp_percentage > 25 else "red"

    # HPバー
    hp_bars = int(hp_percentage / 5)
    hp_bar = "█" * hp_bars + "░" * (20 - hp_bars)

    table = Table(show_header=False, box=None, padding=(0, 1))
    table.add_column(style="bold cyan", width=8)
    table.add_column()

    table.add_row("名前", f"[bold]{character.name}[/bold]")
    table.add_row("HP", f"[{hp_color}]{hp_bar}[/{hp_color}] {character.hp}/{character.max_hp}")

    if is_player:
        mp_bars = int((character.mp / character.max_mp) * 20)
        mp_bar = "█" * mp_bars + "░" * (20 - mp_bars)
        table.add_row("MP", f"[blue]{mp_bar}[/blue] {character.mp}/{character.max_mp}")
        
        # ↓↓↓ ここから追加 ↓↓↓
        table.add_row("レベル", f"[magenta]{character.level}[/magenta]")
        
        # 経験値バー
        exp_percentage = (character.exp / character.exp_to_next) * 100
        exp_bars = int(exp_percentage / 5)
        exp_bar = "█" * exp_bars + "░" * (20 - exp_bars)
        table.add_row("EXP", f"[yellow]{exp_bar}[/yellow] {character.exp}/{character.exp_to_next}")
        # ↑↑↑ ここまで追加 ↑↑↑
        
        table.add_row("攻撃力", f"[yellow]{character.attack}[/yellow]")
        table.add_row("防御力", f"[cyan]{character.defense}[/cyan]")

    border_color = "green" if is_player else "red"
    emoji = "🛡️" if is_player else "👹"

    return Panel(
        table,
        title=f"{emoji} {character.name}",
        border_style=border_color
    )


def show_action_menu(player):
    """アクションメニューを表示して選択を取得"""
    table = Table(show_header=False, box=None, padding=(0, 2))
    table.add_column(style="bold yellow", width=3)
    table.add_column(style="white")

    table.add_row("1", "⚔️  攻撃")
    table.add_row("2", f"✨ 魔法 (MP: {player.mp}/{player.max_mp})")
    table.add_row("3", "🎒 アイテム")
    table.add_row("4", "🏃 逃げる")

    console.print(table)

    choice = Prompt.ask(
        "[bold cyan]行動を選択してください[/bold cyan]",
        choices=["1", "2", "3", "4"],
        default="1"
    )

    return choice


def show_magic_menu(player):
    """魔法選択メニューを表示"""
    table = Table(title="✨ 魔法リスト", show_header=True)
    table.add_column("No.", style="cyan", width=4)
    table.add_column("魔法", style="magenta", width=12)
    table.add_column("MP", style="blue", width=6)
    table.add_column("効果", style="white")

    magic_list = [
        ("1", "ファイア", 10, "敵に炎属性ダメージ", 1.5),
        ("2", "ヒール", 15, "HPを30回復", 0),
        ("3", "サンダー", 20, "敵に雷属性ダメージ", 2.0),
    ]

    available_choices = ["0"]
    for num, name, mp, effect, _ in magic_list:
        if player.mp < mp:
            table.add_row(num, f"[dim]{name}[/dim]", f"[dim]{mp}[/dim]", f"[dim]{effect}[/dim]")
        else:
            table.add_row(num, name, str(mp), effect)
            available_choices.append(num)

    console.print(table)

    choice = Prompt.ask(
        "使用する魔法を選択 (0: 戻る)",
        choices=available_choices
    )

    if choice == "0":
        return None

    return magic_list[int(choice) - 1]


def show_item_menu(player):
    """アイテムメニューを表示"""
    table = Table(title="🎒 アイテム", show_header=True)
    table.add_column("No.", style="cyan", width=4)
    table.add_column("アイテム", style="green", width=12)
    table.add_column("所持数", style="yellow", width=8)
    table.add_column("効果", style="white")

    item_list = [
        ("1", "回復薬", "HP 50回復"),
        ("2", "魔法の水", "MP 20回復"),
    ]

    available_choices = ["0"]
    for idx, (num, name, effect) in enumerate(item_list, 1):
        count = player.items.get(name, 0)
        if count > 0:
            table.add_row(num, name, f"x{count}", effect)
            available_choices.append(num)
        else:
            table.add_row(num, f"[dim]{name}[/dim]", f"[dim]x{count}[/dim]", f"[dim]{effect}[/dim]")

    console.print(table)

    if len(available_choices) == 1:
        console.print("[red]使用できるアイテムがありません[/red]")
        import time
        time.sleep(1)
        return None

    choice = Prompt.ask(
        "使用するアイテムを選択 (0: 戻る)",
        choices=available_choices
    )

    if choice == "0":
        return None

    return item_list[int(choice) - 1][1]

def show_level_up(level_up_data):
    """レベルアップの演出を表示"""
    from rich.console import Console
    from rich.panel import Panel
    import time
    
    console = Console()
    level = level_up_data["level"]
    
    console.print()
    console.print(Panel(
        f"[bold yellow]✨ LEVEL UP! ✨[/bold yellow]\n\n"
        f"[cyan]レベル {level - 1}[/cyan] → [bold cyan]レベル {level}[/bold cyan]\n\n"
        f"[green]HP[/green] +{level_up_data['hp_gain']}\n"
        f"[blue]MP[/blue] +{level_up_data['mp_gain']}\n"
        f"[yellow]攻撃力[/yellow] +{level_up_data['attack_gain']}\n"
        f"[cyan]防御力[/cyan] +{level_up_data['defense_gain']}\n\n"
        f"[bold green]HP・MPが全回復した![/bold green]",
        title="🎉 レベルアップ",
        border_style="bold yellow"
    ))
    time.sleep(3)

def show_save_menu(save_system, max_slots=3):
    """
    セーブスロット選択メニューを表示
    
    Args:
        save_system: SaveSystemオブジェクト
        max_slots: 最大スロット数
    
    Returns:
        int: 選択されたスロット番号（キャンセル時は0）
    """
    from rich.console import Console
    from rich.table import Table
    from rich.prompt import IntPrompt
    from save_system import format_datetime
    
    console = Console()
    
    table = Table(title="💾 セーブスロット選択", show_header=True)
    table.add_column("スロット", style="cyan", width=8)
    table.add_column("名前", style="green", width=12)
    table.add_column("レベル", style="yellow", width=8)
    table.add_column("戦績", style="magenta", width=15)
    table.add_column("保存日時", style="white", width=20)
    
    saves = save_system.list_saves(max_slots)
    
    for i, save_info in enumerate(saves, 1):
        if save_info:
            win_rate = (save_info["total_victories"] / save_info["total_battles"] * 100) if save_info["total_battles"] > 0 else 0
            table.add_row(
                str(i),
                save_info["name"],
                f"Lv.{save_info['level']}",
                f"{save_info['total_victories']}/{save_info['total_battles']} ({win_rate:.0f}%)",
                format_datetime(save_info["save_date"])
            )
        else:
            table.add_row(str(i), "[dim]--- 空き ---[/dim]", "-", "-", "-")
    
    console.print(table)
    console.print("\n[dim]0: キャンセル[/dim]")
    
    choice = IntPrompt.ask(
        "スロットを選択してください",
        choices=[str(i) for i in range(0, max_slots + 1)],
        default=1
    )
    
    return choice


def show_load_menu(save_system, max_slots=3):
    """
    ロードスロット選択メニューを表示（セーブメニューとほぼ同じ）
    
    Args:
        save_system: SaveSystemオブジェクト
        max_slots: 最大スロット数
    
    Returns:
        int: 選択されたスロット番号（キャンセル時は0）
    """
    from rich.console import Console
    from rich.table import Table
    from rich.prompt import IntPrompt
    from save_system import format_datetime
    
    console = Console()
    
    table = Table(title="📂 ロードスロット選択", show_header=True)
    table.add_column("スロット", style="cyan", width=8)
    table.add_column("名前", style="green", width=12)
    table.add_column("レベル", style="yellow", width=8)
    table.add_column("戦績", style="magenta", width=15)
    table.add_column("保存日時", style="white", width=20)
    
    saves = save_system.list_saves(max_slots)
    available_slots = ["0"]
    
    for i, save_info in enumerate(saves, 1):
        if save_info:
            win_rate = (save_info["total_victories"] / save_info["total_battles"] * 100) if save_info["total_battles"] > 0 else 0
            table.add_row(
                str(i),
                save_info["name"],
                f"Lv.{save_info['level']}",
                f"{save_info['total_victories']}/{save_info['total_battles']} ({win_rate:.0f}%)",
                format_datetime(save_info["save_date"])
            )
            available_slots.append(str(i))
        else:
            table.add_row(str(i), "[dim]--- 空き ---[/dim]", "-", "-", "-")
    
    console.print(table)
    console.print("\n[dim]0: キャンセル[/dim]")
    
    if len(available_slots) == 1:
        console.print("[red]ロード可能なセーブデータがありません[/red]")
        return 0
    
    choice = IntPrompt.ask(
        "ロードするスロットを選択してください",
        choices=available_slots,
        default=1 if "1" in available_slots else 0
    )
    
    return choice