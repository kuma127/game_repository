// テキストRPG - Ink版
// 変数定義
VAR playerHealth = 100
VAR playerGold = 50
VAR hasKey = false
VAR hasSword = false
VAR dragonDefeated = false

-> start

=== start ===
あなたは冒険者です。古い城の前に立っています。
~ showStatus()

+ [城に入る] -> castle_entrance
+ [街に戻る] -> town

=== town ===
街の広場に戻りました。
~ showStatus()

+ [宿屋で休む(20ゴールド)] -> inn
+ [武器屋に行く] -> weapon_shop
+ [城に向かう] -> castle_entrance

=== inn ===
{ playerGold >= 20:
    ~ playerGold = playerGold - 20
    ~ playerHealth = 100
    宿屋で一晩休みました。体力が全回復しました!
    ~ showStatus()
    -> town
- else:
    お金が足りません...
    ~ showStatus()
    -> town
}

=== weapon_shop ===
武器屋の店主が話しかけてきます。
「いらっしゃい!良い剣があるよ」

+ [剣を買う(30ゴールド)] -> buy_sword
+ [立ち去る] -> town

=== buy_sword ===
{ playerGold >= 30:
    ~ playerGold = playerGold - 30
    ~ hasSword = true
    剣を手に入れました!これで戦いが有利になるでしょう。
    -> town
- else:
    お金が足りません...
    -> town
}

=== castle_entrance ===
城の入口です。重い扉が閉まっています。
~ showStatus()

+ [扉を開けて中に入る] -> castle_hall
+ [戻る] -> town

=== castle_hall ===
大広間に入りました。薄暗い廊下が奥へ続いています。

+ [左の部屋へ] -> treasure_room
+ [右の部屋へ] -> dragon_room
+ [外に出る] -> castle_entrance

=== treasure_room ===
宝物庫を見つけました!
{ hasKey == false:
    古い鍵を見つけました。
    ~ hasKey = true
    -> castle_hall
- else:
    空の宝箱があるだけです。
    -> castle_hall
}

=== dragon_room ===
{ dragonDefeated == false:
    巨大なドラゴンが現れた!
    + [戦う] -> fight_dragon
    + [逃げる] -> castle_hall
- else:
    ドラゴンを倒した部屋です。静かです。
    -> castle_hall
}

=== fight_dragon ===
ドラゴンとの戦い!
{ hasSword:
    ~ playerHealth = playerHealth - 20
    剣のおかげでダメージを軽減できた!
- else:
    ~ playerHealth = playerHealth - 30
}

{ playerHealth > 0:
    激しい戦いの末、ドラゴンを倒しました!
    ~ dragonDefeated = true
    ~ playerGold = playerGold + 100
    100ゴールドを手に入れた!
    ~ showStatus()
    -> victory
- else:
    あなたは倒れてしまいました...
    -> game_over
}

=== victory ===
おめでとうございます!ドラゴンを倒し、平和を取り戻しました!
最終HP: {playerHealth}
最終ゴールド: {playerGold}
-> END

=== game_over ===
GAME OVER
あなたの冒険はここで終わりました...
最終HP: {playerHealth}
最終ゴールド: {playerGold}
-> END

=== function showStatus ===
HP: {playerHealth}
ゴールド: {playerGold}
~ return
