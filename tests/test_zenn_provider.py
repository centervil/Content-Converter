"""
Zennプロバイダーのテスト
"""

from content_converter.platforms.zenn.provider import ZennProvider


class TestZennProvider:
    """ZennProviderクラスのテスト"""

    def setup_method(self):
        """テスト前のセットアップ"""
        self.provider = ZennProvider()

    def test_convert_with_minimal_content(self):
        """最小限のコンテンツでの変換テスト"""
        # 入力コンテンツ
        content = {"metadata": {}, "content": "テストコンテンツ"}

        # 変換
        result = self.provider.convert(content)

        # 結果の検証
        assert "metadata" in result
        assert "content" in result
        assert result["content"] == "テストコンテンツ"

        # デフォルト値の検証
        metadata = result["metadata"]
        assert metadata["title"] == "Untitled Article"
        assert metadata["emoji"] == "✨"
        assert metadata["type"] == "tech"
        assert metadata["topics"] == []
        assert metadata["published"] is True

    def test_convert_with_full_content(self):
        """完全なコンテンツでの変換テスト"""
        # 入力コンテンツ
        content = {
            "metadata": {
                "title": "テスト記事",
                "emoji": "🚀",
                "type": "idea",
                "topics": ["Python", "Markdown"],
                "published": False,
            },
            "content": "テストコンテンツ",
        }

        # 変換
        result = self.provider.convert(content)

        # 結果の検証
        assert "metadata" in result
        assert "content" in result
        assert result["content"] == "テストコンテンツ"

        # メタデータの検証
        metadata = result["metadata"]
        assert metadata["title"] == "テスト記事"
        assert metadata["emoji"] == "🚀"
        assert metadata["type"] == "idea"
        assert metadata["topics"] == ["Python", "Markdown"]
        assert metadata["published"] is False

    def test_convert_with_too_many_topics(self):
        """トピック数制限のテスト"""
        # 入力コンテンツ（トピックが5つ以上）
        content = {
            "metadata": {
                "title": "テスト記事",
                "emoji": "🚀",
                "type": "tech",
                "topics": [
                    "Python", "Markdown", "Zenn",
                    "Content", "Converter"
                ],
            },
            "content": "テストコンテンツ",
        }

        # 変換
        result = self.provider.convert(content)

        # 結果の検証（トピック数の制限を確認）
        metadata = result["metadata"]
        assert len(metadata["topics"]) == 4
        assert metadata["topics"] == ["Python", "Markdown", "Zenn", "Content"]

    def test_validate_valid_content(self):
        """有効なコンテンツの検証テスト"""
        # 有効なコンテンツ
        content = {
            "metadata": {
                "title": "テスト記事",
                "emoji": "🚀",
                "type": "tech",
                "topics": ["Python", "Markdown"],
            },
            "content": "テストコンテンツ",
        }

        # 検証
        is_valid = self.provider.validate(content)
        assert is_valid is True

    def test_validate_invalid_content(self):
        """無効なコンテンツの検証テスト"""
        # 必須フィールドが不足しているコンテンツ
        content = {
            "metadata": {
                "title": "テスト記事"
                # emojiが不足
                # typeが不足
                # topicsが不足
            },
            "content": "テストコンテンツ",
        }

        # 検証
        is_valid = self.provider.validate(content)
        assert is_valid is False

    def test_validate_invalid_type(self):
        """無効なタイプ値の検証テスト"""
        # タイプ値が無効なコンテンツ
        content = {
            "metadata": {
                "title": "テスト記事",
                "emoji": "🚀",
                "type": "invalid",  # techまたはideaではない
                "topics": ["Python", "Markdown"],
            },
            "content": "テストコンテンツ",
        }

        # 検証
        is_valid = self.provider.validate(content)
        assert is_valid is False
