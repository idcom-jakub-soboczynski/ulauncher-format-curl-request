from ulauncher.api.client.Extension import Extension
from ulauncher.api.client.EventListener import EventListener
from ulauncher.api.shared.event import KeywordQueryEvent, ItemEnterEvent
from ulauncher.api.shared.item.ExtensionResultItem import ExtensionResultItem
from ulauncher.api.shared.action.RenderResultListAction import RenderResultListAction
from ulauncher.api.shared.action.HideWindowAction import HideWindowAction
from ulauncher.api.shared.action.CopyToClipboardAction import CopyToClipboardAction
import pyperclip
from curl import format_curl_request


class CurlFormatExtension(Extension):
    def __init__(self):
        super().__init__()
        self.subscribe(KeywordQueryEvent, KeywordQueryEventListener())


class KeywordQueryEventListener(EventListener):

    def on_event(self, event, extension):
        # Get the query typed by the user
        query = event.get_argument()
        items = []

        # If no query provided, try to get curl from clipboard
        if not query:
            try:
                clipboard_content = pyperclip.paste()
                if clipboard_content.strip().startswith('curl'):
                    success, result = format_curl_request(clipboard_content)
                    if success:
                        items.append(ExtensionResultItem(icon='images/icon.png',
                                                      name='Format Clipboard cURL Request',
                                                      description='Click to copy formatted result',
                                                      on_enter=CopyToClipboardAction(result)))
                    else:
                        items.append(ExtensionResultItem(icon='images/icon.png',
                                                      name='Error Formatting Clipboard Content',
                                                      description='Start typing your curl request or fix clipboard content',
                                                      on_enter=HideWindowAction()))
                else:
                    items.append(ExtensionResultItem(icon='images/icon.png',
                                                  name='No cURL Request Found',
                                                  description='Start typing your curl request (e.g., curl http://example.com)',
                                                  on_enter=HideWindowAction()))

                    # Add a second item to show example
                    items.append(ExtensionResultItem(icon='images/icon.png',
                                                  name='Example Usage',
                                                  description='Type "curl -X POST http://api.example.com -H \'Content-Type: application/json\'"',
                                                  on_enter=HideWindowAction()))
            except Exception:
                items.append(ExtensionResultItem(icon='images/icon.png',
                                              name='Start New Request',
                                              description='Type your curl request (e.g., curl http://example.com)',
                                              on_enter=HideWindowAction()))
        else:
            # Format the curl request from query
            success, result = format_curl_request(query)

            if not success:
                items.append(ExtensionResultItem(icon='images/icon.png',
                                              name='Invalid cURL Request',
                                              description=f'Error: {result}. Make sure your request starts with "curl"',
                                              on_enter=HideWindowAction()))
            else:
                items.append(ExtensionResultItem(icon='images/icon.png',
                                              name='Formatted cURL Request',
                                              description='Click to copy the formatted result',
                                              on_enter=CopyToClipboardAction(result)))

        return RenderResultListAction(items)

if __name__ == '__main__':
    CurlFormatExtension().run()
