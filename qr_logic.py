import qrcode
from qrcode.image.styledpil import StyledPilImage
from qrcode.image.styles.moduledrawers.pil import (
    SquareModuleDrawer, GappedSquareModuleDrawer, CircleModuleDrawer, 
    RoundedModuleDrawer, VerticalBarsDrawer, HorizontalBarsDrawer
)
from qrcode.image.styles.colormasks import (
    SolidFillColorMask, RadialGradiantColorMask, 
    SquareGradiantColorMask, HorizontalGradiantColorMask, VerticalGradiantColorMask
)
from PIL import Image, ImageColor
import io
import os

class QRGeneratorLogic:
    @staticmethod
    def generate_qr(data, box_size=10, border=4, fill_color="black", back_color="white", 
                    error_correction="H", logo_path=None, module_style="Square", color_style="Solid"):
        """Generates a highly styled QR code."""
        ec_map = {
            "L": qrcode.constants.ERROR_CORRECT_L,
            "M": qrcode.constants.ERROR_CORRECT_M,
            "Q": qrcode.constants.ERROR_CORRECT_Q,
            "H": qrcode.constants.ERROR_CORRECT_H,
        }
        
        qr = qrcode.QRCode(
            version=1,
            error_correction=ec_map.get(error_correction, qrcode.constants.ERROR_CORRECT_H),
            box_size=box_size,
            border=border,
        )
        qr.add_data(data)
        qr.make(fit=True)

        # Module Drawer Selection
        drawers = {
            "Square": SquareModuleDrawer(),
            "Gapped": GappedSquareModuleDrawer(),
            "Circle": CircleModuleDrawer(),
            "Rounded": RoundedModuleDrawer(),
            "Vertical": VerticalBarsDrawer(),
            "Horizontal": HorizontalBarsDrawer()
        }
        drawer = drawers.get(module_style, SquareModuleDrawer())

        # Color Mask Selection
        # Convert hex to RGB tuples
        try:
            fg_rgb = ImageColor.getcolor(fill_color, "RGB")
            bg_rgb = ImageColor.getcolor(back_color, "RGB")
        except:
            fg_rgb = (0, 240, 255) # Cyan fallback
            bg_rgb = (0, 0, 0)     # Black fallback

        if color_style == "Radial":
            mask = RadialGradiantColorMask(back_color=bg_rgb, center_color=fg_rgb, edge_color=(0,0,0))
        elif color_style == "Horizontal":
            mask = HorizontalGradiantColorMask(back_color=bg_rgb, left_color=fg_rgb, right_color=(0,0,0))
        elif color_style == "Vertical":
            mask = VerticalGradiantColorMask(back_color=bg_rgb, top_color=fg_rgb, bottom_color=(0,0,0))
        else:
            mask = SolidFillColorMask(back_color=bg_rgb, front_color=fg_rgb)

        # Generate Styled Image
        img = qr.make_image(
            image_factory=StyledPilImage,
            module_drawer=drawer,
            color_mask=mask,
            embeded_image_path=logo_path if logo_path and os.path.exists(logo_path) else None
        ).convert('RGB')

        return img

    @staticmethod
    def format_vcard(name, phone, email, org="", title="", url=""):
        vcard = [
            "BEGIN:VCARD", "VERSION:3.0",
            f"FN:{name}", f"TEL;TYPE=CELL:{phone}",
            f"EMAIL:{email}", f"ORG:{org}",
            f"TITLE:{title}", f"URL:{url}",
            "END:VCARD"
        ]
        return "\n".join(vcard)

    @staticmethod
    def generate_svg(data, box_size=10, border=4, error_correction="H"):
        from qrcode.image.svg import SvgImage
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_H,
            box_size=box_size,
            border=border,
            image_factory=SvgImage
        )
        qr.add_data(data)
        qr.make(fit=True)
        img = qr.make_image()
        buffer = io.BytesIO()
        img.save(buffer)
        return buffer.getvalue().decode('utf-8')

    @staticmethod
    def format_wifi_data(ssid, password, security="WPA"):
        return f"WIFI:S:{ssid};T:{security};P:{password};;"

    @staticmethod
    def format_email_data(to_email, subject="", body=""):
        import urllib.parse
        subject_enc = urllib.parse.quote(subject)
        body_enc = urllib.parse.quote(body)
        return f"mailto:{to_email}?subject={subject_enc}&body={body_enc}"
