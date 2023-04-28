from abc import ABC
import json
import logging
import os

import torch
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer
from keybert import KeyBERT
from sklearn.feature_extraction.text import CountVectorizer
from sentence_transformers import SentenceTransformer
from transformers import pipeline
from keybert.backend import BaseEmbedder
from ts.torch_handler.base_handler import BaseHandler

logger = logging.getLogger(__name__)


class CustomEmbedder(BaseEmbedder):
    def __init__(self, embedding_model):
        super().__init__()
        self.embedding_model = embedding_model

    def embed(self, documents, verbose=False):
        embeddings = self.embedding_model.encode(documents, show_progress_bar=verbose)
        return embeddings

class TransformersClassifierHandler(BaseHandler):
    """
    Transformers text classifier handler class. This handler takes a text (string) and
    as input and returns the classification text based on the serialized transformers checkpoint.
    """
    def __init__(self):
        self._context = None
        self.initialized = False
        self.model = None
        self.device = None


    def initialize(self, ctx):
        self.manifest = ctx.manifest

        properties = ctx.system_properties
        model_dir = properties.get("model_dir")
        # setup_config_path = os.path.join(model_dir, "setup_config.json")
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

        # Read model serialize/pt file
        # print(model_dir, flush=True)
        # print(os.listdir(), os.curdir, flush=True)
        self.model = AutoModelForSeq2SeqLM.from_pretrained(model_dir)
        self.tokenizer = AutoTokenizer.from_pretrained('t5-base')
        self.extractor = SentenceTransformer('sentence-transformers/sentence-t5-base').to(self.device)
        self.summarizer = pipeline("summarization", model=self.model, framework='pt', tokenizer=self.tokenizer, num_beams=10,  device=0)
        self.vectorizer = CountVectorizer(ngram_range=(1, 2), stop_words="english")

        self.kw_model = KeyBERT(model=CustomEmbedder(embedding_model=self.extractor))

        self.model.eval()
        self.extractor.eval()

        logger.debug('Transformer model from path {0} loaded successfully'.format(model_dir))

        self.initialized = True

    def preprocess(self, data):
        # print(data, len(data), flush=True)
        return data[0]
        

    def inference(self, inputs, task):
        if task == 'embeds':
            inputs = inputs['data'].decode().split('$___^^&&___^^')
            print(len(inputs), flush=True)

            emebd = self.extractor.encode(inputs)
            print("EMBEDS GENERATION:", len(emebd), flush=True)
            print(emebd[0].shape, flush=True)
            final = [i.tolist() for i in emebd]
            return [final]
    
            
        elif task == 'summary':
            inputs['prompt'] = inputs['prompt'].decode().split('$___^^&&___^^')
            min_token = int(inputs['min_token'].decode())
            max_token = int(inputs['max_token'].decode())
            out = [self.summarizer(inputs['prompt'], min_length=min_token, max_length=max_token)]
            print("SUMMARY GENERATION:", out, flush=True)
            return out

        elif task == 'keywords':
            out = [self.kw_model.extract_keywords(inputs['data'].decode().split('$___^^&&___^^'), vectorizer=self.vectorizer)]
            print("KEYWORD GENERATION:", out, flush=True)
            return out


    def postprocess(self, inference_output):
        # TODO: Add any needed post-processing of the model predictions here
        # inference_output = self.tokenizer.decode(inference_output[0], skip_special_tokens=True)
        return inference_output


_service = TransformersClassifierHandler()


def handle(data, context):
    try:
        if not _service.initialized:
            _service.initialize(context)

        if data is None:
            return None

        data = _service.preprocess(data)

        # print(data, flush=True)
        task = data['task'].decode()
        
        data = _service.inference(data, task)
        # data = _service.postprocess(data)
        return data
        # return str(data)
    except Exception as e:
        raise e
