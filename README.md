# Content-Converter

テキストファイルを様々な公開プラットフォーム用に最適化して変換するツールです。

## 概要

Content-Converterは、LLM（大規模言語モデル）を活用して、テンプレートに基づいたテキスト変換を実現します。CI/CDパイプラインから呼び出せる形式で提供され、自動化された変換処理を可能にします。

## 主な機能

- テキストファイルの変換処理
- テンプレートベースの出力形式定義
- LLMによるコンテンツ最適化
- 複数LLMプロバイダー対応（下記参照）
- カスタムプロンプト機能
- 任意のテキスト形式に対応

## サポートされているLLMプロバイダー

サポートされているLLMプロバイダーとその設定方法については、[LLMプロバイダー一覧](docs/supported_llm_providers.md)を参照してください。


## 使用方法

```bash
content-converter --input article.md --template zenn_template.md --output converted.md
```

詳細な使用方法や設定については、[仕様書](docs/specification.md)を参照してください。

## 出力形式

- 任意のテキスト形式に対応
- カスタムテンプレートで柔軟な出力が可能
- 入力と同形式の出力をサポート
- 環境変数またはコマンドライン引数でのAPIキー指定（[詳細](docs/specification.md#apiキーの指定方法)）
- その他のプラットフォーム（拡張予定）

## 依存関係

必須依存パッケージ:
- pyyaml>=6.0
- python-frontmatter>=1.0.0
- requests>=2.28.0
- python-dotenv>=1.0.0
- markdown>=3.4.0
- pydantic>=2.5.2

## ライセンス

MIT License