

from datetime import datetime

from kivy.clock import Clock
from kivy.properties import BooleanProperty

from kivy.graphics import Color, Rectangle
from kivy.graphics.texture import Texture

from kivy.core.text import Label as CoreLabel
from kivy.uix.label import Label
from kivy.uix.image import Image

from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.stacklayout import StackLayout
from kivy.uix.anchorlayout import AnchorLayout


class SelfScalingLabel(Label):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bind(size=lambda inst, val: setattr(inst, 'text_size', val))
        self._bind_autofit_text()

    def _bind_autofit_text(self, min_font=10, max_font=None, respect_height=True, timeout_retry=0.05):
        """
        Bind label so its font_size auto-scales to ensure the full text fits *in one line* horizontally.

        - No wrapping, no shortening, no clipping.
        - Keeps alignment (halign/valign) functional.
        - Recomputes on size/text change.
        """

        def _fit_text_size(*_):
            # Ensure layout exists before computing
            w, h = self.size
            if w <= 8 or h <= 8:
                Clock.schedule_once(lambda dt: _fit_text_size(), timeout_retry)
                return

            text = self.text or ""
            if not text.strip():
                return

            high = max_font if max_font is not None else max(self.font_size, h)
            low = min_font
            best = low

            while low <= high:
                mid = (low + high) // 2
                core = CoreLabel(
                    text=text,
                    font_size=mid,
                    font_name=getattr(self, "font_name", None),
                    bold=getattr(self, "bold", False),
                    markup=getattr(self, "markup", False),
                )
                # Do NOT set text_size → no wrapping
                core.refresh()
                tex_w, tex_h = core.texture.size

                fits_width = tex_w <= w
                fits_height = not respect_height or tex_h <= h

                if fits_width and fits_height:
                    best = mid
                    low = mid + 1
                else:
                    high = mid - 1

            self.font_size = best
            # text_size should match full size for proper halign/valign (but no wrapping)
            self.text_size = (w, None)

        self.bind(size=_fit_text_size, text=_fit_text_size)
        Clock.schedule_once(lambda dt: _fit_text_size(), 0)


class CameraPreviewWidget(RelativeLayout):
    """
    Pure-Kivy widget for displaying a single camera stream.
    It doesn't fetch frames itself — expects external .update_frame() calls.
    """

    show_ts = BooleanProperty(True)
    show_key = BooleanProperty(True)
    show_path = BooleanProperty(True)
    show_card = BooleanProperty(True)

    preview_running = BooleanProperty(True)

    def __init__(self,
                 camera_key=None, connection_path=None, camera_card=None,
                 show_key=True, show_path=True, show_card=True, show_ts=True,
                 **kwargs):
        super().__init__(**kwargs)

        self._updating_texture = False
        self._last_frame = None

        self.camera_key = camera_key or "Unknown"
        self.connection_path = connection_path or "N/A"
        self.camera_card = camera_card or "Unknown"

        self._bottom_left_anchor = None
        self._top_right_stack = None
        self._bottom_right_stack = None

        self._alias_label = None
        self._pause_label = None
        self._timestamp_label = None
        self._connection_label = None
        self._card_label = None

        # Main image
        self.preview_image = Image(allow_stretch=True, keep_ratio=True)
        self.add_widget(self.preview_image)

        # Overlay
        self._build_overlay()

        self.bind(
            show_ts=self._remount_overlay,
            show_key=self._remount_overlay,
            show_path=self._remount_overlay,
            show_card=self._remount_overlay
        )

        # Freeze shading overlay
        with self.canvas.after:
            self._freeze_color = Color(0, 0, 0, 0)
            self._freeze_rect = Rectangle(pos=self.pos, size=self.size)

        self.bind(preview_running=self._set_freeze_overlay)
        self.bind(pos=self._update_overlay_geometry,
                  size=self._update_overlay_geometry)

    def _remount_overlay(self, *_):
        # raise RuntimeError(_)
        if self.show_key:
            if not self._alias_label.parent:
                self._bottom_left_anchor.add_widget(self._alias_label)
        else:
            if self._alias_label.parent:
                self._bottom_left_anchor.remove_widget(self._alias_label)

        if self.show_path:
            if not self._connection_label.parent:
                self._top_right_stack.add_widget(self._connection_label)
        else:
            if self._connection_label.parent:
                self._top_right_stack.remove_widget(self._connection_label)

        if self.show_card:
            if not self._card_label.parent:
                self._top_right_stack.add_widget(self._card_label)
        else:
            if self._card_label.parent:
                self._top_right_stack.remove_widget(self._card_label)

        if self.show_ts:
            if not self._timestamp_label.parent:
                self._bottom_right_stack.add_widget(self._timestamp_label)
        else:
            if self._timestamp_label.parent:
                self._bottom_right_stack.remove_widget(self._timestamp_label)

    def _build_overlay(self):
        self._bottom_left_anchor = AnchorLayout(anchor_x='left', anchor_y='bottom', padding=10)
        self.add_widget(self._bottom_left_anchor)

        top_right_anchor = AnchorLayout(anchor_x='right', anchor_y='top', padding=10)
        self.add_widget(top_right_anchor)

        bottom_right_anchor = AnchorLayout(anchor_x='right', anchor_y='bottom', padding=10)
        self.add_widget(bottom_right_anchor)

        self._top_right_stack = StackLayout(orientation='tb-rl')
        top_right_anchor.add_widget(self._top_right_stack)

        self._bottom_right_stack = StackLayout(orientation='bt-rl')
        bottom_right_anchor.add_widget(self._bottom_right_stack)

        if self.camera_key:
            self._alias_label = SelfScalingLabel(
                text=self.camera_key,
                color=(1, 1, 1, 0.9),
                halign='left',
                size_hint_x=0.5,
                size_hint_y=0.5,
                size_hint_max_y=100,
                font_size=90,
                bold=True,
            )

        if self.connection_path:
            self._connection_label = SelfScalingLabel(
                text=self.connection_path,
                color=(1, 1, 1, 0.9),
                halign='right',
                size_hint_x=0.8,
                size_hint_y=0.25,
                size_hint_max_y=48,
                font_size=42,
                bold=True,
            )

        if self.camera_card:
            self._card_label = SelfScalingLabel(
                text=self.camera_card,
                color=(1, 1, 1, 0.9),
                halign='right',
                size_hint_x=0.8,
                size_hint_y=0.20,
                size_hint_max_y=38,
                font_size=32,
            )

        self._pause_label = SelfScalingLabel(
            text="[paused]",
            color=(1, 1, 1, 0.9),
            halign='right',
            valign='center',
            size_hint_x=0.5,
            size_hint_y=0.25,
            size_hint_max_y=48,
            font_size=42,
        )

        # --- Timestamp label (bottom-right corner) ---
        self._timestamp_label = SelfScalingLabel(
            text="--:--:--.---",
            color=(1, 1, 1, 0.9),
            halign='right',
            valign='bottom',
            size_hint_x=0.5,
            size_hint_y=0.25,
            size_hint_max_y=48,
            font_size=42,
        )
        self._remount_overlay()

    def start_preview(self, *_):
        if self.preview_running:
            return
        self.preview_running = True

    def stop_preview(self, *_):
        if not self._preview_running:
            return
        self.preview_running = False

    def _set_freeze_overlay(self, *_):
        if not self.preview_running:
            self._freeze_color.a = 0.4
            if not self._pause_label.parent:
                self._bottom_right_stack.add_widget(self._pause_label)
        else:
            self._freeze_color.a = 0
            if self._pause_label.parent:
                self._bottom_right_stack.remove_widget(self._pause_label)

    def _update_overlay_geometry(self, *args):
        self._freeze_rect.pos = self.pos
        self._freeze_rect.size = self.size

    def update_frame(self, frame, timestamp=None):
        """Called externally to provide a new frame (NumPy array)."""
        if not self.preview_running:
            return
        if self._updating_texture:
            return

        self._last_frame = frame
        self._updating_texture = True

        if hasattr(self, "_timestamp_label"):
            if timestamp is None:
                timestamp = datetime.now()
            if isinstance(timestamp, (int, float)):
                ts_str = datetime.fromtimestamp(timestamp).strftime("%H:%M:%S.%f")[:-3]
            elif isinstance(timestamp, datetime):
                ts_str = timestamp.strftime("%H:%M:%S.%f")[:-3]
            else:
                ts_str = str(timestamp)
            self._timestamp_label.text = ts_str

        Clock.schedule_once(self._do_update_texture, 0)

    def _do_update_texture(self, dt):
        frame = self._last_frame
        if frame is None:
            self._updating_texture = False
            return
        try:
            h, w = frame.shape[:2]
            colorfmt = "bgr" if frame.shape[2] == 3 else "bgra"
            buf = frame[::-1].tobytes()
            texture = Texture.create(size=(w, h), colorfmt=colorfmt)
            texture.blit_buffer(buf, colorfmt=colorfmt, bufferfmt="ubyte")
            self.preview_image.texture = texture
        finally:
            self._updating_texture = False
