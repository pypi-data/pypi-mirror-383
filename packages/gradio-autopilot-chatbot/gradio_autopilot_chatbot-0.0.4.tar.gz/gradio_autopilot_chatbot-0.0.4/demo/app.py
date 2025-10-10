
import gradio as gr
from gradio_autopilot_chatbot import AgentChatbot


example = AgentChatbot().example_value()

with gr.Blocks() as demo:
    with gr.Row():
        # AgentChatbot(label="Blank"),  # blank component
        AgentChatbot(
            value=example, 
            label="Populated",
            avatar_images=(
            "/Users/franklee/Documents/Projects/Development/Agent-Chatbot/agentchatbot/demo/avatars/user.png",
            "/Users/franklee/Documents/Projects/Development/Agent-Chatbot/agentchatbot/demo/avatars/terminal.png",
            "/Users/franklee/Documents/Projects/Development/Agent-Chatbot/agentchatbot/demo/avatars/robot.png",
            
            ),
            editable="llm",
    ),  # populated component


if __name__ == "__main__":
    demo.launch()
