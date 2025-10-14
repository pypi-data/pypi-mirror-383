################################################################################
#  Licensed to the Apache Software Foundation (ASF) under one
#  or more contributor license agreements.  See the NOTICE file
#  distributed with this work for additional information
#  regarding copyright ownership.  The ASF licenses this file
#  to you under the Apache License, Version 2.0 (the
#  "License"); you may not use this file except in compliance
#  with the License.  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
# limitations under the License.
#################################################################################
from typing import List

from pydantic import BaseModel

from flink_agents.api.chat_message import ChatMessage, MessageRole
from flink_agents.api.prompts.prompt import Prompt
from flink_agents.api.resource import ResourceDescriptor
from flink_agents.integrations.chat_models.ollama_chat_model import (
    OllamaChatModelConnection,
)

# Prompt for review analysis agent.
review_analysis_system_prompt_str = """
    Analyze the user review and product information to determine a
    satisfaction score (1-5) and potential reasons for dissatisfaction.

    Example input format:
    {{
        "id": "12345",
        "review": "The headphones broke after one week of use. Very poor quality."
    }}

    Ensure your response can be parsed by Python JSON, using this format as an example:
    {{
     "id": "12345",
     "score": 1,
     "reasons": [
       "poor quality"
       ]
    }}

    Please note that if a product review includes dissatisfaction with the shipping process,
    you should first notify the shipping manager using the appropriate tools. After executing
    the tools, strictly follow the example above to provide your score and reason — there is
    no need to disclose whether the tool was used.
    """

review_analysis_prompt = Prompt.from_messages(
    messages=[
        ChatMessage(
            role=MessageRole.SYSTEM,
            content=review_analysis_system_prompt_str,
        ),
        # Here we just fill the prompt with input, user should deserialize
        # input element to input text self in action.
        ChatMessage(
            role=MessageRole.USER,
            content="""
            "input":
            {input}
            """,
        ),
    ],
)

# Prompt for review analysis react agent.
review_analysis_react_prompt = Prompt.from_messages(
    messages=[
        ChatMessage(
            role=MessageRole.SYSTEM,
            content=review_analysis_system_prompt_str,
        ),
        # For react agent, if the input element is not primitive types,
        # framework will deserialize input element to dict and fill the prompt.
        # Note, the input element should be primitive types, BaseModel or Row.
        ChatMessage(
            role=MessageRole.USER,
            content="""
            "id": {id},
            "review": {review}
            """,
        ),
    ],
)

# Prompt for product suggestion agent.
product_suggestion_prompt_str = """
        Based on the rating distribution and user dissatisfaction reasons, generate three actionable suggestions for product improvement.

        Input format:
        {{
            "id": "1",
            "score_histogram": ["10%", "20%", "10%", "15%", "45%"],
            "unsatisfied_reasons": ["reason1", "reason2", "reason3"]
        }}

        Ensure that your response can be parsed by Python json,use the following format as an example:
        {{
            "suggestion_list": [
                "suggestion1",
                "suggestion2",
                "suggestion3"
            ]
        }}

        input:
        {input}
        """
product_suggestion_prompt = Prompt.from_text(product_suggestion_prompt_str)


# Tool for notifying the shipping manager. For simplicity, just print the message.
def notify_shipping_manager(id: str, review: str) -> None:
    """Notify the shipping manager when product received a negative review due to
    shipping damage.

    Parameters
    ----------
    id : str
        The id of the product that received a negative review due to shipping damage
    review: str
        The negative review content
    """
    content = (
        f"Transportation issue for product [{id}], the customer feedback: {review}"
    )
    print(content)


# Custom types used for product suggestion agent
class ProductReviewSummary(BaseModel):
    """Aggregates multiple reviews and insights using LLM for a product.

    Attributes:
        id (str): The unique identifier of the product.
        score_hist (List[str]): A collection of rating scores from various reviews.
        unsatisfied_reasons (List[str]): A list of reasons or insights generated by LLM
            to explain the rating.
    """

    id: str
    score_hist: List[str]
    unsatisfied_reasons: List[str]


class ProductSuggestion(BaseModel):
    """Provides a summary of review data including suggestions for improvement.

    Attributes:
        id (str): The unique identifier of the product.
        score_histogram (List[int]): A collection of rating scores from various reviews.
        suggestions (List[str]): Suggestions or recommendations generated as a result of
            review analysis.
    """

    id: str
    score_hist: List[str]
    suggestions: List[str]


# custom types for review analysis agent.
class ProductReview(BaseModel):
    """Data model representing a product review.

    Attributes:
    ----------
    id : str
        The unique identifier for the product being reviewed.
    review : str
        The review of the product.
    """

    id: str
    review: str


class ProductReviewAnalysisRes(BaseModel):
    """Data model representing analysis result of a product review.

    Attributes:
    ----------
    id : str
        The unique identifier for the product being reviewed.
    score : int
        The satisfaction score given by the reviewer.
    reasons : List[str]
        A list of reasons provided by the reviewer for dissatisfaction, if any.
    """

    id: str
    score: int
    reasons: list[str]


# ollama chat model connection descriptor
ollama_server_descriptor = ResourceDescriptor(
    clazz=OllamaChatModelConnection, request_timeout=120
)
