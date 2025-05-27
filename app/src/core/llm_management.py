import torch
import logging

from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig

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
        if preferred_torch_dtype == "float16":
            model = AutoModelForCausalLM.from_pretrained(
            definitions.TRAINED_MODEL_PATH,
            torch_dtype=torch.float16,
            device_map="cpu"
        )
        elif preferred_torch_dtype == "float32":
            model = AutoModelForCausalLM.from_pretrained(
                definitions.TRAINED_MODEL_PATH,
                torch_dtype=torch.float32,
                device_map="cpu"
            )
        else:
            raise ValueError("Unsupported dtype. Use 'float16' or 'float32'.")


        logging.info("Model loaded successfully.")
        return model
    except Exception as e:
        logging.error(f"Error loading model: {e}")
        raise
