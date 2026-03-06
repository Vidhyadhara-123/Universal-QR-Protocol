from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.uix.spinner import Spinner
from kivy.uix.scrollview import ScrollView
from kivy.core.window import Window
from kivy.utils import get_color_from_hex
from kivy.clock import Clock
import qrcode
import os

# Theme
BG_COLOR = '#050510'
FG_COLOR = get_color_from_hex('#00f0ff')
ACCENT_COLOR = get_color_from_hex('#00aaff')
PANEL_COLOR = get_color_from_hex('#0a0a1a')

class JarvisQRApp(App):
    def build(self):
        self.title = "J.A.R.V.I.S. QR"
        # Root
        root = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        # Header
        header = Label(
            text="[b]J.A.R.V.I.S.[/b]\nSTABLE_PROTO_v1.6", 
            markup=True, font_size='20sp', color=FG_COLOR, size_hint_y=None, height='80dp'
        )
        root.add_widget(header)

        # Scroll
        scroll = ScrollView()
        content = BoxLayout(orientation='vertical', size_hint_y=None, spacing=15, padding=10)
        content.bind(minimum_height=content.setter('height'))

        # UI Elements
        content.add_widget(Label(text="PROTOCOL TYPE", font_size='12sp', color=ACCENT_COLOR, size_hint_y=None, height='20dp'))
        self.spinner = Spinner(
            text='Website URL', values=('Website URL', 'Text', 'WiFi', 'Email', 'vCard'),
            size_hint_y=None, height='50dp', background_normal='', background_color=PANEL_COLOR, color=FG_COLOR
        )
        self.spinner.bind(text=self.on_type_change)
        content.add_widget(self.spinner)

        content.add_widget(Label(text="DATA STREAM", font_size='12sp', color=ACCENT_COLOR, size_hint_y=None, height='20dp'))
        self.input_field = TextInput(
            text="https://", multiline=True, size_hint_y=None, height='100dp',
            background_color=PANEL_COLOR, foreground_color=FG_COLOR, cursor_color=FG_COLOR
        )
        content.add_widget(self.input_field)

        content.add_widget(Label(text="ARTIFACT PREVIEW", font_size='12sp', color=ACCENT_COLOR, size_hint_y=None, height='20dp'))
        self.qr_image = Image(size_hint_y=None, height='300dp', allow_stretch=True)
        content.add_widget(self.qr_image)

        scroll.add_widget(content)
        root.add_widget(scroll)

        # Buttons
        btn_box = BoxLayout(size_hint_y=None, height='60dp', spacing=10)
        btn_gen = Button(text='INITIATE', bold=True, background_normal='', background_color=FG_COLOR, color=get_color_from_hex(BG_COLOR))
        btn_gen.bind(on_press=self.generate_qr)
        btn_clear = Button(text='RESET', bold=True, background_normal='', background_color=PANEL_COLOR, color=FG_COLOR)
        btn_clear.bind(on_press=self.reset_all)
        
        btn_box.add_widget(btn_gen)
        btn_box.add_widget(btn_clear)
        root.add_widget(btn_box)

        self.status_label = Label(text="SYSTEM STANDBY", font_size='10sp', color=ACCENT_COLOR, size_hint_y=None, height='20dp')
        root.add_widget(self.status_label)
        
        return root

    def on_start(self):
        # Set window color safely after start
        Window.clearcolor = get_color_from_hex(BG_COLOR)

    def on_type_change(self, spinner, text):
        templates = {
            "WiFi": "SSID: MyNetwork\nPassword: MyPassword",
            "vCard": "Name: Tony Stark\nPhone: +1 555 123",
            "Email": "To: recipient@example.com",
            "Website URL": "https://"
        }
        self.input_field.text = templates.get(text, "")

    def generate_qr(self, instance):
        if not self.input_field.text.strip(): return
        
        # Path to temp file
        temp_path = os.path.join(self.user_data_dir, 'temp_qr.png')
        
        try:
            # Generate
            qr = qrcode.make(self.input_field.text.strip())
            qr.save(temp_path)
            
            # Update Image - Reloading the source ensures Kivy refreshes properly
            self.qr_image.source = '' # Clear
            self.qr_image.source = temp_path
            self.qr_image.reload()
            
            self.status_label.text = "ARTIFACT GENERATED"
        except Exception as e:
            self.status_label.text = "ERROR: " + str(e)[:20]

    def reset_all(self, instance):
        self.input_field.text = ""
        self.qr_image.source = ''
        self.status_label.text = "SYSTEM RESET"

if __name__ == '__main__':
    JarvisQRApp().run()
