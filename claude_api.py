import os
import anthropic
from typing import List, Dict
import json

class ClaudeAPIClient:
    def __init__(self):
        self.client = anthropic.Anthropic(
            api_key=os.getenv('ANTHROPIC_API_KEY')
        )
    
    def generate_primary_topics(self, user_info: Dict) -> List[str]:
        """1次トピックリストを生成"""
        prompt = f"""
あなたは語学教材作成の専門家です。以下の受講者情報に基づいて、実践的で現実的なビジネス英語の学習トピックを8個生成してください。

【受講者情報】
- 業界: {user_info.get('industry', '一般企業')}
- 職種: {user_info.get('job_role', 'ビジネスパーソン')}
- 英語レベル: {user_info.get('english_level', '中級')}
- 学習目標: {user_info.get('learning_goal', 'ビジネス英語向上')}
- カウンセリングメモ: {user_info.get('counseling_memo', '')[:200]}...

【要件】
1. 受講者が実際に遭遇する可能性が高いシーンを重視
2. 誇張された設定ではなく、日常業務で起こりうる現実的な場面
3. 指定された英語レベルに適切な難易度
4. 各トピックは簡潔に（10-15文字程度）

【出力形式】
JSON配列で8個のトピックを返してください。
例: ["クライアントとの初回面談", "商品デモンストレーション", ...]
"""

        try:
            response = self.client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=1000,
                messages=[{"role": "user", "content": prompt}]
            )
            
            # レスポンスからJSONを抽出
            content = response.content[0].text
            # JSON部分のみを抽出（前後のテキストを除去）
            start = content.find('[')
            end = content.rfind(']') + 1
            if start != -1 and end != 0:
                topics_json = content[start:end]
                # 制御文字を除去
                topics_json = ''.join(char for char in topics_json if ord(char) >= 32 or char in '\n\r\t')
                topics = json.loads(topics_json)
                return topics
            else:
                return self._get_fallback_topics()
                
        except Exception as e:
            print(f"Claude API エラー: {e}")
            return self._get_fallback_topics()
    
    def generate_detailed_situations(self, user_info: Dict, topic: str) -> List[str]:
        """詳細シチュエーションを生成"""
        prompt = f"""
以下のトピックについて、具体的で実践的なシチュエーション3個を生成してください。

【トピック】: {topic}
【受講者情報】:
- 業界: {user_info.get('industry', '一般企業')}
- 職種: {user_info.get('job_role', 'ビジネスパーソン')}
- 英語レベル: {user_info.get('english_level', '中級')}

【要件】
1. 現実的で実際に起こりうるシチュエーション
2. 受講者の業界・職種に関連性がある
3. 各シチュエーションは15-25文字程度

【出力形式】
JSON配列で3個のシチュエーションを返してください。
例: ["新規顧客への製品説明", "既存顧客からの苦情対応", "社内チームとの進捗確認"]
"""

        try:
            response = self.client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=800,
                messages=[{"role": "user", "content": prompt}]
            )
            
            content = response.content[0].text
            start = content.find('[')
            end = content.rfind(']') + 1
            if start != -1 and end != 0:
                situations_json = content[start:end]
                # 制御文字を除去
                situations_json = ''.join(char for char in situations_json if ord(char) >= 32 or char in '\n\r\t')
                situations = json.loads(situations_json)
                return situations
            else:
                return self._get_fallback_situations()
                
        except Exception as e:
            print(f"Claude API エラー: {e}")
            return self._get_fallback_situations()

    def generate_roleplay_material(self, context_data: Dict, topic: str, template_config: Dict = None) -> Dict:
        """ロールプレイ教材を生成"""
        
        # テンプレート設定の適用
        template = template_config or {}
        dialogue_length = template.get('dialogue_length', '160-200語')
        participants = template.get('participants', 2)
        useful_expressions_count = template.get('useful_expressions_count', 10)
        additional_questions_count = template.get('additional_questions_count', 4)
        include_audio = template.get('include_audio', True)
        parts = template.get('parts', {})
        custom_instructions = template.get('custom_instructions', '')
        
        # サンプルテキストの活用
        sample_dialogue = template.get('sample_dialogue', '')
        sample_expressions = template.get('sample_expressions', '')
        sample_questions = template.get('sample_questions', '')
        
        # パート構成の指示
        parts_instruction = ""
        if parts:
            included_parts = [part for part, include in parts.items() if include]
            if included_parts:
                parts_instruction = f"対話には以下の要素を含めてください: {', '.join(included_parts)}"
        
        # サンプルテキストを活用したプロンプト
        sample_section = ""
        if sample_dialogue or sample_expressions or sample_questions:
            sample_section = "\n【参考サンプル】"
            if sample_dialogue:
                sample_section += f"\n- 対話例: {sample_dialogue}"
            if sample_expressions:
                sample_section += f"\n- 表現例: {sample_expressions}"
            if sample_questions:
                sample_section += f"\n- 質問例: {sample_questions}"
        
        prompt = f"""
あなたは語学教材作成の専門家です。以下の情報に基づいて、実践的なロールプレイ教材を作成してください。

【コンテキスト情報】
- 業界: {context_data.get('industry', '一般企業')}
- 職種: {context_data.get('job_role', 'ビジネスパーソン')}
- 英語レベル: {context_data.get('english_level', '中級')}
- 学習目標: {context_data.get('learning_goal', 'ビジネス英語向上')}

【トピック】
{topic}

【テンプレート設定】
- 対話長: {dialogue_length}
- 参加者数: {participants}名
- 有用表現数: {useful_expressions_count}個
- 追加質問数: {additional_questions_count}個
- 音声練習: {'含む' if include_audio else '含まない'}
{parts_instruction}

{sample_section}

【カスタム指示】
{custom_instructions}

【要件】
1. {dialogue_length}程度の自然な対話
2. {participants}名の登場人物
3. 現実的で実践的なシチュエーション
4. 指定された英語レベルに適した表現
5. ビジネスシーンで実際に使用される表現
6. サンプルテキストのスタイルや構造を参考にする

【必要な構成要素】
- model_dialogue: モデル対話
- useful_expressions: {useful_expressions_count}個の有用表現（英語フレーズ: 日本語説明）
- additional_questions: {additional_questions_count}個の追加質問
{f'- audio_notes: 音声練習のポイント' if include_audio else ''}

【出力形式】
以下のJSON形式で出力してください：
{{
  "model_dialogue": "A: ... B: ...",
  "useful_expressions": ["例1: I'd like to propose... - 提案したいのですが", "例2: ..."],
  "additional_questions": ["質問1", "質問2", "質問3", "質問4"]
  {f', "audio_notes": "音声練習での注意点"' if include_audio else ''}
}}
"""

        try:
            response = self.client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=2500,
                messages=[{"role": "user", "content": prompt}]
            )
            
            content = response.content[0].text
            start = content.find('{')
            end = content.rfind('}') + 1
            if start != -1 and end != 0:
                material_json = content[start:end]
                # 制御文字を除去
                material_json = ''.join(char for char in material_json if ord(char) >= 32 or char in '\n\r\t')
                material = json.loads(material_json)
                material["type"] = "ロールプレイ"
                if include_audio:
                    material["audio_script"] = "※音声ファイル作成用スクリプト（開発予定）"
                return material
            else:
                return self._get_fallback_roleplay()
                
        except Exception as e:
            print(f"Claude API エラー: {e}")
            return self._get_fallback_roleplay()

    def generate_discussion_material(self, context_data: Dict, topic: str, template_config: Dict = None) -> Dict:
        """ディスカッション教材を生成"""
        
        # テンプレート設定の適用
        template = template_config or {}
        topic_complexity = template.get('topic_complexity', '中程度')
        discussion_time = template.get('discussion_time', '20分')
        viewpoints_count = template.get('viewpoints_count', 3)
        supporting_materials = template.get('supporting_materials', True)
        conclusion_required = template.get('conclusion_required', True)
        custom_instructions = template.get('custom_instructions', '')
        
        # サンプルテキストの活用
        sample_topic = template.get('sample_topic', '')
        sample_viewpoints = template.get('sample_viewpoints', '')
        sample_materials = template.get('sample_materials', '')
        
        # サンプルテキストを活用したプロンプト
        sample_section = ""
        if sample_topic or sample_viewpoints or sample_materials:
            sample_section = "\n【参考サンプル】"
            if sample_topic:
                sample_section += f"\n- トピック例: {sample_topic}"
            if sample_viewpoints:
                sample_section += f"\n- 観点例: {sample_viewpoints}"
            if sample_materials:
                sample_section += f"\n- 参考資料例: {sample_materials}"
        
        prompt = f"""
あなたは語学教材作成の専門家です。以下の情報に基づいて、実践的なディスカッション教材を作成してください。

【コンテキスト情報】
- 業界: {context_data.get('industry', '一般企業')}
- 職種: {context_data.get('job_role', 'ビジネスパーソン')}
- 英語レベル: {context_data.get('english_level', '中級')}
- 学習目標: {context_data.get('learning_goal', 'ビジネス英語向上')}

【トピック】
{topic}

【テンプレート設定】
- 複雑度: {topic_complexity}
- 討議時間: {discussion_time}
- 観点数: {viewpoints_count}個
- 参考資料: {'含む' if supporting_materials else '含まない'}
- 結論: {'必要' if conclusion_required else '不要'}

{sample_section}

【カスタム指示】
{custom_instructions}

【要件】
1. {topic_complexity}レベルの議論テーマ
2. {viewpoints_count}つの異なる視点からの検討
3. {discussion_time}での討議に適した内容量
4. 指定された英語レベルに適した内容
5. ビジネス場面での実用性
6. サンプルテキストのスタイルや構造を参考にする

【必要な構成要素】
- discussion_topic: ディスカッショントピック
- background_info: 背景情報
- key_points: 議論のポイント（{viewpoints_count}つ）
- useful_expressions: 議論で使える表現（8個）
- discussion_questions: 議論を深める質問（5個）
{f'- supporting_materials: 参考資料情報' if supporting_materials else ''}

【出力形式】
以下のJSON形式で出力してください：
{{
  "discussion_topic": "議論のテーマ",
  "background_info": "背景情報や説明",
  "key_points": ["ポイント1", "ポイント2", "ポイント3"],
  "useful_expressions": ["表現1: 意味", "表現2: 意味", ...],
  "discussion_questions": ["質問1", "質問2", ...]
  {f', "supporting_materials": "参考資料の情報"' if supporting_materials else ''}
}}
"""

        try:
            response = self.client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=2000,
                messages=[{"role": "user", "content": prompt}]
            )
            
            content = response.content[0].text
            start = content.find('{')
            end = content.rfind('}') + 1
            if start != -1 and end != 0:
                material_json = content[start:end]
                # 制御文字を除去
                material_json = ''.join(char for char in material_json if ord(char) >= 32 or char in '\n\r\t')
                material = json.loads(material_json)
                material["type"] = "ディスカッション"
                return material
            else:
                return self._get_fallback_discussion()
                
        except Exception as e:
            print(f"Claude API エラー: {e}")
            return self._get_fallback_discussion()

    def generate_expression_practice_material(self, context_data: Dict, topic: str, template_config: Dict = None) -> Dict:
        """表現練習教材を生成"""
        
        # テンプレート設定の適用
        template = template_config or {}
        chart_types = template.get('chart_types', ['棒グラフ'])
        explanation_length = template.get('explanation_length', '100-150語')
        vocabulary_count = template.get('vocabulary_count', 8)
        practice_questions_count = template.get('practice_questions', 3)
        include_numbers = template.get('include_numbers', True)
        custom_instructions = template.get('custom_instructions', '')
        
        # サンプルテキストの活用
        sample_chart_description = template.get('sample_chart_description', '')
        sample_vocabulary = template.get('sample_vocabulary', '')
        chart_generation_prompt = template.get('chart_generation_prompt', '')
        
        # 図表タイプの選択
        chart_type = chart_types[0] if chart_types else '棒グラフ'
        
        # サンプルテキストを活用したプロンプト
        sample_section = ""
        if sample_chart_description or sample_vocabulary or chart_generation_prompt:
            sample_section = "\n【参考サンプル】"
            if sample_chart_description:
                sample_section += f"\n- 図表説明例: {sample_chart_description}"
            if sample_vocabulary:
                sample_section += f"\n- 語彙例: {sample_vocabulary}"
            if chart_generation_prompt:
                sample_section += f"\n- 図表生成指示: {chart_generation_prompt}"
        
        prompt = f"""
あなたは語学教材作成の専門家です。以下の情報に基づいて、グラフや数値を使った表現練習教材を作成してください。

【コンテキスト情報】
- 業界: {context_data.get('industry', '一般企業')}
- 職種: {context_data.get('job_role', 'ビジネスパーソン')}
- 英語レベル: {context_data.get('english_level', '中級')}
- 学習目標: {context_data.get('learning_goal', 'ビジネス英語向上')}

【トピック】
{topic}

【テンプレート設定】
- 図表タイプ: {chart_type}
- 説明文長: {explanation_length}
- 語彙数: {vocabulary_count}個
- 練習問題数: {practice_questions_count}個
- 数値重視: {'はい' if include_numbers else 'いいえ'}

{sample_section}

【カスタム指示】
{custom_instructions}

【要件】
1. 業界に関連した現実的なデータ（{chart_type}形式）
2. {explanation_length}程度の説明文
3. 指定された英語レベルに適した表現
4. 数値やトレンドの説明練習
5. サンプルテキストのスタイルや構造を参考にする

【必要な構成要素】
- chart_description: 図表の説明（{explanation_length}）
- chart_data: 図表データ（JSON形式）
- useful_vocabulary: 数値表現語彙（{vocabulary_count}個）
- practice_questions: 練習問題（{practice_questions_count}個）
- explanation_points: 説明のポイント
{f'- chart_generation_prompt: AIによる図表生成用プロンプト' if chart_generation_prompt else ''}

【出力形式】
以下のJSON形式で出力してください：
{{
  "chart_description": "図表の詳細説明文",
  "chart_data": {{"labels": ["Q1", "Q2", "Q3", "Q4"], "values": [100, 120, 110, 140]}},
  "useful_vocabulary": ["substantial increase - 大幅な増加", "decline - 減少", ...],
  "practice_questions": ["質問1", "質問2", "質問3"],
  "explanation_points": "説明時の重要ポイント"
  {f', "chart_generation_prompt": "図表生成用の詳細プロンプト"' if chart_generation_prompt else ''}
}}
"""

        try:
            response = self.client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=2000,
                messages=[{"role": "user", "content": prompt}]
            )
            
            content = response.content[0].text
            start = content.find('{')
            end = content.rfind('}') + 1
            if start != -1 and end != 0:
                material_json = content[start:end]
                # 制御文字を除去
                material_json = ''.join(char for char in material_json if ord(char) >= 32 or char in '\n\r\t')
                material = json.loads(material_json)
                material["type"] = "表現練習"
                return material
            else:
                return self._get_fallback_expression_practice()
                
        except Exception as e:
            print(f"Claude API エラー: {e}")
            return self._get_fallback_expression_practice()

    # フォールバック用のメソッド群
    def _get_fallback_topics(self) -> List[str]:
        return [
            "クライアントとの初回面談",
            "商品デモンストレーション", 
            "チーム会議での進捗報告",
            "顧客からの苦情対応",
            "新商品の企画提案",
            "年次売上報告",
            "海外支社との電話会議",
            "契約条件の交渉"
        ]
    
    def _get_fallback_situations(self) -> List[str]:
        return [
            "新規顧客への製品説明",
            "既存顧客からの苦情対応", 
            "社内チームとの進捗確認"
        ]
    
    def _get_fallback_roleplay(self) -> Dict:
        return {
            "type": "ロールプレイ",
            "model_dialogue": "A: Good morning! I'm here for our 10 o'clock meeting.\nB: Perfect timing! Please come in and have a seat.\nA: Thank you. I'm excited to discuss our new project proposal.\nB: Excellent. I've reviewed your initial documents and I'm impressed with the concept.",
            "useful_expressions": [
                "Perfect timing! - タイミングがぴったりです",
                "I'm excited to... - ～するのを楽しみにしています",
                "I'm impressed with... - ～に感銘を受けました"
            ],
            "additional_questions": [
                "初対面の相手にどのように自己紹介しますか？",
                "会議の目的を明確にするために何と言いますか？"
            ],
            "audio_script": "※音声ファイル作成用スクリプト（開発予定）"
        }
    
    def _get_fallback_discussion(self) -> Dict:
        return {
            "type": "ディスカッション",
            "discussion_topic": "リモートワークの効果と課題について",
            "background_info": "コロナ禍を経てリモートワークが普及しましたが、その効果と課題について議論します。",
            "key_points": [
                "生産性の向上",
                "コミュニケーションの課題",
                "ワークライフバランス"
            ],
            "useful_expressions": [
                "From my perspective... - 私の観点では",
                "On the other hand... - 一方で",
                "I would argue that... - ～だと主張します"
            ],
            "discussion_questions": [
                "リモートワークの最大のメリットは何だと思いますか？",
                "対面でのコミュニケーションは本当に必要でしょうか？"
            ]
        }
    
    def _get_fallback_expression_practice(self) -> Dict:
        return {
            "type": "表現練習",
            "chart_description": "この棒グラフは四半期ごとの売上実績を示しています。Q1が230万円、Q2が310万円と大幅に増加しました。",
            "chart_data": {"labels": ["Q1", "Q2", "Q3", "Q4"], "values": [230, 310, 280, 350]},
            "useful_vocabulary": [
                "substantial increase - 大幅な増加",
                "steady decline - 安定した減少",
                "fluctuation - 変動"
            ],
            "practice_questions": [
                "グラフの最も印象的な傾向は何ですか？",
                "Q3の結果についてどう説明しますか？"
            ],
            "explanation_points": "数値の変化に注目し、原因や背景も合わせて説明すること"
        } 