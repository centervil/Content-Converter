"""
Zenn provider module
------------------

Zennプラットフォーム向けのプロバイダークラスを提供するモジュール
"""

from typing import Dict, Any, List, Optional
from ..base import PlatformProvider


class ZennProvider(PlatformProvider):
    """Zennプラットフォーム向けのプロバイダークラス"""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        初期化メソッド

        Args:
            config: Zenn固有の設定値
        """
        self.config = config or {}
        
    def convert(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """
        コンテンツをZenn向けの形式に変換する

        Args:
            content: 変換元のコンテンツ（メタデータとコンテンツを含む辞書）

        Returns:
            Dict[str, Any]: 変換後のコンテンツ
        """
        metadata = content.get('metadata', {}).copy()
        content_text = content.get('content', '')
        
        # Zenn特有のメタデータフィールドの処理
        if 'title' not in metadata:
            metadata['title'] = 'Untitled Article'
            
        if 'emoji' not in metadata:
            metadata['emoji'] = '✨'
            
        if 'type' not in metadata:
            metadata['type'] = 'tech'  # tech または idea
            
        if 'topics' not in metadata:
            metadata['topics'] = []
        elif not isinstance(metadata['topics'], list):
            metadata['topics'] = [metadata['topics']]
            
        # 最大4つのトピックまで
        if len(metadata['topics']) > 4:
            metadata['topics'] = metadata['topics'][:4]
            
        # 必須ではないがZenn推奨のメタデータ
        if 'published' not in metadata:
            metadata['published'] = True
            
        return {
            'metadata': metadata,
            'content': content_text
        }
    
    def validate(self, content: Dict[str, Any]) -> bool:
        """
        コンテンツがZennの要件を満たしているかを検証する

        Args:
            content: 検証するコンテンツ（メタデータとコンテンツを含む辞書）

        Returns:
            bool: 検証結果（True: 有効、False: 無効）
        """
        metadata = content.get('metadata', {})
        
        # 必須フィールドの検証
        required_fields = ['title', 'emoji', 'type', 'topics']
        for field in required_fields:
            if field not in metadata:
                return False
                
        # type は 'tech' または 'idea' のみ許可
        if metadata['type'] not in ['tech', 'idea']:
            return False
            
        # topics は最大4つまで
        if len(metadata.get('topics', [])) > 4:
            return False
            
        return True