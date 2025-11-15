from rich.tree import Tree
from rich.console import Console

console = Console()

tree = Tree("🎒 インベントリ")
weapons = tree.add("⚔️ 武器")
weapons.add("鉄の剣")
weapons.add("木の盾")

items = tree.add("📦 アイテム")
items.add("回復薬 x3")
items.add("魔法の石 x1")

console.print(tree)