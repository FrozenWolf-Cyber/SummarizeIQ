
import uvicorn
import openai
import numpy as np
from typing import Dict
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
# from gensim.summarization import keywords
from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
# from sumy.summarizers.lsa import LsaSummarizer as Summarizer
from sumy.nlp.stemmers import Stemmer
from sumy.summarizers.lex_rank import LexRankSummarizer
# from sumy.summarizers.lsa import LsaSummarizer
from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
# from sumy.summarizers.luhn import LuhnSummarizer
# from sumy.utils import get_stop_words
from sumy.summarizers.text_rank import TextRankSummarizer
# from transformers import pipeline
from numpy import dot
from numpy.linalg import norm
from threaded import scrape_threaded
import requests
from transformers import BertTokenizer

tokenizer = BertTokenizer.from_pretrained('bert-base-cased')
LANGUAGE = "english"
SENTENCES_COUNT = 10

stemmer = Stemmer(LANGUAGE)
# summarizer = Summarizer(stemmer)
# summarizer.stop_words = get_stop_words(LANGUAGE)

summarizer_lex = LexRankSummarizer()
# summarizer_lsa = LsaSummarizer()
# summarizer_1 = LuhnSummarizer()
summarizer_rank = TextRankSummarizer()
# summarizer_t5 = pipeline("summarization", model='t5-base', tokenizer="t5-base", framework="pt", device=0)

openai.api_key = "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"

torch_url = "http://127.0.0.1:8080/predictions/t5"

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# def gen_total_summary(articles, max_token=120, min_token=10, SENTENCES_COUNT=10):
#     prompt = ''
#     for i in articles.values():
#         prompt+=i[0]
#         prompt+='\n'

    
#     summary = {}

#     try:
#         response = openai.Completion.create(
#                     model="text-davinci-003",
#                     prompt=prompt+"\n\nTl;dr",
#                     temperature=0.7,
#                     max_tokens=max_token,
#                     top_p=1,
#                     frequency_penalty=0,
#                     presence_penalty=1
#         )

#         r = response['choices']
#         # print(r,"\n\n\n", flush=True)
#         summary['openai'] = r[0]['text']

#     except Exception as err:
#         summary['openai'] = str(err)

#     parser = PlaintextParser.from_string(prompt, Tokenizer(LANGUAGE))



#     try:
#         summary['lex'] = ""
#         for sentence in summarizer_lex(parser.document, SENTENCES_COUNT):
#             summary['lex']+= "• "+str(sentence)+'\n'
#     except Exception as err:
#         summary['lex'] = str(err)

#     try:
#         summary['text_rank'] = ""
#         for sentence in summarizer_rank(parser.document, SENTENCES_COUNT):
#             summary['text_rank']+= "• "+str(sentence)+'\n'
#     except Exception as err:
#         summary['text_rank'] = str(err)

#     try:
#         summary['t5'] = summarizer_t5(prompt, min_length=min_token, max_length=max_token)[0]['summary_text']
#     except Exception as err:
#         summary['t5'] = str(err)

#     keywords = kw_model.extract_keywords(prompt, vectorizer=vectorizer)

#     summary['keywords'] = [i[0] for i in keywords]

#     summary['results'] = articles

#     return summary

def gen_summary_for(prompt, model="lex", max_token=200, min_token=75, SENTENCES_COUNT=6):
 
    summary = {}
    if model == "openai":
        try:
            new_prompt = prompt

            while tokenizer(new_prompt,return_tensors='pt', add_special_tokens=False).input_ids.shape[1]>4000-max_token:
                check = new_prompt.split(' ')
                new_prompt = ' '.join(check[:-150])


            response = openai.Completion.create(
                        model="text-davinci-003",
                        prompt=new_prompt+"\n\nTl;dr",
                        temperature=0.7,
                        max_tokens=max_token,
                        top_p=1,
                        frequency_penalty=0,
                        presence_penalty=1
            )

            r = response['choices']
            # print(r,"\n\n\n", flush=True)
            summary['openai'] = r[0]['text']

        except Exception as err:
            summary['openai'] = str(err)

    else:

        parser = PlaintextParser.from_string(prompt, Tokenizer(LANGUAGE))
    # try:
    #     summary['lsa'] = []
    #     for sentence in summarizer(parser.document, SENTENCES_COUNT):
    #         summary['lsa'].append(str(sentence))

    # except Exception as err:
    #     summary['lsa'] = [str(err)]

        if model == 'lex':

            try:
                summary['lex'] = ""
                for sentence in summarizer_lex(parser.document, SENTENCES_COUNT):
                    summary['lex']+= "• "+str(sentence)+'\n'

            except Exception as err:
                summary['lex'] = str(err)

        # try:
        #     summary['lunh'] = []
        #     for sentence in summarizer_1(parser.document, SENTENCES_COUNT):
        #         summary['lunh'].append(str(sentence))

        # except Exception as err:
        #     summary['lunh'] = [str(err)]

        # try:
        #     summary['lsa'] = []
        #     for sentence in summarizer_lsa(parser.document, SENTENCES_COUNT):
        #         summary['lsa'].append(str(sentence))

        # except Exception as err:
        #     summary['lsa'] = [str(err)]
        elif model == 'text_rank':
            try:
                summary['text_rank'] = ""
                for sentence in summarizer_rank(parser.document, SENTENCES_COUNT):
                    summary['text_rank']+= "• "+str(sentence)+'\n'


            except Exception as err:
                summary['text_rank'] = str(err)

        elif model == 't5':
            try:
                new_prompt = prompt

                while tokenizer(new_prompt,return_tensors='pt', add_special_tokens=False).input_ids.shape[1]>450:
                    check = new_prompt.split(' ')
                    new_prompt = ' '.join(check[:-150])


                summary['t5'] = get_t5_summary([new_prompt], min_token,max_token)[0]['summary_text']

            except Exception as err:
                summary['t5'] = str(err)

        else:
            print("Invalid model: ",model, flush=True)

    keywords = get_t5_keywords([prompt])

    summary['keywords'] = [i[0] for i in keywords]

    return summary

# def get_articles(prompt):
#     return get_embeddings(scrape(prompt))

# def crawl_home_feed():
#     return get_embeddings(scrape())

def get_t5_emebddings(prompt):
    return requests.post("http://127.0.0.1:8080/predictions/t5", data={'task':'embeds', 'data':'$___^^&&___^^'.join(prompt)}).json()

def get_t5_keywords(prompt):
    return requests.post("http://127.0.0.1:8080/predictions/t5", data={'task':'keywords', 'data':'$___^^&&___^^'.join(prompt)}).json()


def get_t5_summary(prompt, min_tokens, max_tokens):
    return requests.post("http://127.0.0.1:8080/predictions/t5", data={'task':'summary', 'prompt':'$___^^&&___^^'.join(prompt), 'min_token':min_tokens, 'max_token':max_tokens}).json()



def get_articles(prompt):
    a = scrape_threaded(prompt, 8)
    # print(a.keys())
    a_ = list(a.keys())
    for i in a_:
        a[i.replace("\n","").lstrip().rstrip()] = a[i]
        if i.replace("\n","").lstrip().rstrip() != i:
            del a[i]

    print(a.keys())
    return get_embeddings(a)
    # return get_embeddings(articles)

def crawl_home_feed():
    a = scrape_threaded('', 8)
    a_ = list(a.keys())
    for i in a_:
        a[i.replace("\n","").lstrip().rstrip()] = a[i]
        if i.replace("\n","").lstrip().rstrip() != i:
            del a[i]

    print(a.keys())
    return get_embeddings(a)
    # return get_embeddings(articles)

def get_embeddings(results):
    each_article =[]
    for title in results:
        a = results[title][0]
        each_article.append(a)

        new_prompt = a

        while tokenizer(new_prompt,return_tensors='pt', add_special_tokens=False).input_ids.shape[1]>4000:
            check = new_prompt.split(' ')
            new_prompt = ' '.join(check[:-150])


        openai_response_emebd = openai.Embedding.create(input = [new_prompt.replace("\n", " ")], model="text-embedding-ada-002")['data'][0]['embedding']
        results[title].append([openai_response_emebd])

    filtered = []
    for a in each_article:
        while tokenizer(new_prompt,return_tensors='pt', add_special_tokens=False).input_ids.shape[1]>450:
            check = new_prompt.split(' ')
            new_prompt = ' '.join(check[:-150])

        filtered.append(new_prompt)

    t5_embeddings = get_t5_emebddings(filtered)

    for i, title in enumerate(results):
        results[title][2].append(t5_embeddings[i])

    return results

@app.post('/search')
def search(json_data: Dict):
    # if Request.method == 'POST':
    print(json_data, flush=True)
    prompt = json_data['prompt']

    results = get_articles(prompt)
    # print(results, flush=True)
    return results


@app.post('/get_summary')
def get_summary(json_data: Dict):
    # if Request.method == 'POST':
    # print(json_data, flush=True)
    prompt = json_data['prompt']
    model = json_data['model']

    results = gen_summary_for(prompt, model)
    # print(results, flush=True)
    return results


@app.post('/get_home_feed')
def get_home_feed():
    # if Request.method == 'POST':

    results = crawl_home_feed()
    # print(results, flush=True)
    return results


@app.post('/get_scores')
def get_scores(json_data: Dict):
    # if Request.method == 'POST':
    query = json_data['query']
    results = json_data['results']

    rank = {}

    query_openai_emebd = np.asarray(openai.Embedding.create(input = [query.replace("\n", " ")], model="text-embedding-ada-002")['data'][0]['embedding'])
    
    t5_embeddings = get_t5_emebddings([query])
    query_t5_embeddings = np.asarray(t5_embeddings[0])

    for title in results:
        article_openai_emebd = results[title][2][0]
        article_t5_emebd = results[title][2][1]

        rank[title] = [dot(article_openai_emebd, query_openai_emebd)/(norm(article_openai_emebd)*norm(query_openai_emebd)),
                        dot(query_t5_embeddings, article_t5_emebd)/(norm(query_t5_embeddings)*norm(article_t5_emebd))]

    print(rank, flush=True)
    return rank

if __name__ == '__main__':
    uvicorn.run(app, port=5000)
