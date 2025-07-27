import os
import json
from datetime import datetime
from typing import Dict, Optional
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

class GoogleDocsAPIClient:
    def __init__(self):
        self.service = None
        self.credentials_path = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
        self._initialize_service()
    
    def _initialize_service(self):
        """Google Docs APIサービスを初期化"""
        if not self.credentials_path or not os.path.exists(self.credentials_path):
            print("Google認証情報が見つかりません。")
            return
        
        try:
            # サービスアカウント認証
            credentials = service_account.Credentials.from_service_account_file(
                self.credentials_path,
                scopes=[
                    'https://www.googleapis.com/auth/documents',
                    'https://www.googleapis.com/auth/drive'
                ]
            )
            
            self.service = build('docs', 'v1', credentials=credentials)
            print("Google Docs API初期化成功")
            
        except Exception as e:
            print(f"Google Docs API初期化エラー: {e}")
            self.service = None
    
    def is_available(self) -> bool:
        """Google Docs APIが利用可能かチェック"""
        return self.service is not None
    
    def create_document(self, title: str) -> Optional[str]:
        """新しいドキュメントを作成"""
        if not self.is_available():
            return None
        
        try:
            document = {
                'title': title
            }
            
            doc = self.service.documents().create(body=document).execute()
            document_id = doc.get('documentId')
            print(f'ドキュメント作成成功: {document_id}')
            return document_id
            
        except HttpError as e:
            print(f'ドキュメント作成エラー: {e}')
            return None
    
    def write_material_to_doc(self, document_id: str, material_data: Dict) -> bool:
        """教材データをGoogle Docsに書き込み"""
        if not self.is_available():
            return False
        
        try:
            # ドキュメント構造を作成
            requests = []
            current_index = 1
            
            # タイトル挿入
            requests.append({
                'insertText': {
                    'location': {'index': current_index},
                    'text': f"📚 語学教材: {material_data.get('type', '教材')}\n\n"
                }
            })
            current_index += len(f"📚 語学教材: {material_data.get('type', '教材')}\n\n")
            
            # 基本情報
            if 'user_info' in material_data:
                info = material_data['user_info']
                basic_info = f"""📋 基本情報
• 業界: {info.get('industry', 'N/A')}
• 職種: {info.get('job_role', 'N/A')}
• 英語レベル: {info.get('english_level', 'N/A')}
• 学習目標: {info.get('learning_goal', 'N/A')}

"""
                requests.append({
                    'insertText': {
                        'location': {'index': current_index},
                        'text': basic_info
                    }
                })
                current_index += len(basic_info)
            
            # シチュエーション
            if 'final_situation' in material_data:
                situation_text = f"""🎯 シチュエーション
{material_data['final_situation']}

"""
                requests.append({
                    'insertText': {
                        'location': {'index': current_index},
                        'text': situation_text
                    }
                })
                current_index += len(situation_text)
            
            # 教材コンテンツ
            if 'generated_material' in material_data:
                material = material_data['generated_material']
                material_type = material.get('type', '教材')
                
                if material_type == 'ロールプレイ':
                    # モデルダイアログ
                    if 'model_dialogue' in material:
                        dialogue_text = f"""💬 モデルダイアログ
{material['model_dialogue']}

"""
                        requests.append({
                            'insertText': {
                                'location': {'index': current_index},
                                'text': dialogue_text
                            }
                        })
                        current_index += len(dialogue_text)
                    
                    # 有用表現・語彙
                    if 'useful_expressions' in material:
                        expressions_text = "📝 有用表現・語彙\n"
                        for i, expr in enumerate(material['useful_expressions'], 1):
                            expressions_text += f"{i}. {expr}\n"
                        expressions_text += "\n"
                        
                        requests.append({
                            'insertText': {
                                'location': {'index': current_index},
                                'text': expressions_text
                            }
                        })
                        current_index += len(expressions_text)
                    
                    # 追加質問
                    if 'additional_questions' in material:
                        questions_text = "❓ 追加質問\n"
                        for i, question in enumerate(material['additional_questions'], 1):
                            questions_text += f"{i}. {question}\n"
                        questions_text += "\n"
                        
                        requests.append({
                            'insertText': {
                                'location': {'index': current_index},
                                'text': questions_text
                            }
                        })
                        current_index += len(questions_text)
                
                elif material_type == 'ディスカッション':
                    # ディスカッショントピック
                    if 'discussion_topic' in material:
                        topic_text = f"""💭 ディスカッショントピック
{material['discussion_topic']}

"""
                        requests.append({
                            'insertText': {
                                'location': {'index': current_index},
                                'text': topic_text
                            }
                        })
                        current_index += len(topic_text)
                    
                    # ディスカッションの狙い
                    if 'discussion_aim' in material:
                        aim_text = f"""🎯 ディスカッションの狙い
{material['discussion_aim']}

"""
                        requests.append({
                            'insertText': {
                                'location': {'index': current_index},
                                'text': aim_text
                            }
                        })
                        current_index += len(aim_text)
                    
                    # ガイド質問
                    if 'guide_questions' in material:
                        guide_text = "❓ ガイド質問\n"
                        for i, question in enumerate(material['guide_questions'], 1):
                            guide_text += f"{i}. {question}\n"
                        guide_text += "\n"
                        
                        requests.append({
                            'insertText': {
                                'location': {'index': current_index},
                                'text': guide_text
                            }
                        })
                        current_index += len(guide_text)
                    
                    # 有用表現・語彙
                    if 'useful_expressions' in material:
                        expressions_text = "📝 有用表現・語彙\n"
                        for i, expr in enumerate(material['useful_expressions'], 1):
                            expressions_text += f"{i}. {expr}\n"
                        expressions_text += "\n"
                        
                        requests.append({
                            'insertText': {
                                'location': {'index': current_index},
                                'text': expressions_text
                            }
                        })
                        current_index += len(expressions_text)
                
                elif material_type == '表現練習':
                    # 図表・データ説明
                    if 'chart_description' in material:
                        chart_text = f"""📊 図表・データ説明
{material['chart_description']}

"""
                        requests.append({
                            'insertText': {
                                'location': {'index': current_index},
                                'text': chart_text
                            }
                        })
                        current_index += len(chart_text)
                    
                    # キーフレーズ
                    if 'key_phrases' in material:
                        phrases_text = "🔑 キーフレーズ\n"
                        for i, phrase in enumerate(material['key_phrases'], 1):
                            phrases_text += f"{i}. {phrase}\n"
                        phrases_text += "\n"
                        
                        requests.append({
                            'insertText': {
                                'location': {'index': current_index},
                                'text': phrases_text
                            }
                        })
                        current_index += len(phrases_text)
                    
                    # 段階的練習ステップ
                    if 'practice_steps' in material:
                        steps_text = "📚 段階的練習ステップ\n"
                        for i, step in enumerate(material['practice_steps'], 1):
                            steps_text += f"{i}. {step}\n"
                        steps_text += "\n"
                        
                        requests.append({
                            'insertText': {
                                'location': {'index': current_index},
                                'text': steps_text
                            }
                        })
                        current_index += len(steps_text)
                    
                    # 追加質問
                    if 'additional_questions' in material:
                        questions_text = "❓ 追加質問\n"
                        for i, question in enumerate(material['additional_questions'], 1):
                            questions_text += f"{i}. {question}\n"
                        questions_text += "\n"
                        
                        requests.append({
                            'insertText': {
                                'location': {'index': current_index},
                                'text': questions_text
                            }
                        })
                        current_index += len(questions_text)
            
            # フッター
            footer_text = f"""
---
作成日時: {datetime.now().strftime('%Y年%m月%d日 %H:%M')}
作成者: 語学教材作成支援ツール
"""
            requests.append({
                'insertText': {
                    'location': {'index': current_index},
                    'text': footer_text
                }
            })
            
            # バッチアップデート実行
            if requests:
                self.service.documents().batchUpdate(
                    documentId=document_id,
                    body={'requests': requests}
                ).execute()
                
                return True
                
        except HttpError as e:
            print(f'ドキュメント書き込みエラー: {e}')
            return False
        
        return False
    
    def create_and_write_material(self, title: str, material_data: Dict) -> Optional[str]:
        """教材用ドキュメントを作成して内容を書き込み"""
        document_id = self.create_document(title)
        if not document_id:
            return None
        
        success = self.write_material_to_doc(document_id, material_data)
        if success:
            # Google DocsのURLを生成
            doc_url = f"https://docs.google.com/document/d/{document_id}/edit"
            return doc_url
        
        return None
    
    def get_setup_instructions(self) -> str:
        """Google Docs API設定手順を返す"""
        return """
## Google Docs API設定手順

### 1. Google Cloud Consoleでプロジェクト作成
1. https://console.cloud.google.com/ にアクセス
2. 新しいプロジェクトを作成（例：「語学教材ツール」）

### 2. Google Docs APIを有効化
1. 「APIとサービス」→「ライブラリ」
2. 「Google Docs API」を検索して有効化

### 3. サービスアカウント作成
1. 「APIとサービス」→「認証情報」
2. 「認証情報を作成」→「サービスアカウント」
3. サービスアカウント名を入力（例：「docs-writer」）
4. 役割：「編集者」を選択

### 4. キーファイルダウンロード
1. 作成したサービスアカウントをクリック
2. 「キー」タブ→「キーを追加」→「新しいキーを作成」
3. JSON形式を選択してダウンロード

### 5. ファイル配置と環境変数設定
1. ダウンロードしたJSONファイルを `google_credentials.json` にリネーム
2. プロジェクトフォルダに配置
3. .envファイルに以下を追加：
   ```
   GOOGLE_APPLICATION_CREDENTIALS=./google_credentials.json
   ```

### 6. 動作確認
- アプリを再起動してGoogle Docs出力機能をテスト
""" 