import chainlit as cl
import openai
import os

from chainlit.prompt import Prompt, PromptMessage
from chainlit.playground.providers import ChatOpenAI
from chainlit import user_session


openai.api_key = os.environ.get("OPENAI_API_KEY")


socratic_system_message = """You are a Socratic tutor. Use the following principles in responding to students:

- Ask thought-provoking, open-ended questions that challenge students' preconceptions and encourage them to engage in deeper reflection and critical thinking.
- Facilitate open and respectful dialogue among students, creating an environment where diverse viewpoints are valued and students feel comfortable sharing their ideas.
- Actively listen to students' responses, paying careful attention to their underlying thought processes and making a genuine effort to understand their perspectives.
- Guide students in their exploration of topics by encouraging them to discover answers independently, rather than providing direct answers, to enhance their reasoning and analytical skills.
- Promote critical thinking by encouraging students to question assumptions, evaluate evidence, and consider alternative viewpoints in order to arrive at well-reasoned conclusions.
- Demonstrate humility by acknowledging your own limitations and uncertainties, modeling a growth mindset and exemplifying the value of lifelong learning.
"""


settings = {
    "model": "gpt-3.5-turbo",
    "temperature": 0,
    "max_tokens": 500,
    "top_p": 1,
    "frequency_penalty": 0,
    "presence_penalty": 0,
}


@cl.on_chat_start
async def start():
    """Starting message!"""
    question = "What do you want to learn about?"
    res = await cl.AskUserMessage(content=question).send()
    if res:
        user_session.set("topic", res['content'])
        
        system_message = PromptMessage(formatted=socratic_system_message, role="system")
        user_message = PromptMessage(formatted=f"Help me understand {res['content']}", role="user")

        prompt = Prompt(
            provider=ChatOpenAI.id,
            messages=[system_message, user_message],
            settings=settings,
        )
        # Prepare the message for streaming
        msg = cl.Message(content="")

        # Call OpenAI
        async for stream_resp in await openai.ChatCompletion.acreate(
            messages=[m.to_openai() for m in prompt.messages], stream=True, **settings
        ):
            token = stream_resp.choices[0]["delta"].get("content", "")
            await msg.stream_token(token)

        # Update the prompt object with the completion
        prompt.completion = msg.content
        msg.prompt = prompt
        
        # add the assistant response back to prompt
        assistant_message = PromptMessage(formatted=msg.content, role="assistant")
        prompt.messages.append(assistant_message)
        user_session.set('prompt', prompt)



@cl.on_message
async def main(message: str):
    # Create the prompt object
    prompt = user_session.get("prompt")
    
    # append the user message
    prompt.messages.append(PromptMessage(formatted=message, role="user"))

    # Prepare the message for streaming
    msg = cl.Message(content="")

    # Call OpenAI
    async for stream_resp in await openai.ChatCompletion.acreate(
        messages=[m.to_openai() for m in prompt.messages], stream=True, **settings
    ):
        token = stream_resp.choices[0]["delta"].get("content", "")
        await msg.stream_token(token)

    # Update the prompt object with the completion
    prompt.completion = msg.content
    msg.prompt = prompt
    
    # add the assistant response back to prompt
    assistant_message = PromptMessage(formatted=msg.content, role="assistant")
    prompt.messages.append(assistant_message)

    # Send and close the message stream
    await msg.send()
    user_session.set('prompt', prompt)
