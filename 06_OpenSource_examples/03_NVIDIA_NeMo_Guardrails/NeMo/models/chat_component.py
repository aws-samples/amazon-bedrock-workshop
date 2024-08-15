from datetime import datetime
from IPython.display import HTML, display
from ipywidgets import widgets


# create class which renders the chat component
class ChatComponent:
    def __init__(self, llm):
        self.llm = llm
        # Create chat history
        self.chat_history = []
        self.in_text = widgets.Text()
        self.in_text.continuous_update = False
        self.in_text.observe(self.text_event_handler, "value")
        self.output = widgets.Output()
        self.answer = ""

        load_image_file = open("images/loading.gif", "rb")
        loading_image = load_image_file.read()
        self.loading_bar = widgets.Image(
            value=loading_image,
            format="gif",
            width="20",
            height="20",
            layout={"display": "None"},
        )

    def text_event_handler(self, *args):
        # Needed bc when we "reset" the text input
        # it fires instantly another event since
        # we "changed" it's value to ""
        if args[0]["new"] == "":
            return

        # Show loading animation
        self.loading_bar.layout.display = "block"

        # Get question
        question = args[0]["new"]

        # Reset text field
        args[0]["owner"].value = ""

        # Formatting question for output
        q = (
            f'<div class="chat-message-right pb-4"><div>'
            + f'<img src="images/w_human.png" class="rounded-circle mr-1" width="40" height="40">'
            + f'<div class="text-muted small text-nowrap mt-2">{datetime.now().strftime("%H:%M:%S")}</div></div>'
            + '<div class="flex-shrink-1 rounded py-2 px-3 ml-3">'
            + f'<div class="font-weight-bold mb-1">You</div>{question}</div>'
        )

        # Display formatted question
        self.output.append_display_data(HTML(q))

        try:
            self.answer = self.llm.generate(prompt=question)
            self.chat_history.append((question, self.answer))
        except Exception as e:
            self.answer = "<b>Error:</b> " + str(e)

        # Formatting answer for output
        # Replacing all $ otherwise matjax would format them in a strange way
        answer_formatted = self.answer.replace("$", r"\$")
        a = (
            f'<div class="chat-message-left pb-4"><div>'
            + f'<img src="images/w_ai.png" class="rounded-circle mr-1" width="40" height="40">'
            + f'<div class="text-muted small text-nowrap mt-2">{datetime.now().strftime("%H:%M:%S")}</div></div>'
            + '<div class="flex-shrink-1 rounded py-2 px-3 ml-3">'
            + f'<div class="font-weight-bold mb-1">Assistant</div><xmp class="chat-message-content-xmp">{answer_formatted}</xmp></div>'
        )

        # Turn off loading animation
        self.loading_bar.layout.display = "none"

        self.output.append_display_data(HTML(a))

    def render(self):
        # Render chat component
        display(
            widgets.HBox(
                [self.output],
                layout=widgets.Layout(
                    width="100%",
                    margin="25px",
                    max_height="500px",
                    display="inline-flex",
                    flex_flow="column-reverse",
                ),
            )
        )

        display(
            widgets.Box(
                children=[self.loading_bar, self.in_text],
                layout=widgets.Layout(display="flex", flex_flow="row"),
            )
        )
