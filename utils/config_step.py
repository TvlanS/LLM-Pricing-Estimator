import yaml
from pyprojroot import here

class Config():
    def __init__ (self):
        with open(here("config/config.yml"), "r") as f:
            config = yaml.safe_load(f)

            self.api_key = config["deepseek"]["api_key"]
            self.website_url = config["deepseek"]["website_url"]
            self.prompt = config["prompt"]["system_prompt2"]
            self.xero_prompt = config["prompt"]["prompt_xero"]
            