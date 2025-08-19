import json
import os
from typing import Dict, List
from pydantic import Field
from pydantic_settings import BaseSettings


class Config(BaseSettings):
    openai_key: str = Field(default='default_openai_key', description="OpenAI API key")
    relative_restriction_path: str = Field(default='data/restricted_stations.json', description="相対的な制約のパス")
    absolute_restriction_path: str = Field(default='data/absolute_restricted_stations.json', description="絶対的な制約のパス")
    target_device: str = Field(default='OT-2', description="配置の最大数")
    process_flow_path: str = Field(default='data/process_flow.txt', description="プロセスフローのパス")
    process_flow: str = Field(default='', description="プロセスフロー")
    max_iter: int = Field(default=10, description="最大イテレーション数")
    model: str = Field(default='o1-preview', description="モデル")
    base_dir: str = Field(default=f'{os.getcwd()}/result_dir', description="ベースディレクトリ")
    auto_mode: bool = Field(default=False, description="オートモード")
    allowed_objects_path: str = Field(default="", description="許可されたオブジェクトのJsonのパス")
    prompt: str = Field(default="test_case/hard_coded_variables/PROMPT.txt", description="Promptのパス")
    prompt_template: str = Field(default="test_case/hard_coded_variables/PROMPT_TEMPLATE_SCRIPT.txt", description="Promptのテンプレートのパス")
    prompt_haichi: str = Field(default="test_case/hard_coded_variables/PROMPT_HAICHI.txt", description="Promptの配置のパス")
    prompt_骨子_haichi_replace: str = Field(default="test_case/hard_coded_variables/PROMPT_骨子_HAICHI_REPLACE.txt", description="Promptの骨子と配置の置換のパス")
    # Simply add a new configuration variable and it will be loaded automatically.
    # Example.
    # API_ENDPOINT: str = Field(default=‘https://api.example.com’, description=‘API endpoint’)

    # post_init method
    def model_post_init(self, __context):
        if self.process_flow == '':
            print(f"self.process_flow_path: {self.process_flow_path}")
            try:
                with open(self.process_flow_path, "r") as f:
                    self.process_flow = f.read()
            except FileNotFoundError:
                print(f"FileNotFoundError: {self.process_flow_path}. Set PROCESS_FLOW variable.")
                self.process_flow = "process_flow"

        with open(self.prompt, "r") as f:
            self.prompt = f.read()

        with open(self.prompt_template, "r") as f:
            self.prompt_template = f.read()

        with open(self.prompt_haichi, "r") as f:
            self.prompt_haichi = f.read()

        with open(self.prompt_骨子_haichi_replace, "r") as f:
            self.prompt_骨子_haichi_replace = f.read()
        
        def load_data(file_path: str) -> List[Dict]:
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                return data
            except FileNotFoundError:
                print(f"Error: File not found - {file_path}")
                return []
            except json.JSONDecodeError as e:
                print(f"Error: Failed to decode JSON. {e}")
                return []
            
        print(f"{load_data(self.allowed_objects_path)=}")
            
        

    class Config:
        env_file = '.env'

# 設定のインスタンスを作成
config = Config()
# config.model_post_init(__context=None)

for key, value in config.model_dump().items():
    print(f"{key}: {value}")
