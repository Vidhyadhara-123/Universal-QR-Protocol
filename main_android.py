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
from kivy.uix.filechooser import FileChooserIconView
from kivy.uix.popup import Popup

import qrcode
from qrcode.image.styledpil import StyledPilImage
from qrcode.image.styles.moduledrawers.pil import SquareModuleDrawer, CircleModuleDrawer, RoundedModuleDrawer
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
        self.title = "J.A.R.V.I.S. QR PROTOCOL PRO"
        self.logo_path = None
        
        # Root Layout
        root = BoxLayout(orientation='vertical', padding=15, spacing=10)
        
        # Header
        header = Label(
            text="[b]J.A.R.V.I.S.[/b]\n[size=14]MOBILE PROTOCOL PRO[/size]", 
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

        # Module Style
        content.add_widget(Label(text="MODULE STYLE", font_size='12sp', color=ACCENT_COLOR, size_hint_y=None, height='20dp'))
        self.style_spinner = Spinner(
            text='Square', values=('Square', 'Rounded', 'Circle'),
            size_hint_y=None, height='50dp', background_normal='', background_color=PANEL_COLOR, color=FG_COLOR
        )
        content.add_widget(self.style_spinner)

        # Logo Toggle
        self.btn_logo = Button(
            text='ADD LOGO OVERLAY', size_hint_y=None, height='50dp',
            background_normal='', background_color=PANEL_COLOR, color=FG_COLOR
        )
        self.btn_logo.bind(on_press=self.open_file_chooser)
        content.add_widget(self.btn_logo)

        # Input Area
        content.add_widget(Label(text="DATA STREAM", font_size='12sp', color=ACCENT_COLOR, size_hint_y=None, height='20dp'))
        self.input_field = TextInput(
            text="https://", multiline=True, size_hint_y=None, height='120dp',
            background_color=PANEL_COLOR, foreground_color=FG_COLOR, cursor_color=FG_COLOR
        )
        content.add_widget(self.input_field)

        # Preview
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

    def open_file_chooser(self, instance):
        content = BoxLayout(orientation='vertical')
        chooser = FileChooserIconView(path=os.path.expanduser('~'))
        content.add_widget(chooser)
        
        btn_layout = BoxLayout(size_hint_y=None, height='50dp')
        select_btn = Button(text='SELECT')
        cancel_btn = Button(text='CANCEL')
        btn_layout.add_widget(select_btn)
        btn_layout.add_widget(cancel_btn)
        content.add_widget(btn_layout)

        popup = Popup(title="Select Logo (PNG/JPG)", content=content, size_hint=(0.9, 0.9))
        
        def on_select(btn):
            if chooser.selection:
                self.logo_path = chooser.selection[0]
                self.btn_logo.text = f"LOGO: {os.path.basename(self.logo_path)}"
                self.btn_logo.background_color = ACCENT_COLOR
                self.btn_logo.color = BG_COLOR
            popup.dismiss()

        select_btn.bind(on_press=on_select)
        cancel_btn.bind(on_press=lambda x: popup.dismiss())
        popup.open()

    def generate_qr(self, instance):
        raw_text = self.input_field.text.strip()
        if not raw_text: return
            
        try:
            # Process Data
            data = raw_text
            if self.spinner.text in ["WiFi", "vCard", "Email"]:
                d = {l.split(':', 1)[0].strip().lower(): l.split(':', 1)[1].strip() for l in raw_text.split('\n') if ':' in l}
                if self.spinner.text == "WiFi": data = f"WIFI:S:{d.get('ssid','')};T:{d.get('security','WPA')};P:{d.get('password','')};;"
                if self.spinner.text == "vCard": data = f"BEGIN:VCARD\nVERSION:3.0\nFN:{d.get('name','')}\nTEL:{d.get('phone','')}\nEMAIL:{d.get('email','')}\nORG:{d.get('org','')}\nEND:VCARD"
                if self.spinner.text == "Email": data = f"mailto:{d.get('to','')}?subject={d.get('subject','')}&body={d.get('body','')}"

            # Generate Styled QR
            qr = qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_H)
            qr.add_data(data)
            
            drawers = {"Square": SquareModuleDrawer(), "Rounded": RoundedModuleDrawer(), "Circle": CircleModuleDrawer()}
            drawer = drawers.get(self.style_spinner.text, SquareModuleDrawer())

            img = qr.make_image(
                image_factory=StyledPilImage,
                module_drawer=drawer,
                embeded_image_path=self.logo_path if self.logo_path else None
            ).convert('RGB')
            
            # Display
            buf = BytesIO()
            img.save(buf, format='png')
            buf.seek(0)
            im = CoreImage(BytesIO(buf.read()), ext='png')
            self.qr_image.texture = im.texture
            self.status_label.text = "PROTOCOL EXECUTED SUCCESSFULLY"
        except Exception as e:
            self.status_label.text = f"CRITICAL ERROR: {str(e)}"

    def reset_all(self, instance):
        self.input_field.text = ""
        self.logo_path = None
        self.btn_logo.text = "ADD LOGO OVERLAY"
        self.btn_logo.background_color = PANEL_COLOR
        self.btn_logo.color = FG_COLOR
        self.qr_image.texture = None
        self.status_label.text = "SYSTEM RESET"

if __name__ == '__main__':
    JarvisQRApp().run()
