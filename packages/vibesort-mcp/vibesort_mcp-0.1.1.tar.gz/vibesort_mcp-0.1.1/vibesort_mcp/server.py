from mcp.server.fastmcp import FastMCP
from openai import OpenAI, AuthenticationError
from pydantic import BaseModel, Field
from typing import Any
from argparse import ArgumentParser
import logging

class VibeSortInput(BaseModel):
    data: list[Any] = Field(..., description="The list of items to be sorted.")
    key: str = Field(None, description="Optional key function for sorting.")
    
def main():
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s | %(levelname)-8s | %(message)s',
        datefmt='%H:%M:%S'
    )
    logger = logging.getLogger(__name__)

    parser = ArgumentParser()
    parser.add_argument('--openai-api-key', type=str, help='OpenAI API key')
    args = parser.parse_args()

    if not args.openai_api_key:
        logger.error("❌ No OpenAI API key provided")
        raise ValueError("Please provide an OpenAI API key via --openai-api-key argument.")

    openai_api_key = args.openai_api_key


    try:
        client = OpenAI(api_key=openai_api_key)
        _result = client.models.list()

        logger.info("VibeSort MCP Server: Initializing Server...")

        vibe_sort_mcp = FastMCP(name="VibeSort MCP")

        @vibe_sort_mcp.tool()
        def sort(input_data: VibeSortInput) -> list[Any]:
            """Sorts an array of items as needed. Input is a VibeSortInput object containing an iterable array or tuple of strings or ints"""
            data = input_data.data
            key = input_data.key
            if isinstance(data, (list, tuple)):
                if isinstance(data, tuple):
                    data = list(data)
                else:
                    pass
            else:
                raise ValueError("Unsupported data type. Please provide a list or array.")

            sort_instruction_prompt = f"""You are sorting algorithm. You are given a list of values, and you must sort them in ascending order, and return them in a pythonic string format. Each request includes an array of data, and a sorting key. Interperet the key, and sort the data accordingly. If no key is provided, sort the data in ascending order.
                Example 1: {{'data': [1, 4, 7, 10, 6, 8], 'key':'value'}} -> [1, 4, 6, 7, 8, 10]
                Example 2: {{'data': ['apple', 'banana', 'cherry'], 'key':'alphabetical'}} -> ['apple', 'banana', 'cherry']
                Example 3: {{'data': [-4 , -2, 0 , 1, 7], 'key':'absolute value'}} -> [0, 1, -2, -4, 7]
            """

            input_string = f"data: {data}, key: {key}"

            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": sort_instruction_prompt},
                    {"role": "user", "content": input_string}
                ],
                temperature=0.5
            )

            result_string = response.choices[0].message.content.strip('[] \n')
            result = result_string.split(',')

            return result

        logger.info("VibeSort MCP Server: Starting...")
        vibe_sort_mcp.run()
        logger.info("VibeSort MCP Server: Running")
    except AuthenticationError as e:
        logger.error("Invalid OpenAI API key.")
        raise e

if __name__ == "__main__":
    main()