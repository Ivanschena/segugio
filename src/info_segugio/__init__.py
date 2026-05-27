import chainlit as cl
from openai import OpenAI
from config import Config
import json
from tavily import TavilyClient
from prompts import query_writer_instructions


client = OpenAI(base_url=Config.AI_API_URL, api_key=Config.AI_API_KEY)

def llm(developer_prompt, user_prompt, temperature = 0 , response_format={"type":"json_object"}):
        response = client.chat.completions.create(
              
                model= Config.LLM_MODEL_LOW,
                messages=[
                      {"role": "developer","content": developer_prompt},
                      {"role": "user", "content": user_prompt}
                ],
                temperature=temperature,
                response_format=response_format
        )
        return response.choices[0].message.content



def optimize_search_query(research_topic):
      formatted_instructions = query_writer_instructions.format(research_topic = research_topic)
      result = llm(formatted_instructions, "Genera una query per la ricerca web:")
      obj = json.loads(result)
      return obj

def web_research(search_query):
      tavily_client = TavilyClient(Config.tavily_key)
      response = tavily_client.search(search_query)
      print(response)


@cl.on_message
async def main(message: cl.Message):
    # Your custom logic goes here...
    user_message = message.content
    osq = optimize_search_query(user_message)


    #feedback per l'ameba 
    query, aspect, reason = osq['query'],osq['aspect'], osq['reason']
    await cl. Message(author="system_assistant",
                        content=f"Query di ricerca ottimizzata: In {query}. In Mi sono soffermato su questo aspetto: \n {aspect}. \n Per questo motivo: \n {reason}. \n").send()

    #esegui la ricerca web
    results = web_research(query)



    # Send a response back to the user
    await cl.Message(
        author="system_assistant",
        content=f"Fonti trovate: {results['sources_gathered'][0]}",
    ).send()


