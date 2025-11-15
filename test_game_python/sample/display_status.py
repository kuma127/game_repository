from rich.table import Table
from rich.console import Console

console = Console()

table = Table(title="キャラクターステータス")
table.add_column("項目", style="cyan")
table.add_column("値", style="magenta")

table.add_row("名前", "勇者")
table.add_row("レベル", "5")
table.add_row("HP", "85/100")
table.add_row("MP", "30/50")
table.add_row("攻撃力", "25")

console.print(table)