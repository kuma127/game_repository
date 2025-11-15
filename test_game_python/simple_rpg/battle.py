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
    show_item_menu,
    show_level_up
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


def start_battle(player: Character) -> str:
    """戦闘を開始する"""
    console.clear()

    # キャラクター初期化
    enemy = create_enemy(player.level)

    battle_log = BattleLog()

    # 戦闘回数をカウント（戦闘開始時に追加）
    player.total_battles += 1

    # 戦闘開始メッセージ
    console.print(Panel(
        f"[bold red]{enemy.name} (Lv.{enemy.level}) が現れた![/bold red]",
        title="⚔️ 戦闘開始",
        border_style="bold red"
    ))
    battle_log.add(f"{enemy.name} (Lv.{enemy.level}) が現れた!", "red")
    time.sleep(2)

    # 戦闘ループ
    turn = 1
    while True:
        result = battle_turn(player, enemy, battle_log)

        if result == "victory":
            player.total_victories += 1

            console.clear()

            # 経験値獲得
            exp_gained = enemy.exp_reward
            console.print(Panel(
                f"[bold green]🎉 {enemy.name} を倒した! 🎉[/bold green]\n\n"
                f"[yellow]経験値 {exp_gained} を獲得![/yellow]",
                title="✨ 勝利",
                border_style="bold green"
            ))
            time.sleep(2)

            # レベルアップ判定（追加）
            level_ups = player.gain_exp(exp_gained)
            
            for level_up_data in level_ups:
                show_level_up(level_up_data)

            return result

        elif result == "defeat":
            console.clear()
            console.print(Panel(
                f"[bold red]💀 {player.name} は力尽きた... 💀[/bold red]",
                title="☠️ 敗北",
                border_style="bold red"
            ))
            return result

        elif result == "escaped":
            console.clear()
            console.print(Panel(
                "[yellow]無事に逃げ切った![/yellow]",
                title="🏃 脱出成功",
                border_style="yellow"
            ))
            return result

        turn += 1

def create_enemy(player_level):
    """プレイヤーのレベルに応じた敵を生成"""
    import random
    from character import Character  # インポートパスは適宜調整
    
    # レベルに応じて敵の種類を変更
    enemy_types = [
        {"name": "スライム", "hp_base": 30, "attack_base": 10, "defense_base": 3, "exp": 20},
        {"name": "ゴブリン", "hp_base": 50, "attack_base": 15, "defense_base": 5, "exp": 40},
        {"name": "オーク", "hp_base": 80, "attack_base": 20, "defense_base": 8, "exp": 70},
        {"name": "トロール", "hp_base": 120, "attack_base": 25, "defense_base": 12, "exp": 100},
    ]
    
    # プレイヤーレベルに応じて出現する敵を決定
    if player_level <= 2:
        enemy_data = enemy_types[0]  # スライム
    elif player_level <= 4:
        enemy_data = random.choice(enemy_types[0:2])  # スライム or ゴブリン
    elif player_level <= 7:
        enemy_data = random.choice(enemy_types[1:3])  # ゴブリン or オーク
    else:
        enemy_data = random.choice(enemy_types[2:4])  # オーク or トロール
    
    # レベルに応じてステータスを調整
    level_modifier = 1 + (player_level - 1) * 0.1
    
    enemy = Character(
        name=enemy_data["name"],
        hp=int(enemy_data["hp_base"] * level_modifier),
        max_hp=int(enemy_data["hp_base"] * level_modifier),
        mp=0,
        max_mp=0,
        attack=int(enemy_data["attack_base"] * level_modifier),
        defense=int(enemy_data["defense_base"] * level_modifier),
        level=max(1, player_level - 1 + random.randint(-1, 1))
    )
    
    enemy.exp_reward = int(enemy_data["exp"] * level_modifier)
    
    return enemy