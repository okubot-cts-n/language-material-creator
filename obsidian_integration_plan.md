# 📚 Obsidian連携による個人コンテキスト管理計画

## 🎯 概要
語学教材作成ツールとObsidianを連携させ、個人のコンテキストファイルを効率的に管理するシステム

## 📁 フォルダ構造案

```
語学教材プロジェクト/
├── 01_カウンセリング/
│   ├── クライアントA_2024-07.md
│   ├── クライアントB_2024-08.md
│   └── テンプレート_カウンセリング.md
├── 02_システムプロンプト/
│   ├── 金融業界_営業.md
│   ├── IT業界_エンジニア.md
│   └── 製造業_管理職.md
├── 03_テンプレート/
│   ├── ロールプレイ_金融.json
│   ├── ディスカッション_IT.json
│   └── 表現練習_製造.json
├── 04_トピックリスト/
│   ├── クライアントA_トピック.md
│   ├── クライアントB_トピック.md
│   └── 業界別_トピック集.md
├── 05_生成教材/
│   ├── クライアントA_2024-07/
│   │   ├── 教材01_融資提案.json
│   │   ├── 教材02_業績報告.json
│   │   └── 教材03_リスク評価.json
│   └── クライアントB_2024-08/
│       ├── 教材01_システム説明.json
│       └── 教材02_技術提案.json
└── 06_設定/
    ├── 連携設定.json
    └── エクスポート設定.md
```

## 🔧 Obsidianプラグイン活用

### **推奨プラグイン**
1. **Templater**: テンプレート自動化
2. **Dataview**: データベース機能
3. **QuickAdd**: 高速ファイル作成
4. **Calendar**: 日付管理
5. **Git**: バージョン管理

### **自動化スクリプト例**

#### **Templater スクリプト（カウンセリング記録）**
```javascript
// カウンセリング記録テンプレート
<%*
// 自動的に日付とクライアント名を設定
const today = new Date().toISOString().split('T')[0];
const clientName = await tp.system.prompt("クライアント名");
const fileName = `${clientName}_${today}`;
await tp.file.move(`01_カウンセリング/${fileName}`);
_%>

# カウンセリング記録: <%= clientName %>

## 📅 日付
<%= today %>

## 👤 クライアント情報
- **名前**: <%= clientName %>
- **業界**: 
- **職種**: 
- **レベル**: 

## 📝 カウンセリング内容
### 学習目標
- 

### 現在の課題
- 

### 希望する教材タイプ
- [ ] ロールプレイ
- [ ] ディスカッション  
- [ ] 表現練習

## 🎯 次のアクション
- [ ] 教材生成
- [ ] フォローアップ
```

#### **Dataview クエリ（教材一覧）**
```dataview
TABLE 
  生成日時 as "生成日",
  クライアント as "クライアント",
  教材タイプ as "タイプ",
  品質スコア as "品質"
FROM "05_生成教材"
SORT 生成日時 DESC
```

## 🔄 Streamlit連携方法

### **1. ファイル監視方式**
```python
# app_practical.py に追加
import watchdog.observers
import watchdog.events

class ObsidianFileHandler(watchdog.events.FileSystemEventHandler):
    def on_modified(self, event):
        if event.is_directory:
            return
        if event.src_path.endswith('.md'):
            # Obsidianファイルの変更を検知
            self.update_context_from_obsidian(event.src_path)
    
    def update_context_from_obsidian(self, file_path):
        # マークダウンファイルを解析してコンテキストを更新
        pass
```

### **2. エクスポート機能**
```python
def export_to_obsidian(materials, client_name):
    """教材をObsidian形式でエクスポート"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Obsidianフォルダパス
    obsidian_path = f"語学教材プロジェクト/05_生成教材/{client_name}_{timestamp}/"
    
    for i, material in enumerate(materials):
        # マークダウンファイル生成
        md_content = generate_obsidian_markdown(material)
        
        # JSONファイルも同時生成
        json_content = json.dumps(material, ensure_ascii=False, indent=2)
        
        # ファイル保存
        save_to_obsidian(obsidian_path, f"教材{i+1:02d}_{material['topic']}", md_content, json_content)
```

## 🎨 UI改善案

### **Obsidian連携タブ**
```python
def show_obsidian_integration():
    st.header("📚 Obsidian連携")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📁 フォルダ監視")
        obsidian_path = st.text_input("Obsidianフォルダパス", 
                                     value="~/Documents/語学教材プロジェクト/")
        
        if st.button("🔍 フォルダ監視開始"):
            start_obsidian_watcher(obsidian_path)
            st.success("✅ Obsidianフォルダの監視を開始しました")
    
    with col2:
        st.subheader("📤 エクスポート")
        client_name = st.text_input("クライアント名")
        
        if st.button("📥 Obsidianにエクスポート"):
            export_to_obsidian(st.session_state.generated_materials, client_name)
            st.success("✅ Obsidianにエクスポートしました")
```

## 🚀 実装ステップ

### **Phase 1: 基本連携**
1. Obsidianフォルダ構造の作成
2. 基本的なエクスポート機能
3. マークダウンテンプレート作成

### **Phase 2: 自動化**
1. Templaterプラグインの設定
2. ファイル監視機能の実装
3. Dataviewクエリの作成

### **Phase 3: 高度な機能**
1. 双方向同期
2. バージョン管理
3. チーム共有機能

## 💡 代替案

### **1. Notion連携**
- **利点**: データベース機能、API連携
- **欠点**: 有料、学習コスト

### **2. ローカルファイル管理**
- **利点**: シンプル、無料
- **欠点**: 自動化が限定的

### **3. Google Drive + Apps Script**
- **利点**: クラウド、既存環境
- **欠点**: 複雑、API制限

## 🎯 推奨実装順序

1. **Obsidian基本セットアップ** (1日)
2. **フォルダ構造作成** (1日)  
3. **Streamlit連携機能** (2-3日)
4. **自動化スクリプト** (2-3日)
5. **UI統合** (1日)

**総実装時間: 約1週間** 