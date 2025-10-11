from dataclasses import dataclass

from aiwebexplorer.dependencies import get_agent_dep


@dataclass
class AgentsIds: ...


model_id_map = {
    "togetherai": "openai/gpt-oss-20b",
    "deepseek": "chat",
    "openai": "gpt4o",
}

evaluate_request_agent = get_agent_dep()(
    name="evaluate_request_agent",
    instructions=[
        "You will evaluate the request of a user to extract information from a web page.",
        "You need to make sure that the request is valid.",
        (
            "In order to be valid, the request must contain a url or a popular website name that you can extract "
            "the url from."
        ),
        "Make sure that the question is clear and complete.",
        "If any information is missing, return an error message explaining why you are not able to perform the task.",
        "Refine the question if necessary.",
        "Respond with: ",
        " - The url of the website where the search will be performed ([URL])",
        " - The refined question that will be used to extract the information ([QUESTION])",
        (
            " - A comma separated list of keywords that can be used to extract the information from the webpage "
            "([KEYWORDS])"
        ),
        (
            " - A marker at the end of your response to indicate if the response is successful or not. The marker "
            "should be [RESULT]: OK if the response is successful, or [RESULT]: ERROR if you are not able to "
            "perform the task ([RESULT])"
        ),
        (
            "If, for any reason, you are not able to extract either the url or the question, return the error "
            "message explaining why you are not able to perform the task ([MESSAGE])"
        ),
        "Example of a valid response: ",
        "[QUESTION]: When was the Space shuttle first launched?",
        "[URL]: https://en.wikipedia.org/wiki/Space_Shuttle",
        "[KEYWORDS]: Space shuttle, launch date",
        "[RESULT]: OK",
        "Example of an invalid response: ",
        "[MESSAGE]: The question is not clear and complete. Please refine the question.",
        "[RESULT]: ERROR",
        "In order to provide useful keywords, focus on the specific information that you are trying to extract.",
        "If the request is about some specifications of an electronic devices",
        "keywords might be 'specs', 'specifications' but also 'memory', 'cpu', 'display size' etc."
        "Try to find as many keywords as possible that can be used to target important information in the webpage.",
        (
            "For example, if you are trying to extract the launch date of the Space shuttle, the keywords should be "
            "'launch date', 'launch', 'launched', 'first launch',"
        ),
        "Do not provide obvious keywords, like 'Space shuttle'",
        "If the user requires a summary of the content, do not return any keywords.",
    ],
    model_id_map=model_id_map,
)

extraction_agent = get_agent_dep()(
    name="extraction_agent",
    instructions=[
        "Extract ONLY the requested information from the content. Be precise and concise.",
        "",
        "RULES:",
        "1. Return only what's asked - no explanations",
        "2. Extract exactly as it appears on the page",
        "3. If not found: 'Not available'",
        "4. Multiple items: one per line",
        "5. Add [SOURCE]: snippet of text where info was found",
        "6. End with [CONFIDENCE]: HIGH/MEDIUM/LOW",
        "7. If incomplete info: add [PARTIAL]",
        "",
        "Example:",
        "Question: What is the price and model?",
        "Response:",
        "$299.99",
        "iPhone 15",
        "[SOURCE]: Price: $299.99",
        "[SOURCE]: Model: iPhone 15",
        "[CONFIDENCE]: HIGH",
    ],
    model_id_map=model_id_map,
)

finalizer_agent = get_agent_dep()(
    name="finalizer_agent",
    instructions=[
        "You are a finalization agent that synthesizes extracted information into a clear, comprehensive answer.",
        "Your role is to take raw extracted information and formulate a proper response to the user's question.",
        "",
        "CRITICAL RULES:",
        "1. Read all provided extracted information carefully",
        "2. Synthesize the information into a coherent, well-structured answer",
        "3. Answer the user's question directly and completely",
        "4. If information is missing or unclear, acknowledge this in your response",
        "5. If multiple pieces of information are provided, organize them appropriately",
        "6. Do not add information that wasn't in the extracted data",
        "7. Do not return tables",
        "Example:",
        "Question: What are the main features of this product?",
        "Extracted info: 'Wireless charging, 5G connectivity, 48MP camera, 128GB storage'",
        "Response: 'The main features of this product include:",
        "- Wireless charging capability",
        "- 5G connectivity for fast internet speeds",
        "- 48MP camera for high-quality photos",
        "- 128GB of storage space'",
        "",
        "Provide a complete, well-formatted answer that directly addresses the user's question.",
    ],
    model_id_map=model_id_map,
)
