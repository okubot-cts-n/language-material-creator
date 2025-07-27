import streamlit as st
import os
from datetime import datetime
import json
from dotenv import load_dotenv
from claude_api import ClaudeAPIClient
from google_docs_api import GoogleDocsAPIClient

# 環境変数を読み込み
load_dotenv()

# Streamlitページ設定
st.set_page_config(
    page_title="語学教材作成支援ツール",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# カスタムCSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .step-header {
        font-size: 1.5rem;
        color: #ff7f0e;
        margin: 1rem 0;
        border-bottom: 2px solid #ff7f0e;
        padding-bottom: 0.5rem;
    }
    .success-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

def main():
    # メインヘッダー
    st.markdown('<h1 class="main-header">📚 語学教材作成支援ツール</h1>', unsafe_allow_html=True)
    
    # サイドバー - 進行状況
    with st.sidebar:
        st.header("🔄 作業進行状況")
        progress_steps = [
            "基本情報入力",
            "トピック設定", 
            "教材生成",
            "品質チェック",
            "出力・保存"
        ]
        
        # セッション状態の初期化
        if 'current_step' not in st.session_state:
            st.session_state.current_step = 0
            
        for i, step in enumerate(progress_steps):
            if i <= st.session_state.current_step:
                st.success(f"✅ {step}")
            else:
                st.info(f"⏳ {step}")
    
    # メインコンテンツエリア
    tab1, tab2, tab3, tab4 = st.tabs(["📝 基本設定", "🎯 トピック生成", "📚 教材作成", "📤 出力管理"])
    
    with tab1:
        st.markdown('<div class="step-header">📝 Step 1: 基本情報入力</div>', unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("受講者情報")
            industry = st.selectbox(
                "業界",
                ["IT・テクノロジー", "金融・銀行", "商社・貿易", "製造業", "医療・製薬", 
                 "コンサルティング", "教育", "小売・サービス", "その他"]
            )
            
            job_role = st.selectbox(
                "職種",
                ["営業", "マネージャー", "エンジニア", "マーケティング", "人事", 
                 "経理・財務", "企画", "カスタマーサポート", "その他"]
            )
            
            english_level = st.selectbox(
                "英語レベル",
                ["初級（TOEIC 300-500）", "中級（TOEIC 500-700）", 
                 "中上級（TOEIC 700-850）", "上級（TOEIC 850+）"]
            )
        
        with col2:
            st.subheader("学習目標")
            learning_goal = st.text_area(
                "具体的な学習目標・シーン",
                placeholder="例：海外クライアントとの商談、プレゼンテーション、メール対応等",
                height=100
            )
            
            material_type = st.selectbox(
                "教材タイプ",
                ["ロールプレイ", "ディスカッション", "表現練習"]
            )
            
            urgency = st.selectbox(
                "緊急度",
                ["通常", "急ぎ", "最優先"]
            )
        
        if st.button("✅ 基本情報を保存", type="primary"):
            # セッション状態に保存
            st.session_state.user_info = {
                "industry": industry,
                "job_role": job_role,
                "english_level": english_level,
                "learning_goal": learning_goal,
                "material_type": material_type,
                "urgency": urgency,
                "created_at": datetime.now().isoformat()
            }
            st.session_state.current_step = 1
            st.success("✅ 基本情報が保存されました！")
            st.rerun()
    
    with tab2:
        st.markdown('<div class="step-header">🎯 Step 2: トピック生成</div>', unsafe_allow_html=True)
        
        if 'user_info' not in st.session_state:
            st.warning("⚠️ まず基本情報を入力してください。")
            return
            
        st.info(f"選択された教材タイプ: **{st.session_state.user_info['material_type']}**")
        
        # 環境変数チェック
        if not os.getenv('ANTHROPIC_API_KEY'):
            st.error("❌ ANTHROPIC_API_KEY環境変数が設定されていません。")
            st.info("💡 `.env`ファイルを作成してAPIキーを追加してください。")
            return
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.subheader("1次トピックリスト生成")
            if st.button("🎯 トピックリストを生成", type="primary"):
                with st.spinner("🤖 Claude APIでトピックを生成中..."):
                    try:
                        claude_client = ClaudeAPIClient()
                        topics = claude_client.generate_primary_topics(st.session_state.user_info)
                        st.session_state.primary_topics = topics
                        st.success("✅ 1次トピックリストを生成しました！")
                    except Exception as e:
                        st.error(f"❌ トピック生成エラー: {str(e)}")
                        st.info("💡 フォールバックデータを使用します。")
        
        with col2:
            st.subheader("2次シチュエーション詳細")
            if 'primary_topics' in st.session_state:
                selected_topic = st.selectbox(
                    "詳細化するトピックを選択",
                    st.session_state.primary_topics
                )
                
                if st.button("🔍 シチュエーション詳細生成"):
                    with st.spinner("🤖 詳細シチュエーションを生成中..."):
                        try:
                            claude_client = ClaudeAPIClient()
                            situations = claude_client.generate_detailed_situations(
                                st.session_state.user_info, selected_topic
                            )
                            st.session_state.detailed_situations = {
                                "topic": selected_topic,
                                "situations": situations
                            }
                            st.success("✅ 詳細シチュエーションを生成しました！")
                        except Exception as e:
                            st.error(f"❌ シチュエーション生成エラー: {str(e)}")
                            st.info("💡 フォールバックデータを使用します。")
        
        # 生成されたコンテンツの表示
        if 'primary_topics' in st.session_state:
            with st.expander("📋 1次トピックリスト", expanded=True):
                for i, topic in enumerate(st.session_state.primary_topics, 1):
                    st.write(f"{i}. {topic}")
        
        if 'detailed_situations' in st.session_state:
            with st.expander("🔍 詳細シチュエーション", expanded=True):
                st.write(f"**選択トピック**: {st.session_state.detailed_situations['topic']}")
                for i, situation in enumerate(st.session_state.detailed_situations['situations'], 1):
                    st.write(f"{i}. {situation}")
                    
                # 最終シチュエーション選択
                final_situation = st.selectbox(
                    "最終シチュエーションを選択",
                    st.session_state.detailed_situations['situations']
                )
                
                if st.button("✅ シチュエーション確定", type="primary"):
                    st.session_state.final_situation = final_situation
                    st.session_state.current_step = 2
                    st.success("✅ シチュエーションが確定されました！")
                    st.rerun()
    
    with tab3:
        st.markdown('<div class="step-header">📚 Step 3: 教材作成</div>', unsafe_allow_html=True)
        
        if 'final_situation' not in st.session_state:
            st.warning("⚠️ まずトピックとシチュエーションを確定してください。")
            return
        
        st.info(f"**確定シチュエーション**: {st.session_state.final_situation}")
        
        # 教材生成ボタン
        if st.button("📚 教材を生成", type="primary"):
            with st.spinner("🤖 教材を生成中..."):
                try:
                    claude_client = ClaudeAPIClient()
                    material_type = st.session_state.user_info['material_type']
                    
                    if material_type == 'ロールプレイ':
                        material = claude_client.generate_roleplay_material(
                            st.session_state.user_info, 
                            st.session_state.final_situation
                        )
                    elif material_type == 'ディスカッション':
                        material = claude_client.generate_discussion_material(
                            st.session_state.user_info,
                            st.session_state.final_situation
                        )
                    elif material_type == '表現練習':
                        material = claude_client.generate_expression_practice_material(
                            st.session_state.user_info,
                            st.session_state.final_situation
                        )
                    else:
                        st.error("❌ 未対応の教材タイプです。")
                        return
                    
                    st.session_state.generated_material = material
                    st.session_state.current_step = 3
                    st.success("✅ 教材が生成されました！")
                    
                except Exception as e:
                    st.error(f"❌ 教材生成エラー: {str(e)}")
                    st.info("💡 フォールバックデータを使用します。")
                    # フォールバック
                    if st.session_state.user_info['material_type'] == 'ロールプレイ':
                        sample_material = generate_sample_roleplay()
                    else:
                        sample_material = {"type": "エラー", "content": "教材生成に失敗しました。"}
                    st.session_state.generated_material = sample_material
        
        # 生成された教材の表示
        if 'generated_material' in st.session_state:
            display_generated_material(st.session_state.generated_material)
    
    with tab4:
        st.markdown('<div class="step-header">📤 Step 4: 出力・保存</div>', unsafe_allow_html=True)
        
        if 'generated_material' not in st.session_state:
            st.warning("⚠️ まず教材を生成してください。")
            return
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📄 Google Docs出力")
            doc_title = st.text_input(
                "ドキュメントタイトル",
                value=f"教材_{datetime.now().strftime('%Y%m%d_%H%M')}"
            )
            
            # Google Docs API接続チェック
            google_client = GoogleDocsAPIClient()
            
            if not google_client.is_available():
                st.warning("⚠️ Google Docs APIが設定されていません。")
                with st.expander("🔧 Google Docs API設定手順", expanded=False):
                    st.markdown(google_client.get_setup_instructions())
            
            if st.button("📄 Google Docsに出力", type="primary"):
                if google_client.is_available():
                    with st.spinner("🤖 Google Docsに出力中..."):
                        material_data = {
                            "user_info": st.session_state.user_info,
                            "final_situation": st.session_state.final_situation,
                            "generated_material": st.session_state.generated_material
                        }
                        
                        doc_url = google_client.create_and_write_material(doc_title, material_data)
                        
                        if doc_url:
                            st.success("✅ Google Docsに出力完了！")
                            st.markdown(f"📄 [ドキュメントを開く]({doc_url})")
                        else:
                            st.error("❌ Google Docs出力に失敗しました。")
                else:
                    st.error("❌ Google Docs API設定が必要です。上記の設定手順を参照してください。")
        
        with col2:
            st.subheader("💾 ローカル保存")
            if st.button("💾 JSONファイルで保存"):
                save_data = {
                    "user_info": st.session_state.user_info,
                    "final_situation": st.session_state.final_situation,
                    "generated_material": st.session_state.generated_material,
                    "created_at": datetime.now().isoformat()
                }
                
                filename = f"教材_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(save_data, f, ensure_ascii=False, indent=2)
                
                st.success(f"✅ {filename} に保存されました！")
                st.session_state.current_step = 4

def generate_sample_roleplay():
    """サンプルロールプレイ教材生成（後でClaude APIに置き換え）"""
    return {
        "type": "ロールプレイ",
        "model_dialogue": """
A: 田中と申します。本日はお時間をいただき、ありがとうございます。
B: こちらこそ、ありがとうございます。Smith です。よろしくお願いします。
A: 早速ですが、弊社の新しいソリューションについてご紹介させていただきたいと思います。
B: はい、ぜひお聞かせください。どのようなソリューションでしょうか？
A: こちらは業務効率を30%向上させることができるシステムです。
B: それは興味深いですね。具体的にはどのような機能があるのでしょうか？
        """,
        "useful_expressions": [
            "お時間をいただき、ありがとうございます - Thank you for taking your time",
            "早速ですが - Let me get straight to the point",
            "ご紹介させていただきたい - I would like to introduce",
            "業務効率を向上させる - improve work efficiency",
            "興味深いですね - That sounds interesting"
        ],
        "additional_questions": [
            "このシステムの導入にはどのくらいの期間が必要ですか？",
            "初期費用はどの程度でしょうか？",
            "サポート体制について教えてください。"
        ],
        "audio_script": "※音声ファイル作成用スクリプト（開発予定）"
    }

def display_generated_material(material):
    """生成された教材を表示"""
    st.subheader(f"📋 生成された教材 - {material.get('type', '教材')}")
    
    if material.get('type') == 'ロールプレイ':
        # モデルダイアログ
        with st.expander("💬 モデルダイアログ", expanded=True):
            st.text_area("会話内容", material["model_dialogue"], height=200, disabled=True, label_visibility="collapsed")
        
        # 有用表現・語彙
        with st.expander("📝 有用表現・語彙", expanded=True):
            for expr in material["useful_expressions"]:
                st.write(f"• {expr}")
        
        # 追加質問
        with st.expander("❓ 追加質問", expanded=True):
            for i, question in enumerate(material["additional_questions"], 1):
                st.write(f"{i}. {question}")
    
    elif material.get('type') == 'ディスカッション':
        # ディスカッショントピック
        with st.expander("💭 ディスカッショントピック", expanded=True):
            st.text_area("トピック内容", material["discussion_topic"], height=150, disabled=True, label_visibility="collapsed")
        
        # 狙いの説明
        with st.expander("🎯 ディスカッションの狙い", expanded=True):
            st.text_area("学習目標", material["discussion_aim"], height=100, disabled=True, label_visibility="collapsed")
        
        # ガイド質問
        with st.expander("❓ ガイド質問", expanded=True):
            for i, question in enumerate(material["guide_questions"], 1):
                st.write(f"{i}. {question}")
        
        # 有用表現・語彙
        with st.expander("📝 有用表現・語彙", expanded=True):
            for expr in material["useful_expressions"]:
                st.write(f"• {expr}")
    
    elif material.get('type') == '表現練習':
        # 図表・データ説明
        with st.expander("📊 図表・データ説明", expanded=True):
            st.text_area("データ内容", material["chart_description"], height=150, disabled=True, label_visibility="collapsed")
        
        # キーフレーズ
        with st.expander("🔑 キーフレーズ", expanded=True):
            for phrase in material["key_phrases"]:
                st.write(f"• {phrase}")
        
        # 段階的練習問題
        with st.expander("📚 段階的練習ステップ", expanded=True):
            for i, step in enumerate(material["practice_steps"], 1):
                st.write(f"**{step}**")
        
        # 追加質問
        with st.expander("❓ 追加質問", expanded=True):
            for i, question in enumerate(material["additional_questions"], 1):
                st.write(f"{i}. {question}")
    
    else:
        st.warning("⚠️ 未対応の教材タイプです。")

if __name__ == "__main__":
    main() 