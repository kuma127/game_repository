"""戦闘フロー管理"""

import random
import time

from battle_log import BattleLog
from character import Character
from combat import animate_attack, calculate_damage, show_damage_effect
from enemy_manager import get_enemy_manager
from equipment_manager import get_equipment_manager
from rich.console import Console
from rich.layout import Layout
from rich.panel import Panel
from ui import (
    create_battle_layout,
    create_character_panel,
    show_action_menu,
    show_equipment_drop,
    show_item_menu,
    show_level_up,
    show_magic_menu,
)

console = Console()


def battle_turn(player: Character, enemy: Character, battle_log):
    """1ターンの戦闘処理"""
    console.clear()

    # レイアウト作成
    layout = create_battle_layout()

    # ステータス表示
    status_layout = Layout()
    status_layout.split_row(
        Layout(create_character_panel(player, True)),
        Layout(create_character_panel(enemy, False)),
    )
    layout["main"]["status"].update(status_layout)

    # ログ表示
    layout["main"]["log"].update(battle_log.render())

    layout["footer"].update("")

    console.print(layout)
    console.print()

    # === プレイヤーのターン開始時処理 ===
    player_turn_messages = player.status_effects.process_turn_effects(
        player, player.name
    )
    for message in player_turn_messages:
        console.print(f"[yellow]{message}[/yellow]")
        battle_log.add(message, "yellow")
        time.sleep(0.5)

    if not player.is_alive():
        return "defeat"

    # 行動可能かチェック
    can_act, reason = player.status_effects.can_act()
    if not can_act:
        console.print(f"[yellow]{reason}[/yellow]")
        battle_log.add(reason, "yellow")
        time.sleep(1.5)
    else:
        # 通常のプレイヤーターン処理
        while True:
            action = show_action_menu(player)

            if action == "1":  # 攻撃
                # 攻撃可能かチェック
                if not player.status_effects.can_perform_action("attack"):
                    console.print("[red]状態異常により攻撃できません！[/red]")
                    time.sleep(1)
                    continue

                damage, is_critical, wake_message = calculate_damage(player, enemy)
                console.print()

                if wake_message:
                    console.print(f"[cyan]{wake_message}[/cyan]")
                    battle_log.add(wake_message, "cyan")
                    time.sleep(0.5)

                animate_attack(player.name, enemy.name, damage)
                show_damage_effect(damage, is_critical)
                enemy.take_damage(damage)

                crit_text = " (クリティカル!)" if is_critical else ""
                battle_log.add(
                    f"{player.name} の攻撃! {enemy.name} に {damage} ダメージ{crit_text}",
                    "cyan",
                )
                break

            elif action == "2":  # 魔法
                # 魔法使用可能かチェック
                if not player.status_effects.can_perform_action("magic"):
                    console.print("[red]状態異常により魔法を使えません！[/red]")
                    time.sleep(1)
                    continue
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
                        battle_log.add(
                            f"{player.name} は {name} を使用! HP +{heal_amount}",
                            "green",
                        )
                    else:
                        damage, is_critical, wake_message = calculate_damage(
                            player, enemy, multiplier
                        )
                        if wake_message:
                            console.print(f"[cyan]{wake_message}[/cyan]")
                            battle_log.add(wake_message, "cyan")
                            time.sleep(0.5)
                        console.print(f"[magenta]✨ {name}![/magenta]")
                        time.sleep(0.5)
                        show_damage_effect(damage, is_critical)
                        enemy.take_damage(damage)

                        crit_text = " (クリティカル!)" if is_critical else ""
                        battle_log.add(
                            f"{player.name} の {name}! {enemy.name} に {damage} ダメージ{crit_text}",
                            "magenta",
                        )

                    time.sleep(1)
                    break

            elif action == "3":  # アイテム
                # アイテム使用可能かチェック
                if not player.status_effects.can_perform_action("item"):
                    console.print("[red]状態異常によりアイテムを使えません！[/red]")
                    time.sleep(1)
                    continue
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
                    console.print(
                        f"[green]{item} を使用! HP が {heal_amount} 回復した![/green]"
                    )
                    battle_log.add(
                        f"{player.name} は {item} を使用! HP +{heal_amount}", "green"
                    )
                elif item == "魔法の水":
                    mp_amount = 20
                    player.restore_mp(mp_amount)
                    player.items[item] -= 1
                    console.print(
                        f"[blue]{item} を使用! MP が {mp_amount} 回復した![/blue]"
                    )
                    battle_log.add(
                        f"{player.name} は {item} を使用! MP +{mp_amount}", "blue"
                    )

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

    enemy_turn_messages = enemy.status_effects.process_turn_effects(enemy, enemy.name)
    for message in enemy_turn_messages:
        console.print(f"[yellow]{message}[/yellow]")
        battle_log.add(message, "yellow")
        time.sleep(0.5)

    # 敵が死亡していないかチェック
    if not enemy.is_alive():
        return "victory"

    # 敵の行動可能チェック
    can_act, reason = enemy.status_effects.can_act()
    if not can_act:
        console.print(f"[yellow]{reason}[/yellow]")
        battle_log.add(reason, "yellow")
        time.sleep(1.5)
    else:
        # 敵のAI (シンプルな行動選択)
        enemy_action = random.choices(["attack", "strong_attack"], weights=[0.7, 0.3])[
            0
        ]

        if enemy_action == "attack":
            damage, is_critical, wake_message = calculate_damage(enemy, player)
            if wake_message:
                console.print(f"[cyan]{wake_message}[/cyan]")
                battle_log.add(wake_message, "cyan")
                time.sleep(0.5)
            animate_attack(enemy.name, player.name, damage)
            show_damage_effect(damage, is_critical)
            player.take_damage(damage)

            crit_text = " (クリティカル!)" if is_critical else ""
            battle_log.add(
                f"{enemy.name} の攻撃! {player.name} に {damage} ダメージ{crit_text}",
                "red",
            )

        elif enemy_action == "strong_attack":
            damage, is_critical, wake_message = calculate_damage(enemy, player, 1.5)

            if wake_message:
                console.print(f"[cyan]{wake_message}[/cyan]")
                battle_log.add(wake_message, "cyan")
                time.sleep(0.5)
            console.print(f"[bold red]{enemy.name} の強攻撃![/bold red]")
            time.sleep(0.5)
            show_damage_effect(damage, is_critical)
            player.take_damage(damage)

            crit_text = " (クリティカル!)" if is_critical else ""
            battle_log.add(
                f"{enemy.name} の強攻撃! {player.name} に {damage} ダメージ{crit_text}",
                "red",
            )

    time.sleep(1.5)

    if not player.is_alive():
        return "defeat"

    return "continue"


def start_battle(player: Character) -> str:
    """戦闘を開始する"""
    console.clear()

    # キャラクター初期化
    enemy = create_enemy(player.level)

    battle_log = BattleLog()

    # 戦闘回数をカウント（戦闘開始時に追加）
    player.total_battles += 1

    # 戦闘開始メッセージ
    console.print(
        Panel(
            f"[bold red]{enemy.name} (Lv.{enemy.level}) が現れた![/bold red]",
            title="⚔️ 戦闘開始",
            border_style="bold red",
        )
    )
    battle_log.add(f"{enemy.name} (Lv.{enemy.level}) が現れた!", "red")
    time.sleep(2)

    # 戦闘ループ
    turn = 1
    while True:
        result = battle_turn(player, enemy, battle_log)

        if result == "victory":
            player.total_victories += 1

            console.clear()

            # 経験値とゴールド獲得
            exp_gained = enemy.exp_reward
            gold_gained = enemy.gold_reward

            console.print(
                Panel(
                    f"[bold green]🎉 {enemy.name} を倒した! 🎉[/bold green]\n\n"
                    f"[yellow]経験値 {exp_gained} を獲得![/yellow]\n"
                    f"[yellow]ゴールド {gold_gained} G を獲得![/yellow]",
                    title="✨ 勝利",
                    border_style="bold green",
                )
            )

            player.gold += gold_gained
            time.sleep(2)

            # 装備ドロップ判定
            equipment_manager = get_equipment_manager()
            dropped_equipment = equipment_manager.roll_equipment_drop(enemy.rarity)

            if dropped_equipment:
                show_equipment_drop(dropped_equipment)
                player.add_equipment_to_inventory(dropped_equipment)

            # レベルアップ判定（追加）
            level_ups = player.gain_exp(exp_gained)

            for level_up_data in level_ups:
                show_level_up(level_up_data)

            return result

        elif result == "defeat":
            console.clear()
            console.print(
                Panel(
                    f"[bold red]💀 {player.name} は力尽きた... 💀[/bold red]",
                    title="☠️ 敗北",
                    border_style="bold red",
                )
            )
            return result

        elif result == "escaped":
            console.clear()
            console.print(
                Panel(
                    "[yellow]無事に逃げ切った![/yellow]",
                    title="🏃 脱出成功",
                    border_style="yellow",
                )
            )
            return result

        turn += 1


def create_enemy(player_level):
    """
    プレイヤーのレベルに応じた敵を生成

    Args:
        player_level: プレイヤーのレベル

    Returns:
        Character: 敵のCharacterオブジェクト
    """
    from character import Character

    # EnemyManagerから敵情報を取得
    enemy_manager = get_enemy_manager()
    enemy_info = enemy_manager.create_enemy(player_level)

    # Characterオブジェクトを生成
    enemy = Character(
        name=enemy_info["name"],
        hp=enemy_info["hp"],
        max_hp=enemy_info["max_hp"],
        mp=enemy_info["mp"],
        max_mp=enemy_info["max_mp"],
        attack=enemy_info["attack"],
        defense=enemy_info["defense"],
        level=enemy_info["level"],
    )

    # 追加情報を属性として付与
    enemy.exp_reward = enemy_info["exp_reward"]
    enemy.gold_reward = enemy_info.get("gold_reward", 0)
    enemy.ai_pattern = enemy_info.get("ai_pattern", "simple_attack")
    enemy.special_abilities = enemy_info.get("special_abilities", [])
    enemy.rarity = enemy_info.get("rarity", "common")
    enemy.enemy_id = enemy_info["id"]

    return enemy


def apply_status_effect(target, status_id, attacker_name, battle_log):
    """
    状態異常を付与する

    Args:
        target: 対象のCharacter
        status_id: 状態異常ID
        attacker_name: 攻撃者の名前
        battle_log: BattleLogオブジェクト

    Returns:
        bool: 付与に成功したか
    """
    import time

    from rich.console import Console
    from status_manager import get_status_manager

    console = Console()
    status_manager = get_status_manager()

    # 状態異常を生成
    status = status_manager.create_status(status_id)
    if not status:
        return False

    # 状態異常を付与
    success, message = target.status_effects.add_status(status, target.name)

    if success:
        console.print(f"[magenta]{message}[/magenta]")
        battle_log.add(message, "magenta")
        time.sleep(1)
        return True

    return False


# 敵の特殊能力で状態異常を付与する例
def enemy_special_attack(enemy, player, battle_log):
    """
    敵の特殊攻撃（状態異常付与）

    Args:
        enemy: 敵のCharacter
        player: プレイヤーのCharacter
        battle_log: BattleLogオブジェクト
    """
    import random

    from rich.console import Console

    console = Console()

    # 敵IDに応じた特殊攻撃
    if hasattr(enemy, "enemy_id"):
        if enemy.enemy_id == "hornet" and random.random() < 0.3:
            # ホーネットの毒針
            console.print(f"[bold red]{enemy.name} の毒針![/bold red]")
            apply_status_effect(player, "poison", enemy.name, battle_log)

        elif enemy.enemy_id == "dark_wizard" and random.random() < 0.4:
            # ダークウィザードの呪い
            console.print(f"[bold purple]{enemy.name} の呪いの魔法![/bold purple]")
            apply_status_effect(player, "curse", enemy.name, battle_log)

        elif enemy.enemy_id == "bat" and random.random() < 0.25:
            # コウモリの麻痺攻撃
            console.print(f"[bold yellow]{enemy.name} の痺れ攻撃![/bold yellow]")
            apply_status_effect(player, "paralysis", enemy.name, battle_log)
