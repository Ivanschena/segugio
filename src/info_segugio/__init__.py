#extraenumeriamo il codice in meta paperella style

#embedded import
from datetime import datetime
import json

#external libs
import chainlit as cl
from openai import OpenAI
from tavily import TavilyClient

#root docs
from config import Config
from prompts import (
    reflection_instructions,
    query_writer_instructions,
    summarizer_instructions,
)

#GLOBAL
today = datetime.now().strftime("%d/%m/%Y")




#core strumentalicum
def web_research(search_query):
    client = TavilyClient(Config.tavily_key)
    max_results = 1
    include_raw = False

    response = client.search(
        query=search_query, max_results=max_results, include_raw_content=include_raw
    )
    print(response)
    results = response.get("results", [])
    titles = [result["title"] for result in results]
    contents = [_format_content(result) for result in results[:max_results]]
    print(titles, contents)
    return {"sources_gathered": titles, "web_research_results": contents}


def llm(
    developer_prompt,
    user_prompt,
    temperature=1,
    response_format={"type": "json_object"},
):
    client = OpenAI(base_url=Config.AI_API_URL, api_key=Config.AI_API_KEY)
    response = client.chat.completions.create(
                                                    model=Config.LLM_MODEL,
                                                    messages=[
                                                        {"role": "developer", "content": developer_prompt},
                                                        {"role": "user", "content": user_prompt},
                                                    ],
                                                    temperature=temperature,
                                                    response_format=response_format,
                                                )
    return response.choices[0].message.content



#support functions

def _format_content(result):
    return f"""
            Fonte: {result['title']}:\n===\n
            Url: {result['url']}\n===\n
            Contenuto più rilevante: {result['content']}\n===\n
            """

def optimize_search_query(research_topic):
    formatted_instructions = query_writer_instructions.format(
        research_topic=research_topic
    )
    result = llm(formatted_instructions, f"Genera una query per la ricerca web tenendo conto che oggi è :{today}")
    obj = json.loads(result)
    return obj

def rifletti_sul_riassunto(research_topic, running_summary):
    result = llm(
        reflection_instructions.format(research_topic=research_topic),
        f"Identifica una lacuna e genera una domanda per la prossima ricerca basandoti su: {running_summary}",
    )
    return json.loads(result)

# Sintetizza i risultati della ricerca in un riassunto coerente
def summarize_sources(web_research_results, research_topic, running_summary=None):
    current_results = web_research_results[-1]  # solo ultimo risultato
    if running_summary:
        message = (
            f"Estendi questo riassunto: {running_summary} \n\n"
            f"Con questi nuovi risultati: {current_results} "
            f"Sul tema: {research_topic}"
        )
    else:
        message = (
            f"Genera un riassunto di questi risultati: {current_results}"
            f"Sul tema: {research_topic}"
        )
    output_formatter = None  # Vogliamo del testo semplice
    return llm(summarizer_instructions, message, 0.2, output_formatter)



#CHAINLIT GUI

@cl.on_message
async def main(message: cl.Message):
    # Your custom logic goes here...
    user_message = message.content
    osq = optimize_search_query(user_message)

    # feedback per l'amoeba(ovvero me medesimo)
    query, aspect, reason = osq["query"], osq["aspect"], osq["reason"]
    await cl.Message(
        author="system_assistant",
        content=f"Query di ricerca ottimizzata: In {query}. In Mi sono soffermato su questo aspetto: \n {aspect}. \n Per questo motivo: \n {reason}. \n",
    ).send()

    running_summary = None
    max_cycles = 2

    while True:

        # esegui la ricerca web
        results = web_research(query)

        summary = summarize_sources(
            results["web_research_results"], query, running_summary
        )
        running_summary = summary

        # Send a response back to the user
        await cl.Message(
            author="system_assistant",
            content=f"Fonti trovate: {results['sources_gathered'][0]}",
        ).send()

        # summary = llm("sei un assistente preparato e sai riassumere le informazioni perfettamente.",
        #         f"Ecco le informazioni che devi riassumere: {results['web_research_results']}",
        #         0.2, None
        #             )

        await cl.Message(
            author="system_assistant", content=f"Riassunto attuale: {summary}"
        ).send()

        max_cycles -= 1
        if max_cycles <= 0:
            break

        # prossima query verso il ciclo finale parte 3

        ros = rifletti_sul_riassunto(query, summary)
        query = ros.get("domanda_approfondimento", f"Dimmi di più su {query}")
        lacuna_conoscenza = ros.get("lacuna_conoscenza", "")

        await cl.Message(
            author="system_assistant",
            content=f"Prossima ricerca: \n{query}.\n Mi sono soffermato su questo perchè' : \n {lacuna_conoscenza}",
        ).send()
