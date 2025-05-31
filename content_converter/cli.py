"""
CLI module
---------

コマンドラインインターフェースを提供するモジュール
"""

import argparse
import sys
from pathlib import Path

from .factory import ConverterFactory


def parse_args() -> argparse.Namespace:
    """
    コマンドライン引数をパースする

    Returns:
        argparse.Namespace: パースされた引数
    """
    parser = argparse.ArgumentParser(
        description="Content-Converter: マークダウンファイルを各種プラットフォーム用に変換するツール"
    )

    parser.add_argument(
        "--input",
        required=True,
        help="変換するマークダウンファイルのパス（必須）"
    )

    parser.add_argument(
        "-p",
        "--platform",
        choices=["zenn", "note"],
        default="zenn",
        help="出力先プラットフォーム (デフォルト: zenn)",
    )

    parser.add_argument(
        "-o",
        "--output",
        help="出力先ファイルパス（省略時は入力ファイル名_<プラットフォーム>.md）",
    )

    parser.add_argument(
        "--use-llm", action="store_true", help="LLMによるコンテンツ最適化を有効にする"
    )

    parser.add_argument(
        "--llm-provider",
        choices=["gemini", "openrouter"],
        default="gemini",
        help="使用するLLMプロバイダー（デフォルト: gemini）",
    )

    parser.add_argument(
        "--model",
        type=str,
        help="LLMのモデル名（例: gemini-2.0-flash-001）。指定がなければデフォルト値を使用"
    )

    parser.add_argument(
        "--prompt-file",
        type=str,
        help="プロンプトファイルのパス。指定がなければデフォルトプロンプトを使用"
    )

    parser.add_argument(
        "--generate-summary", action="store_true", help="LLMを使用して要約を生成する"
    )

    parser.add_argument(
        "--summary-length",
        type=int,
        default=100,
        help="要約の最大文字数（デフォルト: 100）",
    )

    return parser.parse_args()


def main() -> None:
    """コマンドラインからのエントリーポイント"""
    args = parse_args()

    # 入力ファイルの確認
    input_path = Path(args.input)
    if not input_path.exists():
        print(
            f"エラー: 入力ファイル '{args.input}' が見つかりません。",
            file=sys.stderr,
        )
        sys.exit(1)

    # 出力ファイルのパスを決定
    if args.output:
        output_path = args.output
    else:
        # デフォルトの出力パス（入力ファイル名_<プラットフォーム>.md）
        stem = input_path.stem
        suffix = input_path.suffix
        output_path = f"{stem}_{args.platform}{suffix}"

    try:
        # LLMプロバイダーの設定
        llm_provider = None
        if args.use_llm:
            # LLMプロバイダーのインスタンス化（将来実装）
            print("注意: LLM機能は現在実装中です。")

        # 設定の構築
        config = {
            "use_llm": args.use_llm,
            "llm_provider": args.llm_provider,
            "generate_summary": args.generate_summary,
            "summary_length": args.summary_length,
            "model": args.model,
            "prompt_file": args.prompt_file,
        }

        # コンバーターの作成
        platform = args.platform
        converter = ConverterFactory.create_converter(
            platform_type=platform, llm_provider=llm_provider, config=config
        )

        # 変換処理の実行
        input_file = args.input
        print(f"ファイル '{input_file}' を {args.platform} 形式に変換中...")
        converted_content = converter.convert_file(args.input)

        # 変換結果の保存
        converter.save_converted_file(converted_content, output_path)
        print(f"変換完了: '{output_path}' に保存されました。")

    except Exception as e:
        print(f"エラー: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
