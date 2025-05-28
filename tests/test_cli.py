"""
CLIモジュールのテスト
"""

import os
import sys
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

from content_converter.cli import parse_args, main


class TestCLI:
    """CLIモジュールのテスト"""

    def setup_method(self):
        """テスト前のセットアップ"""
        # テスト用の一時ファイルを作成
        self.temp_dir = tempfile.TemporaryDirectory()
        self.test_file_path = os.path.join(self.temp_dir.name, "test_markdown.md")

        # テスト用のマークダウンコンテンツ
        test_content = """---
title: テスト記事
description: これはテスト用の記事です
tags:
  - テスト
  - マークダウン
---

# テスト記事

これはテスト用のマークダウンコンテンツです。
"""
        # ファイルに書き込み
        with open(self.test_file_path, "w", encoding="utf-8") as f:
            f.write(test_content)

    def teardown_method(self):
        """テスト後のクリーンアップ"""
        # 一時ディレクトリを削除
        self.temp_dir.cleanup()

    @patch("argparse.ArgumentParser.parse_args")
    def test_parse_args_default(self, mock_parse_args):
        """デフォルト引数での解析テスト"""
        # モックの戻り値を設定
        mock_args = MagicMock()
        mock_args.input_file = self.test_file_path
        mock_args.platform = "zenn"
        mock_args.output = None
        mock_args.use_llm = False
        mock_args.llm_provider = "gemini"
        mock_args.generate_summary = False
        mock_args.summary_length = 100
        mock_parse_args.return_value = mock_args

        # テスト対象関数を実行
        args = parse_args()

        # 結果の検証
        assert args.input_file == self.test_file_path
        assert args.platform == "zenn"
        assert args.output is None
        assert args.use_llm is False
        assert args.llm_provider == "gemini"
        assert args.generate_summary is False
        assert args.summary_length == 100

    @patch("sys.argv", ["content_converter", "input.md", "--platform", "note"])
    def test_parse_args_custom_platform(self):
        """カスタムプラットフォーム指定のテスト"""
        # テスト用の引数を設定しパース
        with patch.object(sys, "argv", ["content_converter", "input.md", "--platform", "note"]):
            args = parse_args()
            assert args.platform == "note"

    @patch("sys.argv", ["content_converter", "input.md", "-o", "output.md"])
    def test_parse_args_custom_output(self):
        """カスタム出力ファイル指定のテスト"""
        # テスト用の引数を設定しパース
        with patch.object(sys, "argv", ["content_converter", "input.md", "-o", "output.md"]):
            args = parse_args()
            assert args.output == "output.md"

    @patch("sys.argv", ["content_converter", "input.md", "--use-llm", "--llm-provider", "openrouter"])
    def test_parse_args_llm_options(self):
        """LLMオプション指定のテスト"""
        # テスト用の引数を設定しパース
        with patch.object(sys, "argv", ["content_converter", "input.md", "--use-llm", "--llm-provider", "openrouter"]):
            args = parse_args()
            assert args.use_llm is True
            assert args.llm_provider == "openrouter"

    @patch("sys.argv", ["content_converter", "input.md", "--generate-summary", "--summary-length", "200"])
    def test_parse_args_summary_options(self):
        """要約オプション指定のテスト"""
        # テスト用の引数を設定しパース
        with patch.object(sys, "argv", ["content_converter", "input.md", "--generate-summary", "--summary-length", "200"]):
            args = parse_args()
            assert args.generate_summary is True
            assert args.summary_length == 200

    @patch("content_converter.cli.parse_args")
    @patch("content_converter.cli.ConverterFactory.create_converter")
    def test_main_file_not_found(self, mock_create_converter, mock_parse_args):
        """存在しないファイルを指定したときのテスト"""
        # モックの戻り値を設定
        mock_args = MagicMock()
        mock_args.input_file = "non_existent_file.md"
        mock_args.platform = "zenn"
        mock_args.output = None
        mock_args.use_llm = False
        mock_args.llm_provider = "gemini"
        mock_args.generate_summary = False
        mock_args.summary_length = 100
        mock_parse_args.return_value = mock_args

        # sys.exit をモック化してテスト
        with pytest.raises(SystemExit) as e:
            main()
        assert e.value.code == 1

    @patch("content_converter.cli.parse_args")
    @patch("content_converter.cli.ConverterFactory.create_converter")
    def test_main_valid_file(self, mock_create_converter, mock_parse_args):
        """有効なファイルでの変換テスト"""
        # モックの戻り値を設定
        mock_args = MagicMock()
        mock_args.input_file = self.test_file_path
        mock_args.platform = "zenn"
        mock_args.output = None
        mock_args.use_llm = False
        mock_args.llm_provider = "gemini"
        mock_args.generate_summary = False
        mock_args.summary_length = 100
        mock_parse_args.return_value = mock_args

        # コンバーターのモック
        mock_converter = MagicMock()
        mock_converter.convert_file.return_value = "変換後のコンテンツ"
        mock_create_converter.return_value = mock_converter

        # テスト対象関数を実行
        main()

        # モックの呼び出し確認
        mock_create_converter.assert_called_once()
        mock_converter.convert_file.assert_called_once_with(self.test_file_path)
        mock_converter.save_converted_file.assert_called_once()

    @patch("content_converter.cli.parse_args")
    @patch("content_converter.cli.ConverterFactory.create_converter")
    def test_main_custom_output(self, mock_create_converter, mock_parse_args):
        """カスタム出力先を指定したときのテスト"""
        # モックの戻り値を設定
        mock_args = MagicMock()
        mock_args.input_file = self.test_file_path
        mock_args.platform = "zenn"
        mock_args.output = "custom_output.md"
        mock_args.use_llm = False
        mock_args.llm_provider = "gemini"
        mock_args.generate_summary = False
        mock_args.summary_length = 100
        mock_parse_args.return_value = mock_args

        # コンバーターのモック
        mock_converter = MagicMock()
        mock_converter.convert_file.return_value = "変換後のコンテンツ"
        mock_create_converter.return_value = mock_converter

        # テスト対象関数を実行
        main()

        # モックの呼び出し確認
        mock_converter.save_converted_file.assert_called_once_with("変換後のコンテンツ", "custom_output.md")

    @patch("content_converter.cli.parse_args")
    @patch("content_converter.cli.ConverterFactory.create_converter")
    def test_main_with_llm_options(self, mock_create_converter, mock_parse_args):
        """LLMオプションを指定したときのテスト"""
        # モックの戻り値を設定
        mock_args = MagicMock()
        mock_args.input_file = self.test_file_path
        mock_args.platform = "zenn"
        mock_args.output = None
        mock_args.use_llm = True
        mock_args.llm_provider = "openrouter"
        mock_args.generate_summary = True
        mock_args.summary_length = 200
        mock_parse_args.return_value = mock_args

        # コンバーターのモック
        mock_converter = MagicMock()
        mock_converter.convert_file.return_value = "変換後のコンテンツ"
        mock_create_converter.return_value = mock_converter

        # テスト対象関数を実行
        main()

        # モックの呼び出し確認（configの検証）
        expected_config = {
            "use_llm": True,
            "llm_provider": "openrouter",
            "generate_summary": True,
            "summary_length": 200,
        }
        mock_create_converter.assert_called_once_with(
            platform_type="zenn", llm_provider=None, config=expected_config
        )

    @patch("content_converter.cli.parse_args")
    @patch("content_converter.cli.ConverterFactory.create_converter")
    def test_main_converter_exception(self, mock_create_converter, mock_parse_args):
        """変換処理で例外が発生したときのテスト"""
        # モックの戻り値を設定
        mock_args = MagicMock()
        mock_args.input_file = self.test_file_path
        mock_args.platform = "zenn"
        mock_args.output = None
        mock_args.use_llm = False
        mock_args.llm_provider = "gemini"
        mock_args.generate_summary = False
        mock_args.summary_length = 100
        mock_parse_args.return_value = mock_args

        # コンバーターのモックで例外を発生させる
        mock_converter = MagicMock()
        mock_converter.convert_file.side_effect = Exception("変換エラー")
        mock_create_converter.return_value = mock_converter

        # sys.exit をモック化してテスト
        with pytest.raises(SystemExit) as e:
            main()
        assert e.value.code == 1


if __name__ == "__main__":
    pytest.main()
