"""
Factory module
------------

各種コンポーネントのファクトリークラスを提供するモジュール
"""

from typing import Dict, Any, Optional
from .platforms.base import PlatformProvider
from .platforms.zenn.provider import ZennProvider
from .platforms.note.provider import NoteProvider
from .llm.base import LLMProvider


class PlatformFactory:
    """プラットフォームプロバイダーのファクトリークラス"""

    @staticmethod
    def create(platform_type: str,
               config: Optional[Dict[str, Any]] = None) -> PlatformProvider:
        """
        プラットフォームタイプに基づいてプロバイダーインスタンスを作成する

        Args:
            platform_type: プラットフォームタイプ ('zenn', 'note', etc.)
            config: プラットフォーム固有の設定

        Returns:
            PlatformProvider: プラットフォームプロバイダーのインスタンス

        Raises:
            ValueError: サポートされていないプラットフォームタイプの場合
        """
        platform_type = platform_type.lower()

        if platform_type == 'zenn':
            return ZennProvider(config)
        elif platform_type == 'note':
            return NoteProvider(config)
        else:
            raise ValueError(f"Unsupported platform type: {platform_type}")


class ConverterFactory:
    """コンテンツコンバーターのファクトリークラス"""

    @staticmethod
    def create_converter(
            platform_type: str,
            llm_provider: Optional[LLMProvider] = None,
            config: Optional[Dict[str, Any]] = None):
        """
        プラットフォームタイプに基づいてコンテンツコンバーターを作成する

        Args:
            platform_type: プラットフォームタイプ
            llm_provider: LLMプロバイダー（省略可能）
            config: コンバーター設定

        Returns:
            ContentConverter: コンテンツコンバーターのインスタンス
        """
        from .converter import ContentConverter

        platform_provider = PlatformFactory.create(platform_type, config)

        return ContentConverter(
            platform_provider=platform_provider,
            llm_provider=llm_provider,
            config=config
        )
