
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
