from rich.prompt import Prompt, IntPrompt, Confirm
from rich.console import Console

console = Console()

# 選択肢
action = Prompt.ask(
    "行動を選択してください",
    choices=["attack", "defend", "item", "run"],
    default="attack"
)

# 数値入力
item_index = IntPrompt.ask("使用するアイテムの番号を入力")

# Yes/No確認
if Confirm.ask("本当に実行しますか?"):
    console.print(f"{item_index}のアイテムを使って{action}を実行しました")
else:
    console.print("キャンセルされました")