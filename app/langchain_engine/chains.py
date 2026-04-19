from langchain_groq import ChatGroq
from langchain_core.output_parsers import PydanticOutputParser, StrOutputParser
from langchain_core.runnables import RunnableLambda
from app.langchain_engine.prompts import review_prompt
from app.langchain_engine.output_schemas import ReviewOutput
from app.github.diff_parser import parse_diff
from dotenv import load_dotenv
import os
import re

load_dotenv()

def clean_json(text: str) -> str:
    text = text.strip()
    text = re.sub(r"^```json\s*", "", text)
    text = re.sub(r"^```\s*", "", text)
    text = re.sub(r"\s*```$", "", text)
    return text.strip()

def get_review_chain():
    llm = ChatGroq(
        model="llama-3.3-70b-versatile",
        temperature=0,
        api_key=os.getenv("GROQ_API_KEY")
    )
    parser = PydanticOutputParser(pydantic_object=ReviewOutput)

    return (
        review_prompt
        | llm
        | StrOutputParser()
        | RunnableLambda(clean_json)
        | parser
    )

async def run_review_chain(
    filename: str,
    patch: str,
    valid_lines: list = None
) -> ReviewOutput:
    chain = get_review_chain()
    return await chain.ainvoke({
        "filename": filename,
        "patch": patch,
        "valid_lines": str(valid_lines) if valid_lines else "unknown"
    })