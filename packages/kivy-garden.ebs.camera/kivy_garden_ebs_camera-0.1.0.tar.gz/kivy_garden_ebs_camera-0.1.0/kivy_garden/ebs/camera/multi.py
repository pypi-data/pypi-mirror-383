

from kivy.clock import Clock
from kivy.properties import NumericProperty
from kivy.properties import BooleanProperty

from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout

from .single import CameraPreviewWidget


class MultiCameraPreviewWidget(ScrollView):
    """
    Pure Kivy container for multiple CameraPreviewWidget instances.
     - Automatically reflows based on available width.
     - Keeps 4:3 aspect ratio for camera previews.
     - Expands previews proportionally when more space is available.
     - Scrolls vertically only when needed.
    """

    spacing = NumericProperty(8)
    padding = NumericProperty(8)

    show_ts = BooleanProperty(True)
    show_key = BooleanProperty(True)
    show_path = BooleanProperty(True)
    show_card = BooleanProperty(True)
    preview_running = BooleanProperty(True)

    desired_width = NumericProperty(320)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.camera_widgets = {}

        self._grid = GridLayout(
            cols=1,
            spacing=self.spacing,
            padding=self.padding,
            size_hint_y=None,  # height managed manually for scrolling
        )

        self._grid.bind(minimum_height=self._grid.setter("height"))
        self.add_widget(self._grid)

        # reflow grid on container resize
        self.bind(size=self._on_resize)

    def _propagate_setting(self, name, value):
        for widget in self.camera_widgets.values():
            setattr(widget, name, value)

    def on_show_ts(self, *_):
        self._propagate_setting('show_ts', self.show_ts)

    def on_show_key(self, *_):
        self._propagate_setting('show_key', self.show_key)

    def on_show_path(self, *_):
        self._propagate_setting('show_path', self.show_path)

    def on_show_card(self, *_):
        self._propagate_setting('show_card', self.show_card)

    def on_desired_width(self, *_):
        Clock.schedule_once(lambda dt: self._reflow())

    def on_preview_running(self, *_):
        self._propagate_setting('preview_running', self.preview_running)

    # ------------------------------------------------------------------
    # Camera management
    # ------------------------------------------------------------------
    def add_camera(self, camera_key, connection_path=None, camera_card=None):
        if camera_key in self.camera_widgets:
            return self.camera_widgets[camera_key]

        widget = CameraPreviewWidget(
            camera_key=camera_key,
            connection_path=connection_path or "N/A",
            camera_card=camera_card or "",
            size_hint=(None, None),  # will be explicitly sized
        )
        self._grid.add_widget(widget)
        self.camera_widgets[camera_key] = widget
        Clock.schedule_once(lambda dt: self._reflow())
        return widget

    def remove_camera(self, camera_key):
        widget = self.camera_widgets.pop(camera_key, None)
        if widget:
            self._grid.remove_widget(widget)
        Clock.schedule_once(lambda dt: self._reflow())

    def clear_all(self):
        for widget in list(self.camera_widgets.values()):
            self._grid.remove_widget(widget)
        self.camera_widgets.clear()
        Clock.schedule_once(lambda dt: self._reflow())

    # ------------------------------------------------------------------
    # Layout logic
    # ------------------------------------------------------------------
    def _on_resize(self, *args):
        Clock.schedule_once(lambda dt: self._reflow())

    def _reflow(self, *args):
        """Recalculate grid columns and resize children responsively."""

        n = len(self.camera_widgets)
        if n == 0:
            return

        grid_width = self.width - 2 * self.padding

        # Heuristic tuning parameters
        desired_width = self.desired_width  # target width for one preview
        min_width = desired_width * 0.7  # allow up to 30% compression

        # Start by estimating how many previews fit at desired size
        cols = max(1, int(grid_width // (desired_width + self.spacing)))

        # Ensure we have at least 1 and at most N columns
        cols = min(max(cols, 1), n)

        # Now compute actual width based on this many columns
        total_spacing = self.spacing * (cols - 1)
        available = grid_width - total_spacing
        child_width = available / cols

        # If too small, drop columns until we're above min_width
        while cols > 1 and child_width < min_width:
            cols -= 1
            total_spacing = self.spacing * (cols - 1)
            available = grid_width - total_spacing
            child_width = available / cols

        # Apply final column count
        self._grid.cols = cols

        # Maintain 4:3 aspect ratio
        child_height = child_width * 3 / 4

        # Update each preview
        for w in self.camera_widgets.values():
            w.size = (child_width, child_height)

        # Adjust grid height
        rows = (n + cols - 1) // cols
        grid_height = rows * (child_height + self.spacing) - self.spacing + 2 * self.padding
        self._grid.height = max(grid_height, self.height)
