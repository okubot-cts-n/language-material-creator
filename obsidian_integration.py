"""
Obsidian連携機能
個人コンテキストファイルの管理とStreamlitアプリとの連携
"""

import os
import json
import shutil
from datetime import datetime
from pathlib import Path
import streamlit as st
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import markdown
import re

class ObsidianIntegration:
    """Obsidian連携クラス"""
    
    def __init__(self, base_path="~/Documents/語学教材プロジェクト"):
        self.base_path = Path(base_path).expanduser()
        self.setup_folders()
    
    def setup_folders(self):
        """必要なフォルダ構造を作成"""
        folders = [
            "01_カウンセリング",
            "02_システムプロンプト", 
            "03_テンプレート",
            "04_トピックリスト",
            "05_生成教材",
            "06_設定"
        ]
        
        for folder in folders:
            folder_path = self.base_path / folder
            folder_path.mkdir(parents=True, exist_ok=True)
    
    def export_materials_to_obsidian(self, materials, client_name, topic_list=None):
        """教材をObsidian形式でエクスポート"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # クライアントフォルダ作成
        client_folder = self.base_path / "05_生成教材" / f"{client_name}_{timestamp}"
        client_folder.mkdir(parents=True, exist_ok=True)
        
        exported_files = []
        
        # 教材ファイルのエクスポート
        for i, material in enumerate(materials):
            # マークダウンファイル生成
            md_content = self.generate_material_markdown(material, i+1)
            md_filename = f"教材{i+1:02d}_{material.get('topic', 'Unknown')}.md"
            md_path = client_folder / md_filename
            
            with open(md_path, 'w', encoding='utf-8') as f:
                f.write(md_content)
            
            # JSONファイルも同時生成
            json_filename = f"教材{i+1:02d}_{material.get('topic', 'Unknown')}.json"
            json_path = client_folder / json_filename
            
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(material, f, ensure_ascii=False, indent=2)
            
            exported_files.append({
                'markdown': str(md_path),
                'json': str(json_path),
                'topic': material.get('topic', 'Unknown')
            })
        
        # サマリーファイル生成
        summary_content = self.generate_summary_markdown(materials, client_name, timestamp)
        summary_path = client_folder / "README.md"
        
        with open(summary_path, 'w', encoding='utf-8') as f:
            f.write(summary_content)
        
        # トピックリストも保存
        if topic_list:
            topics_content = self.generate_topics_markdown(topic_list, client_name)
            topics_path = client_folder / "トピックリスト.md"
            
            with open(topics_path, 'w', encoding='utf-8') as f:
                f.write(topics_content)
        
        return {
            'folder': str(client_folder),
            'files': exported_files,
            'summary': str(summary_path)
        }
    
    def generate_material_markdown(self, material, index):
        """教材のマークダウンファイルを生成"""
        topic = material.get('topic', 'Unknown')
        material_type = material.get('type', 'Unknown')
        generated_at = material.get('generated_at', 'Unknown')
        
        md_content = f"""# 教材{index:02d}: {topic}

## 📋 基本情報
- **タイプ**: {material_type}
- **生成日時**: {generated_at}
- **トピック**: {topic}

"""
        
        # ロールプレイの場合
        if 'model_dialogue' in material:
            md_content += f"""## 🎭 モデルダイアログ

```dialogue
{material['model_dialogue']}
```

"""
        
        # 有用表現
        if 'useful_expressions' in material:
            md_content += "## 💡 有用表現・語彙\n\n"
            for expr in material['useful_expressions']:
                md_content += f"- {expr}\n"
            md_content += "\n"
        
        # 追加質問
        if 'additional_questions' in material:
            md_content += "## ❓ 追加質問\n\n"
            for q in material['additional_questions']:
                md_content += f"- {q}\n"
            md_content += "\n"
        
        # ディスカッションの場合
        if 'discussion_topic' in material:
            md_content += f"""## 💬 ディスカッショントピック

{material['discussion_topic']}

"""
        
        if 'background_info' in material:
            md_content += f"""## 📚 背景情報

{material['background_info']}

"""
        
        if 'key_points' in material:
            md_content += "## 🎯 議論ポイント\n\n"
            for point in material['key_points']:
                md_content += f"- {point}\n"
            md_content += "\n"
        
        if 'discussion_questions' in material:
            md_content += "## 🤔 討議質問\n\n"
            for q in material['discussion_questions']:
                md_content += f"- {q}\n"
            md_content += "\n"
        
        # 表現練習の場合
        if 'chart_description' in material:
            md_content += f"""## 📊 図表説明

{material['chart_description']}

"""
        
        if 'vocabulary' in material:
            md_content += "## 📖 重要語彙\n\n"
            for vocab in material['vocabulary']:
                md_content += f"- {vocab}\n"
            md_content += "\n"
        
        if 'practice_questions' in material:
            md_content += "## ✏️ 練習問題\n\n"
            for q in material['practice_questions']:
                md_content += f"- {q}\n"
            md_content += "\n"
        
        # 音声スクリプト
        if 'audio_script' in material:
            md_content += f"""## 🎤 音声スクリプト

```audio
{material['audio_script']}
```

"""
        
        # タグ
        md_content += f"""## 🏷️ タグ
#教材/{material_type} #クライアント/{material.get('client', 'Unknown')} #生成日/{datetime.now().strftime('%Y-%m-%d')}

---
*生成日時: {generated_at}*
"""
        
        return md_content
    
    def generate_summary_markdown(self, materials, client_name, timestamp):
        """サマリーファイルを生成"""
        content = f"""# 📚 教材セット: {client_name}

## 📋 概要
- **クライアント**: {client_name}
- **生成日時**: {timestamp}
- **教材数**: {len(materials)}件
- **教材タイプ**: {', '.join(set(m.get('type', 'Unknown') for m in materials))}

## 📁 ファイル構成
"""
        
        for i, material in enumerate(materials):
            topic = material.get('topic', 'Unknown')
            material_type = material.get('type', 'Unknown')
            content += f"- **教材{i+1:02d}**: {topic} ({material_type})\n"
        
        content += f"""

## 🔗 関連ファイル
- [[トピックリスト]] - 使用されたトピック一覧
- [[教材01_*]] - 個別教材ファイル
- [[教材*.json]] - JSON形式データ

## 📊 統計
- 総表現数: {sum(len(m.get('useful_expressions', [])) for m in materials)}
- 平均品質スコア: {sum(m.get('quality_score', 4.0) for m in materials) / len(materials):.1f}/5.0

---
*生成日時: {datetime.now().isoformat()}*
"""
        
        return content
    
    def generate_topics_markdown(self, topic_list, client_name):
        """トピックリストのマークダウンファイルを生成"""
        content = f"""# 📝 トピックリスト: {client_name}

## 📅 作成日
{datetime.now().strftime('%Y-%m-%d')}

## 🎯 トピック一覧
"""
        
        for i, topic in enumerate(topic_list, 1):
            content += f"{i}. {topic}\n"
        
        content += f"""

## 📊 統計
- **総トピック数**: {len(topic_list)}
- **使用済み**: {len(topic_list)}件
- **残り**: 0件

## 🔗 関連
- [[README]] - 教材セット概要
- [[教材*]] - 生成された教材

---
*作成日時: {datetime.now().isoformat()}*
"""
        
        return content
    
    def import_context_from_obsidian(self, file_path):
        """Obsidianファイルからコンテキストをインポート"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # マークダウンを解析
            context_data = self.parse_markdown_context(content)
            return context_data
        
        except Exception as e:
            st.error(f"ファイル読み込みエラー: {e}")
            return None
    
    def parse_markdown_context(self, content):
        """マークダウンコンテンツを解析"""
        context_data = {
            'counseling_memo': '',
            'teaching_policy': '',
            'business_scenes': '',
            'topic_list': []
        }
        
        # セクション別に解析
        sections = content.split('##')
        
        for section in sections:
            if 'カウンセリング内容' in section:
                context_data['counseling_memo'] = self.extract_section_content(section)
            elif '学習方針' in section:
                context_data['teaching_policy'] = self.extract_section_content(section)
            elif 'ビジネスシーン' in section:
                context_data['business_scenes'] = self.extract_section_content(section)
            elif 'トピック' in section:
                topics = self.extract_list_items(section)
                context_data['topic_list'].extend(topics)
        
        return context_data
    
    def extract_section_content(self, section):
        """セクションの内容を抽出"""
        lines = section.split('\n')
        content_lines = []
        in_content = False
        
        for line in lines:
            if line.strip() and not line.startswith('#'):
                content_lines.append(line.strip())
        
        return '\n'.join(content_lines)
    
    def extract_list_items(self, section):
        """リストアイテムを抽出"""
        items = []
        lines = section.split('\n')
        
        for line in lines:
            if line.strip().startswith('- ') or line.strip().startswith('* '):
                item = line.strip()[2:].strip()
                if item:
                    items.append(item)
        
        return items

class ObsidianFileHandler(FileSystemEventHandler):
    """Obsidianファイル変更監視ハンドラー"""
    
    def __init__(self, callback_function):
        self.callback = callback_function
    
    def on_modified(self, event):
        if event.is_directory:
            return
        
        if event.src_path.endswith('.md'):
            # マークダウンファイルの変更を検知
            self.callback(event.src_path)

def start_obsidian_watcher(obsidian_path, callback_function):
    """Obsidianフォルダの監視を開始"""
    event_handler = ObsidianFileHandler(callback_function)
    observer = Observer()
    observer.schedule(event_handler, obsidian_path, recursive=True)
    observer.start()
    return observer

# Streamlit UI用関数
def show_obsidian_integration():
    """Obsidian連携タブのUI"""
    st.header("📚 Obsidian連携")
    st.markdown("**個人コンテキストファイルの管理** - Obsidianとの連携で効率的な教材管理")
    
    # Obsidian統合インスタンス
    if 'obsidian_integration' not in st.session_state:
        st.session_state.obsidian_integration = ObsidianIntegration()
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📁 フォルダ管理")
        
        # フォルダパス表示
        base_path = st.session_state.obsidian_integration.base_path
        st.info(f"**Obsidianフォルダ**: {base_path}")
        
        # フォルダ構造確認
        if st.button("📂 フォルダ構造確認"):
            folders = list(base_path.glob("*"))
            if folders:
                st.success("✅ フォルダ構造が正常です")
                for folder in folders:
                    if folder.is_dir():
                        st.write(f"📁 {folder.name}")
            else:
                st.warning("⚠️ フォルダが空です")
        
        # ファイル監視
        if st.button("🔍 ファイル監視開始"):
            if 'observer' not in st.session_state:
                def file_changed(file_path):
                    st.info(f"📝 ファイル変更検知: {file_path}")
                
                st.session_state.observer = start_obsidian_watcher(
                    str(base_path), file_changed
                )
                st.success("✅ ファイル監視を開始しました")
            else:
                st.info("✅ 既に監視中です")
    
    with col2:
        st.subheader("📤 エクスポート")
        
        # クライアント名入力
        client_name = st.text_input("クライアント名", placeholder="例: 田中商事_山田様")
        
        # エクスポート実行
        if st.button("📥 Obsidianにエクスポート") and client_name:
            if st.session_state.generated_materials:
                with st.spinner("Obsidianにエクスポート中..."):
                    result = st.session_state.obsidian_integration.export_materials_to_obsidian(
                        st.session_state.generated_materials,
                        client_name,
                        st.session_state.context_data.get('topic_list', [])
                    )
                
                st.success(f"✅ {len(result['files'])}件の教材をエクスポートしました")
                st.info(f"📁 保存先: {result['folder']}")
                
                # ファイル一覧表示
                with st.expander("📋 エクスポートされたファイル"):
                    for file_info in result['files']:
                        st.write(f"• {file_info['topic']}")
                        st.write(f"  - マークダウン: {file_info['markdown']}")
                        st.write(f"  - JSON: {file_info['json']}")
            else:
                st.warning("⚠️ エクスポートする教材がありません")
        
        # インポート機能
        st.subheader("📥 インポート")
        uploaded_file = st.file_uploader("Obsidianファイルをアップロード", type=['md'])
        
        if uploaded_file is not None:
            if st.button("📖 コンテキストをインポート"):
                content = uploaded_file.read().decode('utf-8')
                context_data = st.session_state.obsidian_integration.parse_markdown_context(content)
                
                if context_data:
                    st.session_state.context_data.update(context_data)
                    st.success("✅ コンテキストをインポートしました")
                else:
                    st.error("❌ インポートに失敗しました")
    
    # ヘルプ情報
    with st.expander("💡 Obsidian連携の使い方"):
        st.markdown("""
        **📚 Obsidian連携機能**
        
        ### 🔧 セットアップ
        1. **Obsidianインストール**: https://obsidian.md/ からダウンロード
        2. **プラグイン追加**: Templater, Dataview, QuickAdd
        3. **フォルダ設定**: 語学教材プロジェクトフォルダを作成
        
        ### 📁 推奨フォルダ構造
        ```
        語学教材プロジェクト/
        ├── 01_カウンセリング/
        ├── 02_システムプロンプト/
        ├── 03_テンプレート/
        ├── 04_トピックリスト/
        ├── 05_生成教材/
        └── 06_設定/
        ```
        
        ### 🔄 ワークフロー
        1. **カウンセリング記録**: Obsidianでクライアント情報を記録
        2. **教材生成**: Streamlitで教材を作成
        3. **エクスポート**: Obsidianに自動エクスポート
        4. **管理・共有**: Obsidianで教材を管理・共有
        
        ### 📊 Dataviewクエリ例
        ```dataview
        TABLE 
           生成日時 as "生成日",
           クライアント as "クライアント", 
           教材タイプ as "タイプ"
        FROM "05_生成教材"
        SORT 生成日時 DESC
        ```
        """)

if __name__ == "__main__":
    # テスト用
    integration = ObsidianIntegration()
    print(f"Obsidian統合セットアップ完了: {integration.base_path}") 