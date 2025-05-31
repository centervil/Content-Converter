"""
Converter module
--------------

コンテンツ変換の中核機能を提供するモジュール
"""

from typing import Any, Dict, Optional

from .core.parser import MarkdownParser
from .llm.base import LLMProvider
from .platforms.base import PlatformProvider


class ContentConverter:
    """コンテンツ変換を行うメインクラス"""

    def __init__(
        self,
        platform_provider: PlatformProvider,
        llm_provider: Optional[LLMProvider] = None,
        config: Optional[Dict[str, Any]] = None,
    ):
        """
        初期化メソッド

        Args:
            platform_provider: プラットフォームプロバイダー
            llm_provider: LLMプロバイダー（省略可能）
            config: コンバーター設定
        """
        self.platform_provider = platform_provider
        self.llm_provider = llm_provider
        self.config = config or {}
        self.parser = MarkdownParser()

    def convert_file(self, file_path: str) -> Dict[str, Any]:
        """
        マークダウンファイルを指定されたプラットフォーム用に変換する

        Args:
            file_path: 変換するマークダウンファイルのパス

        Returns:
            Dict[str, Any]: 変換後のコンテンツ

        Raises:
            FileNotFoundError: ファイルが存在しない場合
            ValueError: 変換処理に失敗した場合
        """
        import os
        # ファイルの解析
        parsed_content = self.parser.parse_file(file_path)

        # プロンプトファイルの決定
        prompt_file = self.config.get("prompt_file")
        if prompt_file is None or not os.path.isfile(prompt_file):
            prompt_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), "prompts", "default_prompt.txt")
        
        # 入力ファイル内容
        input_text = parsed_content["content"]
        template_text = ""
        # テンプレートファイル指定が将来的にあればここで取得
        # 現状は空文字列で展開
        with open(prompt_file, "r", encoding="utf-8") as f:
            prompt_template = f.read()
        prompt_text = prompt_template.replace("{{input}}", input_text).replace("{{template}}", template_text)

        # LLMによる最適化（設定されている場合）
        if self.llm_provider and self.config.get("use_llm", True):
            optimized_content = self.llm_provider.optimize_content(
                prompt_text, options=self.config.get("llm_options")
            )
            parsed_content["content"] = optimized_content

            # メタデータの拡張（LLMから取得した要約など）
            if self.config.get("generate_summary", False):
                max_len = self.config.get("summary_length", 100)
                summary = self.llm_provider.generate_summary(
                    input_text, max_length=max_len
                )
                parsed_content["metadata"]["summary"] = summary

        # プラットフォーム固有の変換処理
        converted_content = self.platform_provider.convert(parsed_content)

        # 変換結果の検証
        if not self.platform_provider.validate(converted_content):
            msg = "コンテンツがプラットフォームの要件を満たしていません"
            raise ValueError(msg)

        return converted_content

    def save_converted_file(
        self, converted_content: Dict[str, Any], output_path: str
    ) -> None:
        """
        変換後のコンテンツをファイルに保存する

        Args:
            converted_content: 変換後のコンテンツ
            output_path: 出力先ファイルパス

        Raises:
            IOError: ファイル保存に失敗した場合
        """
        from pathlib import Path

        import frontmatter

        # フロントマターと本文を結合
        post = frontmatter.Post(
            converted_content["content"], **converted_content["metadata"]
        )

        # ファイルに保存
        try:
            output_file = Path(output_path)
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(frontmatter.dumps(post))
        except Exception as e:
            raise IOError(f"ファイル保存に失敗しました: {e}")
