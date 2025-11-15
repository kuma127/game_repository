"""戦闘ロジック関連の関数"""

import random
import time
from rich.console import Console
from rich.panel import Panel

console = Console()


def animate_attack(attacker_name, target_name, damage):
    """攻撃アニメーションを表示"""
    frames = [
        f"[yellow]{attacker_name}[/yellow] が構える...",
        f"[yellow]{attacker_name}[/yellow] の攻撃!",
        f"[red]⚔️ {damage}ダメージ![/red]",
    ]

    for frame in frames:
        console.print(frame)
        time.sleep(0.4)


def calculate_damage(attacker, defender, skill_multiplier=1.0):
    """ダメージ計算（クリティカルヒット判定含む）"""
    base_damage = attacker.attack * skill_multiplier
    defense_reduction = defender.defense * 0.5
    damage = int(max(1, base_damage - defense_reduction))

    # クリティカルヒット判定
    is_critical = random.random() < 0.15
    if is_critical:
        damage = int(damage * 1.5)

    return damage, is_critical


def show_damage_effect(damage, is_critical):
    """ダメージエフェクトを表示"""
    if is_critical:
        console.print(
            Panel(
                f"[bold red]💥 CRITICAL HIT! 💥[/bold red]\n[yellow]{damage} ダメージ![/yellow]",
                border_style="bold red"
            )
        )
    else:
        console.print(f"[red]⚔️ {damage} ダメージ![/red]")
    time.sleep(0.8)
