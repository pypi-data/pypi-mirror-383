import argparse
import os
from typing import Optional

import matplotlib.pyplot as plt
import numpy as np
import skimage
import tifffile


from textual import on, work
from textual.app import App, ComposeResult
from textual.containers import Horizontal, HorizontalScroll, Vertical, VerticalScroll
from textual.widgets import Button, Footer, Header, Label, Select, RadioButton, RadioSet, Switch

import textual_fspicker as tfs
import textual_plotext as tplt

from climax._imagepanel import ImagePanel
from climax._slider import Slider
from climax.version import __version__


class climax(App):
    """a Command Line IMAge eXplorer."""
    __default_filename__: str = 'climax_logo_100x100.png'
    __default_cmap__: str = 'gray'
    __default_channels__: tuple[str] = ('', )
    __default_zoom__: float = 1.0

    CSS_PATH = "climax.tcss"
    orientations = {'x-y': [0, 1, 2], 'z-y': [2, 1, 0], 'z-x': [1, 2, 0]}
    image_extensions: tuple[str] = ('.tif', '.tiff', '.jpg', '.jpeg', '.gif', '.png', '.bmp')
    image_filter: tfs.Filters = tfs.Filters(("Images", lambda p: p.suffix.lower() in climax.image_extensions))    
    zoom_factors: tuple[float] = (1./32., 1./16., 1./8., 1./4., 1./2., 1., 2., 4., 8., 16., 32.)
    colormaps: list[str] = plt.colormaps()


    BINDINGS = [
                (".", "next_slice", "next slice"),
                ("comma", "prev_slice", "previous slice"),
                ("+", "zoom('in')", "zoom in"),
                ("=", "zoom('in')", None),
                ("-", "zoom('out')", "zoom out"),
                ("_", "zoom('out')", None),
                ("i", "toggle_interpolation", "toggle interpolation"),
                ("k", "toggle_dark", "toggle dark mode"),
                ("o", "open_image", "open image"),
                ("t", "import_sequence", "import sequence"),
                ("s", "save_display", "save display"),
                ]

    AUTO_FOCUS = "#image-panel"

    def __init__(self, filename: str|list[str]='', channel_strs: Optional[tuple[str]] = __default_channels__, cmap: str = __default_cmap__, zoomf: float = __default_zoom__):
        super().__init__()

        self.input_image = True
        
        # This if statement here for debugging purposes.
        if filename==[] or filename is None or filename is False or filename=='':
            filename = os.path.join(os.path.dirname(__file__), climax.__default_filename__)
            self.input_image = False

        self.cmap: str = cmap 

        self.invert_image: bool = False  # invert image
        self.continuous_update: bool = True  # continuous update
        self.curslice: int = 0
        self.view_plane: str = list(climax.orientations.keys())[0]
        self.zoom_index: int = climax.zoom_factors.index(zoomf) if zoomf in climax.zoom_factors else 0

        self.volume: np.ndarray = None
        self.color: np.ndarray = None
        self.slices: np.ndarray = None
        self.pix_val_min_max: list = [-1, -1]
        self.image_data: np.ndarray = None
        self.image_panel: ImagePanel = None

        self.load_volume(filename, channel_strs)

        self.create_UI()
        self._setupUI()
        self.image_panel = ImagePanel(self.image_data[self.curslice], cmap=self.cmap, id="image-panel")


    def load_volume(self, filename: str|list[str], channel_strs: Optional[tuple[str]] = ('', )) -> None:        
        if isinstance(filename, str):
            volume = climax.read_image(filename, channel_strs)
            if volume is None:
                # throw exception instead.
                print(f'No volume found at that path. The current path is {os.path.curdir}.')

        elif isinstance(filename, list):
            volume_list: list = []
            for afile in filename:
                loaded_stack = climax.read_image(afile, channel_strs)
                if loaded_stack is not None:
                    volume_list.append(loaded_stack)

            volume = np.concatenate(np.asarray(volume_list), axis=volume_list[0].ndim-1)

        self.volume: np.ndarray = volume
        self.slices: np.ndarray = None

        match self.volume.ndim:
            case 1:
                self.volume = np.expand_dims(self.volume, axis=(0, 1, 2, 3, ))
            case 2:
                self.volume = np.expand_dims(self.volume, axis=(0, 1, 2, ))
            case 3:
                self.volume = np.expand_dims(self.volume, axis=(0, 1, ))
            case 4:
                self.volume = np.expand_dims(self.volume, axis=0)
            case 5:
                pass
            case _:
                print(f"I don't know how to deal with {self.volume.ndim}-dimensional images. But file an issue at https://bitbucket.org/rfg_lab/climax/issues and someone will teach me.")

       # image quality control: for images that are not unsigned int, convert to unsigned int with as many bits as necessary for the image range.
        if not self.volume.dtype.kind == 'u':
            self.volume = self.volume.astype(np.uint16)
            im_range = int(np.ceil(self.volume.max()-self.volume.min())) if self.volume.min() < 0. else int(np.ceil(self.volume.max()))
            min_bytes = int(np.ceil(len(bin(im_range)[2:])/8))
            self.volume = self.volume.astype(np.dtype(f'uint{min_bytes*8}'))

        self.color = self.volume[0]
        self.slices = self.color[0]

        self.pix_val_min_max: list = [np.min(self.color), np.max(self.color)]
        self.image_data = np.transpose(self.slices, climax.orientations[self.view_plane])

    async def on_mount(self) -> None:
        self.theme = "textual-dark"  # set the default theme to dark mode
        if not self.input_image:
            self.action_open_image()

    def create_UI(self):
        max_Z = self.slices.shape[0]-1 if self.slices.shape[0]>1 else 1        
        self.Z_slider_name_label = Label("image slice:", id="image-slice-label")
        self.Z_slider_value_label = Label(f"{self.curslice}", id="image-slice-value")
        self.Z_slider = Slider(0, max_Z, id="Z-slider")
        self.Z_slider_group = HorizontalScroll(self.Z_slider_name_label, self.Z_slider, self.Z_slider_value_label, id="Z-slider-group")

        max_time = self.volume.shape[1]-1 if self.volume.shape[1]>1 else 1
        self.time_slider_name_label = Label("time point: ", id="time-point-label")
        self.time_slider_value_label = Label(f"{self.curslice}", id="time-point-value")
        self.time_slider = Slider(0, max_time, id="time-slider")
        self.time_slider_group = HorizontalScroll(self.time_slider_name_label, self.time_slider, self.time_slider_value_label, id="time-slider-group")

        max_channel = self.volume.shape[0]-1 if self.volume.shape[0]>1 else 1
        self.channel_slider_name_label = Label("channel:    ", id="channel-point-label")
        self.channel_slider_value_label = Label(f"{self.curslice}", id="channel-point-value")
        self.channel_slider = Slider(0, max_channel, id="channel-slider")
        self.channel_slider_group = HorizontalScroll(self.channel_slider_name_label, self.channel_slider, self.channel_slider_value_label, id="channel-slider-group")

        self.vmin_label = Label("minimum pixel value:", id="vmin-label")
        self.vmin_value_label = Label(f"{self.curslice}", id="vmin-value-label")
        self.vmin_slider = Slider(0, self.pix_val_min_max[1], value=self.pix_val_min_max[0], id="vmin-slider")
        self.vmin_group = HorizontalScroll(self.vmin_label, self.vmin_slider, self.vmin_value_label, id="vmin-slider-group")

        self.vmax_label = Label("maximum pixel value:", id="vmax-label")
        self.vmax_value_label = Label(f"{self.curslice}", id="vmax-value-label")
        self.vmax_slider = Slider(0, self.pix_val_min_max[1], value=self.pix_val_min_max[1], id="vmax-slider")
        self.vmax_group = HorizontalScroll(self.vmax_label, self.vmax_slider, self.vmax_value_label, id="vmax-slider-group")

        self.rotate_button = Button("rotate", id="rotate-button", tooltip="rotate 90° clockwise")
        self.flip_horizontal_button = Button("flip h.", id="fliph-button", tooltip="flip horizontal")
        self.flip_vertical_button = Button("flip v.", id="flipv-button", tooltip="flip vertical")
        self.invert_image_label = Label("invert: ", id="invert-label")
        self.invert_image_switch = Switch(value=self.invert_image, id="invert-switch", tooltip="invert image")
        self.continuous_update_label = Label("update: ", id="update-label")
        self.continuous_update_switch = Switch(value=self.continuous_update, id="update-switch", tooltip="update continuously")

        self.slice_radio_set = RadioSet(*[RadioButton(anorientation, value=(not anindex)) for anindex, anorientation in enumerate(self.orientations.keys())], id="plane-radio", tooltip='slicing plane')
                
        self.auto_contrast_button = Button("auto", id="auto-contrast-button", tooltip="Scale display from image mode to 99th percentile")
        self.colormap_select = Select.from_values(self.colormaps, value=self.cmap, id="colormap-select")

        self.button_bar = HorizontalScroll(self.rotate_button, self.flip_horizontal_button, self.flip_vertical_button, self.invert_image_label, self.invert_image_switch, self.continuous_update_label, self.continuous_update_switch)

        self.hist_plt = tplt.PlotextPlot()

        self.dashboard = Horizontal(Vertical(self.channel_slider_group, self.time_slider_group, self.Z_slider_group, self.button_bar), self.slice_radio_set, Vertical(self.vmin_group, self.vmax_group, HorizontalScroll(self.auto_contrast_button, self.colormap_select)), self.hist_plt, id='dashboard')

    def _setupUI(self):
        if self.volume.shape[0] > 1:
            self.channel_slider.disabled = False
        else:
            self.channel_slider.disabled = True
            self.channel_slider.value = 0
            self.channel_slider_value_label.update("0")

        if self.volume.shape[1] > 1:
            self.time_slider.disabled = False
        else:
            self.time_slider.disabled = True
            self.time_slider.value = 0
            self.time_slider_value_label.update("0")
            
        self.Z_slider.disabled = False if self.slices.shape[0] > 1 else True
        self.slice_radio_set.disabled = False if self.slices.shape[0] > 1 else True

    def display_slice(self, reset_slices: Optional[bool] = False, curslice: Optional[int] = -1) -> None:
        if reset_slices or (self.slice_radio_set.pressed_button and self.view_plane != str(self.slice_radio_set.pressed_button.label)):
            self.view_plane = str(self.slice_radio_set.pressed_button.label) if self.slice_radio_set.pressed_button else list(climax.orientations.keys())[0]
            
            self.image_data = np.transpose(self.slices, climax.orientations[self.view_plane])
    
            self.Z_slider.max = self.image_data.shape[0]-1 if self.image_data.shape[0]>1 else 1 
            self.Z_slider.value = curslice if 0 <= curslice <= self.Z_slider.max else 0 

            self.vmin_slider.max = self.pix_val_min_max[1]
            self.vmax_slider.max = self.pix_val_min_max[1]
            #self.vmin_slider.value = self.pix_val_min_max[0]
            #self.vmax_slider.value = self.pix_val_min_max[1]

            self.channel_slider.max = self.volume.shape[0]-1 if self.volume.shape[0]>1 else 1
            self.channel_slider.value = int(self.channel_slider_value_label._content)
            self.time_slider.max = self.volume.shape[1]-1 if self.volume.shape[1]>1 else 1
            self.time_slider.value = int(self.time_slider_value_label._content)

            self._setupUI()

        elif 0 <= curslice <= self.Z_slider.max:
            self.Z_slider.value = curslice
            self.channel_slider.value = int(self.channel_slider_value_label._content)
            self.time_slider.value = int(self.time_slider_value_label._content)

        self.curslice = self.Z_slider.value  
        self.Z_slider_value_label.update(f"{self.curslice}")  
        self.vmin_value_label.update(f"{self.vmin_slider.value}")
        self.vmax_value_label.update(f"{self.vmax_slider.value}")
        self.image_panel.set_pixels(self.image_data[self.curslice], self.vmin_slider.value, self.vmax_slider.value, zoom_factor=self.zoom_factors[self.zoom_index])

        self.plot_histogram()
        self.image_panel.display_slice()

    def resetUI(self):
        "Actions to perform ONLY when a new image or sequence is loaded."
        self.vmin_slider.value = self.pix_val_min_max[0]
        self.vmax_slider.value = self.pix_val_min_max[1]
        self.Z_slider.value = 0
        self.channel_slider.value = 0
        self.time_slider.value = 0
        self.view_plane: str = list(climax.orientations.keys())[0]
        self.zoom_index: int = climax.zoom_factors.index(1.0)
            
    def plot_histogram(self):
        self.hist_plt.plt.clf()
        self.hist_plt.plt.hist(self.image_data[self.curslice].ravel(), int(self.pix_val_min_max[1]), norm=True)
        self.hist_plt.plt.xlim(0, int(self.pix_val_min_max[1]))
        self.hist_plt.plt.ylim(0, None)
        self.hist_plt.plt.xticks(np.arange(0, int(self.pix_val_min_max[1]), int(self.pix_val_min_max[1]/10)))

        max_y = max(max(self.hist_plt.plt._active.monitor.y))

        self.hist_plt.plt.plot([self.vmin_slider.value, self.vmin_slider.value], [0, max_y], color='red')
        self.hist_plt.plt.plot([self.vmax_slider.value, self.vmax_slider.value], [0, max_y], color='cyan')
        self.hist_plt.refresh()

    def compose(self) -> ComposeResult:
        """Create child widgets for the app."""
        yield Header(id="header")

        image_scroll = VerticalScroll(
            HorizontalScroll(self.image_panel, id="horizontal-scroll"),
            id="vertical-scroll"
        )
        yield Vertical(self.dashboard, image_scroll, id="main")
        yield Footer(id="footer")


    def action_toggle_dark(self) -> None:
        """An action to toggle dark mode."""
        self.theme = (
            "textual-dark" if self.theme == "textual-light" else "textual-light"
        )

    def action_next_slice(self):
        self.display_slice(curslice=self.curslice+1)

    def action_prev_slice(self):
        self.display_slice(curslice=self.curslice-1)

    def action_zoom(self, direction: str) -> None:
        """An action to change zoom."""
        if direction == "in":
            self.zoom_index = min(self.zoom_index + 1, len(self.zoom_factors) - 1)
        elif direction == "out":
            self.zoom_index = max(self.zoom_index - 1, 0)
        self.display_slice()

    def action_toggle_interpolation(self) -> None:
        """An action to interpolate images."""
        self.image_panel.renderer.interpolation_order = 1 if self.image_panel.renderer.interpolation_order == 0 else 0
        self.display_slice()

    @work
    async def action_open_image(self) -> None:
        """An action to open a new image."""
        if opened := await self.push_screen_wait(tfs.FileOpen(title="Open image", filters=climax.image_filter)):
            self.load_volume(str(opened))  # FileOpen returns a Path object, but we need a string.
            self.display_slice(True, 0)  
            self.resetUI()
                        
    @work
    async def action_import_sequence(self) -> None:
        """An action to import a file sequence."""
        if opened := await self.push_screen_wait(tfs.SelectDirectory(title="Select folder")):
            self.load_volume(str(opened))  # FileOpen returns a Path object, but we need a string.
            self.display_slice(True, 0)  
            self.resetUI()
    @work
    async def action_save_display(self) -> None:
        """An action to save the current display."""
        if saved := await self.push_screen_wait(tfs.FileSave(title="Save image", filters=climax.image_filter)):
            skimage.io.imsave(climax.set_extension(str(saved), climax.image_extensions[0]), self.image_panel.get_rgb())  # FileSave returns a Path object, but we need a string.

    @on(Slider.Changed, "#Z-slider")
    def _Z_slider_change(self) -> None:
        if not self.Z_slider.disabled and self.Z_slider.value != self.curslice:
            self.curslice = self.Z_slider.value
            self.Z_slider_value_label.update(f"{self.curslice}")

            if self.continuous_update:
                self.display_slice()

    @on(Slider.Clicked, "#Z-slider")
    def _Z_slider_click(self) -> None:
        if not self.Z_slider.disabled and not self.continuous_update:
            self.display_slice()

    @on(Slider.Keyed, "#Z-slider")
    def _Z_slider_key(self) -> None:
        if not self.Z_slider.disabled:
            self.display_slice()

    @on(Slider.Changed, "#time-slider")
    def _time_slider_change(self) -> None:
        if not self.time_slider.disabled:
            curtime = self.time_slider.value
            self.slices = self.color[curtime]
            self.time_slider_value_label.update(f"{curtime}")
            if self.continuous_update:
                self.display_slice(True, self.curslice)

    @on(Slider.Keyed, "#time-slider")
    def _time_slider_key(self) -> None:
        if not self.time_slider.disabled:
            curtime = self.time_slider.value
            self.slices = self.color[curtime]
            self.time_slider_value_label.update(f"{curtime}")
            self.display_slice(True, self.curslice)

    @on(Slider.Clicked, "#time-slider")
    def _time_slider_click(self) -> None:
        if not self.time_slider.disabled and not self.continuous_update:
            self.display_slice(True, self.curslice)

    @on(Slider.Changed, "#channel-slider")
    def _channel_slider_change(self) -> None:
        if not self.channel_slider.disabled:
            curchannel = self.channel_slider.value
            self.color = self.volume[curchannel]
            self.slices = self.color[self.time_slider.value]
            self.channel_slider_value_label.update(f"{curchannel}")
            if self.continuous_update:
                self.display_slice(True, self.curslice)

    @on(Slider.Keyed, "#channel-slider")
    def _channel_slider_key(self) -> None:
        if not self.channel_slider.disabled:
            curchannel = self.channel_slider.value
            self.color = self.volume[curchannel]
            self.slices = self.color[self.time_slider.value]
            self.channel_slider_value_label.update(f"{curchannel}")
            self.display_slice(True, self.curslice)

    @on(Slider.Clicked, "#channel-slider")
    def _channel_slider_click(self) -> None:
        if not self.channel_slider.disabled and not self.continuous_update:
            self.display_slice(True, self.curslice)

    @on(Slider.Changed, "#vmin-slider")
    def _vmin_slider_change(self) -> None:
        if self.vmin_slider.value > self.vmax_slider.value:
            self.vmax_slider.value = self.vmin_slider.value
        self.vmin_value_label.update(f"{self.vmin_slider.value}")
        if self.continuous_update:
            self.display_slice()

    @on(Slider.Keyed, "#vmin-slider")
    def _vmin_slider_key(self) -> None:
        if self.vmin_slider.value > self.vmax_slider.value:
            self.vmax_slider.value = self.vmin_slider.value
        self.vmin_value_label.update(f"{self.vmin_slider.value}")
        self.display_slice()

    @on(Slider.Clicked, "#vmin-slider")
    def _vmin_slider_click(self) -> None:
            if not self.continuous_update:
                self.display_slice()

    @on(Slider.Changed, "#vmax-slider")
    def _vmax_slider_change(self) -> None:
        if self.vmax_slider.value < self.vmin_slider.value:
            self.vmin_slider.value = self.vmax_slider.value
        self.vmax_value_label.update(f"{self.vmax_slider.value}")
        if self.continuous_update:
            self.display_slice()

    @on(Slider.Keyed, "#vmax-slider")
    def _vmax_slider_key(self) -> None:
        if self.vmax_slider.value < self.vmin_slider.value:
            self.vmin_slider.value = self.vmax_slider.value
        self.vmax_value_label.update(f"{self.vmax_slider.value}")
        self.display_slice()

    @on(Slider.Clicked, "#vmax-slider")
    def _vmax_slider_click(self) -> None:
            if not self.continuous_update:
                self.display_slice()

    @on(Button.Pressed, "#rotate-button")
    def _rotate_button_press(self) -> None:
        self.volume = np.rot90(self.volume, -1, (3, 4))
        self.color = self.volume[self.channel_slider.value]
        self.slices = self.color[self.time_slider.value]
        self.display_slice(True, self.curslice)

    @on(Button.Pressed, "#fliph-button")
    def _flip_horizontal_button_press(self) -> None:
        self.volume = self.volume[..., ::-1]
        self.color = self.volume[self.channel_slider.value]
        self.slices = self.color[self.time_slider.value]
        self.display_slice(True, self.curslice)

    @on(Button.Pressed, "#flipv-button")
    def _flip_vertical_button_press(self) -> None:
        self.volume = self.volume[..., ::-1, :]
        self.color = self.volume[self.channel_slider.value]
        self.slices = self.color[self.time_slider.value]
        self.display_slice(True, self.curslice)

    @on(Switch.Changed, "#update-switch")
    def _update_switch_change(self) -> None:
        self.continuous_update = not self.continuous_update

    @on(Switch.Changed, "#invert-switch")
    def _invert_switch_change(self) -> None:
        self.invert_image = not self.invert_image
        if self.cmap.endswith("_r"):
            self.cmap = self.cmap[:-2]
        else:
            self.cmap += "_r"

        self.colormap_select.value = self.cmap
        self.image_panel.set_cmap(self.cmap)
        self.display_slice()

    @on(Button.Pressed, "#auto-contrast-button")
    def _auto_contrast_pressed(self) -> None:
        """Scale from mode to 99th percentile."""
        low = climax.mode(self.image_data[self.curslice,:,:].ravel())[0]
        high = int(np.percentile(self.image_data[self.curslice,:,:], 99))

        self.vmin_slider.value = low  # This triggers vmin and vmax changed events. Would be nicer if only one event was triggered, but we still need to update the sliders ...
        self.vmax_slider.value = high

        old_update = self.continuous_update
        self.continuous_update = True

        self._vmin_slider_change()
        self._vmax_slider_change()

        self.continuous_update = old_update

    @on(Select.Changed, "#colormap-select")
    def _cmap_changed(self) -> None:
        self.cmap = self.colormap_select.value
        self.image_panel.set_cmap(self.cmap)
        self.display_slice()

    @on(RadioSet.Changed, "#plane-radio")
    def _plane_changed(self) -> None:
        self.display_slice(True, 0)

    @classmethod
    def read_image(cls, file_path: str, channel_strs: Optional[tuple[str]]=('',)) -> Optional[np.ndarray]:
        im: np.ndarray = None

        if os.path.isfile(file_path):        
            _, ext = os.path.splitext(file_path)

            # First try to read images within the allowed extensions.
            if str.lower(ext) in climax.image_extensions:
                im = skimage.io.imread(file_path)
            # If the extension is unknown, try to read as a tiff file.
            else:
                try:
                    im = tifffile.imread(file_path)
                except Exception:
                    return None
            
            # Multi-channel images: shift the number of channels (im.shape[2]) to the first dimension.
            if im.ndim == 3 and (im.shape[2] == 3 or im.shape[2] == 4): # without (3) or with (4) alpha channel
                im = np.rollaxis(im, 2) # ignore the alpha channel if there were one.

            # Multi-channel time series.
            elif im.ndim == 4:
                # shift the number of channels (im.shape[2]) to the first dimension.
                im = np.rollaxis(im, 3)

                #volume_list: list = []
                #for achannel in im:
                #    volume_list.append(achannel)
                #
                #im = np.concatenate(np.asarray(volume_list), axis=volume_list[0].ndim-1)

        
        elif os.path.isdir(file_path):
            channels: list[np.ndarray] = [[] for _ in channel_strs]

            for filename in sorted(os.listdir(file_path)):
                img = cls.read_image(os.path.join(file_path, filename))

                if img is not None:
                    index_list = [theindex for theindex in range(len(channel_strs)) if channel_strs[theindex] in filename]

                    if index_list != []:
                        channels[index_list[0]].append(img)

            im = np.asarray(channels)

        return im
    
    @classmethod
    def mode(cls, anarray: np.ndarray):
        vals, cnts = np.unique(anarray, return_counts=True)
        modes, counts = vals[cnts.argmax()], cnts.max()
        return modes[()], counts[()]

    @classmethod
    def set_extension(cls, filename: str, extension: str) -> str:
        """
        Generates a string based on filename that concludes in the desired extension.
        If the filename string already had an extension, it will be substituted with
        the provided one.

        :param filename:
        :param extension:
        :return:
        """
        # Make sure file extension is extension.
        thefile, old_ext = os.path.splitext(filename)
        if old_ext != extension:
            return thefile + extension
        else:
            return filename
    
    @classmethod
    def parse_arguments(cls) -> argparse.Namespace:
        parser = argparse.ArgumentParser(
            prog='climax',
            description='a Comand Line IMAge eXplorer',
        )

        parser.add_argument('filename', nargs='*', help='path to a file to open, or to a folder that contains an image sequence')  # this could be a list?
        parser.add_argument('-s', '--strings', nargs='*', default=climax.__default_channels__, help='substrings to distinguish which files in a folder belong to which channel')
        parser.add_argument('-c', '--cmap', default=climax.__default_cmap__, help='colormap used to display the image (see https://matplotlib.org/stable/users/explain/colors/colormaps.html)')
        parser.add_argument('-v', '--version', action='version', version=f'%(prog)s {__version__}', help='display the version number and exit')
        parser.add_argument('-z', '--zoom', default=climax.__default_zoom__, help='zoom factor for displaying the image', type=float)

        return parser.parse_args()
    
def main():
    args = climax.parse_arguments()
    app = climax(args.filename, cmap=args.cmap, channel_strs=args.strings, zoomf=args.zoom)
    app.run()

if __name__ == "__main__":
    main()

    