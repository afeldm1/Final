from typing import Union
from fastapi import FastAPI, Request
from pydantic import BaseModel
import openai
import os

app = FastAPI()

openai.api_key = os.getenv("OPENAI_API_KEY")

class MCPRequest(BaseModel):
    jsonrpc: str
    method: str
    params: dict
    id: Union[str, int]

@app.post("/")
async def handle_mcp(request: Request):
    body = await request.json()
    mcp = MCPRequest(**body)

    if mcp.method == "complete":
        prompt = mcp.params.get("prompt", "")
        system = mcp.params.get("system_prompt", "You are a helpful assistant.")
        model = "gpt-4"

        try:
            completion = openai.ChatCompletion.create(
                model=model,
                messages=[
                    {"role": "system", "content": system},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
            )

            result = completion.choices[0].message["content"]
            return {
                "jsonrpc": "2.0",
                "id": mcp.id,
                "result": {
                    "completion": result,
                }
            }

        except Exception as e:
            return {
                "jsonrpc": "2.0",
                "id": mcp.id,
                "error": {
                    "code": -32000,
                    "message": str(e)
                }
            }

    return {
        "jsonrpc": "2.0",
        "id": mcp.id,
        "error": {
            "code": -32601,
            "message": "Method not found"
        }
    }
