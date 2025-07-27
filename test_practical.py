#!/usr/bin/env python3
"""
実用版アプリの動作テスト
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from claude_api import ClaudeAPIClient
from dotenv import load_dotenv

def test_claude_api():
    """Claude APIの動作テスト"""
    load_dotenv()
    
    print("🧪 Claude API動作テスト開始")
    
    client = ClaudeAPIClient()
    
    # テストデータ
    context_data = {
        'industry': '金融',
        'job_role': '営業',
        'english_level': '中級',
        'learning_goal': 'ビジネス英語向上',
        'counseling_memo': '顧客との面談機会が多く、英語でのプレゼンテーション能力向上が急務',
        'teaching_policy': '実践的なビジネスシーンを重視'
    }
    
    template_config = {
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
        'custom_instructions': '金融業界特有の表現を重視',
        'sample_dialogue': '''A: Good morning, Mr. Johnson. Thank you for taking the time to meet with us today.
B: Good morning. I'm looking forward to hearing about your financing options.
A: Based on our initial assessment, I'd like to propose a structured loan package...''',
        'sample_expressions': '''• "I'd like to propose..." - 提案したいのですが
• "Based on our analysis..." - 分析に基づいて''',
        'sample_questions': '''1. How would you present this proposal to a more conservative client?
2. What additional information might you need before finalizing this deal?'''
    }
    
    topic = "新規顧客への融資提案"
    
    try:
        print(f"📝 トピック生成テスト...")
        topics = client.generate_primary_topics(context_data)
        print(f"✅ トピック生成成功: {len(topics)}件")
        
        print(f"🎭 ロールプレイ教材生成テスト...")
        roleplay = client.generate_roleplay_material(context_data, topic, template_config)
        print(f"✅ ロールプレイ生成成功: {roleplay.get('type', 'Unknown')}")
        
        print(f"💬 ディスカッション教材生成テスト...")
        discussion = client.generate_discussion_material(context_data, topic, template_config)
        print(f"✅ ディスカッション生成成功: {discussion.get('type', 'Unknown')}")
        
        print(f"📊 表現練習教材生成テスト...")
        expression = client.generate_expression_practice_material(context_data, topic, template_config)
        print(f"✅ 表現練習生成成功: {expression.get('type', 'Unknown')}")
        
        print("🎉 全テスト完了!")
        return True
        
    except Exception as e:
        print(f"❌ テスト失敗: {e}")
        return False

if __name__ == "__main__":
    success = test_claude_api()
    if success:
        print("\n✅ 実用版システムは正常に動作しています！")
    else:
        print("\n❌ システムに問題があります。設定を確認してください。") 