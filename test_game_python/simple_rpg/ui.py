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
