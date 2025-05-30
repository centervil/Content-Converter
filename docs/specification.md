# Content-Converter 仕様書

## 概要

Content-Converterは、テキストファイルを様々な公開プラットフォーム用に最適化して変換するツールです。LLM（大規模言語モデル）を活用して、テンプレートに基づいたテキスト変換を実現します。CI/CDパイプラインから呼び出せる形式で提供され、自動化された変換処理を可能にします。

## ユースケース

### テキスト変換の自動化

**目的**: 入力テキストを指定されたテンプレートに基づいて変換

**フロー**:
1. 入力ファイルとテンプレートファイルを指定
2. `content-converter`を実行
3. 変換されたテキストを出力

### カスタムテンプレートを使用した変換

**目的**: 独自のテンプレートに基づいた柔軟なテキスト変換

**フロー**:
1. 変換ルールを定義したテンプレートを作成
2. 入力ファイルと共に指定して変換を実行
3. テンプレートに従って変換されたテキストを取得

## インターフェース

### コマンドライン引数

## APIキーの指定方法

### 環境変数を使用する場合

```bash
export GOOGLE_API_KEY='your-api-key'  # Google Geminiを使用する場合
export OPENROUTER_API_KEY='your-api-key'  # OpenRouterを使用する場合
```

### コマンドライン引数で指定する場合

```bash
# Google Geminiを使用する場合
--api-key gemini:your-api-key

# OpenRouterを使用する場合
--api-key openrouter:your-api-key
```

> **注意**: コマンドライン引数で指定されたAPIキーは、環境変数よりも優先されます。

### コマンドライン引数

| 引数 | 説明 | 必須 | デフォルト値 |
|------|------|:----:|------------|
| `--input` | 入力ファイルのパス | ✓ | - |
| `--template` | テンプレートファイルのパス | ✓ | - |
| `--prompt` | カスタムプロンプトファイルのパス | | デフォルトプロンプト |
| `--output` | 出力先ファイルパス | | 標準出力 |
| `--llm-provider` | 使用するLLMプロバイダー | | openai |
| `--model` | 使用するLLMモデル | | プロバイダーのデフォルト |

### 入力ファイル

変換元となるテキストファイル。任意の形式が使用可能です。

### テンプレートファイル

出力形式を定義するファイル。プレースホルダーを含む任意の形式が使用可能です。

例:
```markdown
---
title: "{{title}}"
emoji: "{{emoji}}"
type: "tech"
topics: {{topics}}
published: true
---

{{content}}
```

### プロンプトファイル

LLMへの指示を含むテキストファイル。デフォルトプロンプトを使用するか、カスタムプロンプトを指定できます。

例:
```text
以下の入力テキストを指定されたテンプレートの形式に変換してください。

# 入力テキスト
{{input}}

# 使用するテンプレート
{{template}}

# 出力要件
- テンプレート内のプレースホルダーを適切に置き換えてください
- フォーマットを維持してください
- 構造を保持してください
```

## 使用例

### 基本的な使用方法

```bash
content-converter --input article.md --template zenn_template.md --output converted.md
```

### カスタムプロンプトの使用

```bash
content-converter --input article.md --template zenn_template.md --prompt custom_prompt.txt --output converted.md
```

### 異なるLLMプロバイダーの指定

```bash
content-converter --input article.md --template zenn_template.md --llm-provider gemini --model gemini-pro --output converted.md
```

## 出力形式

このツールは、指定されたテンプレートに基づいて任意の形式のテキストを出力できます。

- テンプレートの形式に制限はありません
- 入力と同様、任意のテキスト形式に対応
- 出力は指定されたテンプレートの構造に従います
