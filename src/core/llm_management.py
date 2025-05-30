import torch
import logging

from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig
from peft import PeftModel, PeftConfig

import utils.definitions as definitions

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def load_tokenizer():
    logger.info("Loading tokenizer...")
    try:
        logging.info(f"Using model path: {definitions.TRAINED_MODEL_PATH}")
        tokenizer = AutoTokenizer.from_pretrained(
            definitions.TRAINED_MODEL_PATH)
        tokenizer.pad_token = tokenizer.eos_token
        logging.info("Tokenizer loaded successfully.")
    except Exception as e:
        logging.error(f"Error loading tokenizer: {e}")
        raise
    return tokenizer


def load_model(preferred_torch_dtype="float16"):
    logger.info("Loading model...")
    try:
        # Load the adapter configuration to know the base model
        peft_config = PeftConfig.from_pretrained(definitions.TRAINED_MODEL_PATH)
        base_model = AutoModelForCausalLM.from_pretrained(
            peft_config.base_model_name_or_path,
            torch_dtype=torch.float16 if preferred_torch_dtype == "float16" else torch.float32,
            device_map="cpu"
        )

        # Load the fine-tuned model with LoRA
        model = PeftModel.from_pretrained(base_model, definitions.TRAINED_MODEL_PATH)

        logging.info("Model loaded successfully.")
        return model
    except Exception as e:
        logging.error(f"Error loading model: {e}")
        raise
