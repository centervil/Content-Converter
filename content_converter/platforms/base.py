"""
Platform Base module
------------------

プラットフォーム連携の基底クラスを提供するモジュール
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional


class PlatformProvider(ABC):
    """プラットフォーム連携の基底クラス"""

    @abstractmethod
    def convert(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """
        コンテンツをプラットフォーム固有の形式に変換する

        Args:
            content: 変換元のコンテンツ（メタデータとコンテンツを含む辞書）
                {
                    'metadata': Dict[str, Any],  # フロントマター（メタデータ）
                    'content': str  # 本文コンテンツ
                }

        Returns:
            Dict[str, Any]: 変換後のコンテンツ
        """
        pass
    
    @abstractmethod
    def validate(self, content: Dict[str, Any]) -> bool:
        """
        コンテンツがプラットフォームの要件を満たしているかを検証する

        Args:
            content: 検証するコンテンツ（メタデータとコンテンツを含む辞書）

        Returns:
            bool: 検証結果（True: 有効、False: 無効）
        """
        pass