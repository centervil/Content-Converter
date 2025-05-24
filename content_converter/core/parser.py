"""
Parser module
------------

マークダウンファイルの読み込みと解析を行うモジュール
"""

import frontmatter
from pathlib import Path
from typing import Dict, Any


class MarkdownParser:
    """マークダウンファイルの解析を行うクラス"""

    def __init__(self):
        """初期化メソッド"""
        pass

    def parse_file(self, file_path: str) -> Dict[str, Any]:
        """
        マークダウンファイルを解析し、フロントマターとコンテンツを分離して返す

        Args:
            file_path: 解析するマークダウンファイルのパス

        Returns:
            Dict[str, Any]: フロントマターとコンテンツを含む辞書
                {
                    'metadata': Dict[str, Any],  # フロントマター（メタデータ）
                    'content': str  # 本文コンテンツ
                }

        Raises:
            FileNotFoundError: ファイルが存在しない場合
            ValueError: ファイルの解析に失敗した場合
        """
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        try:
            with open(path, "r", encoding="utf-8") as f:
                post = frontmatter.load(f)

            return {"metadata": post.metadata, "content": post.content}
        except Exception as e:
            raise ValueError(f"Failed to parse markdown file: {e}")
