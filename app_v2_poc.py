import streamlit as st
import json
import os
from datetime import datetime
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path

# ページ設定
st.set_page_config(
    page_title="語学教材作成支援ツール v2.0 - PoC",
    page_icon="📚",
    layout="wide"
)

# サンプルデータの読み込み
def load_sample_data():
    """サンプルデータを読み込み"""
    sample_contexts = {
        "金融業界A社": {
            "業界": "金融サービス",
            "受講者数": 15,
            "平均レベル": "TOEIC 600-750",
            "重点領域": ["専門用語", "数値説明", "提案・交渉"],
            "更新日": "2025-01-27"
        },
        "製造業B社": {
            "業界": "製造業",
            "受講者数": 25,
            "平均レベル": "TOEIC 500-650",
            "重点領域": ["品質管理", "技術説明", "安全管理"],
            "更新日": "2025-01-25"
        },
        "IT企業C社": {
            "業界": "IT・ソフトウェア",
            "受講者数": 20,
            "平均レベル": "TOEIC 650-800",
            "重点領域": ["プレゼン", "技術仕様", "プロジェクト管理"],
            "更新日": "2025-01-26"
        }
    }
    
    sample_templates = {
        "ロールプレイ（金融）": {
            "対象業界": "金融サービス",
            "難易度": "中級",
            "構成要素": ["対話文", "有用表現", "追加質問", "音声スクリプト"],
            "推定時間": "45分"
        },
        "ディスカッション（IT）": {
            "対象業界": "IT・ソフトウェア",
            "難易度": "上級",
            "構成要素": ["討論トピック", "論点整理", "参考資料"],
            "推定時間": "60分"
        },
        "表現練習（製造）": {
            "対象業界": "製造業",
            "難易度": "中級",
            "構成要素": ["図表資料", "説明練習", "専門用語", "Q&A"],
            "推定時間": "40分"
        }
    }
    
    sample_materials = [
        {
            "id": "MAT_001",
            "題名": "融資条件の説明と交渉",
            "タイプ": "ロールプレイ",
            "業界": "金融",
            "難易度": "中級",
            "生成日": "2025-01-27",
            "品質スコア": 4.2,
            "重複度": 0.05,
            "ステータス": "承認済み"
        },
        {
            "id": "MAT_002", 
            "題名": "新商品の市場分析討論",
            "タイプ": "ディスカッション",
            "業界": "製造",
            "難易度": "上級",
            "生成日": "2025-01-26",
            "品質スコア": 3.8,
            "重複度": 0.12,
            "ステータス": "要修正"
        },
        {
            "id": "MAT_003",
            "題名": "プロジェクト進捗報告",
            "タイプ": "表現練習",
            "業界": "IT",
            "難易度": "中級",
            "生成日": "2025-01-25",
            "品質スコア": 4.5,
            "重複度": 0.03,
            "ステータス": "承認待ち"
        }
    ]
    
    return sample_contexts, sample_templates, sample_materials

# メインアプリケーション
def main():
    # サンプルデータ読み込み
    contexts, templates, materials = load_sample_data()
    
    # サイドバーナビゲーション
    st.sidebar.title("📚 語学教材作成支援ツール v2.0")
    st.sidebar.markdown("---")
    
    menu_options = [
        "🏠 ダッシュボード",
        "📁 コンテキスト管理", 
        "🎨 テンプレート設計",
        "⚡ 一括生成",
        "🔍 品質管理",
        "👥 承認ワークフロー"
    ]
    
    selected_menu = st.sidebar.selectbox("メニュー選択", menu_options)
    
    # メインコンテンツ
    if selected_menu == "🏠 ダッシュボード":
        show_dashboard(materials)
        
    elif selected_menu == "📁 コンテキスト管理":
        show_context_management(contexts)
        
    elif selected_menu == "🎨 テンプレート設計":
        show_template_designer(templates)
        
    elif selected_menu == "⚡ 一括生成":
        show_batch_generation(contexts, templates)
        
    elif selected_menu == "🔍 品質管理":
        show_quality_management(materials)
        
    elif selected_menu == "👥 承認ワークフロー":
        show_approval_workflow(materials)

def show_dashboard(materials):
    """メインダッシュボード表示"""
    st.title("🏠 ダッシュボード")
    
    # KPI表示
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("今月生成数", "47教材", "↑12")
    with col2:
        st.metric("平均品質スコア", "4.2", "↑0.3")
    with col3:
        st.metric("承認待ち", "8教材", "↓3")
    with col4:
        st.metric("重複検出", "2件", "→0")
    
    st.markdown("---")
    
    # グラフエリア
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 教材生成推移")
        # サンプルデータでグラフ作成
        dates = pd.date_range('2025-01-01', '2025-01-27', freq='D')
        values = [max(0, 5 + int(3 * (i % 7)) + (i % 3)) for i in range(len(dates))]
        
        fig = px.line(x=dates, y=values, title="日別教材生成数")
        fig.update_layout(height=300)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("🎯 教材タイプ分布")
        types = ["ロールプレイ", "ディスカッション", "表現練習"]
        counts = [28, 12, 7]
        
        fig = px.pie(values=counts, names=types, title="教材タイプ別生成数")
        fig.update_layout(height=300)
        st.plotly_chart(fig, use_container_width=True)
    
    # アラート・通知エリア
    st.subheader("⚠️ 注意事項・アラート")
    
    alerts = [
        {"type": "warning", "message": "金融業界向け教材で重複表現が検出されました (2件)", "action": "品質管理で確認"},
        {"type": "info", "message": "新しいテンプレート「製造業_安全管理」が追加されました", "action": "テンプレート設計で確認"},
        {"type": "success", "message": "IT企業C社向け教材15件が承認されました", "action": "完了"}
    ]
    
    for alert in alerts:
        if alert["type"] == "warning":
            st.warning(f"⚠️ {alert['message']} → [{alert['action']}]")
        elif alert["type"] == "info":
            st.info(f"ℹ️ {alert['message']} → [{alert['action']}]")
        elif alert["type"] == "success":
            st.success(f"✅ {alert['message']}")

def show_context_management(contexts):
    """コンテキスト管理画面"""
    st.title("📁 コンテキスト管理")
    
    tabs = st.tabs(["📝 カウンセリングメモ", "📋 教務方針", "🏢 業界設定"])
    
    with tabs[0]:
        st.subheader("カウンセリングメモ管理")
        
        # 既存コンテキスト一覧
        st.write("### 登録済みクライアント")
        for name, info in contexts.items():
            with st.expander(f"{name} ({info['業界']}) - {info['受講者数']}名"):
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**平均レベル**: {info['平均レベル']}")
                    st.write(f"**更新日**: {info['更新日']}")
                with col2:
                    st.write("**重点領域**:")
                    for area in info['重点領域']:
                        st.write(f"• {area}")
                
                if st.button(f"編集", key=f"edit_{name}"):
                    st.info("編集機能（実装予定）")
        
        # 新規追加
        st.write("### 新規クライアント追加")
        with st.form("new_client"):
            client_name = st.text_input("クライアント名")
            industry = st.selectbox("業界", ["金融", "製造", "IT", "商社", "その他"])
            num_students = st.number_input("受講者数", min_value=1, value=10)
            level = st.selectbox("平均レベル", ["TOEIC 300-500", "TOEIC 500-750", "TOEIC 750-900"])
            
            if st.form_submit_button("追加"):
                st.success(f"クライアント「{client_name}」を追加しました（デモ）")
    
    with tabs[1]:
        st.subheader("教務方針設定")
        
        # レベル基準設定
        st.write("### レベル基準")
        level_standards = {
            "初級 (A1-A2)": {
                "TOEIC範囲": "300-500点",
                "語彙目安": "1000語程度",
                "重点": "基本文法、頻出表現"
            },
            "中級 (B1-B2)": {
                "TOEIC範囲": "500-750点", 
                "語彙目安": "2500語程度",
                "重点": "実践シーン、専門用語"
            },
            "上級 (B2-C1)": {
                "TOEIC範囲": "750-900点",
                "語彙目安": "4000語以上",
                "重点": "複雑な議論、文化的配慮"
            }
        }
        
        for level, details in level_standards.items():
            with st.expander(level):
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**TOEIC範囲**: {details['TOEIC範囲']}")
                    st.write(f"**語彙目安**: {details['語彙目安']}")
                with col2:
                    st.write(f"**重点領域**: {details['重点']}")
        
        # 品質基準設定
        st.write("### 品質チェック基準")
        st.slider("最低品質スコア", 1.0, 5.0, 4.0, 0.1)
        st.slider("重複許容度", 0.0, 0.3, 0.1, 0.01)
        st.multiselect("必須チェック項目", 
                      ["実用性", "文化的適切性", "難易度一致", "テンプレート準拠"],
                      default=["実用性", "難易度一致"])
    
    with tabs[2]:
        st.subheader("業界別設定")
        
        industries = ["金融", "製造", "IT", "商社", "医療", "教育"]
        
        for industry in industries:
            with st.expander(f"{industry}業界"):
                col1, col2 = st.columns(2)
                with col1:
                    st.text_area(f"{industry}_専門用語", 
                               placeholder="金融: 融資, 金利, 担保, リスク評価...",
                               height=100)
                with col2:
                    st.text_area(f"{industry}_典型シーン",
                               placeholder="• 顧客との商談\n• 社内会議\n• プレゼンテーション...",
                               height=100)

def show_template_designer(templates):
    """テンプレート設計画面"""
    st.title("🎨 テンプレート設計")
    
    tabs = st.tabs(["📋 テンプレート一覧", "➕ 新規作成", "🔧 カスタマイズ"])
    
    with tabs[0]:
        st.subheader("登録済みテンプレート")
        
        for name, details in templates.items():
            with st.expander(f"{name} - {details['対象業界']}"):
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.write(f"**難易度**: {details['難易度']}")
                    st.write(f"**推定時間**: {details['推定時間']}")
                
                with col2:
                    st.write("**構成要素**:")
                    for element in details['構成要素']:
                        st.write(f"• {element}")
                
                with col3:
                    st.button("編集", key=f"edit_template_{name}")
                    st.button("複製", key=f"copy_template_{name}")
                    st.button("削除", key=f"delete_template_{name}")
    
    with tabs[1]:
        st.subheader("新規テンプレート作成")
        
        with st.form("new_template"):
            col1, col2 = st.columns(2)
            
            with col1:
                template_name = st.text_input("テンプレート名")
                target_industry = st.selectbox("対象業界", ["金融", "製造", "IT", "共通"])
                difficulty = st.selectbox("難易度", ["初級", "中級", "上級"])
                material_type = st.selectbox("教材タイプ", ["ロールプレイ", "ディスカッション", "表現練習"])
            
            with col2:
                estimated_time = st.slider("推定学習時間（分）", 20, 90, 45, 5)
                include_audio = st.checkbox("音声スクリプト含む", True)
                include_images = st.checkbox("図表・画像含む", False)
                custom_elements = st.multiselect("追加要素", 
                                               ["語彙リスト", "文法ポイント", "文化的注意点", "宿題"])
            
            # 構造定義
            st.write("### 構造定義")
            
            if material_type == "ロールプレイ":
                dialogue_length = st.slider("対話文の長さ（語数）", 100, 300, 200, 10)
                participants = st.number_input("参加者数", 2, 4, 2)
                expressions_count = st.slider("有用表現数", 5, 15, 10)
                questions_count = st.slider("追加質問数", 3, 8, 4)
            
            elif material_type == "ディスカッション":
                topic_complexity = st.selectbox("トピック複雑度", ["単純", "中程度", "複雑"])
                discussion_time = st.slider("想定討論時間（分）", 10, 30, 20)
                viewpoints = st.number_input("提示観点数", 2, 5, 3)
            
            elif material_type == "表現練習":
                chart_types = st.multiselect("図表タイプ", 
                                           ["棒グラフ", "線グラフ", "円グラフ", "表", "フローチャート"])
                explanation_length = st.slider("説明文の長さ（語数）", 50, 150, 100)
            
            if st.form_submit_button("テンプレート作成"):
                st.success(f"テンプレート「{template_name}」を作成しました（デモ）")
    
    with tabs[2]:
        st.subheader("テンプレートカスタマイズ")
        
        selected_template = st.selectbox("編集するテンプレート", list(templates.keys()))
        
        if selected_template:
            st.write(f"### {selected_template} の設定")
            
            # JSON表示・編集
            sample_json = {
                "template_id": "roleplay_finance_v1",
                "name": selected_template,
                "structure": {
                    "model_dialogue": {"length_words": "180-220", "participants": 2},
                    "useful_expressions": {"count": "10-12", "difficulty": "intermediate"},
                    "additional_questions": {"count": 4}
                }
            }
            
            edited_json = st.text_area("テンプレート設定 (JSON)", 
                                     json.dumps(sample_json, indent=2, ensure_ascii=False),
                                     height=300)
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("設定を保存"):
                    st.success("設定を保存しました（デモ）")
            with col2:
                if st.button("テスト生成"):
                    st.info("テスト教材を生成します（デモ）")

def show_batch_generation(contexts, templates):
    """一括生成画面"""
    st.title("⚡ 一括生成")
    
    tabs = st.tabs(["🎯 生成設定", "📊 進捗管理", "📁 生成履歴"])
    
    with tabs[0]:
        st.subheader("一括生成設定")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("### 基本設定")
            selected_context = st.selectbox("対象クライアント", list(contexts.keys()))
            selected_template = st.selectbox("使用テンプレート", list(templates.keys()))
            generation_count = st.number_input("生成数", 1, 50, 10)
            
            st.write("### トピック設定")
            topic_source = st.radio("トピック選択方法", 
                                   ["自動生成", "リストから選択", "手動入力"])
            
            if topic_source == "リストから選択":
                sample_topics = [
                    "新規顧客開拓営業",
                    "既存顧客フォローアップ",
                    "商品・サービス説明",
                    "価格・条件交渉",
                    "クレーム対応",
                    "契約締結",
                    "アフターサービス"
                ]
                selected_topics = st.multiselect("生成トピック", sample_topics)
        
        with col2:
            st.write("### 品質設定")
            quality_level = st.selectbox("品質チェックレベル", ["標準", "厳密", "最高"])
            duplicate_check = st.checkbox("重複チェック実行", True)
            auto_approval = st.checkbox("自動承認（条件満たす場合）", False)
            
            st.write("### 出力設定")
            output_format = st.multiselect("出力形式", 
                                         ["Google Docs", "PDF", "Word", "JSON"],
                                         default=["Google Docs"])
            include_stats = st.checkbox("統計レポート含む", True)
        
        # 生成実行
        st.markdown("---")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("🚀 生成開始", type="primary"):
                st.session_state.batch_running = True
                st.success("一括生成を開始しました！")
        
        with col2:
            if st.button("💾 設定を保存"):
                st.info("生成設定を保存しました")
        
        with col3:
            if st.button("🔄 設定をリセット"):
                st.warning("設定をリセットしました")
    
    with tabs[1]:
        st.subheader("進行中の生成タスク")
        
        # 進捗表示（サンプル）
        if st.session_state.get('batch_running', False):
            current_progress = st.progress(0)
            status_text = st.empty()
            
            import time
            for i in range(100):
                time.sleep(0.01)
                current_progress.progress(i + 1)
                if i < 30:
                    status_text.text(f'トピック生成中... {i+1}/10')
                elif i < 70:
                    status_text.text(f'教材生成中... {i-29}/40')
                elif i < 90:
                    status_text.text(f'品質チェック中... {i-69}/20')
                else:
                    status_text.text(f'出力中... {i-89}/10')
            
            st.success("✅ 一括生成が完了しました！")
            st.session_state.batch_running = False
        else:
            st.info("現在実行中のタスクはありません")
        
        # タスク履歴
        st.write("### 最近のタスク")
        task_data = {
            "タスクID": ["BATCH_001", "BATCH_002", "BATCH_003"],
            "クライアント": ["金融業界A社", "IT企業C社", "製造業B社"],
            "生成数": [15, 8, 12],
            "ステータス": ["完了", "実行中", "エラー"],
            "開始時刻": ["2025-01-27 09:00", "2025-01-27 10:30", "2025-01-27 11:15"]
        }
        st.dataframe(pd.DataFrame(task_data), use_container_width=True)
    
    with tabs[2]:
        st.subheader("生成履歴")
        
        # フィルター
        col1, col2, col3 = st.columns(3)
        with col1:
            date_filter = st.date_input("期間フィルター")
        with col2:
            client_filter = st.selectbox("クライアントフィルター", ["全て"] + list(contexts.keys()))
        with col3:
            status_filter = st.selectbox("ステータスフィルター", ["全て", "完了", "エラー", "実行中"])
        
        # 履歴表示
        history_data = {
            "日時": ["2025-01-27 09:00", "2025-01-26 14:30", "2025-01-25 16:45"],
            "クライアント": ["金融業界A社", "IT企業C社", "製造業B社"],
            "テンプレート": ["ロールプレイ（金融）", "ディスカッション（IT）", "表現練習（製造）"],
            "生成数": [15, 8, 12],
            "成功数": [14, 8, 11],
            "品質スコア": [4.2, 4.5, 3.9],
            "アクション": ["詳細", "詳細", "詳細"]
        }
        
        st.dataframe(pd.DataFrame(history_data), use_container_width=True)

def show_quality_management(materials):
    """品質管理画面"""
    st.title("🔍 品質管理")
    
    tabs = st.tabs(["📊 品質ダッシュボード", "🔄 重複チェック", "📈 難易度分析", "✅ 総合評価"])
    
    with tabs[0]:
        st.subheader("品質概要")
        
        # 品質メトリクス
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("平均品質スコア", "4.2/5.0", "↑0.3")
        with col2:
            st.metric("合格率", "87%", "↑5%")
        with col3:
            st.metric("重複検出", "3件", "↓2")
        with col4:
            st.metric("要修正", "6件", "→0")
        
        # 品質推移グラフ
        st.subheader("品質スコア推移")
        dates = pd.date_range('2025-01-20', '2025-01-27', freq='D')
        scores = [3.8, 4.0, 4.1, 3.9, 4.2, 4.3, 4.2]
        
        fig = px.line(x=dates, y=scores, title="日別平均品質スコア")
        fig.add_hline(y=4.0, line_dash="dash", line_color="red", 
                     annotation_text="最低基準 (4.0)")
        st.plotly_chart(fig, use_container_width=True)
    
    with tabs[1]:
        st.subheader("重複チェック")
        
        # 重複検出設定
        col1, col2 = st.columns(2)
        
        with col1:
            similarity_threshold = st.slider("類似度閾値", 0.5, 0.95, 0.8, 0.05)
            check_elements = st.multiselect("チェック対象", 
                                          ["有用表現", "シチュエーション", "語彙", "文構造"],
                                          default=["有用表現", "シチュエーション"])
        
        with col2:
            if st.button("重複チェック実行"):
                st.info("重複チェックを実行中...")
        
        # 重複検出結果
        st.subheader("検出結果")
        duplicate_data = {
            "教材1": ["MAT_001", "MAT_003", "MAT_005"],
            "教材2": ["MAT_007", "MAT_009", "MAT_012"],
            "類似度": [0.85, 0.78, 0.82],
            "重複要素": ["有用表現", "シチュエーション", "語彙"],
            "対処": ["要修正", "許容範囲", "要修正"]
        }
        
        df_duplicates = pd.DataFrame(duplicate_data)
        st.dataframe(df_duplicates, use_container_width=True)
    
    with tabs[2]:
        st.subheader("難易度分析")
        
        # 難易度分布
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("### 語彙難易度分布")
            vocab_levels = ["A1", "A2", "B1", "B2", "C1"]
            vocab_counts = [5, 15, 35, 30, 15]
            
            fig = px.bar(x=vocab_levels, y=vocab_counts, title="CEFR別語彙分布")
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.write("### 文法複雑度")
            complexity_data = {
                "レベル": ["Simple", "Compound", "Complex"],
                "割合": [40, 35, 25]
            }
            
            fig = px.pie(values=complexity_data["割合"], names=complexity_data["レベル"],
                        title="文構造複雑度")
            st.plotly_chart(fig, use_container_width=True)
        
        # 難易度調整提案
        st.subheader("調整提案")
        
        adjustment_suggestions = [
            {"教材ID": "MAT_002", "現在レベル": "B2", "目標レベル": "B1", 
             "提案": "専門用語を基本語彙に置換", "優先度": "高"},
            {"教材ID": "MAT_005", "現在レベル": "A2", "目標レベル": "B1",
             "提案": "文構造を複雑化", "優先度": "中"},
            {"教材ID": "MAT_008", "現在レベル": "C1", "目標レベル": "B2",
             "提案": "表現を平易化", "優先度": "高"}
        ]
        
        for suggestion in adjustment_suggestions:
            priority_color = "red" if suggestion["優先度"] == "高" else "orange" if suggestion["優先度"] == "中" else "green"
            st.markdown(f"""
            <div style="border-left: 4px solid {priority_color}; padding-left: 10px; margin: 10px 0;">
                <strong>{suggestion['教材ID']}</strong>: {suggestion['現在レベル']} → {suggestion['目標レベル']}<br>
                💡 {suggestion['提案']} <span style="color: {priority_color};">(優先度: {suggestion['優先度']})</span>
            </div>
            """, unsafe_allow_html=True)
    
    with tabs[3]:
        st.subheader("総合品質評価")
        
        # 教材別品質スコア
        st.write("### 教材別詳細評価")
        
        for material in materials:
            with st.expander(f"{material['題名']} (ID: {material['id']})"):
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("総合スコア", f"{material['品質スコア']}/5.0")
                    st.metric("重複度", f"{material['重複度']:.1%}")
                
                with col2:
                    # レーダーチャート（サンプル）
                    categories = ['実用性', '適切性', '難易度', '構成', '語彙']
                    values = [4.2, 4.0, 4.5, 3.8, 4.1]
                    
                    fig = go.Figure()
                    fig.add_trace(go.Scatterpolar(
                        r=values,
                        theta=categories,
                        fill='toself',
                        name=material['id']
                    ))
                    fig.update_layout(
                        polar=dict(radialaxis=dict(visible=True, range=[0, 5])),
                        showlegend=False,
                        height=250
                    )
                    st.plotly_chart(fig, use_container_width=True)
                
                with col3:
                    st.write("**ステータス**")
                    status_color = {"承認済み": "green", "要修正": "red", "承認待ち": "orange"}[material['ステータス']]
                    st.markdown(f"<span style='color: {status_color};'>●</span> {material['ステータス']}", 
                              unsafe_allow_html=True)
                    
                    if material['ステータス'] == "要修正":
                        if st.button(f"修正実行", key=f"fix_{material['id']}"):
                            st.success("修正を実行しました（デモ）")

def show_approval_workflow(materials):
    """承認ワークフロー画面"""
    st.title("👥 承認ワークフロー")
    
    tabs = st.tabs(["📋 承認待ち", "✅ 承認済み", "🔄 ワークフロー設定"])
    
    with tabs[0]:
        st.subheader("承認待ち教材")
        
        pending_materials = [m for m in materials if m['ステータス'] == '承認待ち']
        
        for material in pending_materials:
            with st.expander(f"{material['題名']} - 品質スコア: {material['品質スコア']}"):
                col1, col2, col3 = st.columns([2, 1, 1])
                
                with col1:
                    st.write(f"**教材ID**: {material['id']}")
                    st.write(f"**タイプ**: {material['タイプ']}")
                    st.write(f"**業界**: {material['業界']}")
                    st.write(f"**生成日**: {material['生成日']}")
                
                with col2:
                    if st.button("✅ 承認", key=f"approve_{material['id']}"):
                        st.success("承認しました")
                    
                    if st.button("📝 修正要求", key=f"request_fix_{material['id']}"):
                        st.info("修正要求を送信しました")
                
                with col3:
                    if st.button("👁️ プレビュー", key=f"preview_{material['id']}"):
                        st.info("プレビュー表示（実装予定）")
                    
                    if st.button("❌ 却下", key=f"reject_{material['id']}"):
                        st.warning("却下しました")
        
        if not pending_materials:
            st.info("現在承認待ちの教材はありません")
    
    with tabs[1]:
        st.subheader("承認済み教材")
        
        approved_materials = [m for m in materials if m['ステータス'] == '承認済み']
        
        # フィルター・ソート
        col1, col2, col3 = st.columns(3)
        with col1:
            industry_filter = st.selectbox("業界フィルター", ["全て", "金融", "IT", "製造"])
        with col2:
            type_filter = st.selectbox("タイプフィルター", ["全て", "ロールプレイ", "ディスカッション", "表現練習"])
        with col3:
            sort_by = st.selectbox("ソート", ["生成日", "品質スコア", "教材ID"])
        
        # 承認済み教材一覧
        approved_data = {
            "教材ID": [m['id'] for m in approved_materials],
            "題名": [m['題名'] for m in approved_materials],
            "タイプ": [m['タイプ'] for m in approved_materials],
            "業界": [m['業界'] for m in approved_materials],
            "品質スコア": [m['品質スコア'] for m in approved_materials],
            "生成日": [m['生成日'] for m in approved_materials]
        }
        
        st.dataframe(pd.DataFrame(approved_data), use_container_width=True)
    
    with tabs[2]:
        st.subheader("ワークフロー設定")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("### 承認基準")
            min_quality_score = st.slider("最低品質スコア", 1.0, 5.0, 4.0, 0.1)
            max_duplicate_rate = st.slider("最大重複率", 0.0, 0.3, 0.1, 0.01)
            
            auto_approve_conditions = st.multiselect("自動承認条件",
                                                   ["品質スコア4.5以上", "重複率5%以下", "特定業界", "特定テンプレート"])
        
        with col2:
            st.write("### 通知設定")
            notify_approval = st.checkbox("承認時に通知", True)
            notify_rejection = st.checkbox("却下時に通知", True)
            notify_fix_request = st.checkbox("修正要求時に通知", True)
            
            notification_methods = st.multiselect("通知方法", 
                                                ["メール", "Slack", "チャット", "ダッシュボード"])
        
        # 承認者設定
        st.write("### 承認者設定")
        
        approvers_data = {
            "承認者": ["田中主任", "佐藤課長", "山田部長"],
            "権限レベル": ["レベル1", "レベル2", "レベル3"],
            "担当業界": ["IT・製造", "金融・商社", "全業界"],
            "ステータス": ["アクティブ", "アクティブ", "アクティブ"]
        }
        
        st.dataframe(pd.DataFrame(approvers_data), use_container_width=True)
        
        if st.button("設定を保存"):
            st.success("ワークフロー設定を保存しました")

if __name__ == "__main__":
    main() 