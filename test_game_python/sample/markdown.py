from rich.markdown import Markdown
from rich.console import Console

console = Console()

story = """
# 第1章: 冒険の始まり

あなたは小さな村で目を覚ました。

## 目標
- 村の長老に会う
- 伝説の剣を見つける
"""

console.print(Markdown(story))