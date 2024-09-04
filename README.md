# SummarizeIQ: An Integrated Summarization and Content Analysis Engine
This project integrates T5 like LLM summarization models with Torch Serve, enhanced by extractive methods like LexRank and TextRank. It also includes keyword generation and implements query-based content filtering using cosine similarity, offering a comprehensive solution for article summarization and analysis.

## Deploy and run:
1) Go to ![server](https://github.com/FrozenWolf-Cyber/Scalable-Summarization/tree/master/server)
2) Start the server by executing 
``` python app.py ```

3) Go to ![website](https://github.com/FrozenWolf-Cyber/Scalable-Summarization/tree/master/website) and open ![index.html](https://github.com/FrozenWolf-Cyber/Scalable-Summarization/blob/master/website/index.html)

### Features:
- Can give both abstract and extractive based summaries for each article and all articles combined.
- Can give keyword representive of an article which can be used to search other related articles which can also be automated for nested crawling
- Uses Cosine similarity on encoded query vectors and article vectors to get articles that have content matching the required query.

![flow](https://github.com/FrozenWolf-Cyber/Scalable-Summarization/blob/master/FLOWCHART.drawio.png)
