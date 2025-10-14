
import gradio as gr
from app import demo as app
import os

_docs = {'GoodTab': {'description': 'Tab (or its alias TabItem) is a layout element. Components defined within the Tab will be visible when this tab is selected tab.\n    with gr.Blocks() as demo:\n        with gr.Tab("Lion"):\n            gr.Image("lion.jpg")\n            gr.Button("New Lion")\n        with gr.Tab("Tiger"):\n            gr.Image("tiger.jpg")\n            gr.Button("New Tiger")', 'members': {'__init__': {'label': {'type': 'str | None', 'default': 'None', 'description': 'The visual label for the tab'}, 'visible': {'type': 'bool', 'default': 'True', 'description': 'If False, Tab will be hidden.'}, 'interactive': {'type': 'bool', 'default': 'True', 'description': 'If False, Tab will not be clickable.'}, 'id': {'type': 'int | str | None', 'default': 'None', 'description': 'An optional identifier for the tab, required if you wish to control the selected tab from a predict function.'}, 'elem_id': {'type': 'str | None', 'default': 'None', 'description': 'An optional string that is assigned as the id of the <div> containing the contents of the Tab layout. The same string followed by "-button" is attached to the Tab button. Can be used for targeting CSS styles.'}, 'elem_classes': {'type': 'list[str] | str | None', 'default': 'None', 'description': 'An optional string or list of strings that are assigned as the class of this component in the HTML DOM. Can be used for targeting CSS styles.'}, 'render': {'type': 'bool', 'default': 'True', 'description': 'If False, this layout will not be rendered in the Blocks context. Should be used if the intention is to assign event listeners now but render the component later.'}, 'key': {'type': 'str | None', 'default': 'None', 'description': 'Added for new gradio compatibility, has no effect for now.'}}, 'postprocess': {}}, 'events': {'select': {'type': None, 'default': None, 'description': 'Event listener for when the user selects or deselects the GoodTab. Uses event data gradio.SelectData to carry `value` referring to the label of the GoodTab, and `selected` to refer to state of the GoodTab. See EventData documentation on how to use this event data'}}}, '__meta__': {'additional_interfaces': {}}, 'GoodTabs': {'description': 'GoodTabs is a layout element within Blocks that can contain multiple "Tab" Components.', 'members': {'__init__': {'selected': {'type': 'int | str | None', 'default': 'None', 'description': 'The currently selected tab. Must correspond to an id passed to the one of the child TabItems. Defaults to the first TabItem.'}, 'visible': {'type': 'bool', 'default': 'True', 'description': 'If False, GoodTabs will be hidden.'}, 'elem_id': {'type': 'str | None', 'default': 'None', 'description': 'An optional string that is assigned as the id of this component in the HTML DOM. Can be used for targeting CSS styles.'}, 'elem_classes': {'type': 'list[str] | str | None', 'default': 'None', 'description': 'An optional string or list of strings that are assigned as the class of this component in the HTML DOM. Can be used for targeting CSS styles.'}, 'render': {'type': 'bool', 'default': 'True', 'description': 'If False, this layout will not be rendered in the Blocks context. Should be used if the intention is to assign event listeners now but render the component later.'}, 'key': {'type': 'str | None', 'default': 'None', 'description': 'Added for new gradio compatibility, has no effect for now.'}}, 'postprocess': {}}, 'events': {'change': {'type': None, 'default': None, 'description': 'Triggered when the value of the GoodTabs changes either because of user input (e.g. a user types in a textbox) OR because of a function update (e.g. an image receives a value from the output of an event trigger). See `.input()` for a listener that is only triggered by user input.'}, 'select': {'type': None, 'default': None, 'description': 'Event listener for when the user selects or deselects the GoodTabs. Uses event data gradio.SelectData to carry `value` referring to the label of the GoodTabs, and `selected` to refer to state of the GoodTabs. See EventData documentation on how to use this event data'}}}}

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
# `gradio_goodtabs`

<div style="display: flex; gap: 7px;">
<a href="https://pypi.org/project/gradio_goodtabs/" target="_blank"><img alt="PyPI - Version" src="https://img.shields.io/pypi/v/gradio_goodtabs"></a>  
</div>

Python library for easily interacting with trained machine learning models
""", elem_classes=["md-custom"], header_links=True)
    app.render()
    gr.Markdown(
"""
## Installation

```bash
pip install gradio_goodtabs
```

## Usage

```python

import gradio as gr
from gradio_goodtabs import GoodTabs
from gradio_goodtab import GoodTab as Tab
# from gradio_goodtabs import GoodTab as Tab
# gr.Tab = Tab
gr.Tabs = GoodTabs

with gr.Blocks() as demo:
    with gr.Row():
        with GoodTabs():  
            with Tab("Tab 1 long long long long long long long long long"):
                gr.Textbox(value="foo", interactive=True)
            with Tab("Tab 1 long long long long long long long long long"):
                gr.Textbox(value="foo", interactive=True)
            with Tab("Tab 1 long long long long long long long long long"):
                gr.Textbox(value="foo", interactive=True)
            with Tab("Tab 1 long long long long long long long long long"):
                gr.Textbox(value="foo", interactive=True)
            with Tab("Tab 1 long long long long long long long long long"):
                gr.Textbox(value="foo", interactive=True)
            with Tab("Tab 1 long long long long long long long long long"):
                gr.Textbox(value="foo", interactive=True)
            with Tab("Tab 1 long long long long long long long long long"):
                gr.Textbox(value="foo", interactive=True)
            with Tab("Tab 1 long long long long long long long long long"):
                gr.Textbox(value="foo", interactive=True)
            with Tab("Tab 1 long long long long long long long long long"):
                gr.Textbox(value="foo", interactive=True)
            with Tab("Tab 1 long long long long long long long long long"):
                gr.Textbox(value="foo", interactive=True)
            with Tab("Tab 1 long long long long long long long long long"):
                gr.Textbox(value="foo", interactive=True)
            with Tab("Tab 1 long long long long long long long long long"):
                gr.Textbox(value="foo", interactive=True)
            # with gr.Tab("Tab 1 long long long long long long long long long"):
            #     gr.Textbox(value="foo", interactive=True)
            # with gr.Tab("Tab 1 long long long long long long long long long"):
            #     gr.Textbox(value="foo", interactive=True)
            # with gr.Tab("Tab 1 long long long long long long long long long"):
            #     gr.Textbox(value="foo", interactive=True)
            # with gr.Tab("Tab 1 long long long long long long long long long"):
            #     gr.Textbox(value="foo", interactive=True)
            # with gr.Tab("Tab 1 long long long long long long long long long"):
            #     gr.Textbox(value="foo", interactive=True)
            # with gr.Tab("Tab 1 long long long long long long long long long"):
            #     gr.Textbox(value="foo", interactive=True)
            # with gr.Tab("Tab 2"):
            #     gr.Number(value=10, interactive=True)


if __name__ == "__main__":
    demo.launch()

```
""", elem_classes=["md-custom"], header_links=True)


    gr.Markdown("""
## `GoodTab`

### Initialization
""", elem_classes=["md-custom"], header_links=True)

    gr.ParamViewer(value=_docs["GoodTab"]["members"]["__init__"], linkify=[])


    gr.Markdown("### Events")
    gr.ParamViewer(value=_docs["GoodTab"]["events"], linkify=['Event'])





    gr.Markdown("""
## `GoodTabs`

### Initialization
""", elem_classes=["md-custom"], header_links=True)

    gr.ParamViewer(value=_docs["GoodTabs"]["members"]["__init__"], linkify=[])


    gr.Markdown("### Events")
    gr.ParamViewer(value=_docs["GoodTabs"]["events"], linkify=['Event'])







    demo.load(None, js=r"""function() {
    const refs = {};
    const user_fn_refs = {};
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
