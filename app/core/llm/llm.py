from transformers import AutoModelForCausalLM, AutoTokenizer
import torch
from app.core.config.settings import config
from app.core.config.logging import logger
import json

class generator():
    def __init__(self, model_name="microsoft/Phi-4-mini-instruct"):
        #self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.device = "cpu"
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.tokenizer.pad_token_id = self.tokenizer.eos_token_id
        self.model = AutoModelForCausalLM.from_pretrained(
            model_name,
            torch_dtype=torch.float16,
            device_map={"": "cpu"},
            trust_remote_code=True,
        )
        self.messages = []

    def gen(self, input_prompt, system_prompt, context_prompt):
        prompt = {"role": "user", "content": f"Using, paraphrasing and summarizing this context: {context_prompt} Answer this question in your own words: {input_prompt}"}
        if len(self.messages) == 0:
            self.messages.append({"role": "system", "content": system_prompt})
        self.messages.append(prompt)
        
        logger.info(json.dumps({
            "prompt": prompt
        }))

        inputs = self.tokenizer.apply_chat_template(
            self.messages,
            return_tensors="pt",
            add_generation_prompt=True
        ).to(self.device)

        attention_mask = torch.ones_like(inputs)
        self.tokenizer.pad_token_id = self.tokenizer.eos_token_id

        with torch.no_grad():
            if config.LLM_TEMPERATURE <= 0:
                outputs = self.model.generate(
                    inputs,
                    max_new_tokens=config.MAX_TOKENS,
                    temperature=None,
                    do_sample=False,
                    top_p=None,
                    attention_mask = attention_mask,
                    pad_token_id=self.tokenizer.eos_token_id,
                )   
            else:
                outputs = self.model.generate(
                    inputs,
                    max_new_tokens=config.MAX_TOKENS,
                    temperature=config.LLM_TEMPERATURE,
                    do_sample=True,
                    top_p=0.9,
                    attention_mask = attention_mask,
                    pad_token_id=self.tokenizer.eos_token_id,
                )  
        answer = self.tokenizer.decode(
            outputs[0][inputs.shape[-1]:],
            skip_special_tokens=True
        )

        logger.info(json.dumps({
            "prompt": {"role": "assistant", "content": answer}
        }))

        return answer