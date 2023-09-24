import chainlit as cl


@cl.on_chat_start
async def start():
    # Send the elements globally
    await cl.Text(content="Here is a side text document", name="text1", display="side").send()
    await cl.Text(content="Here is a page text document", name="text2", display="page").send()

    # Send the same message twice
    content = "Here is image1, a nice image of a cat! As well as text1 and text2!"

    await cl.Message(
        content=content,
    ).send()

    await cl.Message(
        content=content,
    ).send()
    
    topic = await cl.AskUserMessage(content="What do you want to learn about?", timeout=10).send()
    if topic:
        await cl.Message(
            content=f"You want to learn about: {topic['content']}",
        ).send()
