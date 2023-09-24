import chainlit as cl
import openai
import os

from chainlit.prompt import Prompt, PromptMessage
from chainlit.playground.providers import ChatOpenAI

openai.api_key = os.environ.get("OPENAI_API_KEY")


template = """You are an expert in \[*Python*\] and an educator. Your job is to explain to me one thing, in a very clear, jargon free way, from first principles. I have \[*a Masters Degree*\], but am \[*completely untrained*\] in \[*Coding*\].

I would like to understand

\- \[{input}\] from first principles.

You never give me large chunks of text or lectures. Instead, you ask me what I know, and try to get me to explain what I understand and don't understand.

Before telling me anything, you always ask me to guess what the answer might be first and your explanations work with what vou read from my guesses and attempts to understand.

Let’s start.:
```"""


settings = {
    "model": "gpt-3.5-turbo",
    "temperature": 0,
    "max_tokens": 500,
    "top_p": 1,
    "frequency_penalty": 0,
    "presence_penalty": 0,
    # "stop": ["```"],
}

@cl.on_chat_start
async def start():
    content = "What do you want to learn about?"

    await cl.Message(
        content=content,
    ).send()


@cl.on_message
async def main(message: str):
    # Create the prompt object for the Prompt Playground
    prompt = Prompt(
        provider=ChatOpenAI.id,
        messages=[
            PromptMessage(
                role="user",
                template=template,
                formatted=template.format(input=message)
            )
        ],
        settings=settings,
        inputs={"input": message},
    )

    # Prepare the message for streaming
    msg = cl.Message(
        content="",
        # language="sql",
    )

    # Call OpenAI
    async for stream_resp in await openai.ChatCompletion.acreate(
        messages=[m.to_openai() for m in prompt.messages], stream=True, **settings
    ):
        token = stream_resp.choices[0]["delta"].get("content", "")
        await msg.stream_token(token)

    # Update the prompt object with the completion
    prompt.completion = msg.content
    msg.prompt = prompt

    # Send and close the message stream
    await msg.send()
