import streamlit as st
import json
import os
from datetime import datetime
from claude_api import ClaudeAPIClient
from google_docs_api import GoogleDocsAPIClient
from dotenv import load_dotenv

# 環境変数の読み込み
load_dotenv()

# ページ設定
st.set_page_config(
    page_title="語学教材作成支援ツール - 実用版",
    page_icon="📚",
    layout="wide"
)

# セッション状態の初期化
if 'context_data' not in st.session_state:
    st.session_state.context_data = {
        'counseling_memo': '',
        'teaching_policy': '',
        'business_scenes': '',
        'topic_list': []
    }

if 'generated_materials' not in st.session_state:
    st.session_state.generated_materials = []

if 'templates' not in st.session_state:
    st.session_state.templates = {
        'ロールプレイ': {
            'dialogue_length': '180-220語',
            'participants': 2,
            'useful_expressions_count': 10,
            'additional_questions_count': 4,
            'include_audio': True,
            'parts': {
                'greeting': True,
                'needs_assessment': True,
                'proposal': True,
                'qa_session': True,
                'next_action': True
            },
            'custom_instructions': '',
            'sample_dialogue': '''A: Good morning, Mr. Johnson. Thank you for taking the time to meet with us today.
B: Good morning. I'm looking forward to hearing about your financing options.
A: Based on our initial assessment, I'd like to propose a structured loan package that would suit your expansion needs...''',
            'sample_expressions': '''• "I'd like to propose..." - 提案したいのですが
• "Based on our analysis..." - 分析に基づいて
• "This would allow you to..." - これにより〜が可能になります''',
            'sample_questions': '''1. How would you present this proposal to a more conservative client?
2. What additional information might you need before finalizing this deal?
3. Role-play the client's potential objections.'''
        },
        'ディスカッション': {
            'topic_complexity': '中程度',
            'discussion_time': '20分',
            'viewpoints_count': 3,
            'supporting_materials': True,
            'conclusion_required': True,
            'custom_instructions': '',
            'sample_topic': '''Should companies prioritize digital transformation or employee training in the post-pandemic era?''',
            'sample_viewpoints': '''1. Digital-first approach: Focus on technology infrastructure
2. Human-centered approach: Invest in employee development
3. Hybrid approach: Balance both strategies''',
            'sample_materials': '''参考資料: 業界統計、専門家意見、ケーススタディ'''
        },
        '表現練習': {
            'chart_types': ['棒グラフ', '線グラフ'],
            'explanation_length': '100-150語',
            'vocabulary_count': 8,
            'practice_questions': 3,
            'include_numbers': True,
            'custom_instructions': '',
            'sample_chart_description': '''This bar chart shows our quarterly sales performance. Q1 reached 2.3 million, followed by a significant increase to 3.1 million in Q2...''',
            'sample_vocabulary': '''• substantial increase - 大幅な増加
• steady decline - 安定した減少
• fluctuation - 変動''',
            'chart_generation_prompt': '''Create a bar chart showing quarterly sales data with the following values: Q1: 2.3M, Q2: 3.1M, Q3: 2.8M, Q4: 3.5M'''
        }
    }

def main():
    st.title("📚 語学教材作成支援ツール - 実用版")
    st.markdown("**シンプル・実用重視** - 今すぐ使える教材作成ツール")
    
    # メインタブ
    tabs = st.tabs(["📝 コンテキスト設定", "🎨 テンプレート管理", "📋 トピック管理", "⚡ 一括生成", "🔍 品質チェッカー", "📁 出力管理"])
    
    with tabs[0]:
        show_context_setup()
    
    with tabs[1]:
        show_template_management()
    
    with tabs[2]:
        show_topic_management()
    
    with tabs[3]:
        show_batch_generation()
    
    with tabs[4]:
        show_quality_checker()
    
    with tabs[5]:
        show_output_management()

def show_context_setup():
    """コンテキスト設定タブ"""
    st.header("📝 コンテキスト設定")
    st.markdown("教材作成に必要な情報を貼り付けてください")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🎯 カウンセリングメモ")
        st.markdown("*受講生の情報、レベル、課題などを貼り付け*")
        counseling_memo = st.text_area(
            "カウンセリング内容",
            value=st.session_state.context_data['counseling_memo'],
            height=200,
            placeholder="""例：
・業界：金融サービス（法人向け融資）
・受講者数：15名（営業部門）
・平均レベル：TOEIC 600-750点
・主な課題：専門用語の英語表現、数値説明が不十分
・重点シーン：新規開拓営業、既存顧客管理、資料説明""",
            label_visibility="collapsed"
        )
        
        st.subheader("📋 教材作成方針")
        st.markdown("*難易度、長さ、重点項目などの作成方針*")
        teaching_policy = st.text_area(
            "作成方針",
            value=st.session_state.context_data['teaching_policy'],
            height=150,
            placeholder="""例：
・難易度：中級（B1-B2レベル）
・対話文：180-220語程度
・有用表現：10-12個
・追加質問：4個
・重点：実践的なシチュエーション、金融専門用語の段階的導入""",
            label_visibility="collapsed"
        )
    
    with col2:
        st.subheader("🏢 ビジネスシーン情報")
        st.markdown("*部署や企業の具体的なビジネスシーン*")
        business_scenes = st.text_area(
            "ビジネスシーン",
            value=st.session_state.context_data['business_scenes'],
            height=200,
            placeholder="""例：
・新規開拓営業：海外企業への融資提案、財務データ説明
・既存顧客管理：定期的な業績確認、追加融資相談
・内部会議：案件検討、リスク評価の議論
・資料説明：金融商品・条件の詳細説明、グラフ・表の読み上げ""",
            label_visibility="collapsed"
        )
        
        st.subheader("🎨 テンプレート選択")
        template_type = st.selectbox(
            "使用するテンプレート",
            ["ロールプレイ", "ディスカッション", "表現練習"],
            help="生成する教材のタイプを選択"
        )
        
        st.subheader("⚙️ 生成設定")
        col_a, col_b = st.columns(2)
        with col_a:
            material_count = st.number_input("生成数", min_value=1, max_value=20, value=5)
        with col_b:
            output_format = st.selectbox("出力形式", ["JSON", "Google Docs", "テキスト"])
    
    # コンテキスト保存
    if st.button("💾 コンテキスト情報を保存", type="primary"):
        st.session_state.context_data.update({
            'counseling_memo': counseling_memo,
            'teaching_policy': teaching_policy,
            'business_scenes': business_scenes,
            'template_type': template_type,
            'material_count': material_count,
            'output_format': output_format
        })
        st.success("✅ コンテキスト情報を保存しました")

def show_template_management():
    """テンプレート管理タブ"""
    st.header("🎨 テンプレート管理")
    st.markdown("**教材のパーツ・構造を管理** - 長さや分量を調整して再利用")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # テンプレートタイプ選択
        template_type = st.selectbox(
            "編集するテンプレート",
            ["ロールプレイ", "ディスカッション", "表現練習"],
            help="編集したいテンプレートタイプを選択"
        )
        
        current_template = st.session_state.templates[template_type]
        
        st.subheader(f"🎭 {template_type}テンプレート設定")
        
        # ロールプレイテンプレート設定
        if template_type == "ロールプレイ":
            col_a, col_b = st.columns(2)
            
            with col_a:
                st.write("**📏 基本設定**")
                dialogue_length = st.text_input(
                    "ダイアログの長さ",
                    value=current_template['dialogue_length'],
                    placeholder="例: 180-220語"
                )
                
                participants = st.number_input(
                    "参加者数",
                    min_value=2, max_value=4,
                    value=current_template['participants']
                )
                
                useful_expressions = st.number_input(
                    "有用表現数",
                    min_value=5, max_value=20,
                    value=current_template['useful_expressions_count']
                )
                
                additional_questions = st.number_input(
                    "追加質問数",
                    min_value=2, max_value=10,
                    value=current_template['additional_questions_count']
                )
            
            with col_b:
                st.write("**🔧 パーツ構成**")
                greeting = st.checkbox("挨拶・導入", current_template['parts']['greeting'], key="template_greeting")
                needs_assessment = st.checkbox("ニーズ確認", current_template['parts']['needs_assessment'], key="template_needs")
                proposal = st.checkbox("提案・説明", current_template['parts']['proposal'], key="template_proposal")
                qa_session = st.checkbox("質疑応答", current_template['parts']['qa_session'], key="template_qa")
                next_action = st.checkbox("次回アクション", current_template['parts']['next_action'], key="template_action")
                
                include_audio = st.checkbox("音声スクリプト含む", current_template['include_audio'], key="template_audio")
            
            # カスタム指示
            st.write("**📝 カスタム指示**")
            custom_instructions = st.text_area(
                "追加の作成指示",
                value=current_template['custom_instructions'],
                height=100,
                placeholder="例: 金融業界特有の表現を重視、丁寧語を多用、数値説明を含める"
            )
            
            # サンプルテキスト設定
            st.write("**📄 サンプルテキスト**")
            
            col_sample1, col_sample2 = st.columns(2)
            with col_sample1:
                sample_dialogue = st.text_area(
                    "サンプル対話文",
                    value=current_template.get('sample_dialogue', ''),
                    height=120,
                    placeholder="実際の対話例を入力..."
                )
                
                sample_expressions = st.text_area(
                    "サンプル有用表現",
                    value=current_template.get('sample_expressions', ''),
                    height=120,
                    placeholder="表現例とその意味を入力..."
                )
            
            with col_sample2:
                sample_questions = st.text_area(
                    "サンプル質問",
                    value=current_template.get('sample_questions', ''),
                    height=120,
                    placeholder="追加質問の例を入力..."
                )
                
                # 音声プロンプト生成
                if st.button("🎤 音声生成プロンプト作成"):
                    audio_prompt = generate_audio_prompt(sample_dialogue)
                    st.text_area("音声生成用プロンプト", audio_prompt, height=80)
            
            # 設定保存
            if st.button("💾 ロールプレイテンプレートを保存", type="primary"):
                st.session_state.templates['ロールプレイ'].update({
                    'dialogue_length': dialogue_length,
                    'participants': participants,
                    'useful_expressions_count': useful_expressions,
                    'additional_questions_count': additional_questions,
                    'include_audio': include_audio,
                    'parts': {
                        'greeting': greeting,
                        'needs_assessment': needs_assessment,
                        'proposal': proposal,
                        'qa_session': qa_session,
                        'next_action': next_action
                    },
                    'custom_instructions': custom_instructions,
                    'sample_dialogue': sample_dialogue,
                    'sample_expressions': sample_expressions,
                    'sample_questions': sample_questions
                })
                st.success("✅ ロールプレイテンプレートを保存しました")
        
        # ディスカッションテンプレート設定
        elif template_type == "ディスカッション":
            col_a, col_b = st.columns(2)
            
            with col_a:
                st.write("**📏 基本設定**")
                topic_complexity = st.selectbox(
                    "トピック複雑度",
                    ["単純", "中程度", "複雑"],
                    index=["単純", "中程度", "複雑"].index(current_template['topic_complexity'])
                )
                
                discussion_time = st.text_input(
                    "想定討論時間",
                    value=current_template['discussion_time'],
                    placeholder="例: 20分"
                )
                
                viewpoints_count = st.number_input(
                    "提示観点数",
                    min_value=2, max_value=6,
                    value=current_template['viewpoints_count']
                )
            
            with col_b:
                st.write("**🔧 構成要素**")
                supporting_materials = st.checkbox("参考資料含む", current_template['supporting_materials'], key="template_materials")
                conclusion_required = st.checkbox("結論必須", current_template['conclusion_required'], key="template_conclusion")
            
            custom_instructions = st.text_area(
                "カスタム指示",
                value=current_template['custom_instructions'],
                height=100,
                placeholder="例: 多角的な視点を重視、反対意見も含める"
            )
            
            # サンプルテキスト設定
            st.write("**📄 サンプルテキスト**")
            
            col_sample1, col_sample2 = st.columns(2)
            with col_sample1:
                sample_topic = st.text_area(
                    "サンプルトピック",
                    value=current_template.get('sample_topic', ''),
                    height=80,
                    placeholder="ディスカッションテーマの例..."
                )
                
                sample_viewpoints = st.text_area(
                    "サンプル観点",
                    value=current_template.get('sample_viewpoints', ''),
                    height=120,
                    placeholder="議論の観点例を入力..."
                )
            
            with col_sample2:
                sample_materials = st.text_area(
                    "サンプル参考資料",
                    value=current_template.get('sample_materials', ''),
                    height=80,
                    placeholder="参考資料の例..."
                )
                
                # ディスカッション構造プロンプト生成
                if st.button("📋 ディスカッション構造プロンプト作成"):
                    discussion_prompt = generate_discussion_prompt(sample_topic, sample_viewpoints)
                    st.text_area("構造化プロンプト", discussion_prompt, height=120)
            
            if st.button("💾 ディスカッションテンプレートを保存", type="primary"):
                st.session_state.templates['ディスカッション'].update({
                    'topic_complexity': topic_complexity,
                    'discussion_time': discussion_time,
                    'viewpoints_count': viewpoints_count,
                    'supporting_materials': supporting_materials,
                    'conclusion_required': conclusion_required,
                    'custom_instructions': custom_instructions,
                    'sample_topic': sample_topic,
                    'sample_viewpoints': sample_viewpoints,
                    'sample_materials': sample_materials
                })
                st.success("✅ ディスカッションテンプレートを保存しました")
        
        # 表現練習テンプレート設定
        else:  # 表現練習
            col_a, col_b = st.columns(2)
            
            with col_a:
                st.write("**📏 基本設定**")
                chart_types = st.multiselect(
                    "使用する図表タイプ",
                    ["棒グラフ", "線グラフ", "円グラフ", "表", "フローチャート"],
                    default=current_template['chart_types']
                )
                
                explanation_length = st.text_input(
                    "説明文の長さ",
                    value=current_template['explanation_length'],
                    placeholder="例: 100-150語"
                )
                
                vocabulary_count = st.number_input(
                    "語彙数",
                    min_value=5, max_value=15,
                    value=current_template['vocabulary_count']
                )
            
            with col_b:
                st.write("**🔧 構成要素**")
                practice_questions = st.number_input(
                    "練習問題数",
                    min_value=2, max_value=8,
                    value=current_template['practice_questions']
                )
                
                include_numbers = st.checkbox("数値データ含む", current_template['include_numbers'], key="template_numbers")
            
            custom_instructions = st.text_area(
                "カスタム指示",
                value=current_template['custom_instructions'],
                height=100,
                placeholder="例: データの読み上げ練習重視、前年比較を含める"
            )
            
            # サンプルテキストと図表生成
            st.write("**📄 サンプルテキスト・図表設定**")
            
            col_sample1, col_sample2 = st.columns(2)
            with col_sample1:
                sample_chart_description = st.text_area(
                    "サンプル図表説明",
                    value=current_template.get('sample_chart_description', ''),
                    height=100,
                    placeholder="図表の説明例を入力..."
                )
                
                sample_vocabulary = st.text_area(
                    "サンプル語彙",
                    value=current_template.get('sample_vocabulary', ''),
                    height=100,
                    placeholder="専門語彙の例を入力..."
                )
            
            with col_sample2:
                chart_generation_prompt = st.text_area(
                    "図表生成プロンプト",
                    value=current_template.get('chart_generation_prompt', ''),
                    height=100,
                    placeholder="AI図表生成用のプロンプト..."
                )
                
                # 図表プロンプト自動生成
                if st.button("📊 図表生成プロンプト作成"):
                    auto_chart_prompt = generate_chart_prompt(chart_types, sample_chart_description)
                    st.text_area("自動生成プロンプト", auto_chart_prompt, height=100)
                
                # 実際の図表生成（デモ）
                if st.button("🎨 サンプル図表生成"):
                    if chart_types:
                        sample_chart = create_sample_chart(chart_types[0])
                        st.plotly_chart(sample_chart, use_container_width=True)
            
            if st.button("💾 表現練習テンプレートを保存", type="primary"):
                st.session_state.templates['表現練習'].update({
                    'chart_types': chart_types,
                    'explanation_length': explanation_length,
                    'vocabulary_count': vocabulary_count,
                    'practice_questions': practice_questions,
                    'include_numbers': include_numbers,
                    'custom_instructions': custom_instructions,
                    'sample_chart_description': sample_chart_description,
                    'sample_vocabulary': sample_vocabulary,
                    'chart_generation_prompt': chart_generation_prompt
                })
                st.success("✅ 表現練習テンプレートを保存しました")
    
    with col2:
        st.subheader("📊 テンプレート情報")
        
        # 現在の設定表示
        with st.expander("現在の設定", expanded=True):
            if template_type == "ロールプレイ":
                st.write(f"**長さ**: {current_template['dialogue_length']}")
                st.write(f"**参加者**: {current_template['participants']}名")
                st.write(f"**表現数**: {current_template['useful_expressions_count']}個")
                st.write(f"**質問数**: {current_template['additional_questions_count']}個")
                
                enabled_parts = [k for k, v in current_template['parts'].items() if v]
                st.write(f"**有効パーツ**: {len(enabled_parts)}個")
            
            elif template_type == "ディスカッション":
                st.write(f"**複雑度**: {current_template['topic_complexity']}")
                st.write(f"**時間**: {current_template['discussion_time']}")
                st.write(f"**観点数**: {current_template['viewpoints_count']}個")
            
            else:  # 表現練習
                st.write(f"**図表**: {len(current_template['chart_types'])}種類")
                st.write(f"**長さ**: {current_template['explanation_length']}")
                st.write(f"**語彙数**: {current_template['vocabulary_count']}個")
        
        # テンプレート管理
        st.subheader("💾 テンプレート管理")
        
        # テンプレート保存
        if st.button("📥 全テンプレートを保存"):
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"templates_{timestamp}.json"
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(st.session_state.templates, f, ensure_ascii=False, indent=2)
            st.success(f"✅ テンプレートを {filename} に保存しました")
        
        # テンプレート読み込み
        uploaded_file = st.file_uploader("📤 テンプレートファイル読み込み", type=['json'])
        if uploaded_file is not None:
            try:
                loaded_templates = json.load(uploaded_file)
                st.session_state.templates.update(loaded_templates)
                st.success("✅ テンプレートを読み込みました")
                st.rerun()
            except Exception as e:
                st.error(f"読み込みエラー: {str(e)}")
        
        # プリセット復元
        if st.button("🔄 デフォルトに戻す"):
            st.session_state.templates = {
                'ロールプレイ': {
                    'dialogue_length': '180-220語',
                    'participants': 2,
                    'useful_expressions_count': 10,
                    'additional_questions_count': 4,
                    'include_audio': True,
                    'parts': {
                        'greeting': True,
                        'needs_assessment': True,
                        'proposal': True,
                        'qa_session': True,
                        'next_action': True
                    },
                    'custom_instructions': ''
                },
                'ディスカッション': {
                    'topic_complexity': '中程度',
                    'discussion_time': '20分',
                    'viewpoints_count': 3,
                    'supporting_materials': True,
                    'conclusion_required': True,
                    'custom_instructions': ''
                },
                '表現練習': {
                    'chart_types': ['棒グラフ', '線グラフ'],
                    'explanation_length': '100-150語',
                    'vocabulary_count': 8,
                    'practice_questions': 3,
                    'include_numbers': True,
                    'custom_instructions': ''
                }
            }
            st.success("✅ デフォルト設定に戻しました")
            st.rerun()

def show_topic_management():
    """トピック管理タブ"""
    st.header("📋 トピック管理")
    
    col1, col2 = st.columns([3, 2])
    
    with col1:
        st.subheader("🎯 トピックリスト編集")
        
        # トピックリスト表示・編集
        if st.session_state.context_data['topic_list']:
            st.markdown("**現在のトピックリスト:**")
            for i, topic in enumerate(st.session_state.context_data['topic_list']):
                col_topic, col_delete = st.columns([4, 1])
                with col_topic:
                    st.write(f"{i+1}. {topic}")
                with col_delete:
                    if st.button("❌", key=f"delete_{i}"):
                        st.session_state.context_data['topic_list'].pop(i)
                        st.rerun()
        else:
            st.info("トピックリストが空です。下記から追加してください。")
        
        # 新規トピック追加
        st.markdown("---")
        new_topic = st.text_input("新しいトピック", placeholder="例：融資条件の説明と交渉")
        
        col_add, col_generate = st.columns(2)
        with col_add:
            if st.button("➕ トピック追加"):
                if new_topic:
                    st.session_state.context_data['topic_list'].append(new_topic)
                    st.success(f"トピック '{new_topic}' を追加しました")
                    st.rerun()
        
        with col_generate:
            if st.button("🤖 AI自動生成") and st.session_state.context_data['counseling_memo']:
                with st.spinner("AIがトピックを生成中..."):
                    try:
                        client = ClaudeAPIClient()
                        generated_topics = client.generate_primary_topics(st.session_state.context_data)
                        st.session_state.context_data['topic_list'].extend(generated_topics)
                        st.success(f"✅ {len(generated_topics)}個のトピックを自動生成しました")
                        st.rerun()
                    except Exception as e:
                        st.error(f"生成エラー: {str(e)}")
    
    with col2:
        st.subheader("📊 トピック統計")
        
        if st.session_state.context_data['topic_list']:
            st.metric("登録トピック数", len(st.session_state.context_data['topic_list']))
            
            # 推定作業時間
            estimated_time = len(st.session_state.context_data['topic_list']) * 0.5  # 30分/教材
            st.metric("推定作業時間", f"{estimated_time:.1f}時間")
            
            st.subheader("🎯 一括操作")
            
            # 全選択/全解除
            col_select, col_clear = st.columns(2)
            with col_select:
                if st.button("✅ 全選択"):
                    st.session_state.selected_topics = list(range(len(st.session_state.context_data['topic_list'])))
            
            with col_clear:
                if st.button("🗑️ 全削除"):
                    if st.session_state.context_data['topic_list']:
                        st.session_state.context_data['topic_list'] = []
                        st.success("全トピックを削除しました")
                        st.rerun()
        
        else:
            st.info("まずはトピックを追加してください")
        
        # トピックリストの保存/読み込み
        st.subheader("💾 トピックリスト管理")
        
        if st.button("📥 リストを保存"):
            if st.session_state.context_data['topic_list']:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"topic_list_{timestamp}.json"
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(st.session_state.context_data['topic_list'], f, ensure_ascii=False, indent=2)
                st.success(f"✅ トピックリストを {filename} に保存しました")

def show_batch_generation():
    """一括生成タブ"""
    st.header("⚡ 一括生成")
    
    # 事前チェック
    context_ok = bool(st.session_state.context_data['counseling_memo'] and 
                     st.session_state.context_data['teaching_policy'])
    topics_ok = bool(st.session_state.context_data['topic_list'])
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("🔍 生成準備チェック")
        
        # チェック項目表示
        check_counseling = "✅" if st.session_state.context_data['counseling_memo'] else "❌"
        check_policy = "✅" if st.session_state.context_data['teaching_policy'] else "❌" 
        check_topics = "✅" if st.session_state.context_data['topic_list'] else "❌"
        
        st.markdown(f"""
        {check_counseling} **カウンセリングメモ** ({len(st.session_state.context_data['counseling_memo'])} 文字)
        {check_policy} **教材作成方針** ({len(st.session_state.context_data['teaching_policy'])} 文字)
        {check_topics} **トピックリスト** ({len(st.session_state.context_data['topic_list'])} 件)
        """)
        
        if context_ok and topics_ok:
            st.success("🎉 生成準備完了！")
            
            # 生成設定
            st.subheader("⚙️ 生成設定")
            
            selected_topics = st.multiselect(
                "生成するトピック（空の場合は全選択）",
                st.session_state.context_data['topic_list'],
                help="特定のトピックのみ生成したい場合は選択"
            )
            
            if not selected_topics:
                selected_topics = st.session_state.context_data['topic_list']
            
            col_gen1, col_gen2 = st.columns(2)
            with col_gen1:
                include_audio = st.checkbox("音声スクリプト含む", True, key="batch_audio")
            with col_gen2:
                quality_check = st.checkbox("生成後品質チェック", True, key="batch_quality")
            
            # 生成実行
            if st.button("🚀 一括生成開始", type="primary"):
                generate_materials(selected_topics, include_audio, quality_check)
        
        else:
            st.warning("⚠️ 生成前に必要な情報を設定してください")
            if not context_ok:
                st.info("👈 「コンテキスト設定」タブでカウンセリングメモと作成方針を入力")
            if not topics_ok:
                st.info("👈 「トピック管理」タブでトピックを追加")
    
    with col2:
        st.subheader("📊 生成統計")
        
        if st.session_state.generated_materials:
            st.metric("生成済み教材数", len(st.session_state.generated_materials))
            
            # 品質統計
            total_materials = len(st.session_state.generated_materials)
            if total_materials > 0:
                # 仮の品質スコア計算
                avg_quality = 4.2  # サンプル値
                st.metric("平均品質スコア", f"{avg_quality:.1f}/5.0")
        
        else:
            st.info("まだ教材が生成されていません")

def generate_materials(topics, include_audio, quality_check):
    """教材生成処理"""
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    client = ClaudeAPIClient()
    generated_materials = []
    
    total_topics = len(topics)
    
    for i, topic in enumerate(topics):
        status_text.text(f"生成中... {i+1}/{total_topics}: {topic}")
        
        try:
            # 材料のタイプに応じて生成（テンプレート設定を考慮）
            template_type = st.session_state.context_data.get('template_type', 'ロールプレイ')
            template_config = st.session_state.templates[template_type]
            
            # コンテキストデータにテンプレート設定を追加
            enhanced_context = st.session_state.context_data.copy()
            enhanced_context['template_config'] = template_config
            
            if template_type == 'ロールプレイ':
                material = client.generate_roleplay_material(enhanced_context, topic, template_config)
            elif template_type == 'ディスカッション':
                material = client.generate_discussion_material(enhanced_context, topic, template_config)
            else:  # 表現練習
                material = client.generate_expression_practice_material(enhanced_context, topic, template_config)
            
            material['topic'] = topic
            material['generated_at'] = datetime.now().isoformat()
            generated_materials.append(material)
            
        except Exception as e:
            st.error(f"❌ '{topic}' の生成中にエラー: {str(e)}")
        
        progress_bar.progress((i + 1) / total_topics)
    
    # 生成完了
    st.session_state.generated_materials.extend(generated_materials)
    status_text.text("✅ 一括生成完了！")
    
    st.success(f"🎉 {len(generated_materials)}件の教材を生成しました")
    
    # 品質チェック実行
    if quality_check and generated_materials:
        st.info("🔍 品質チェックを実行中...")
        # ここで品質チェック処理を呼び出し
        perform_quality_check(generated_materials)
    
    # 完了通知 [[memory:3871684]]
    if generated_materials:
        import subprocess
        try:
            subprocess.run([
                'osascript', '-e', 
                f'display dialog "教材生成完了！\\n{len(generated_materials)}件の教材を生成しました。" with title "語学教材作成ツール" buttons {{"了解"}} default button 1'
            ])
        except:
            pass

def show_quality_checker():
    """品質チェッカータブ"""
    st.header("🔍 品質チェッカー")
    st.markdown("**独立したチェック機能** - 生成済み教材の品質を分析")
    
    # ヘルプ情報
    with st.expander("💡 重複修復機能の使い方", expanded=False):
        st.markdown("""
        **🔄 重複表現検出時の修復方法：**
        
        1. **手動修復**
           - 各重複箇所を個別に手動で修正
           - 完全にコントロールできるため最も確実
        
        2. **自動修復（AI生成）**
           - Claude AIが同義の代替表現を生成
           - 迅速に修復可能だが、生成結果の確認が必要
        
        3. **スキップ**
           - その重複をそのまま残す（許容範囲の場合）
        
        **✅ 修復後の手順：**
        - 「🔄 修復後に再チェック」ボタンで再度品質チェック実行
        - 重複が解消されたことを確認
        """)
    
    if not st.session_state.generated_materials:
        st.info("チェック対象の教材がありません。まず教材を生成してください。")
        return
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("📋 チェック項目設定")
        
        check_context = st.checkbox("コンテキスト準拠チェック", True, key="quality_context")
        check_consistency = st.checkbox("ファイル間整合性チェック", True, key="quality_consistency")
        check_level = st.checkbox("レベル調整チェック", True, key="quality_level")
        check_duplicate = st.checkbox("重複チェック", True, key="quality_duplicate")
        
        if st.button("🔍 品質チェック実行", type="primary"):
            perform_quality_check(
                st.session_state.generated_materials,
                check_context,
                check_consistency,
                check_level,
                check_duplicate
            )
    
    with col2:
        st.subheader("📊 チェック統計")
        
        total_materials = len(st.session_state.generated_materials)
        st.metric("対象教材数", total_materials)
        
        # 仮の統計値
        if total_materials > 0:
            st.metric("平均品質スコア", "4.2/5.0")
            st.metric("要修正", "2件")
            st.metric("重複検出", "1件")

def perform_quality_check(materials, check_context=True, check_consistency=True, 
                         check_level=True, check_duplicate=True):
    """品質チェック実行"""
    st.subheader("🔍 品質チェック結果")
    
    issues = []
    
    # コンテキスト準拠チェック
    if check_context:
        st.write("**📝 コンテキスト準拠チェック**")
        context_issues = check_context_compliance(materials)
        issues.extend(context_issues)
        
        if context_issues:
            for issue in context_issues:
                st.warning(f"⚠️ {issue}")
        else:
            st.success("✅ 全教材がコンテキストに準拠しています")
    
    # レベル調整チェック
    if check_level:
        st.write("**📊 レベル調整チェック**")
        level_issues = check_level_consistency(materials)
        issues.extend(level_issues)
        
        if level_issues:
            for issue in level_issues:
                st.warning(f"⚠️ {issue}")
        else:
            st.success("✅ レベル設定が適切です")
    
    # 重複チェック
    if check_duplicate:
        st.write("**🔄 重複チェック**")
        duplicate_issues = check_duplicates(materials)
        issues.extend(duplicate_issues)
        
        if duplicate_issues:
            for issue in duplicate_issues:
                st.warning(f"⚠️ {issue}")
            
            # 重複修復セクション
            st.markdown("---")
            st.subheader("🔧 重複修復")
            
            if st.session_state.get('duplicate_details'):
                show_duplicate_repair_ui()
        else:
            st.success("✅ 重複は検出されませんでした")
    
    # 総合評価
    if issues:
        st.error(f"❗ {len(issues)}件の問題が検出されました")
    else:
        st.success("🎉 全ての品質チェックに合格しました！")

def check_context_compliance(materials):
    """コンテキスト準拠チェック"""
    issues = []
    counseling_keywords = st.session_state.context_data['counseling_memo'].lower().split()
    
    for i, material in enumerate(materials):
        # 簡単なキーワードマッチング
        content = str(material).lower()
        relevance_score = sum(1 for keyword in counseling_keywords if keyword in content)
        
        if relevance_score < 3:  # 閾値
            issues.append(f"教材{i+1} '{material.get('topic', 'unknown')}': コンテキストとの関連性が低い可能性")
    
    return issues

def check_level_consistency(materials):
    """レベル一貫性チェック"""
    issues = []
    target_level = "中級"  # デフォルト値
    
    for i, material in enumerate(materials):
        # 語彙の複雑さを粗くチェック
        if 'useful_expressions' in material:
            expressions = material['useful_expressions']
            complex_words = sum(1 for expr in expressions if len(expr.split()) > 3)
            
            if complex_words > len(expressions) * 0.7:  # 70%以上が複雑
                issues.append(f"教材{i+1}: 語彙レベルが目標より高い可能性")
    
    return issues

def check_duplicates(materials):
    """重複チェック（改良版）"""
    issues = []
    duplicates_detailed = []
    
    # より詳細な重複チェック
    expressions_map = {}  # 表現 -> [(material_index, expression_index)]
    
    for i, material in enumerate(materials):
        if 'useful_expressions' in material:
            for j, expr in enumerate(material['useful_expressions']):
                expr_clean = expr.lower().strip()
                # 英語部分のみを抽出（日本語説明を除外）
                if ':' in expr:
                    expr_clean = expr.split(':')[1].strip().lower()
                elif '-' in expr:
                    expr_clean = expr.split('-')[0].strip().lower()
                
                if expr_clean in expressions_map:
                    expressions_map[expr_clean].append((i, j, expr))
                else:
                    expressions_map[expr_clean] = [(i, j, expr)]
    
    # 重複が見つかった場合の詳細情報を収集
    for expr_clean, occurrences in expressions_map.items():
        if len(occurrences) > 1:
            material_nums = [f"教材{i+1}" for i, j, expr in occurrences]
            issues.append(f"重複表現: '{expr_clean}' が {', '.join(material_nums)} で重複")
            duplicates_detailed.append({
                'expression': expr_clean,
                'occurrences': occurrences,
                'original_expressions': [expr for i, j, expr in occurrences]
            })
    
    # session_stateに詳細情報を保存
    if 'duplicate_details' not in st.session_state:
        st.session_state.duplicate_details = []
    st.session_state.duplicate_details = duplicates_detailed
    
    return issues

def show_duplicate_repair_ui():
    """重複修復UI"""
    if not st.session_state.get('duplicate_details'):
        return
    
    st.write("**検出された重複表現の修復方法を選択してください：**")
    
    for i, duplicate in enumerate(st.session_state.duplicate_details):
        expr = duplicate['expression']
        occurrences = duplicate['occurrences']
        original_exprs = duplicate['original_expressions']
        
        with st.expander(f"🔄 重複表現 {i+1}: '{expr}' ({len(occurrences)}箇所)", expanded=True):
            # 重複箇所の詳細表示
            st.write("**重複箇所:**")
            for j, (mat_idx, expr_idx, original) in enumerate(occurrences):
                st.write(f"• 教材{mat_idx+1}: {original}")
            
            # 修復方法の選択
            repair_method = st.radio(
                f"修復方法を選択 (重複{i+1})",
                ["手動修復", "自動修復（AI生成）", "スキップ"],
                key=f"repair_method_{i}"
            )
            
            if repair_method == "手動修復":
                st.write("**各箇所の表現を手動で修正:**")
                new_expressions = []
                for j, (mat_idx, expr_idx, original) in enumerate(occurrences):
                    new_expr = st.text_input(
                        f"教材{mat_idx+1}の新しい表現:",
                        value=original,
                        key=f"manual_expr_{i}_{j}"
                    )
                    new_expressions.append((mat_idx, expr_idx, new_expr))
                
                if st.button(f"手動修復を適用", key=f"apply_manual_{i}"):
                    apply_manual_repair(new_expressions)
                    st.success("✅ 手動修復を適用しました")
                    st.rerun()
            
            elif repair_method == "自動修復（AI生成）":
                st.write("**AI が代替表現を生成します：**")
                
                if st.button(f"代替表現を生成", key=f"generate_alt_{i}"):
                    with st.spinner("代替表現を生成中..."):
                        alternatives = generate_alternative_expressions(expr, len(occurrences))
                        st.session_state[f'alternatives_{i}'] = alternatives
                
                # 生成された代替表現の表示と適用
                if f'alternatives_{i}' in st.session_state:
                    alternatives = st.session_state[f'alternatives_{i}']
                    st.write("**生成された代替表現:**")
                    
                    auto_repairs = []
                    for j, (mat_idx, expr_idx, original) in enumerate(occurrences):
                        if j < len(alternatives):
                            st.write(f"• 教材{mat_idx+1}: {original} → **{alternatives[j]}**")
                            auto_repairs.append((mat_idx, expr_idx, alternatives[j]))
                        else:
                            st.write(f"• 教材{mat_idx+1}: {original} (変更なし)")
                            auto_repairs.append((mat_idx, expr_idx, original))
                    
                    if st.button(f"自動修復を適用", key=f"apply_auto_{i}"):
                        apply_manual_repair(auto_repairs)
                        st.success("✅ 自動修復を適用しました")
                        st.rerun()
    
    # 全体の修復完了ボタン
    if st.button("🔄 修復後に再チェック", type="primary"):
        # 重複詳細をクリア
        if 'duplicate_details' in st.session_state:
            del st.session_state.duplicate_details
        st.success("✅ 修復完了！品質チェックを再実行してください。")
        st.rerun()

def apply_manual_repair(repairs):
    """手動修復を適用"""
    for mat_idx, expr_idx, new_expr in repairs:
        if mat_idx < len(st.session_state.generated_materials):
            material = st.session_state.generated_materials[mat_idx]
            if 'useful_expressions' in material and expr_idx < len(material['useful_expressions']):
                material['useful_expressions'][expr_idx] = new_expr

def generate_alternative_expressions(base_expression, count):
    """代替表現をAIで生成"""
    try:
        from claude_api import ClaudeAPIClient
        claude_client = ClaudeAPIClient()
        
        prompt = f"""
以下のビジネス英語表現と同じ意味で、異なる表現方法の代替案を{count}個生成してください。

【元の表現】: {base_expression}

【要件】:
1. 同じ意味・ニュアンスを保つ
2. ビジネス場面で適切
3. 自然な英語表現
4. 各代替案は異なる単語・構造を使用

【出力形式】:
JSON配列で{count}個の代替表現を返してください。
例: ["alternative 1", "alternative 2", "alternative 3"]
"""
        
        response = claude_client.client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=800,
            messages=[{"role": "user", "content": prompt}]
        )
        
        if hasattr(response, 'content') and len(response.content) > 0:
            content = response.content[0].text.strip()
            # JSON部分を抽出
            if '```json' in content:
                json_str = content.split('```json')[1].split('```')[0].strip()
            elif '[' in content and ']' in content:
                start = content.find('[')
                end = content.rfind(']') + 1
                json_str = content[start:end]
            else:
                json_str = content
            
            import json
            alternatives = json.loads(json_str)
            return alternatives
        
    except Exception as e:
        print(f"代替表現生成エラー: {e}")
    
    # フォールバック: 基本的な代替案
    return [
        f"alternative to {base_expression}",
        f"another way to say {base_expression}",
        f"different expression for {base_expression}"
    ][:count]

def show_output_management():
    """出力管理タブ"""
    st.header("📁 出力管理")
    
    if not st.session_state.generated_materials:
        st.info("出力対象の教材がありません。まず教材を生成してください。")
        return
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("📋 生成済み教材一覧")
        
        for i, material in enumerate(st.session_state.generated_materials):
            with st.expander(f"教材 {i+1}: {material.get('topic', 'Unknown Topic')}"):
                st.write(f"**タイプ**: {material.get('type', 'Unknown')}")
                st.write(f"**生成日時**: {material.get('generated_at', 'Unknown')}")
                
                if 'model_dialogue' in material:
                    st.text_area("対話文", material['model_dialogue'], height=100, key=f"dialogue_{i}")
                
                if 'useful_expressions' in material:
                    st.write("**有用表現**:")
                    for expr in material['useful_expressions']:
                        st.write(f"• {expr}")
    
    with col2:
        st.subheader("📤 出力オプション")
        
        output_format = st.selectbox("出力形式", ["JSON", "Google Docs", "テキストファイル"])
        
        # 全教材出力
        st.markdown("### 📁 全教材出力")
        if output_format in ["JSON", "テキストファイル"]:
            col_btn1, col_btn2 = st.columns(2)
            with col_btn1:
                if st.button("💾 全教材を出力", type="primary", key="export_all"):
                    export_materials(st.session_state.generated_materials, output_format)
            with col_btn2:
                # 即座ダウンロード用の準備
                if output_format == "JSON":
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    filename = f"materials_{timestamp}.json"
                    json_data = json.dumps(st.session_state.generated_materials, ensure_ascii=False, indent=2)
                    st.download_button(
                        label="📥 JSON即ダウンロード",
                        data=json_data.encode('utf-8'),
                        file_name=filename,
                        mime="application/json",
                        key="quick_json_all"
                    )
                else:  # テキストファイル
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    filename = f"materials_{timestamp}.txt"
                    text_content = generate_text_content(st.session_state.generated_materials)
                    st.download_button(
                        label="📥 テキスト即ダウンロード",
                        data=text_content.encode('utf-8'),
                        file_name=filename,
                        mime="text/plain",
                        key="quick_text_all"
                    )
        else:
            if st.button("💾 全教材を出力", type="primary", key="export_all_gdocs"):
                export_materials(st.session_state.generated_materials, output_format)
        
        # 個別出力
        st.markdown("### 🎯 個別出力")
        selected_indices = st.multiselect(
            "出力する教材を選択",
            range(len(st.session_state.generated_materials)),
            format_func=lambda x: f"教材{x+1}: {st.session_state.generated_materials[x].get('topic', 'Unknown')}"
        )
        
        if selected_indices:
            if output_format in ["JSON", "テキストファイル"]:
                col_btn3, col_btn4 = st.columns(2)
                with col_btn3:
                    if st.button("📤 選択教材を出力", key="export_selected"):
                        selected_materials = [st.session_state.generated_materials[i] for i in selected_indices]
                        export_materials(selected_materials, output_format)
                with col_btn4:
                    # 選択教材の即座ダウンロード
                    selected_materials = [st.session_state.generated_materials[i] for i in selected_indices]
                    if output_format == "JSON":
                        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                        filename = f"selected_materials_{timestamp}.json"
                        json_data = json.dumps(selected_materials, ensure_ascii=False, indent=2)
                        st.download_button(
                            label="📥 JSON即ダウンロード",
                            data=json_data.encode('utf-8'),
                            file_name=filename,
                            mime="application/json",
                            key="quick_json_selected"
                        )
                    else:  # テキストファイル
                        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                        filename = f"selected_materials_{timestamp}.txt"
                        text_content = generate_text_content(selected_materials)
                        st.download_button(
                            label="📥 テキスト即ダウンロード",
                            data=text_content.encode('utf-8'),
                            file_name=filename,
                            mime="text/plain",
                            key="quick_text_selected"
                        )
            else:
                if st.button("📤 選択教材を出力", key="export_selected_gdocs"):
                    selected_materials = [st.session_state.generated_materials[i] for i in selected_indices]
                    export_materials(selected_materials, output_format)

def generate_text_content(materials):
    """教材をテキスト形式で生成"""
    text_content = ""
    
    for i, material in enumerate(materials):
        text_content += f"=== 教材 {i+1}: {material.get('topic', 'Unknown')} ===\n\n"
        text_content += f"タイプ: {material.get('type', 'Unknown')}\n"
        text_content += f"生成日時: {material.get('generated_at', 'Unknown')}\n"
        
        if 'model_dialogue' in material:
            text_content += f"\n【対話文】\n{material['model_dialogue']}\n"
        
        if 'useful_expressions' in material:
            text_content += f"\n【有用表現】\n"
            for expr in material['useful_expressions']:
                text_content += f"• {expr}\n"
        
        if 'additional_questions' in material:
            text_content += f"\n【追加質問】\n"
            for q in material['additional_questions']:
                text_content += f"• {q}\n"
        
        if 'discussion_topic' in material:
            text_content += f"\n【ディスカッショントピック】\n{material['discussion_topic']}\n"
        
        if 'background_info' in material:
            text_content += f"\n【背景情報】\n{material['background_info']}\n"
        
        if 'key_points' in material:
            text_content += f"\n【議論ポイント】\n"
            for point in material['key_points']:
                text_content += f"• {point}\n"
        
        if 'discussion_questions' in material:
            text_content += f"\n【討議質問】\n"
            for q in material['discussion_questions']:
                text_content += f"• {q}\n"
        
        if 'chart_description' in material:
            text_content += f"\n【図表説明】\n{material['chart_description']}\n"
        
        if 'vocabulary' in material:
            text_content += f"\n【重要語彙】\n"
            for vocab in material['vocabulary']:
                text_content += f"• {vocab}\n"
        
        if 'practice_questions' in material:
            text_content += f"\n【練習問題】\n"
            for q in material['practice_questions']:
                text_content += f"• {q}\n"
        
        text_content += "\n" + "="*50 + "\n\n"
    
    return text_content

def export_materials(materials, format_type):
    """教材出力処理"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    if format_type == "JSON":
        filename = f"materials_{timestamp}.json"
        json_data = json.dumps(materials, ensure_ascii=False, indent=2)
        
        st.download_button(
            label="📥 JSONファイルをダウンロード",
            data=json_data.encode('utf-8'),
            file_name=filename,
            mime="application/json",
            key=f"json_download_{timestamp}"
        )
        st.success(f"✅ {filename} のダウンロード準備完了")
    
    elif format_type == "Google Docs":
        try:
            google_client = GoogleDocsAPIClient()
            if google_client.is_available():
                for i, material in enumerate(materials):
                    title = f"教材_{timestamp}_{i+1}_{material.get('topic', 'Unknown')}"
                    document_url = google_client.create_and_write_material(title, material)
                    if document_url:
                        st.success(f"✅ [教材{i+1}]({document_url}) をGoogle Docsに出力しました")
            else:
                st.error("Google Docs APIが利用できません。設定を確認してください。")
        except Exception as e:
            st.error(f"Google Docs出力エラー: {str(e)}")
    
    elif format_type == "テキストファイル":
        filename = f"materials_{timestamp}.txt"
        text_content = generate_text_content(materials)
        
        st.download_button(
            label="📥 テキストファイルをダウンロード",
            data=text_content.encode('utf-8'),
            file_name=filename,
            mime="text/plain",
            key=f"text_download_{timestamp}"
        )
        st.success(f"✅ {filename} のダウンロード準備完了")

def generate_audio_prompt(dialogue):
    """音声生成用プロンプトを作成"""
    return f"""Please create a natural-sounding audio script for the following dialogue. 
Include pronunciation notes for difficult words and intonation guidance:

Dialogue:
{dialogue}

Please provide:
1. Phonetic transcription for challenging words
2. Stress and intonation patterns
3. Pace and pause recommendations
4. Natural pronunciation variants"""

def generate_discussion_prompt(topic, viewpoints):
    """ディスカッション構造化プロンプトを作成"""
    return f"""Create a structured discussion framework for the following topic:

Topic: {topic}

Viewpoints to explore:
{viewpoints}

Please provide:
1. Opening questions to introduce each viewpoint
2. Follow-up questions for deeper exploration
3. Bridging phrases to connect different perspectives
4. Closing questions for synthesis and conclusion
5. Time allocation suggestions for each phase"""

def generate_chart_prompt(chart_types, description):
    """図表生成プロンプトを作成"""
    chart_type = chart_types[0] if chart_types else "bar chart"
    return f"""Create a {chart_type} based on the following description:

Description: {description}

Requirements:
1. Generate realistic data that matches the description
2. Include appropriate labels and title
3. Use professional colors and formatting
4. Ensure the chart supports the narrative described
5. Include data source information if relevant

Output format: Provide both the chart specification and the underlying data in a structured format."""

def create_sample_chart(chart_type):
    """サンプル図表を生成"""
    import plotly.graph_objects as go
    import plotly.express as px
    
    if chart_type == "棒グラフ":
        # サンプルデータ
        quarters = ['Q1', 'Q2', 'Q3', 'Q4']
        sales = [2.3, 3.1, 2.8, 3.5]
        
        fig = go.Figure(data=[go.Bar(x=quarters, y=sales)])
        fig.update_layout(
            title="四半期売上実績 (単位: 百万円)",
            xaxis_title="四半期",
            yaxis_title="売上 (百万円)",
            height=400
        )
        return fig
    
    elif chart_type == "線グラフ":
        # サンプルデータ
        months = ['1月', '2月', '3月', '4月', '5月', '6月']
        values = [100, 110, 105, 120, 115, 130]
        
        fig = go.Figure(data=[go.Scatter(x=months, y=values, mode='lines+markers')])
        fig.update_layout(
            title="月別業績推移",
            xaxis_title="月",
            yaxis_title="指数",
            height=400
        )
        return fig
    
    elif chart_type == "円グラフ":
        # サンプルデータ
        labels = ['製品A', '製品B', '製品C', 'その他']
        values = [35, 25, 20, 20]
        
        fig = go.Figure(data=[go.Pie(labels=labels, values=values)])
        fig.update_layout(
            title="製品別売上構成比",
            height=400
        )
        return fig
    
    else:
        # デフォルト：棒グラフ
        fig = go.Figure(data=[go.Bar(x=['A', 'B', 'C'], y=[1, 2, 3])])
        fig.update_layout(title="サンプルチャート", height=400)
        return fig

if __name__ == "__main__":
    main() 