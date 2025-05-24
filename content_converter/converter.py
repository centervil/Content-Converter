"""
Converter module
--------------

コンテンツ変換の中核機能を提供するモジュール
"""

from typing import Dict, Any, Optional
from .core.parser import MarkdownParser
from .platforms.base import PlatformProvider
from .llm.base import LLMProvider


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
        # ファイルの解析
        parsed_content = self.parser.parse_file(file_path)

        # LLMによる最適化（設定されている場合）
        if self.llm_provider and self.config.get("use_llm", True):
            content_text = parsed_content["content"]
            optimized_content = self.llm_provider.optimize_content(
                content_text, options=self.config.get("llm_options")
            )
            parsed_content["content"] = optimized_content

            # メタデータの拡張（LLMから取得した要約など）
            if self.config.get("generate_summary", False):
                max_len = self.config.get("summary_length", 100)
                summary = self.llm_provider.generate_summary(
                    content_text, max_length=max_len
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
        import frontmatter
        from pathlib import Path

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
