"""UI表示関連の関数"""

from rich.console import Console
from rich.layout import Layout
from rich.panel import Panel
from rich.prompt import IntPrompt, Prompt
from rich.table import Table

console = Console()


def create_battle_layout():
    """戦闘画面全体のレイアウトを作成"""
    layout = Layout()
    layout.split_column(
        Layout(name="header", size=3),
        Layout(name="main"),
        Layout(name="footer", size=1),
    )

    layout["header"].update(
        Panel("[bold red]⚔️  戦闘中  ⚔️[/bold red]", style="bold white on red")
    )

    layout["main"].split_column(Layout(name="status", size=12), Layout(name="log"))

    return layout


def create_character_panel(character, is_player=True):
    """キャラクターステータスパネルを作成"""
    hp_percentage = (character.hp / character.max_hp) * 100
    hp_color = (
        "green" if hp_percentage > 50 else "yellow" if hp_percentage > 25 else "red"
    )

    # HPバー
    hp_bars = int(hp_percentage / 5)
    hp_bar = "█" * hp_bars + "░" * (20 - hp_bars)

    table = Table(show_header=False, box=None, padding=(0, 1))
    table.add_column(style="bold cyan", width=8)
    table.add_column()

    table.add_row("名前", f"[bold]{character.name}[/bold]")
    table.add_row(
        "HP", f"[{hp_color}]{hp_bar}[/{hp_color}] {character.hp}/{character.max_hp}"
    )

    if is_player:
        mp_bars = int((character.mp / character.max_mp) * 20)
        mp_bar = "█" * mp_bars + "░" * (20 - mp_bars)
        table.add_row("MP", f"[blue]{mp_bar}[/blue] {character.mp}/{character.max_mp}")
        table.add_row("レベル", f"[magenta]{character.level}[/magenta]")

        # 経験値バー
        exp_percentage = (character.exp / character.exp_to_next) * 100
        exp_bars = int(exp_percentage / 5)
        exp_bar = "█" * exp_bars + "░" * (20 - exp_bars)
        table.add_row(
            "EXP", f"[yellow]{exp_bar}[/yellow] {character.exp}/{character.exp_to_next}"
        )

        # 状態異常を考慮した攻撃力・防御力
        attack_text = f"[yellow]{character.attack}[/yellow]"
        if character.get_effective_attack() != character.attack:
            attack_text = f"[yellow]{character.attack}[/yellow] → [bold]{character.get_effective_attack()}[/bold]"

        defense_text = f"[cyan]{character.defense}[/cyan]"
        if character.get_effective_defense() != character.defense:
            defense_text = f"[cyan]{character.defense}[/cyan] → [bold]{character.get_effective_defense()}[/bold]"

        table.add_row("攻撃力", attack_text)
        table.add_row("防御力", defense_text)

    # 状態異常表示
    status_display = character.status_effects.get_status_display()
    if status_display:
        table.add_row("状態", f"[magenta]{status_display}[/magenta]")

    border_color = "green" if is_player else "red"
    emoji = "🛡️" if is_player else "👹"

    return Panel(table, title=f"{emoji} {character.name}", border_style=border_color)


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
        default="1",
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
            table.add_row(
                num, f"[dim]{name}[/dim]", f"[dim]{mp}[/dim]", f"[dim]{effect}[/dim]"
            )
        else:
            table.add_row(num, name, str(mp), effect)
            available_choices.append(num)

    console.print(table)

    choice = Prompt.ask("使用する魔法を選択 (0: 戻る)", choices=available_choices)

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
            table.add_row(
                num,
                f"[dim]{name}[/dim]",
                f"[dim]x{count}[/dim]",
                f"[dim]{effect}[/dim]",
            )

    console.print(table)

    if len(available_choices) == 1:
        console.print("[red]使用できるアイテムがありません[/red]")
        import time

        time.sleep(1)
        return None

    choice = Prompt.ask("使用するアイテムを選択 (0: 戻る)", choices=available_choices)

    if choice == "0":
        return None

    return item_list[int(choice) - 1][1]


def show_level_up(level_up_data):
    """レベルアップの演出を表示"""
    import time

    from rich.console import Console
    from rich.panel import Panel

    console = Console()
    level = level_up_data["level"]

    console.print()
    console.print(
        Panel(
            f"[bold yellow]✨ LEVEL UP! ✨[/bold yellow]\n\n"
            f"[cyan]レベル {level - 1}[/cyan] → [bold cyan]レベル {level}[/bold cyan]\n\n"
            f"[green]HP[/green] +{level_up_data['hp_gain']}\n"
            f"[blue]MP[/blue] +{level_up_data['mp_gain']}\n"
            f"[yellow]攻撃力[/yellow] +{level_up_data['attack_gain']}\n"
            f"[cyan]防御力[/cyan] +{level_up_data['defense_gain']}\n\n"
            f"[bold green]HP・MPが全回復した![/bold green]",
            title="🎉 レベルアップ",
            border_style="bold yellow",
        )
    )
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
    from rich.prompt import IntPrompt
    from rich.table import Table
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
            win_rate = (
                (save_info["total_victories"] / save_info["total_battles"] * 100)
                if save_info["total_battles"] > 0
                else 0
            )
            table.add_row(
                str(i),
                save_info["name"],
                f"Lv.{save_info['level']}",
                f"{save_info['total_victories']}/{save_info['total_battles']} ({win_rate:.0f}%)",
                format_datetime(save_info["save_date"]),
            )
        else:
            table.add_row(str(i), "[dim]--- 空き ---[/dim]", "-", "-", "-")

    console.print(table)
    console.print("\n[dim]0: キャンセル[/dim]")

    choice = IntPrompt.ask(
        "スロットを選択してください",
        choices=[str(i) for i in range(0, max_slots + 1)],
        default=1,
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
    from rich.prompt import IntPrompt
    from rich.table import Table
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
            win_rate = (
                (save_info["total_victories"] / save_info["total_battles"] * 100)
                if save_info["total_battles"] > 0
                else 0
            )
            table.add_row(
                str(i),
                save_info["name"],
                f"Lv.{save_info['level']}",
                f"{save_info['total_victories']}/{save_info['total_battles']} ({win_rate:.0f}%)",
                format_datetime(save_info["save_date"]),
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
        default=1 if "1" in available_slots else 0,
    )

    return choice


def show_equipment_menu(player):
    """
    装備メニューを表示

    Args:
        player: Characterオブジェクト

    Returns:
        str: 選択されたアクション
    """
    while True:
        console.clear()

        # 現在の装備状況を表示
        console.print(
            Panel(
                _create_equipment_status(player),
                title="⚔️ 装備状況",
                border_style="cyan",
            )
        )

        console.print("\n[bold yellow]--- 装備メニュー ---[/bold yellow]")
        console.print("1: 装備を変更")
        console.print("2: 装備を外す")
        console.print("3: 装備インベントリ確認")
        console.print("4: 戻る")

        choice = Prompt.ask(
            "選択してください", choices=["1", "2", "3", "4"], default="4"
        )

        if choice == "1":
            _equip_item(player)
        elif choice == "2":
            _unequip_item(player)
        elif choice == "3":
            _show_equipment_inventory(player)
        elif choice == "4":
            break


def _create_equipment_status(player):
    """装備状況のテキストを生成"""
    lines = []

    # 現在の装備
    lines.append("[bold]【現在の装備】[/bold]")

    weapon = player.equipment.weapon
    armor = player.equipment.armor
    accessory = player.equipment.accessory

    if weapon:
        lines.append(
            f"武器: [yellow]{weapon.name}[/yellow] ({weapon.get_all_stats_text()})"
        )
    else:
        lines.append("武器: [dim]なし[/dim]")

    if armor:
        lines.append(f"防具: [cyan]{armor.name}[/cyan] ({armor.get_all_stats_text()})")
    else:
        lines.append("防具: [dim]なし[/dim]")

    if accessory:
        lines.append(
            f"アクセサリ: [magenta]{accessory.name}[/magenta] ({accessory.get_all_stats_text()})"
        )
    else:
        lines.append("アクセサリ: [dim]なし[/dim]")

    # ステータス情報
    lines.append("\n[bold]【ステータス】[/bold]")
    equipment_stats = player.equipment.get_total_stats()

    attack_bonus = equipment_stats.get("attack", 0)
    defense_bonus = equipment_stats.get("defense", 0)
    hp_bonus = equipment_stats.get("max_hp", 0)
    mp_bonus = equipment_stats.get("max_mp", 0)

    lines.append(
        f"攻撃力: {player.base_attack} [green]+{attack_bonus}[/green] = [bold]{player.attack}[/bold]"
    )
    lines.append(
        f"防御力: {player.base_defense} [green]+{defense_bonus}[/green] = [bold]{player.defense}[/bold]"
    )
    lines.append(
        f"最大HP: {player.base_max_hp} [green]+{hp_bonus}[/green] = [bold]{player.max_hp}[/bold]"
    )
    lines.append(
        f"最大MP: {player.base_max_mp} [green]+{mp_bonus}[/green] = [bold]{player.max_mp}[/bold]"
    )

    # インベントリ情報
    lines.append(f"\n所持装備数: [yellow]{len(player.equipment_inventory)}[/yellow]個")
    lines.append(f"所持金: [yellow]{player.gold}[/yellow] G")

    return "\n".join(lines)


def _equip_item(player):
    """装備を変更する"""
    console.clear()

    if not player.equipment_inventory:
        console.print("[red]装備できるアイテムがありません[/red]")
        Prompt.ask("\n[dim]Enterキーで戻る[/dim]", default="")
        return

    # 装備インベントリを表示
    table = Table(title="🎒 装備インベントリ", show_header=True)
    table.add_column("No.", style="cyan", width=4)
    table.add_column("装備名", style="green", width=20)
    table.add_column("種類", style="yellow", width=12)
    table.add_column("必要Lv", style="magenta", width=8)
    table.add_column("効果", style="white", width=30)

    for i, equipment in enumerate(player.equipment_inventory, 1):
        equipment_type_name = {
            "weapon": "武器",
            "armor": "防具",
            "accessory": "アクセサリ",
        }.get(equipment.type, equipment.type)

        # レベル不足の場合は灰色表示
        if equipment.required_level > player.level:
            table.add_row(
                str(i),
                f"[dim]{equipment.name}[/dim]",
                f"[dim]{equipment_type_name}[/dim]",
                f"[dim]Lv.{equipment.required_level}[/dim]",
                f"[dim]{equipment.get_all_stats_text()}[/dim]",
            )
        else:
            table.add_row(
                str(i),
                equipment.name,
                equipment_type_name,
                f"Lv.{equipment.required_level}",
                equipment.get_all_stats_text(),
            )

    console.print(table)
    console.print("\n[dim]0: キャンセル[/dim]")

    choice = IntPrompt.ask(
        "装備する番号を選択",
        choices=[str(i) for i in range(0, len(player.equipment_inventory) + 1)],
        default=0,
    )

    if choice == 0:
        return

    selected_equipment = player.equipment_inventory[choice - 1]

    # 装備を試みる
    success, message = player.equipment.equip(selected_equipment, player.level)

    if success:
        # ステータス再計算
        player.recalculate_stats()
        console.print(f"\n[green]{message}[/green]")
    else:
        console.print(f"\n[red]{message}[/red]")

    import time

    time.sleep(1.5)


def _unequip_item(player):
    """装備を外す"""
    console.clear()

    equipped = player.equipment.get_equipped_list()

    if not equipped:
        console.print("[red]装備しているアイテムがありません[/red]")
        Prompt.ask("\n[dim]Enterキーで戻る[/dim]", default="")
        return

    # 装備中のアイテムを表示
    table = Table(title="📦 装備中のアイテム", show_header=True)
    table.add_column("No.", style="cyan", width=4)
    table.add_column("装備名", style="green", width=20)
    table.add_column("種類", style="yellow", width=12)
    table.add_column("効果", style="white", width=30)

    equipment_types = []
    for i, equipment in enumerate(equipped, 1):
        equipment_type_name = {
            "weapon": "武器",
            "armor": "防具",
            "accessory": "アクセサリ",
        }.get(equipment.type, equipment.type)

        table.add_row(
            str(i), equipment.name, equipment_type_name, equipment.get_all_stats_text()
        )
        equipment_types.append(equipment.type)

    console.print(table)
    console.print("\n[dim]0: キャンセル[/dim]")

    choice = IntPrompt.ask(
        "外す装備の番号を選択",
        choices=[str(i) for i in range(0, len(equipped) + 1)],
        default=0,
    )

    if choice == 0:
        return

    equipment_type = equipment_types[choice - 1]
    success, removed_equipment = player.equipment.unequip(equipment_type)

    if success and removed_equipment:
        # ステータス再計算
        player.recalculate_stats()
        console.print(f"\n[green]{removed_equipment.name} を外しました[/green]")
    else:
        console.print("\n[red]装備を外せませんでした[/red]")

    import time

    time.sleep(1.5)


def _show_equipment_inventory(player):
    """装備インベントリの詳細を表示"""
    console.clear()

    if not player.equipment_inventory:
        console.print("[red]装備インベントリが空です[/red]")
        Prompt.ask("\n[dim]Enterキーで戻る[/dim]", default="")
        return

    # インベントリを表示
    table = Table(title="🎒 装備インベントリ詳細", show_header=True)
    table.add_column("装備名", style="green", width=20)
    table.add_column("種類", style="yellow", width=12)
    table.add_column("レアリティ", style="magenta", width=12)
    table.add_column("必要Lv", style="cyan", width=8)
    table.add_column("効果", style="white", width=30)
    table.add_column("売却", style="yellow", width=10)

    for equipment in player.equipment_inventory:
        equipment_type_name = {
            "weapon": "武器",
            "armor": "防具",
            "accessory": "アクセサリ",
        }.get(equipment.type, equipment.type)

        rarity_color = {
            "common": "white",
            "uncommon": "green",
            "rare": "blue",
            "legendary": "magenta",
        }.get(equipment.rarity, "white")

        rarity_name = {
            "common": "一般",
            "uncommon": "上位",
            "rare": "レア",
            "legendary": "伝説",
        }.get(equipment.rarity, equipment.rarity)

        table.add_row(
            equipment.name,
            equipment_type_name,
            f"[{rarity_color}]{rarity_name}[/{rarity_color}]",
            f"Lv.{equipment.required_level}",
            equipment.get_all_stats_text(),
            f"{equipment.sell_price}G",
        )

    console.print(table)
    Prompt.ask("\n[dim]Enterキーで戻る[/dim]", default="")


def show_equipment_drop(equipment):
    """
    装備ドロップの演出を表示

    Args:
        equipment: ドロップしたEquipmentオブジェクト
    """
    import time

    rarity_color = {
        "common": "white",
        "uncommon": "green",
        "rare": "cyan",
        "legendary": "magenta",
    }.get(equipment.rarity, "white")

    console.print()
    console.print(
        Panel(
            f"[bold {rarity_color}]✨ {equipment.name} を入手! ✨[/bold {rarity_color}]\n\n"
            f"[white]{equipment.description}[/white]\n"
            f"[yellow]効果: {equipment.get_all_stats_text()}[/yellow]",
            title="🎁 装備ドロップ",
            border_style=rarity_color,
        )
    )
    time.sleep(2)
