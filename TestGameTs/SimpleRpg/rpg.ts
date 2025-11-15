import { Story } from 'inkjs';
import * as readline from 'readline';
import * as fs from 'fs';
import * as path from 'path';

// ANSIカラーコード
const colors = {
  reset: '\x1b[0m',
  bright: '\x1b[1m',
  dim: '\x1b[2m',

  // 前景色
  black: '\x1b[30m',
  red: '\x1b[31m',
  green: '\x1b[32m',
  yellow: '\x1b[33m',
  blue: '\x1b[34m',
  magenta: '\x1b[35m',
  cyan: '\x1b[36m',
  white: '\x1b[37m',

  // 背景色
  bgBlack: '\x1b[40m',
  bgRed: '\x1b[41m',
  bgGreen: '\x1b[42m',
  bgYellow: '\x1b[43m',
  bgBlue: '\x1b[44m',
  bgMagenta: '\x1b[45m',
  bgCyan: '\x1b[46m',
  bgWhite: '\x1b[47m'
};

class InkRPGRich {
  private story: Story;
  private rl: readline.Interface;

  constructor() {
    // JSONファイルを読み込み（BOMを削除）
    let storyJson = fs.readFileSync(
      path.join(__dirname, 'story.json'),
      'utf8'
    );

    // BOM（Byte Order Mark）を削除
    if (storyJson.charCodeAt(0) === 0xFEFF) {
      storyJson = storyJson.slice(1);
    }

    this.story = new Story(storyJson);

    this.rl = readline.createInterface({
      input: process.stdin,
      output: process.stdout
    });

    this.showBanner();
    this.continueStory();
  }

  private showBanner(): void {
    console.clear();
    console.log(colors.cyan + colors.bright);
    console.log('╔═══════════════════════════════════════════════════╗');
    console.log('║                                                   ║');
    console.log('║            🏰  テキストRPG - Ink版  ⚔️            ║');
    console.log('║                                                   ║');
    console.log('╚═══════════════════════════════════════════════════╝');
    console.log(colors.reset);
    console.log('');
  }

  private showDivider(): void {
    console.log(colors.dim + '─'.repeat(55) + colors.reset);
  }

  private continueStory(): void {
    // ストーリーテキストを表示
    while (this.story.canContinue) {
      const text = this.story.Continue();
      if (text) {
        // テキストに色を付ける
        const coloredText = this.colorizeText(text.trim());
        console.log(coloredText);
      }
    }

    // 選択肢を表示
    if (this.story.currentChoices.length > 0) {
      this.showChoices();
    } else {
      // ストーリー終了
      this.showEnding();
    }
  }

  private colorizeText(text: string): string {
    // キーワードに応じて色を付ける
    if (text.includes('HP:') || text.includes('ゴールド:')) {
      return colors.yellow + '📊 ' + text + colors.reset;
    }
    if (text.includes('ドラゴン')) {
      return colors.red + colors.bright + '🐉 ' + text + colors.reset;
    }
    if (text.includes('GAME OVER')) {
      return colors.red + colors.bright + '💀 ' + text + colors.reset;
    }
    if (text.includes('おめでとう')) {
      return colors.green + colors.bright + '🎉 ' + text + colors.reset;
    }
    if (text.includes('城') || text.includes('街') || text.includes('宿屋') || text.includes('武器屋')) {
      return colors.cyan + '📍 ' + text + colors.reset;
    }
    if (text.includes('戦い')) {
      return colors.red + '⚔️  ' + text + colors.reset;
    }
    if (text.includes('鍵') || text.includes('剣') || text.includes('宝')) {
      return colors.magenta + '✨ ' + text + colors.reset;
    }

    return '   ' + text;
  }

  private showChoices(): void {
    console.log('');
    this.showDivider();
    console.log(colors.bright + colors.green + '\n📋 選択してください:' + colors.reset);
    console.log('');

    this.story.currentChoices.forEach((choice, index) => {
      const icon = this.getChoiceIcon(choice.text);
      console.log(
        colors.cyan + `  ${index + 1}.` + colors.reset +
        ` ${icon} ${choice.text}`
      );
    });

    console.log('');
    this.rl.question(
      colors.bright + '番号を入力 ➤ ' + colors.reset,
      (answer: string) => {
        const choiceIndex = parseInt(answer) - 1;

        if (choiceIndex >= 0 && choiceIndex < this.story.currentChoices.length) {
          console.log('');
          this.showDivider();
          console.log('');
          this.story.ChooseChoiceIndex(choiceIndex);
          this.continueStory();
        } else {
          console.log(colors.red + '\n❌ 無効な選択です。もう一度入力してください。\n' + colors.reset);
          this.showChoices();
        }
      }
    );
  }

  private getChoiceIcon(text: string): string {
    if (text.includes('戦う')) return '⚔️';
    if (text.includes('逃げる')) return '🏃';
    if (text.includes('入る') || text.includes('向かう')) return '🚪';
    if (text.includes('戻る')) return '↩️';
    if (text.includes('休む') || text.includes('宿屋')) return '🛏️';
    if (text.includes('買う') || text.includes('武器屋')) return '🛒';
    if (text.includes('立ち去る')) return '👋';
    if (text.includes('左')) return '⬅️';
    if (text.includes('右')) return '➡️';
    if (text.includes('外')) return '🚪';
    return '➤';
  }

  private showEnding(): void {
    console.log('');
    this.showDivider();
    console.log(colors.bright + colors.yellow);
    console.log('\n╔═══════════════════════════════════════════════════╗');
    console.log('║                                                   ║');
    console.log('║                  ゲーム終了                        ║');
    console.log('║                                                   ║');
    console.log('╚═══════════════════════════════════════════════════╝\n');
    console.log(colors.reset);

    console.log(colors.cyan + 'プレイしていただき、ありがとうございました！' + colors.reset);
    console.log('');

    this.rl.close();
  }
}

// ゲーム開始
new InkRPGRich();