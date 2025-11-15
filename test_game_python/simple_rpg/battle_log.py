"""戦闘ログ管理クラス"""

from collections import deque
from rich.panel import Panel


class BattleLog:
    """戦闘中のログメッセージを管理するクラス"""

    def __init__(self, max_lines=10):
        self.logs = deque(maxlen=max_lines)

    def add(self, message, style="white"):
        """ログメッセージを追加"""
        self.logs.append((message, style))

    def render(self):
        """ログをパネルとしてレンダリング"""
        lines = []
        for msg, style in self.logs:
            lines.append(f"[{style}]• {msg}[/{style}]")
        return Panel(
            "\n".join(lines) if lines else "[dim]戦闘ログ[/dim]",
            title="📜 ログ",
            border_style="yellow",
            height=12
        )
