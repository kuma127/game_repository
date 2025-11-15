"""戦闘フロー管理"""

import random
import time
from rich.console import Console
from rich.panel import Panel
from rich.layout import Layout

from character import Character
from battle_log import BattleLog
from ui import (
    create_battle_layout,
    create_character_panel,
    show_action_menu,
    show_magic_menu,
    show_item_menu
)
from combat import (
    calculate_damage,
    animate_attack,
    show_damage_effect
)

console = Console()


def battle_turn(player, enemy, battle_log):
    """1ターンの戦闘処理"""
    console.clear()

    # レイアウト作成
    layout = create_battle_layout()

    # ステータス表示
    status_layout = Layout()
    status_layout.split_row(
        Layout(create_character_panel(player, True)),
        Layout(create_character_panel(enemy, False))
    )
    layout["main"]["status"].update(status_layout)

    # ログ表示
    layout["main"]["log"].update(battle_log.render())

    layout["footer"].update("")

    console.print(layout)
    console.print()

    # プレイヤーのターン
    while True:
        action = show_action_menu(player)

        if action == "1":  # 攻撃
            damage, is_critical = calculate_damage(player, enemy)
            console.print()
            animate_attack(player.name, enemy.name, damage)
            show_damage_effect(damage, is_critical)
            enemy.take_damage(damage)

            crit_text = " (クリティカル!)" if is_critical else ""
            battle_log.add(f"{player.name} の攻撃! {enemy.name} に {damage} ダメージ{crit_text}", "cyan")
            break

        elif action == "2":  # 魔法
            console.print()
            magic = show_magic_menu(player)
            if magic is None:
                console.clear()
                layout["main"]["status"].update(status_layout)
                layout["main"]["log"].update(battle_log.render())
                console.print(layout)
                console.print()
                continue

            _, name, mp_cost, _, multiplier = magic

            if player.use_mp(mp_cost):
                console.print()
                if name == "ヒール":
                    heal_amount = 30
                    player.heal(heal_amount)
                    console.print(f"[green]✨ {name}![/green]")
                    console.print(f"[green]HP が {heal_amount} 回復した![/green]")
                    battle_log.add(f"{player.name} は {name} を使用! HP +{heal_amount}", "green")
                else:
                    damage, is_critical = calculate_damage(player, enemy, multiplier)
                    console.print(f"[magenta]✨ {name}![/magenta]")
                    time.sleep(0.5)
                    show_damage_effect(damage, is_critical)
                    enemy.take_damage(damage)

                    crit_text = " (クリティカル!)" if is_critical else ""
                    battle_log.add(f"{player.name} の {name}! {enemy.name} に {damage} ダメージ{crit_text}", "magenta")

                time.sleep(1)
                break

        elif action == "3":  # アイテム
            console.print()
            item = show_item_menu(player)
            if item is None:
                console.clear()
                layout["main"]["status"].update(status_layout)
                layout["main"]["log"].update(battle_log.render())
                console.print(layout)
                console.print()
                continue

            console.print()
            if item == "回復薬":
                heal_amount = 50
                player.heal(heal_amount)
                player.items[item] -= 1
                console.print(f"[green]{item} を使用! HP が {heal_amount} 回復した![/green]")
                battle_log.add(f"{player.name} は {item} を使用! HP +{heal_amount}", "green")
            elif item == "魔法の水":
                mp_amount = 20
                player.restore_mp(mp_amount)
                player.items[item] -= 1
                console.print(f"[blue]{item} を使用! MP が {mp_amount} 回復した![/blue]")
                battle_log.add(f"{player.name} は {item} を使用! MP +{mp_amount}", "blue")

            time.sleep(1)
            break

        elif action == "4":  # 逃げる
            if random.random() < 0.5:
                console.print("[yellow]逃げ出した![/yellow]")
                battle_log.add("戦闘から逃げ出した!", "yellow")
                time.sleep(1)
                return "escaped"
            else:
                console.print("[red]逃げられなかった![/red]")
                battle_log.add("逃げることに失敗した...", "red")
                time.sleep(1)
                break

    if not enemy.is_alive():
        return "victory"

    # 敵のターン
    time.sleep(1)
    console.print()
    console.print("[bold]--- 敵のターン ---[/bold]")
    time.sleep(0.5)

    # 敵のAI (シンプルな行動選択)
    enemy_action = random.choices(["attack", "strong_attack"], weights=[0.7, 0.3])[0]

    if enemy_action == "attack":
        damage, is_critical = calculate_damage(enemy, player)
        animate_attack(enemy.name, player.name, damage)
        show_damage_effect(damage, is_critical)
        player.take_damage(damage)

        crit_text = " (クリティカル!)" if is_critical else ""
        battle_log.add(f"{enemy.name} の攻撃! {player.name} に {damage} ダメージ{crit_text}", "red")

    elif enemy_action == "strong_attack":
        damage, is_critical = calculate_damage(enemy, player, 1.5)
        console.print(f"[bold red]{enemy.name} の強攻撃![/bold red]")
        time.sleep(0.5)
        show_damage_effect(damage, is_critical)
        player.take_damage(damage)

        crit_text = " (クリティカル!)" if is_critical else ""
        battle_log.add(f"{enemy.name} の強攻撃! {player.name} に {damage} ダメージ{crit_text}", "red")

    time.sleep(1.5)

    if not player.is_alive():
        return "defeat"

    return "continue"


def start_battle():
    """戦闘を開始する"""
    console.clear()

    # キャラクター初期化
    player = Character("勇者", 100, 100, 50, 50, 25, 10)
    enemy = Character("ゴブリン", 80, 80, 0, 0, 20, 5)

    battle_log = BattleLog()

    # 戦闘開始メッセージ
    console.print(Panel(
        f"[bold red]{enemy.name} が現れた![/bold red]",
        title="⚔️ 戦闘開始",
        border_style="bold red"
    ))
    battle_log.add(f"{enemy.name} が現れた!", "red")
    time.sleep(2)

    # 戦闘ループ
    turn = 1
    while True:
        result = battle_turn(player, enemy, battle_log)

        if result == "victory":
            console.clear()
            console.print(Panel(
                f"[bold green]🎉 {enemy.name} を倒した! 🎉[/bold green]\n\n[yellow]経験値 100 を獲得![/yellow]",
                title="✨ 勝利",
                border_style="bold green"
            ))
            break

        elif result == "defeat":
            console.clear()
            console.print(Panel(
                f"[bold red]💀 {player.name} は力尽きた... 💀[/bold red]",
                title="☠️ 敗北",
                border_style="bold red"
            ))
            break

        elif result == "escaped":
            console.clear()
            console.print(Panel(
                "[yellow]無事に逃げ切った![/yellow]",
                title="🏃 脱出成功",
                border_style="yellow"
            ))
            break

        turn += 1
