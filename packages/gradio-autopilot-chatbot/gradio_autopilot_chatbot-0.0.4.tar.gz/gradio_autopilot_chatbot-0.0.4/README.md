---
tags: [gradio-custom-component, Chatbot]
title: gradio_agentchatbot
short_description: Agent chatbot for gradio application for Sail Autopilot
colorFrom: blue
colorTo: yellow
sdk: gradio
pinned: false
app_file: space.py
---

# `gradio_autopilot_chatbot`
<a href="https://pypi.org/project/gradio_autopilot_chatbot/" target="_blank"><img alt="PyPI - Version" src="https://img.shields.io/pypi/v/gradio_autopilot_chatbot"></a>  

Agent chatbot for gradio application for Sail Autopilot

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

## `AgentChatbot`

### Initialization

<table>
<thead>
<tr>
<th align="left">name</th>
<th align="left" style="width: 25%;">type</th>
<th align="left">default</th>
<th align="left">description</th>
</tr>
</thead>
<tbody>
<tr>
<td align="left"><code>value</code></td>
<td align="left" style="width: 25%;">

```python
list[MessageDict | Message] | TupleFormat | Callable | None
```

</td>
<td align="left"><code>None</code></td>
<td align="left">Default list of messages to show in chatbot, where each message is of the format {"role": "user", "content": "Help me."}. Role can be one of "user", "assistant", or "system". Content should be either text, or media passed as a Gradio component, e.g. {"content": gr.Image("lion.jpg")}. If a function is provided, the function will be called each time the app loads to set the initial value of this component.</td>
</tr>

<tr>
<td align="left"><code>type</code></td>
<td align="left" style="width: 25%;">

```python
Literal["messages", "tuples"] | None
```

</td>
<td align="left"><code>None</code></td>
<td align="left">The format of the messages passed into the chat history parameter of `fn`. If "messages", passes the value as a list of dictionaries with openai-style "role" and "content" keys. The "content" key's value should be one of the following - (1) strings in valid Markdown (2) a dictionary with a "path" key and value corresponding to the file to display or (3) an instance of a Gradio component. At the moment Image, Plot, Video, Gallery, Audio, HTML, and Model3D are supported. The "role" key should be one of 'user' or 'assistant'. Any other roles will not be displayed in the output. If this parameter is 'tuples', expects a `list[list[str | None | tuple]]`, i.e. a list of lists. The inner list should have 2 elements: the user message and the response message, but this format is deprecated.</td>
</tr>

<tr>
<td align="left"><code>label</code></td>
<td align="left" style="width: 25%;">

```python
str | I18nData | None
```

</td>
<td align="left"><code>None</code></td>
<td align="left">the label for this component. Appears above the component and is also used as the header if there are a table of examples for this component. If None and used in a `gr.Interface`, the label will be the name of the parameter this component is assigned to.</td>
</tr>

<tr>
<td align="left"><code>every</code></td>
<td align="left" style="width: 25%;">

```python
Timer | float | None
```

</td>
<td align="left"><code>None</code></td>
<td align="left">Continously calls `value` to recalculate it if `value` is a function (has no effect otherwise). Can provide a Timer whose tick resets `value`, or a float that provides the regular interval for the reset Timer.</td>
</tr>

<tr>
<td align="left"><code>inputs</code></td>
<td align="left" style="width: 25%;">

```python
Component | Sequence[Component] | set[Component] | None
```

</td>
<td align="left"><code>None</code></td>
<td align="left">Components that are used as inputs to calculate `value` if `value` is a function (has no effect otherwise). `value` is recalculated any time the inputs change.</td>
</tr>

<tr>
<td align="left"><code>show_label</code></td>
<td align="left" style="width: 25%;">

```python
bool | None
```

</td>
<td align="left"><code>None</code></td>
<td align="left">if True, will display label.</td>
</tr>

<tr>
<td align="left"><code>container</code></td>
<td align="left" style="width: 25%;">

```python
bool
```

</td>
<td align="left"><code>True</code></td>
<td align="left">If True, will place the component in a container - providing some extra padding around the border.</td>
</tr>

<tr>
<td align="left"><code>scale</code></td>
<td align="left" style="width: 25%;">

```python
int | None
```

</td>
<td align="left"><code>None</code></td>
<td align="left">relative size compared to adjacent Components. For example if Components A and B are in a Row, and A has scale=2, and B has scale=1, A will be twice as wide as B. Should be an integer. scale applies in Rows, and to top-level Components in Blocks where fill_height=True.</td>
</tr>

<tr>
<td align="left"><code>min_width</code></td>
<td align="left" style="width: 25%;">

```python
int
```

</td>
<td align="left"><code>160</code></td>
<td align="left">minimum pixel width, will wrap if not sufficient screen space to satisfy this value. If a certain scale value results in this Component being narrower than min_width, the min_width parameter will be respected first.</td>
</tr>

<tr>
<td align="left"><code>visible</code></td>
<td align="left" style="width: 25%;">

```python
bool
```

</td>
<td align="left"><code>True</code></td>
<td align="left">If False, component will be hidden.</td>
</tr>

<tr>
<td align="left"><code>elem_id</code></td>
<td align="left" style="width: 25%;">

```python
str | None
```

</td>
<td align="left"><code>None</code></td>
<td align="left">An optional string that is assigned as the id of this component in the HTML DOM. Can be used for targeting CSS styles.</td>
</tr>

<tr>
<td align="left"><code>elem_classes</code></td>
<td align="left" style="width: 25%;">

```python
list[str] | str | None
```

</td>
<td align="left"><code>None</code></td>
<td align="left">An optional list of strings that are assigned as the classes of this component in the HTML DOM. Can be used for targeting CSS styles.</td>
</tr>

<tr>
<td align="left"><code>autoscroll</code></td>
<td align="left" style="width: 25%;">

```python
bool
```

</td>
<td align="left"><code>True</code></td>
<td align="left">If True, will automatically scroll to the bottom of the textbox when the value changes, unless the user scrolls up. If False, will not scroll to the bottom of the textbox when the value changes.</td>
</tr>

<tr>
<td align="left"><code>render</code></td>
<td align="left" style="width: 25%;">

```python
bool
```

</td>
<td align="left"><code>True</code></td>
<td align="left">If False, component will not render be rendered in the Blocks context. Should be used if the intention is to assign event listeners now but render the component later.</td>
</tr>

<tr>
<td align="left"><code>key</code></td>
<td align="left" style="width: 25%;">

```python
int | str | tuple[int | str, ...] | None
```

</td>
<td align="left"><code>None</code></td>
<td align="left">in a gr.render, Components with the same key across re-renders are treated as the same component, not a new component. Properties set in 'preserved_by_key' are not reset across a re-render.</td>
</tr>

<tr>
<td align="left"><code>preserved_by_key</code></td>
<td align="left" style="width: 25%;">

```python
list[str] | str | None
```

</td>
<td align="left"><code>"value"</code></td>
<td align="left">A list of parameters from this component's constructor. Inside a gr.render() function, if a component is re-rendered with the same key, these (and only these) parameters will be preserved in the UI (if they have been changed by the user or an event listener) instead of re-rendered based on the values provided during constructor.</td>
</tr>

<tr>
<td align="left"><code>height</code></td>
<td align="left" style="width: 25%;">

```python
int | str | None
```

</td>
<td align="left"><code>400</code></td>
<td align="left">The height of the component, specified in pixels if a number is passed, or in CSS units if a string is passed. If messages exceed the height, the component will scroll.</td>
</tr>

<tr>
<td align="left"><code>resizable</code></td>
<td align="left" style="width: 25%;">

```python
bool
```

</td>
<td align="left"><code>False</code></td>
<td align="left">If True, the user of the Gradio app can resize the chatbot by dragging the bottom right corner.</td>
</tr>

<tr>
<td align="left"><code>resizeable</code></td>
<td align="left" style="width: 25%;">

```python
bool
```

</td>
<td align="left"><code>False</code></td>
<td align="left">None</td>
</tr>

<tr>
<td align="left"><code>max_height</code></td>
<td align="left" style="width: 25%;">

```python
int | str | None
```

</td>
<td align="left"><code>None</code></td>
<td align="left">The maximum height of the component, specified in pixels if a number is passed, or in CSS units if a string is passed. If messages exceed the height, the component will scroll. If messages are shorter than the height, the component will shrink to fit the content. Will not have any effect if `height` is set and is smaller than `max_height`.</td>
</tr>

<tr>
<td align="left"><code>min_height</code></td>
<td align="left" style="width: 25%;">

```python
int | str | None
```

</td>
<td align="left"><code>None</code></td>
<td align="left">The minimum height of the component, specified in pixels if a number is passed, or in CSS units if a string is passed. If messages exceed the height, the component will expand to fit the content. Will not have any effect if `height` is set and is larger than `min_height`.</td>
</tr>

<tr>
<td align="left"><code>editable</code></td>
<td align="left" style="width: 25%;">

```python
Literal["llm"] | None
```

</td>
<td align="left"><code>None</code></td>
<td align="left">Allows user to edit messages in the chatbot. If set to "user", allows editing of user messages. If set to "all", allows editing of assistant messages as well.</td>
</tr>

<tr>
<td align="left"><code>latex_delimiters</code></td>
<td align="left" style="width: 25%;">

```python
list[dict[str, str | bool]] | None
```

</td>
<td align="left"><code>None</code></td>
<td align="left">A list of dicts of the form {"left": open delimiter (str), "right": close delimiter (str), "display": whether to display in newline (bool)} that will be used to render LaTeX expressions. If not provided, `latex_delimiters` is set to `[{ "left": "$$", "right": "$$", "display": True }]`, so only expressions enclosed in $$ delimiters will be rendered as LaTeX, and in a new line. Pass in an empty list to disable LaTeX rendering. For more information, see the [KaTeX documentation](https://katex.org/docs/autorender.html).</td>
</tr>

<tr>
<td align="left"><code>rtl</code></td>
<td align="left" style="width: 25%;">

```python
bool
```

</td>
<td align="left"><code>False</code></td>
<td align="left">If True, sets the direction of the rendered text to right-to-left. Default is False, which renders text left-to-right.</td>
</tr>

<tr>
<td align="left"><code>show_share_button</code></td>
<td align="left" style="width: 25%;">

```python
bool | None
```

</td>
<td align="left"><code>None</code></td>
<td align="left">If True, will show a share icon in the corner of the component that allows user to share outputs to Hugging Face Spaces Discussions. If False, icon does not appear. If set to None (default behavior), then the icon appears if this Gradio app is launched on Spaces, but not otherwise.</td>
</tr>

<tr>
<td align="left"><code>show_copy_button</code></td>
<td align="left" style="width: 25%;">

```python
bool
```

</td>
<td align="left"><code>False</code></td>
<td align="left">If True, will show a copy button for each chatbot message.</td>
</tr>

<tr>
<td align="left"><code>watermark</code></td>
<td align="left" style="width: 25%;">

```python
str | None
```

</td>
<td align="left"><code>None</code></td>
<td align="left">If provided, this text will be appended to the end of messages copied from the chatbot, after a blank line. Useful for indicating that the message is generated by an AI model.</td>
</tr>

<tr>
<td align="left"><code>avatar_images</code></td>
<td align="left" style="width: 25%;">

```python
tuple[
        str | Path | None,
        str | Path | None,
        str | Path | None,
    ]
    | None
```

</td>
<td align="left"><code>None</code></td>
<td align="left">Tuple of two avatar image paths or URLs for user and bot (in that order). Pass None for either the user or bot image to skip. Must be within the working directory of the Gradio app or an external URL.</td>
</tr>

<tr>
<td align="left"><code>sanitize_html</code></td>
<td align="left" style="width: 25%;">

```python
bool
```

</td>
<td align="left"><code>True</code></td>
<td align="left">If False, will disable HTML sanitization for chatbot messages. This is not recommended, as it can lead to security vulnerabilities.</td>
</tr>

<tr>
<td align="left"><code>render_markdown</code></td>
<td align="left" style="width: 25%;">

```python
bool
```

</td>
<td align="left"><code>True</code></td>
<td align="left">If False, will disable Markdown rendering for chatbot messages.</td>
</tr>

<tr>
<td align="left"><code>feedback_options</code></td>
<td align="left" style="width: 25%;">

```python
list[str] | tuple[str, ...] | None
```

</td>
<td align="left"><code>"Like", "Dislike"</code></td>
<td align="left">A list of strings representing the feedback options that will be displayed to the user. The exact case-sensitive strings "Like" and "Dislike" will render as thumb icons, but any other choices will appear under a separate flag icon.</td>
</tr>

<tr>
<td align="left"><code>feedback_value</code></td>
<td align="left" style="width: 25%;">

```python
Sequence[str | None] | None
```

</td>
<td align="left"><code>None</code></td>
<td align="left">A list of strings representing the feedback state for entire chat. Only works when type="messages". Each entry in the list corresponds to that assistant message, in order, and the value is the feedback given (e.g. "Like", "Dislike", or any custom feedback option) or None if no feedback was given for that message.</td>
</tr>

<tr>
<td align="left"><code>line_breaks</code></td>
<td align="left" style="width: 25%;">

```python
bool
```

</td>
<td align="left"><code>True</code></td>
<td align="left">If True (default), will enable Github-flavored Markdown line breaks in chatbot messages. If False, single new lines will be ignored. Only applies if `render_markdown` is True.</td>
</tr>

<tr>
<td align="left"><code>layout</code></td>
<td align="left" style="width: 25%;">

```python
Literal["panel", "bubble"] | None
```

</td>
<td align="left"><code>None</code></td>
<td align="left">If "panel", will display the chatbot in a llm style layout. If "bubble", will display the chatbot with message bubbles, with the user and bot messages on alterating sides. Will default to "bubble".</td>
</tr>

<tr>
<td align="left"><code>placeholder</code></td>
<td align="left" style="width: 25%;">

```python
str | None
```

</td>
<td align="left"><code>None</code></td>
<td align="left">a placeholder message to display in the chatbot when it is empty. Centered vertically and horizontally in the AgentChatbot. Supports Markdown and HTML. If None, no placeholder is displayed.</td>
</tr>

<tr>
<td align="left"><code>examples</code></td>
<td align="left" style="width: 25%;">

```python
list[ExampleMessage] | None
```

</td>
<td align="left"><code>None</code></td>
<td align="left">A list of example messages to display in the chatbot before any user/assistant messages are shown. Each example should be a dictionary with an optional "text" key representing the message that should be populated in the AgentChatbot when clicked, an optional "files" key, whose value should be a list of files to populate in the AgentChatbot, an optional "icon" key, whose value should be a filepath or URL to an image to display in the example box, and an optional "display_text" key, whose value should be the text to display in the example box. If "display_text" is not provided, the value of "text" will be displayed.</td>
</tr>

<tr>
<td align="left"><code>group_consecutive_messages</code></td>
<td align="left" style="width: 25%;">

```python
bool
```

</td>
<td align="left"><code>True</code></td>
<td align="left">If True, will display consecutive messages from the same role in the same bubble. If False, will display each message in a separate bubble. Defaults to True.</td>
</tr>

<tr>
<td align="left"><code>allow_tags</code></td>
<td align="left" style="width: 25%;">

```python
list[str] | bool
```

</td>
<td align="left"><code>False</code></td>
<td align="left">If a list of tags is provided, these tags will be preserved in the output chatbot messages, even if `sanitize_html` is `True`. For example, if this list is ["thinking"], the tags `<thinking>` and `</thinking>` will not be removed. If True, all custom tags (non-standard HTML tags) will be preserved. If False, no tags will be preserved (default behavior).</td>
</tr>
</tbody></table>


### Events

| name | description |
|:-----|:------------|
| `change` | Triggered when the value of the AgentChatbot changes either because of user input (e.g. a user types in a textbox) OR because of a function update (e.g. an image receives a value from the output of an event trigger). See `.input()` for a listener that is only triggered by user input. |
| `select` | Event listener for when the user selects or deselects the AgentChatbot. Uses event data gradio.SelectData to carry `value` referring to the label of the AgentChatbot, and `selected` to refer to state of the AgentChatbot. See EventData documentation on how to use this event data |
| `like` | This listener is triggered when the user likes/dislikes from within the AgentChatbot. This event has EventData of type gradio.LikeData that carries information, accessible through LikeData.index and LikeData.value. See EventData documentation on how to use this event data. |
| `retry` | This listener is triggered when the user clicks the retry button in the chatbot message. |
| `undo` | This listener is triggered when the user clicks the undo button in the chatbot message. |
| `example_select` | This listener is triggered when the user clicks on an example from within the AgentChatbot. This event has SelectData of type gradio.SelectData that carries information, accessible through SelectData.index and SelectData.value. See SelectData documentation on how to use this event data. |
| `option_select` | This listener is triggered when the user clicks on an option from within the AgentChatbot. This event has SelectData of type gradio.SelectData that carries information, accessible through SelectData.index and SelectData.value. See SelectData documentation on how to use this event data. |
| `copy` | This listener is triggered when the user copies content from the AgentChatbot. Uses event data gradio.CopyData to carry information about the copied content. See EventData documentation on how to use this event data |
| `edit` | This listener is triggered when the user edits the AgentChatbot (e.g. image) using the built-in editor. |



### User function

The impact on the users predict function varies depending on whether the component is used as an input or output for an event (or both).

- When used as an Input, the component only impacts the input signature of the user function.
- When used as an output, the component only impacts the return signature of the user function.

The code snippet below is accurate in cases where the component is used as both an input and an output.

- **As output:** Is passed, if type is 'tuples', passes the messages in the chatbot as a `list[list[str | None | tuple]]`, i.e. a list of lists. The inner list has 2 elements: the user message and the response message. Each message can be (1) a string in valid Markdown, (2) a tuple if there are displayed files: (a filepath or URL to a file, [optional string alt text]), or (3) None, if there is no message displayed. If type is 'messages', passes the value as a list of dictionaries with 'role' and 'content' keys. The `content` key's value supports everything the `tuples` format supports.
- **As input:** Should return, if type is `tuples`, expects a `list[list[str | None | tuple]]`, i.e. a list of lists. The inner list should have 2 elements: the user message and the response message. The individual messages can be (1) strings in valid Markdown, (2) tuples if sending files: (a filepath or URL to a file, [optional string alt text]) -- if the file is image/video/audio, it is displayed in the AgentChatbot, or (3) None, in which case the message is not displayed. If type is 'messages', passes the value as a list of dictionaries with 'role' and 'content' keys. The `content` key's value supports everything the `tuples` format supports.

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
 

## `MessageDict`
```python
class MessageDict(TypedDict):
    name: str
    content: str | FileDataDict | tuple | Component
    role: Literal["user", "assistant", "system"]
    metadata: NotRequired[MetadataDict]
    options: NotRequired[list[OptionDict]]
```

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
```

## `MetadataDict`
```python
class MetadataDict(TypedDict):
    title: NotRequired[str]
    id: NotRequired[int | str]
    parent_id: NotRequired[int | str]
    log: NotRequired[str]
    duration: NotRequired[float]
    status: NotRequired[Literal["pending", "done"]]
```

## `OptionDict`
```python
class OptionDict(TypedDict):
    value: str
    label: NotRequired[str]
```

## `Message`
```python
class Message(GradioModel):
    name: str
    role: str
    metadata: MetadataDict | None = None
    content: Union[str, FileMessage, ComponentMessage]
    options: list[OptionDict] | None = None
```

## `FileMessage`
```python
class FileMessage(GradioModel):
    file: FileData
    alt_text: str | None = None
```

## `ComponentMessage`
```python
class ComponentMessage(GradioModel):
    component: str
    value: Any
    constructor_args: dict[str, Any]
    props: dict[str, Any]
```
