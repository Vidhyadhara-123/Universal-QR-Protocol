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
from kivy.core.image import Image as CoreImage
import qrcode
from io import BytesIO
import os

# J.A.R.V.I.S. Theme Colors
BG_COLOR = get_color_from_hex('#050510')
FG_COLOR = get_color_from_hex('#00f0ff')
ACCENT_COLOR = get_color_from_hex('#00aaff')
PANEL_COLOR = get_color_from_hex('#0a0a1a')

Window.clearcolor = BG_COLOR

class JarvisQRApp(App):
    def build(self):
        self.title = "J.A.R.V.I.S. QR PROTOCOL"
        
        # Root Layout
        root = BoxLayout(orientation='vertical', padding=15, spacing=10)
        
        # Header
        header = Label(
            text="[b]J.A.R.V.I.S.[/b]\n[size=14]MOBILE PROTOCOL[/size]", 
            markup=True, font_size='22sp', color=FG_COLOR, size_hint_y=None, height='80dp'
        )
        root.add_widget(header)

        # Scrollable UI
        scroll = ScrollView()
        content = BoxLayout(orientation='vertical', size_hint_y=None, spacing=15, padding=10)
        content.bind(minimum_height=content.setter('height'))

        # Protocol Type
        content.add_widget(Label(text="PROTOCOL TYPE", font_size='12sp', color=ACCENT_COLOR, size_hint_y=None, height='20dp'))
        self.spinner = Spinner(
            text='Website URL', values=('Website URL', 'Text', 'WiFi', 'Email', 'vCard'),
            size_hint_y=None, height='50dp', background_normal='', background_color=PANEL_COLOR, color=FG_COLOR
        )
        self.spinner.bind(text=self.on_type_change)
        content.add_widget(self.spinner)

        # Input Area
        content.add_widget(Label(text="DATA STREAM", font_size='12sp', color=ACCENT_COLOR, size_hint_y=None, height='20dp'))
        self.input_field = TextInput(
            text="https://", multiline=True, size_hint_y=None, height='120dp',
            background_color=PANEL_COLOR, foreground_color=FG_COLOR, cursor_color=FG_COLOR
        )
        content.add_widget(self.input_field)

        # Preview Area
        content.add_widget(Label(text="ARTIFACT PREVIEW", font_size='12sp', color=ACCENT_COLOR, size_hint_y=None, height='20dp'))
        self.qr_image = Image(size_hint_y=None, height='300dp')
        content.add_widget(self.qr_image)

        scroll.add_widget(content)
        root.add_widget(scroll)

        # Bottom Buttons
        btn_box = BoxLayout(size_hint_y=None, height='60dp', spacing=10)
        self.btn_gen = Button(text='INITIATE', bold=True, background_normal='', background_color=FG_COLOR, color=BG_COLOR)
        self.btn_gen.bind(on_press=self.generate_qr)
        self.btn_clear = Button(text='RESET', bold=True, background_normal='', background_color=PANEL_COLOR, color=FG_COLOR)
        self.btn_clear.bind(on_press=self.reset_all)
        
        btn_box.add_widget(self.btn_gen)
        btn_box.add_widget(self.btn_clear)
        root.add_widget(btn_box)

        self.status_label = Label(text="SYSTEM READY", font_size='10sp', color=ACCENT_COLOR, size_hint_y=None, height='20dp')
        root.add_widget(self.status_label)
        
        return root

    def on_type_change(self, spinner, text):
        templates = {
            "WiFi": "SSID: MyNetwork\nPassword: MyPassword\nSecurity: WPA",
            "vCard": "Name: Tony Stark\nPhone: +1 555 123 4567\nEmail: tony@stark.com\nOrg: Stark Industries",
            "Email": "To: recipient@example.com\nSubject: Hello\nBody: Message",
            "Website URL": "https://"
        }
        self.input_field.text = templates.get(text, "")

    def generate_qr(self, instance):
        raw_text = self.input_field.text.strip()
        if not raw_text:
            self.status_label.text = "ERROR: NULL INPUT"
            return
            
        try:
            # 1. Format Data
            data = raw_text
            ctype = self.spinner.text
            if ctype in ["WiFi", "vCard", "Email"]:
                d = {l.split(':', 1)[0].strip().lower(): l.split(':', 1)[1].strip() for l in raw_text.split('\n') if ':' in l}
                if ctype == "WiFi": data = f"WIFI:S:{d.get('ssid','')};T:{d.get('security','WPA')};P:{d.get('password','')};;"
                if ctype == "vCard": data = f"BEGIN:VCARD\nVERSION:3.0\nFN:{d.get('name','')}\nTEL:{d.get('phone','')}\nEMAIL:{d.get('email','')}\nORG:{d.get('org','')}\nEND:VCARD"
                if ctype == "Email": data = f"mailto:{d.get('to','')}?subject={d.get('subject','')}&body={d.get('body','')}"

            # 2. Generate Standard QR (High Stability)
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            qr.add_data(data)
            qr.make(fit=True)
            
            # Create standard PIL image
            img = qr.make_image(fill_color="black", back_color="white")
            
            # 3. Convert to Kivy Texture
            buf = BytesIO()
            img.save(buf, format='png')
            buf.seek(0)
            
            # Update UI
            im = CoreImage(BytesIO(buf.read()), ext='png')
            self.qr_image.texture = im.texture
            self.status_label.text = "PROTOCOL EXECUTED"
            
        except Exception as e:
            self.status_label.text = f"CRITICAL FAILURE: {str(e)[:30]}"

    def reset_all(self, instance):
        self.input_field.text = ""
        self.qr_image.texture = None
        self.status_label.text = "SYSTEM RESET"

if __name__ == '__main__':
    JarvisQRApp().run()
