
import gradio as gr
from app import demo as app
import os

_docs = {'AgentChatbot': {'description': 'Creates a chatbot that displays user-submitted messages and responses. Supports a subset of Markdown including bold, italics, code, tables.\nAlso supports audio/video/image files, which are displayed in the AgentChatbot, and other kinds of files which are displayed as links. This\ncomponent is usually used as an output component.\n', 'members': {'__init__': {'value': {'type': 'list[MessageDict | Message] | TupleFormat | Callable | None', 'default': 'None', 'description': 'Default list of messages to show in chatbot, where each message is of the format {"role": "user", "content": "Help me."}. Role can be one of "user", "assistant", or "system". Content should be either text, or media passed as a Gradio component, e.g. {"content": gr.Image("lion.jpg")}. If a function is provided, the function will be called each time the app loads to set the initial value of this component.'}, 'type': {'type': 'Literal["messages", "tuples"] | None', 'default': 'None', 'description': 'The format of the messages passed into the chat history parameter of `fn`. If "messages", passes the value as a list of dictionaries with openai-style "role" and "content" keys. The "content" key\'s value should be one of the following - (1) strings in valid Markdown (2) a dictionary with a "path" key and value corresponding to the file to display or (3) an instance of a Gradio component. At the moment Image, Plot, Video, Gallery, Audio, HTML, and Model3D are supported. The "role" key should be one of \'user\' or \'assistant\'. Any other roles will not be displayed in the output. If this parameter is \'tuples\', expects a `list[list[str | None | tuple]]`, i.e. a list of lists. The inner list should have 2 elements: the user message and the response message, but this format is deprecated.'}, 'label': {'type': 'str | I18nData | None', 'default': 'None', 'description': 'the label for this component. Appears above the component and is also used as the header if there are a table of examples for this component. If None and used in a `gr.Interface`, the label will be the name of the parameter this component is assigned to.'}, 'every': {'type': 'Timer | float | None', 'default': 'None', 'description': 'Continously calls `value` to recalculate it if `value` is a function (has no effect otherwise). Can provide a Timer whose tick resets `value`, or a float that provides the regular interval for the reset Timer.'}, 'inputs': {'type': 'Component | Sequence[Component] | set[Component] | None', 'default': 'None', 'description': 'Components that are used as inputs to calculate `value` if `value` is a function (has no effect otherwise). `value` is recalculated any time the inputs change.'}, 'show_label': {'type': 'bool | None', 'default': 'None', 'description': 'if True, will display label.'}, 'container': {'type': 'bool', 'default': 'True', 'description': 'If True, will place the component in a container - providing some extra padding around the border.'}, 'scale': {'type': 'int | None', 'default': 'None', 'description': 'relative size compared to adjacent Components. For example if Components A and B are in a Row, and A has scale=2, and B has scale=1, A will be twice as wide as B. Should be an integer. scale applies in Rows, and to top-level Components in Blocks where fill_height=True.'}, 'min_width': {'type': 'int', 'default': '160', 'description': 'minimum pixel width, will wrap if not sufficient screen space to satisfy this value. If a certain scale value results in this Component being narrower than min_width, the min_width parameter will be respected first.'}, 'visible': {'type': 'bool', 'default': 'True', 'description': 'If False, component will be hidden.'}, 'elem_id': {'type': 'str | None', 'default': 'None', 'description': 'An optional string that is assigned as the id of this component in the HTML DOM. Can be used for targeting CSS styles.'}, 'elem_classes': {'type': 'list[str] | str | None', 'default': 'None', 'description': 'An optional list of strings that are assigned as the classes of this component in the HTML DOM. Can be used for targeting CSS styles.'}, 'autoscroll': {'type': 'bool', 'default': 'True', 'description': 'If True, will automatically scroll to the bottom of the textbox when the value changes, unless the user scrolls up. If False, will not scroll to the bottom of the textbox when the value changes.'}, 'render': {'type': 'bool', 'default': 'True', 'description': 'If False, component will not render be rendered in the Blocks context. Should be used if the intention is to assign event listeners now but render the component later.'}, 'key': {'type': 'int | str | tuple[int | str, ...] | None', 'default': 'None', 'description': "in a gr.render, Components with the same key across re-renders are treated as the same component, not a new component. Properties set in 'preserved_by_key' are not reset across a re-render."}, 'preserved_by_key': {'type': 'list[str] | str | None', 'default': '"value"', 'description': "A list of parameters from this component's constructor. Inside a gr.render() function, if a component is re-rendered with the same key, these (and only these) parameters will be preserved in the UI (if they have been changed by the user or an event listener) instead of re-rendered based on the values provided during constructor."}, 'height': {'type': 'int | str | None', 'default': '400', 'description': 'The height of the component, specified in pixels if a number is passed, or in CSS units if a string is passed. If messages exceed the height, the component will scroll.'}, 'resizable': {'type': 'bool', 'default': 'False', 'description': 'If True, the user of the Gradio app can resize the chatbot by dragging the bottom right corner.'}, 'resizeable': {'type': 'bool', 'default': 'False', 'description': None}, 'max_height': {'type': 'int | str | None', 'default': 'None', 'description': 'The maximum height of the component, specified in pixels if a number is passed, or in CSS units if a string is passed. If messages exceed the height, the component will scroll. If messages are shorter than the height, the component will shrink to fit the content. Will not have any effect if `height` is set and is smaller than `max_height`.'}, 'min_height': {'type': 'int | str | None', 'default': 'None', 'description': 'The minimum height of the component, specified in pixels if a number is passed, or in CSS units if a string is passed. If messages exceed the height, the component will expand to fit the content. Will not have any effect if `height` is set and is larger than `min_height`.'}, 'editable': {'type': 'Literal["llm"] | None', 'default': 'None', 'description': 'Allows user to edit messages in the chatbot. If set to "user", allows editing of user messages. If set to "all", allows editing of assistant messages as well.'}, 'latex_delimiters': {'type': 'list[dict[str, str | bool]] | None', 'default': 'None', 'description': 'A list of dicts of the form {"left": open delimiter (str), "right": close delimiter (str), "display": whether to display in newline (bool)} that will be used to render LaTeX expressions. If not provided, `latex_delimiters` is set to `[{ "left": "$$", "right": "$$", "display": True }]`, so only expressions enclosed in $$ delimiters will be rendered as LaTeX, and in a new line. Pass in an empty list to disable LaTeX rendering. For more information, see the [KaTeX documentation](https://katex.org/docs/autorender.html).'}, 'rtl': {'type': 'bool', 'default': 'False', 'description': 'If True, sets the direction of the rendered text to right-to-left. Default is False, which renders text left-to-right.'}, 'show_share_button': {'type': 'bool | None', 'default': 'None', 'description': 'If True, will show a share icon in the corner of the component that allows user to share outputs to Hugging Face Spaces Discussions. If False, icon does not appear. If set to None (default behavior), then the icon appears if this Gradio app is launched on Spaces, but not otherwise.'}, 'show_copy_button': {'type': 'bool', 'default': 'False', 'description': 'If True, will show a copy button for each chatbot message.'}, 'watermark': {'type': 'str | None', 'default': 'None', 'description': 'If provided, this text will be appended to the end of messages copied from the chatbot, after a blank line. Useful for indicating that the message is generated by an AI model.'}, 'avatar_images': {'type': 'tuple[\n        str | Path | None,\n        str | Path | None,\n        str | Path | None,\n    ]\n    | None', 'default': 'None', 'description': 'Tuple of two avatar image paths or URLs for user and bot (in that order). Pass None for either the user or bot image to skip. Must be within the working directory of the Gradio app or an external URL.'}, 'sanitize_html': {'type': 'bool', 'default': 'True', 'description': 'If False, will disable HTML sanitization for chatbot messages. This is not recommended, as it can lead to security vulnerabilities.'}, 'render_markdown': {'type': 'bool', 'default': 'True', 'description': 'If False, will disable Markdown rendering for chatbot messages.'}, 'feedback_options': {'type': 'list[str] | tuple[str, ...] | None', 'default': '"Like", "Dislike"', 'description': 'A list of strings representing the feedback options that will be displayed to the user. The exact case-sensitive strings "Like" and "Dislike" will render as thumb icons, but any other choices will appear under a separate flag icon.'}, 'feedback_value': {'type': 'Sequence[str | None] | None', 'default': 'None', 'description': 'A list of strings representing the feedback state for entire chat. Only works when type="messages". Each entry in the list corresponds to that assistant message, in order, and the value is the feedback given (e.g. "Like", "Dislike", or any custom feedback option) or None if no feedback was given for that message.'}, 'line_breaks': {'type': 'bool', 'default': 'True', 'description': 'If True (default), will enable Github-flavored Markdown line breaks in chatbot messages. If False, single new lines will be ignored. Only applies if `render_markdown` is True.'}, 'layout': {'type': 'Literal["panel", "bubble"] | None', 'default': 'None', 'description': 'If "panel", will display the chatbot in a llm style layout. If "bubble", will display the chatbot with message bubbles, with the user and bot messages on alterating sides. Will default to "bubble".'}, 'placeholder': {'type': 'str | None', 'default': 'None', 'description': 'a placeholder message to display in the chatbot when it is empty. Centered vertically and horizontally in the AgentChatbot. Supports Markdown and HTML. If None, no placeholder is displayed.'}, 'examples': {'type': 'list[ExampleMessage] | None', 'default': 'None', 'description': 'A list of example messages to display in the chatbot before any user/assistant messages are shown. Each example should be a dictionary with an optional "text" key representing the message that should be populated in the AgentChatbot when clicked, an optional "files" key, whose value should be a list of files to populate in the AgentChatbot, an optional "icon" key, whose value should be a filepath or URL to an image to display in the example box, and an optional "display_text" key, whose value should be the text to display in the example box. If "display_text" is not provided, the value of "text" will be displayed.'}, 'group_consecutive_messages': {'type': 'bool', 'default': 'True', 'description': 'If True, will display consecutive messages from the same role in the same bubble. If False, will display each message in a separate bubble. Defaults to True.'}, 'allow_tags': {'type': 'list[str] | bool', 'default': 'False', 'description': 'If a list of tags is provided, these tags will be preserved in the output chatbot messages, even if `sanitize_html` is `True`. For example, if this list is ["thinking"], the tags `<thinking>` and `</thinking>` will not be removed. If True, all custom tags (non-standard HTML tags) will be preserved. If False, no tags will be preserved (default behavior).'}}, 'postprocess': {'value': {'type': 'Sequence[\n        tuple[\n            typing.Union[str, tuple[str], NoneType][\n                str, tuple[str], None\n            ],\n            typing.Union[str, tuple[str], NoneType][\n                str, tuple[str], None\n            ],\n        ]\n        | list[\n            typing.Union[str, tuple[str], NoneType][\n                str, tuple[str], None\n            ]\n        ]\n    ]\n    | list[MessageDict | Message]\n    | None', 'description': "If type is `tuples`, expects a `list[list[str | None | tuple]]`, i.e. a list of lists. The inner list should have 2 elements: the user message and the response message. The individual messages can be (1) strings in valid Markdown, (2) tuples if sending files: (a filepath or URL to a file, [optional string alt text]) -- if the file is image/video/audio, it is displayed in the AgentChatbot, or (3) None, in which case the message is not displayed. If type is 'messages', passes the value as a list of dictionaries with 'role' and 'content' keys. The `content` key's value supports everything the `tuples` format supports."}}, 'preprocess': {'return': {'type': 'list[list[str | tuple[str] | tuple[str, str] | None]]\n    | list[MessageDict]', 'description': "If type is 'tuples', passes the messages in the chatbot as a `list[list[str | None | tuple]]`, i.e. a list of lists. The inner list has 2 elements: the user message and the response message. Each message can be (1) a string in valid Markdown, (2) a tuple if there are displayed files: (a filepath or URL to a file, [optional string alt text]), or (3) None, if there is no message displayed. If type is 'messages', passes the value as a list of dictionaries with 'role' and 'content' keys. The `content` key's value supports everything the `tuples` format supports."}, 'value': None}}, 'events': {'change': {'type': None, 'default': None, 'description': 'Triggered when the value of the AgentChatbot changes either because of user input (e.g. a user types in a textbox) OR because of a function update (e.g. an image receives a value from the output of an event trigger). See `.input()` for a listener that is only triggered by user input.'}, 'select': {'type': None, 'default': None, 'description': 'Event listener for when the user selects or deselects the AgentChatbot. Uses event data gradio.SelectData to carry `value` referring to the label of the AgentChatbot, and `selected` to refer to state of the AgentChatbot. See EventData documentation on how to use this event data'}, 'like': {'type': None, 'default': None, 'description': 'This listener is triggered when the user likes/dislikes from within the AgentChatbot. This event has EventData of type gradio.LikeData that carries information, accessible through LikeData.index and LikeData.value. See EventData documentation on how to use this event data.'}, 'retry': {'type': None, 'default': None, 'description': 'This listener is triggered when the user clicks the retry button in the chatbot message.'}, 'undo': {'type': None, 'default': None, 'description': 'This listener is triggered when the user clicks the undo button in the chatbot message.'}, 'example_select': {'type': None, 'default': None, 'description': 'This listener is triggered when the user clicks on an example from within the AgentChatbot. This event has SelectData of type gradio.SelectData that carries information, accessible through SelectData.index and SelectData.value. See SelectData documentation on how to use this event data.'}, 'option_select': {'type': None, 'default': None, 'description': 'This listener is triggered when the user clicks on an option from within the AgentChatbot. This event has SelectData of type gradio.SelectData that carries information, accessible through SelectData.index and SelectData.value. See SelectData documentation on how to use this event data.'}, 'copy': {'type': None, 'default': None, 'description': 'This listener is triggered when the user copies content from the AgentChatbot. Uses event data gradio.CopyData to carry information about the copied content. See EventData documentation on how to use this event data'}, 'edit': {'type': None, 'default': None, 'description': 'This listener is triggered when the user edits the AgentChatbot (e.g. image) using the built-in editor.'}}}, '__meta__': {'additional_interfaces': {'MessageDict': {'source': 'class MessageDict(TypedDict):\n    name: str\n    content: str | FileDataDict | tuple | Component\n    role: Literal["user", "assistant", "system"]\n    metadata: NotRequired[MetadataDict]\n    options: NotRequired[list[OptionDict]]', 'refs': ['FileDataDict', 'MetadataDict', 'OptionDict']}, 'FileDataDict': {'source': 'class FileDataDict(TypedDict):\n    path: str  # server filepath\n    url: NotRequired[str | None]  # normalised server url\n    size: NotRequired[int | None]  # size in bytes\n    orig_name: NotRequired[str | None]  # original filename\n    mime_type: NotRequired[str | None]\n    is_stream: NotRequired[bool]\n    meta: dict[Literal["_type"], Literal["gradio.FileData"]]'}, 'MetadataDict': {'source': 'class MetadataDict(TypedDict):\n    title: NotRequired[str]\n    id: NotRequired[int | str]\n    parent_id: NotRequired[int | str]\n    log: NotRequired[str]\n    duration: NotRequired[float]\n    status: NotRequired[Literal["pending", "done"]]'}, 'OptionDict': {'source': 'class OptionDict(TypedDict):\n    value: str\n    label: NotRequired[str]'}, 'Message': {'source': 'class Message(GradioModel):\n    name: str\n    role: str\n    metadata: MetadataDict | None = None\n    content: Union[str, FileMessage, ComponentMessage]\n    options: list[OptionDict] | None = None', 'refs': ['MetadataDict', 'FileMessage', 'ComponentMessage', 'OptionDict']}, 'FileMessage': {'source': 'class FileMessage(GradioModel):\n    file: FileData\n    alt_text: str | None = None'}, 'ComponentMessage': {'source': 'class ComponentMessage(GradioModel):\n    component: str\n    value: Any\n    constructor_args: dict[str, Any]\n    props: dict[str, Any]'}}, 'user_fn_refs': {'AgentChatbot': ['MessageDict', 'Message']}}}

abs_path = os.path.join(os.path.dirname(__file__), "css.css")

with gr.Blocks(
    css=abs_path,
    theme=gr.themes.Default(
        font_mono=[
            gr.themes.GoogleFont("Inconsolata"),
            "monospace",
        ],
    ),
) as demo:
    gr.Markdown(
"""
# `gradio_autopilot_chatbot`

<div style="display: flex; gap: 7px;">
<a href="https://pypi.org/project/gradio_autopilot_chatbot/" target="_blank"><img alt="PyPI - Version" src="https://img.shields.io/pypi/v/gradio_autopilot_chatbot"></a>  
</div>

Agent chatbot for gradio application for Sail Autopilot
""", elem_classes=["md-custom"], header_links=True)
    app.render()
    gr.Markdown(
"""
## Installation

```bash
pip install gradio_autopilot_chatbot
```

## Usage

```python

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

```
""", elem_classes=["md-custom"], header_links=True)


    gr.Markdown("""
## `AgentChatbot`

### Initialization
""", elem_classes=["md-custom"], header_links=True)

    gr.ParamViewer(value=_docs["AgentChatbot"]["members"]["__init__"], linkify=['MessageDict', 'FileDataDict', 'MetadataDict', 'OptionDict', 'Message', 'FileMessage', 'ComponentMessage'])


    gr.Markdown("### Events")
    gr.ParamViewer(value=_docs["AgentChatbot"]["events"], linkify=['Event'])




    gr.Markdown("""

### User function

The impact on the users predict function varies depending on whether the component is used as an input or output for an event (or both).

- When used as an Input, the component only impacts the input signature of the user function.
- When used as an output, the component only impacts the return signature of the user function.

The code snippet below is accurate in cases where the component is used as both an input and an output.

- **As input:** Is passed, if type is 'tuples', passes the messages in the chatbot as a `list[list[str | None | tuple]]`, i.e. a list of lists. The inner list has 2 elements: the user message and the response message. Each message can be (1) a string in valid Markdown, (2) a tuple if there are displayed files: (a filepath or URL to a file, [optional string alt text]), or (3) None, if there is no message displayed. If type is 'messages', passes the value as a list of dictionaries with 'role' and 'content' keys. The `content` key's value supports everything the `tuples` format supports.
- **As output:** Should return, if type is `tuples`, expects a `list[list[str | None | tuple]]`, i.e. a list of lists. The inner list should have 2 elements: the user message and the response message. The individual messages can be (1) strings in valid Markdown, (2) tuples if sending files: (a filepath or URL to a file, [optional string alt text]) -- if the file is image/video/audio, it is displayed in the AgentChatbot, or (3) None, in which case the message is not displayed. If type is 'messages', passes the value as a list of dictionaries with 'role' and 'content' keys. The `content` key's value supports everything the `tuples` format supports.

 ```python
def predict(
    value: list[list[str | tuple[str] | tuple[str, str] | None]]
    | list[MessageDict]
) -> Sequence[
        tuple[
            typing.Union[str, tuple[str], NoneType][
                str, tuple[str], None
            ],
            typing.Union[str, tuple[str], NoneType][
                str, tuple[str], None
            ],
        ]
        | list[
            typing.Union[str, tuple[str], NoneType][
                str, tuple[str], None
            ]
        ]
    ]
    | list[MessageDict | Message]
    | None:
    return value
```
""", elem_classes=["md-custom", "AgentChatbot-user-fn"], header_links=True)




    code_MessageDict = gr.Markdown("""
## `MessageDict`
```python
class MessageDict(TypedDict):
    name: str
    content: str | FileDataDict | tuple | Component
    role: Literal["user", "assistant", "system"]
    metadata: NotRequired[MetadataDict]
    options: NotRequired[list[OptionDict]]
```""", elem_classes=["md-custom", "MessageDict"], header_links=True)

    code_FileDataDict = gr.Markdown("""
## `FileDataDict`
```python
class FileDataDict(TypedDict):
    path: str  # server filepath
    url: NotRequired[str | None]  # normalised server url
    size: NotRequired[int | None]  # size in bytes
    orig_name: NotRequired[str | None]  # original filename
    mime_type: NotRequired[str | None]
    is_stream: NotRequired[bool]
    meta: dict[Literal["_type"], Literal["gradio.FileData"]]
```""", elem_classes=["md-custom", "FileDataDict"], header_links=True)

    code_MetadataDict = gr.Markdown("""
## `MetadataDict`
```python
class MetadataDict(TypedDict):
    title: NotRequired[str]
    id: NotRequired[int | str]
    parent_id: NotRequired[int | str]
    log: NotRequired[str]
    duration: NotRequired[float]
    status: NotRequired[Literal["pending", "done"]]
```""", elem_classes=["md-custom", "MetadataDict"], header_links=True)

    code_OptionDict = gr.Markdown("""
## `OptionDict`
```python
class OptionDict(TypedDict):
    value: str
    label: NotRequired[str]
```""", elem_classes=["md-custom", "OptionDict"], header_links=True)

    code_Message = gr.Markdown("""
## `Message`
```python
class Message(GradioModel):
    name: str
    role: str
    metadata: MetadataDict | None = None
    content: Union[str, FileMessage, ComponentMessage]
    options: list[OptionDict] | None = None
```""", elem_classes=["md-custom", "Message"], header_links=True)

    code_FileMessage = gr.Markdown("""
## `FileMessage`
```python
class FileMessage(GradioModel):
    file: FileData
    alt_text: str | None = None
```""", elem_classes=["md-custom", "FileMessage"], header_links=True)

    code_ComponentMessage = gr.Markdown("""
## `ComponentMessage`
```python
class ComponentMessage(GradioModel):
    component: str
    value: Any
    constructor_args: dict[str, Any]
    props: dict[str, Any]
```""", elem_classes=["md-custom", "ComponentMessage"], header_links=True)

    demo.load(None, js=r"""function() {
    const refs = {
            MessageDict: ['FileDataDict', 'MetadataDict', 'OptionDict'], 
            FileDataDict: [], 
            MetadataDict: [], 
            OptionDict: [], 
            Message: ['MetadataDict', 'FileMessage', 'ComponentMessage', 'OptionDict'], 
            FileMessage: [], 
            ComponentMessage: [], };
    const user_fn_refs = {
          AgentChatbot: ['MessageDict', 'Message'], };
    requestAnimationFrame(() => {

        Object.entries(user_fn_refs).forEach(([key, refs]) => {
            if (refs.length > 0) {
                const el = document.querySelector(`.${key}-user-fn`);
                if (!el) return;
                refs.forEach(ref => {
                    el.innerHTML = el.innerHTML.replace(
                        new RegExp("\\b"+ref+"\\b", "g"),
                        `<a href="#h-${ref.toLowerCase()}">${ref}</a>`
                    );
                })
            }
        })

        Object.entries(refs).forEach(([key, refs]) => {
            if (refs.length > 0) {
                const el = document.querySelector(`.${key}`);
                if (!el) return;
                refs.forEach(ref => {
                    el.innerHTML = el.innerHTML.replace(
                        new RegExp("\\b"+ref+"\\b", "g"),
                        `<a href="#h-${ref.toLowerCase()}">${ref}</a>`
                    );
                })
            }
        })
    })
}

""")

demo.launch()
