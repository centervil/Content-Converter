"""
note.com provider module
----------------------

note.comプラットフォーム向けのプロバイダークラスを提供するモジュール
"""

from typing import Dict, Any, List, Optional
from ..base import PlatformProvider


class NoteProvider(PlatformProvider):
    """note.comプラットフォーム向けのプロバイダークラス"""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        初期化メソッド

        Args:
            config: note.com固有の設定値
        """
        self.config = config or {}
        
    def convert(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """
        コンテンツをnote.com向けの形式に変換する

        Args:
            content: 変換元のコンテンツ（メタデータとコンテンツを含む辞書）

        Returns:
            Dict[str, Any]: 変換後のコンテンツ
        """
        metadata = content.get('metadata', {}).copy()
        content_text = content.get('content', '')
        
        # note.com特有のメタデータフィールドの処理
        if 'title' not in metadata:
            metadata['title'] = 'Untitled Note'
            
        if 'hashtags' not in metadata:
            metadata['hashtags'] = []
        elif not isinstance(metadata['hashtags'], list):
            metadata['hashtags'] = [metadata['hashtags']]
            
        # note.com用のフィールドに変換
        if 'topics' in metadata and 'hashtags' not in metadata:
            metadata['hashtags'] = metadata.pop('topics')
            
        # アイキャッチ画像の処理
        if 'eyecatch' not in metadata and 'image' in metadata:
            metadata['eyecatch'] = metadata.pop('image')
            
        # 公開状態の処理（デフォルトは下書き）
        if 'status' not in metadata:
            metadata['status'] = 'draft'  # draft or public
            
        return {
            'metadata': metadata,
            'content': content_text
        }
    
    def validate(self, content: Dict[str, Any]) -> bool:
        """
        コンテンツがnote.comの要件を満たしているかを検証する

        Args:
            content: 検証するコンテンツ（メタデータとコンテンツを含む辞書）

        Returns:
            bool: 検証結果（True: 有効、False: 無効）
        """
        metadata = content.get('metadata', {})
        
        # 必須フィールドの検証
        required_fields = ['title']
        for field in required_fields:
            if field not in metadata:
                return False
                
        # status は 'draft' または 'public' のみ許可
        if 'status' in metadata and metadata['status'] not in ['draft', 'public']:
            return False
            
        return True