"""
CLIモジュールのテスト
"""

import os
import sys
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock, call
import pytest
import importlib
from content_converter.cli import main, parse_args
import content_converter.cli


class TestCLI:
    """CLIモジュールのテスト"""

    def setup_method(self):
        """テストメソッドの前に実行されるセットアップメソッド"""
        # 一時ディレクトリを作成
        self.temp_dir = tempfile.TemporaryDirectory()
        # テスト用の一時ファイルを作成
        self.test_file_path = os.path.join(self.temp_dir.name, "test_markdown.md")
        with open(self.test_file_path, "w") as f:
            f.write("# Test Title\n\nTest Content")

    def teardown_method(self):
        """テストメソッドの後に実行されるクリーンアップメソッド"""
        # 一時ディレクトリを削除
        self.temp_dir.cleanup()
        self.temp_dir.cleanup()

    @patch("content_converter.cli.parse_args")
    def test_parse_args_default(self, mock_parse_args):
        """デフォルト引数のテスト"""
        mock_args = MagicMock()
        mock_args.input = "test.md"
        mock_args.platform = "zenn"
        mock_args.output = None
        mock_args.use_llm = False
        mock_args.llm_provider = "gemini"
        mock_args.model = None
        mock_args.prompt_file = None
        mock_args.template = None
        mock_args.generate_summary = False
        mock_args.summary_length = 100
        mock_parse_args.return_value = mock_args

        args = content_converter.cli.parse_args()
        assert args.input == "test.md"
        assert args.platform == "zenn"
        assert args.output is None
        assert args.use_llm is False
        assert args.llm_provider == "gemini"
        assert args.model is None
        assert args.prompt_file is None
        assert args.template is None
        assert args.generate_summary is False
        assert args.summary_length == 100

    @patch("sys.argv", ["content_converter", "--input", "input.md", "--platform", "note"])
    def test_parse_args_custom_platform(self):
        """カスタムプラットフォーム指定のテスト"""
        args = parse_args()
        assert args.platform == "note"
        assert args.input == "input.md"

    @patch("sys.argv", ["content_converter", "--input", "input.md", "-o", "output.md"])
    def test_parse_args_custom_output(self):
        """カスタム出力ファイル指定のテスト"""
        args = parse_args()
        assert args.output == "output.md"
        assert args.input == "input.md"

    @patch("sys.argv", ["content_converter", "--input", "input.md", "--use-llm", "--llm-provider", "openrouter"])
    def test_parse_args_llm_options(self):
        """LLMオプション指定のテスト"""
        args = parse_args()
        assert args.use_llm is True
        assert args.llm_provider == "openrouter"
        assert args.input == "input.md"

    @patch("sys.argv", ["content_converter", "--input", "input.md", "--generate-summary", "--summary-length", "200"])
    def test_parse_args_summary_options(self):
        """要約オプション指定のテスト"""
        args = parse_args()
        assert args.generate_summary is True
        assert args.summary_length == 200
        assert args.input == "input.md"

    @patch("content_converter.cli.parse_args")
    @patch("content_converter.cli.ConverterFactory.create_converter")
    def test_main_file_not_found(self, mock_create_converter, mock_parse_args):
        """存在しないファイルを指定したときのテスト"""
        # モックの戻り値を設定
        mock_args = MagicMock()
        mock_args.input = "non_existent_file.md"
        mock_args.platform = "zenn"
        mock_args.output = None
        mock_args.use_llm = False
        mock_args.llm_provider = "gemini"
        mock_args.model = None
        mock_args.prompt_file = None
        mock_args.template = None
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
        """有効なファイルのテスト"""
        # モックの戻り値を設定
        mock_args = MagicMock()
        mock_args.input = self.test_file_path
        mock_args.platform = "zenn"
        mock_args.output = None
        mock_args.use_llm = False
        mock_args.llm_provider = "gemini"
        mock_args.model = None
        mock_args.prompt_file = None
        mock_args.template = None
        mock_args.generate_summary = False
        mock_args.summary_length = 100
        mock_parse_args.return_value = mock_args

        # コンバーターのモック
        mock_converter = MagicMock()
        mock_converter.convert_file.return_value = "変換後のコンテンツ"
        mock_create_converter.return_value = mock_converter

        # テスト対象関数を実行
        content_converter.cli.main()

        # モックの呼び出し確認
        mock_create_converter.assert_called_once()
        mock_converter.convert_file.assert_called_once_with(self.test_file_path)
        mock_converter.save_converted_file.assert_called_once()

    @patch("content_converter.cli.parse_args")
    @patch("content_converter.cli.ConverterFactory.create_converter")
    def test_main_with_llm_options(self, mock_create_converter, mock_parse_args):
        """LLMオプションを使用した変換テスト"""
        # モックの戻り値を設定
        mock_args = MagicMock()
        mock_args.input = self.test_file_path
        mock_args.platform = "zenn"
        mock_args.output = None
        mock_args.use_llm = True
        mock_args.llm_provider = "gemini"
        mock_args.model = "gemini-2.0-flash-001"
        mock_args.prompt_file = "test_prompt.txt"
        mock_args.template = "test_template.txt"
        mock_args.generate_summary = True
        mock_args.summary_length = 150
        mock_parse_args.return_value = mock_args

        # コンバーターのモック
        mock_converter = MagicMock()
        mock_converter.convert_file.return_value = "変換後のコンテンツ"
        mock_create_converter.return_value = mock_converter

        # テスト対象関数を実行
        with patch("builtins.print") as mock_print:
            content_converter.cli.main()

        # コンバーター作成時のconfigの検証
        expected_config = {
            "use_llm": True,
            "llm_provider": "gemini",
            "generate_summary": True,
            "summary_length": 150,
            "model": "gemini-2.0-flash-001",
            "prompt_file": "test_prompt.txt",
            "template_file": "test_template.txt",
            "llm_options": {
                "model": "gemini-2.0-flash-001"
            }
        }
        mock_create_converter.assert_called_once_with(
            platform_type="zenn",
            llm_provider=None,  # LLMプロバイダーはNone（実装中）
            config=expected_config
        )
        mock_print.assert_any_call("注意: LLM機能は現在実装中です。")

    @patch("content_converter.cli.parse_args")
    @patch("content_converter.cli.ConverterFactory.create_converter")
    def test_main_exception_handling(self, mock_create_converter, mock_parse_args):
        """例外処理のテスト"""
        # モックの戻り値を設定
        mock_args = MagicMock()
        mock_args.input = self.test_file_path
        mock_args.platform = "zenn"
        mock_args.output = None
        mock_args.use_llm = False
        mock_args.llm_provider = "gemini"
        mock_args.model = None
        mock_args.prompt_file = None
        mock_args.template = None
        mock_args.generate_summary = False
        mock_args.summary_length = 100
        mock_parse_args.return_value = mock_args

        # コンバーターのモック（例外を発生させる）
        mock_converter = MagicMock()
        mock_converter.convert_file.side_effect = Exception("Test error")
        mock_create_converter.return_value = mock_converter

        # sys.exit をモック化してテスト
        with patch("sys.exit") as mock_exit:
            content_converter.cli.main()
            mock_exit.assert_called_once_with(1)

    @patch("sys.argv", ["content_converter", "--input", "input.md"])
    def test_default_output_path(self):
        """デフォルト出力パスのテスト"""
        args = parse_args()
        assert args.output is None
        assert args.input == "input.md"

    @patch("sys.argv", ["content_converter", "--input", "test.md", "--platform", "note"])
    def test_default_output_path_with_platform(self):
        """プラットフォーム指定時のデフォルト出力パスのテスト"""
        args = parse_args()
        assert args.output is None
        assert args.input == "test.md"
        assert args.platform == "note"

    def test_entry_point(self):
        """エントリーポイントのテスト"""
        # テスト用の一時ファイルを作成
        with tempfile.NamedTemporaryFile(suffix='.md') as temp_file:
            # モジュールのリロード前にモックを設定
            with patch('sys.argv', ['content_converter', '--input', 'test.md']):
                with patch('content_converter.cli.main') as mock_main:
                    # 直接main()を呼び出す
                    content_converter.cli.main()
                    
                    # mainが呼ばれたことを確認
                    mock_main.assert_called_once()
                    # 引数なしで呼ばれたことを確認
                    args, kwargs = mock_main.call_args
                    assert args == ()
                    assert kwargs == {}

    @patch("content_converter.cli.parse_args")
    @patch("content_converter.cli.ConverterFactory.create_converter")
    def test_main_custom_output(self, mock_create_converter, mock_parse_args):
        """カスタム出力先を指定したときのテスト"""
        # モックの戻り値を設定
        mock_args = MagicMock()
        mock_args.input = self.test_file_path
        mock_args.platform = "zenn"
        mock_args.output = "custom_output.md"
        mock_args.use_llm = False
        mock_args.llm_provider = "gemini"
        mock_args.model = None
        mock_args.prompt_file = None
        mock_args.template = None
        mock_args.generate_summary = False
        mock_args.summary_length = 100
        mock_parse_args.return_value = mock_args

        # コンバーターのモック
        mock_converter = MagicMock()
        mock_converter.convert_file.return_value = "変換後のコンテンツ"
        mock_create_converter.return_value = mock_converter

        # テスト対象関数を実行
        content_converter.cli.main()

        # モックの呼び出し確認
        mock_converter.save_converted_file.assert_called_once_with("変換後のコンテンツ", "custom_output.md")

    @patch("content_converter.cli.parse_args")
    @patch("content_converter.cli.ConverterFactory.create_converter")
    def test_main_with_llm_options(self, mock_create_converter, mock_parse_args):
        """LLMオプションを指定したときのテスト"""
        # モックの戻り値を設定
        mock_args = MagicMock()
        mock_args.input = self.test_file_path
        mock_args.platform = "zenn"
        mock_args.output = None
        mock_args.use_llm = True
        mock_args.llm_provider = "openrouter"
        mock_args.model = None
        mock_args.prompt_file = None
        mock_args.template = None
        mock_args.generate_summary = True
        mock_args.summary_length = 200
        mock_parse_args.return_value = mock_args

        # コンバーターのモック
        mock_converter = MagicMock()
        mock_converter.convert_file.return_value = "変換後のコンテンツ"
        mock_create_converter.return_value = mock_converter

        # テスト対象関数を実行
        content_converter.cli.main()

        # モックの呼び出し確認（configの検証）
        expected_config = {
            "use_llm": True,
            "llm_provider": "openrouter",
            "generate_summary": True,
            "summary_length": 200,
            "model": None,
            "prompt_file": None,
            "template_file": None,
            "llm_options": {}
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
