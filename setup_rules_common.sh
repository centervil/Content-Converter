#!/bin/bash

# スクリプトの説明
# このスクリプトは新しいリポジトリに rules-common をサブモジュールとして追加し、
# cursor/windsurf/cline のadapterファイルへのシンボリックリンクを自動的に作成します

# エラーが発生したら停止
set -e

# 色付きの出力用関数
print_info() {
  echo -e "\033[1;34m[INFO]\033[0m $1"
}

print_success() {
  echo -e "\033[1;32m[SUCCESS]\033[0m $1"
}

print_error() {
  echo -e "\033[1;31m[ERROR]\033[0m $1"
}

# 実行ディレクトリをプロジェクトルートに設定
PROJECT_ROOT=$(pwd)
print_info "プロジェクトルート: $PROJECT_ROOT"

# Gitリポジトリかどうかチェック
if [ ! -d "$PROJECT_ROOT/.git" ]; then
  print_error "このディレクトリはGitリポジトリではありません。まずgit initを実行してください。"
  exit 1
fi

# rules-common サブモジュールの設定
RULES_REPO_URL="https://github.com/centervil/my-cursor-rules.git"
RULES_COMMON_PATH="$PROJECT_ROOT/rules-common"

# rules-common サブモジュールが存在するかチェック
if [ -d "$RULES_COMMON_PATH" ]; then
  print_info "rules-common サブモジュールは既に存在します。更新します..."
  git submodule update --init --recursive
else
  print_info "rules-common サブモジュールを追加します..."
  git submodule add "$RULES_REPO_URL" "rules-common"
  git submodule update --init --recursive
fi

# 必要なディレクトリを作成
print_info "必要なディレクトリを作成しています..."

# Cursor用ディレクトリ
mkdir -p "$PROJECT_ROOT/.cursor/rules"

# Windsurf用ディレクトリ
mkdir -p "$PROJECT_ROOT/.windsurf/rules"
mkdir -p "$PROJECT_ROOT/.windsurf/workflows"
# Cline用ディレクトリ
mkdir -p "$PROJECT_ROOT/.cline/rules"

# アダプターファイルのシンボリックリンクを作成
print_info "アダプターファイルのシンボリックリンクを作成します..."

# Cursor用アダプターのシンボリックリンク作成
print_info "Cursor用アダプターのシンボリックリンクを作成中..."
ln -sf "../../rules-common/adapters/cursor_adapter.mdc" "$PROJECT_ROOT/.cursor/rules/cursor_adapter.mdc"
print_success "  リンク作成: cursor_rules_adapter.mdc"

# Windsurf用アダプターのシンボリックリンク作成
print_info "Windsurf用アダプターのシンボリックリンクを作成中..."
ln -sf "../../rules-common/adapters/windsurf_adapter.md" "$PROJECT_ROOT/.windsurf/rules/windsurf_adapter.md"
print_success "  リンク作成: windsurf_adapter.md"

# Cline用アダプターのシンボリックリンク作成
print_info "Cline用アダプターのシンボリックリンクを作成中..."
ln -sf "../../rules-common/adapters/cline_adapter.yaml" "$PROJECT_ROOT/.cline/rules/cline_adapter.yaml"
print_success "  リンク作成: cline_rules_adapter.yaml"

# Workflows用のシンボリックリンク作成
print_info "Workflows用のシンボリックリンクを作成中..."
find "$PROJECT_ROOT/rules-common/workflows" -type f -exec basename {} \; | while read file; do
  ln -sf "../../rules-common/workflows/$file" "$PROJECT_ROOT/.windsurf/workflows/$file"
  print_success "  リンク作成: workflows/$file"
done

print_success "セットアップが完了しました！"
print_info "以下のコマンドを実行してコミットしてください:"
echo "git add .gitmodules rules-common .cursor .windsurf .cline"
echo "git commit -m \"Add rules-common as submodule with adapter symlinks\""
