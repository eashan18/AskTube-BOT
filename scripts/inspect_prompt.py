from backend.rag.retriever import RAGRetriever
from backend.rag.prompts import build_prompt

retriever = RAGRetriever()
question = 'What is the main topic of the video?'
results = retriever.retrieve(question, top_k=5, video_id='kmsBuHT2kTo')
print('Retrieved', len(results), 'snippets')
prompt = build_prompt(results, question)
print('Prompt length:', len(prompt))
print('Contains "natural language processing"?', 'natural language processing' in prompt.lower())
print('Contains "nlp"?', 'nlp' in prompt.lower())
print('\n----PROMPT START----\n')
print(prompt[:3000])
print('\n----PROMPT END----\n')
