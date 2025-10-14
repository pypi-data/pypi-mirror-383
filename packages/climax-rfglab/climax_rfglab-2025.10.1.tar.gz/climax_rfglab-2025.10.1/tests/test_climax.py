# slider widget tests.
# for coverage, run:
# cpython -m coverage run -m pytest -vs
# or if you want to include branches:
# python -m coverage run --branch -m pytest -vs
# followed by:
# python -m coverage report -m

import math
import os

import numpy
import pytest
import textual

from climax.climax import climax
from climax.climax_rs import __version__ as cargo_version
from climax.version import __version__ as climax_version

def test_climax_version():
    assert climax_version == cargo_version, f"climax version mismatch: {climax_version} != {cargo_version}"
    
@pytest.mark.usefixtures("climax_gray_fixture")
@pytest.mark.usefixtures("climax_gray_path_fixture")
def test_climax_initialization_gray(climax_gray_fixture, climax_gray_path_fixture):
    a_climax_instance = climax(climax_gray_path_fixture)
    assert isinstance(a_climax_instance, climax)
    assert numpy.array_equal(a_climax_instance.volume, climax_gray_fixture.volume)
    assert numpy.array_equal(a_climax_instance.color, climax_gray_fixture.color)
    assert numpy.array_equal(a_climax_instance.slices, climax_gray_fixture.slices)

    for anelement, adtype in zip(climax_gray_fixture.compose(), [textual.widgets.Header, textual.containers.Vertical, textual.widgets.Footer]):
        assert isinstance(anelement, adtype)

    a_climax_instance = climax([climax_gray_path_fixture, climax_gray_path_fixture])
    assert isinstance(a_climax_instance, climax)
    assert a_climax_instance.volume.shape[-1] == climax_gray_fixture.volume.shape[-1] * 2
    assert numpy.array_equal(a_climax_instance.image_data[0, :, :a_climax_instance.image_data.shape[2]//2], climax_gray_fixture.image_data[0, :, :])

@pytest.mark.usefixtures("climax_colour_fixture")
@pytest.mark.usefixtures("climax_colour_path_fixture")
def test_climax_initialization_colour(climax_colour_fixture, climax_colour_path_fixture):
    a_climax_instance = climax(climax_colour_path_fixture)
    assert isinstance(a_climax_instance, climax)
    assert numpy.array_equal(a_climax_instance.volume, climax_colour_fixture.volume)
    assert numpy.array_equal(a_climax_instance.color, climax_colour_fixture.color)
    assert numpy.array_equal(a_climax_instance.slices, climax_colour_fixture.slices)

    for anelement, adtype in zip(climax_colour_fixture.compose(), [textual.widgets.Header, textual.containers.Vertical, textual.widgets.Footer]):
        assert isinstance(anelement, adtype)

    a_climax_instance = climax([climax_colour_path_fixture, climax_colour_path_fixture])
    assert isinstance(a_climax_instance, climax)
    assert a_climax_instance.volume.shape[-1] == climax_colour_fixture.volume.shape[-1] * 2
    assert numpy.array_equal(a_climax_instance.image_data[0, :, :a_climax_instance.image_data.shape[2]//2], climax_colour_fixture.image_data[0, :, :])

@pytest.mark.usefixtures("climax_gray_fixture")
def test_climax_basic(climax_gray_fixture):
    assert climax_gray_fixture is not None
    assert climax_gray_fixture.volume.ndim == 5
    assert climax_gray_fixture.color.shape == climax_gray_fixture.volume.shape[1:]
    assert climax_gray_fixture.slices.shape == climax_gray_fixture.volume.shape[2:]

@pytest.mark.usefixtures("climax_gray_fixture")
def test_climax_actions(climax_gray_fixture):
    climax_gray_fixture.action_next_slice()
    assert climax_gray_fixture.curslice == 1
    climax_gray_fixture.action_prev_slice()
    assert climax_gray_fixture.curslice == 0
    zoom_index = climax_gray_fixture.zoom_index
    climax_gray_fixture.action_zoom('in')
    assert climax_gray_fixture.zoom_index == zoom_index + 1
    climax_gray_fixture.action_zoom('out')
    assert climax_gray_fixture.zoom_index == zoom_index
    climax_gray_fixture.action_toggle_dark()
    assert climax_gray_fixture.theme == "textual-light"
    assert not climax_gray_fixture.action_toggle_dark()

@pytest.mark.usefixtures("climax_gray_fixture")
def test_climax_tui(climax_gray_fixture):
    # Test the TUI functionality
    climax_gray_fixture.Z_slider.value = 1
    climax_gray_fixture._Z_slider_change()
    assert climax_gray_fixture.curslice == 1
    assert climax_gray_fixture.hist_plt is not None
    assert climax_gray_fixture.hist_plt.plt._active.monitor.xlim[0] == [float(0), float(int(climax_gray_fixture.pix_val_min_max[1]))]
    hist1 = climax_gray_fixture.hist_plt.plt._active.monitor.y.copy()
    climax_gray_fixture.Z_slider.value = 0
    climax_gray_fixture._Z_slider_change()    
    assert climax_gray_fixture.curslice == 0
    assert not all([math.isclose(hist1[i][1], climax_gray_fixture.hist_plt.plt._active.monitor.y[i][1]) for i in range(len(hist1))])
    climax_gray_fixture.Z_slider.value = 1
    climax_gray_fixture._Z_slider_key()    
    assert climax_gray_fixture.curslice == 1
    assert all([math.isclose(hist1[i][1], climax_gray_fixture.hist_plt.plt._active.monitor.y[i][1]) for i in range(len(hist1))])
    climax_gray_fixture.Z_slider.value = 0
    climax_gray_fixture.continuous_update = False
    climax_gray_fixture._Z_slider_click()
    assert climax_gray_fixture.curslice == 0
    climax_gray_fixture.continuous_update = True
    climax_gray_fixture.vmax_slider.value = 10
    climax_gray_fixture.vmin_slider.value = climax_gray_fixture.vmax_slider.value + 1
    climax_gray_fixture._vmin_slider_change()
    assert climax_gray_fixture.vmin_slider.value == climax_gray_fixture.vmax_slider.value
    climax_gray_fixture.vmin_slider.value = 1
    climax_gray_fixture._update_switch_change()
    assert not climax_gray_fixture.continuous_update
    assert not climax_gray_fixture._vmin_slider_click()
    assert not climax_gray_fixture._vmax_slider_click()
    climax_gray_fixture._update_switch_change()
    assert climax_gray_fixture.continuous_update
    
    climax_gray_fixture.vmax_slider.value = climax_gray_fixture.vmin_slider.value - 1
    climax_gray_fixture._vmax_slider_change()
    assert climax_gray_fixture.vmin_slider.value == climax_gray_fixture.vmax_slider.value
    climax_gray_fixture.vmin_slider.value = climax_gray_fixture.vmax_slider.value + 1
    climax_gray_fixture._vmin_slider_key()
    assert climax_gray_fixture.vmin_slider.value == climax_gray_fixture.vmax_slider.value
    climax_gray_fixture.vmax_slider.value = climax_gray_fixture.vmin_slider.value - 1
    climax_gray_fixture._vmax_slider_key()
    assert climax_gray_fixture.vmax_slider.value == climax_gray_fixture.vmin_slider.value
    climax_gray_fixture.colormap_select.value = "gray"
    assert not climax_gray_fixture._cmap_changed()
    original_volume = climax_gray_fixture.volume.copy()
    climax_gray_fixture._rotate_button_press()
    assert not numpy.array_equal(climax_gray_fixture.volume, original_volume)

    climax_gray_fixture.volume = original_volume  # Reset volume
    climax_gray_fixture._flip_horizontal_button_press()
    assert not numpy.array_equal(climax_gray_fixture.volume, original_volume)
    climax_gray_fixture.volume = original_volume
    climax_gray_fixture._flip_vertical_button_press()
    assert not numpy.array_equal(climax_gray_fixture.volume, original_volume)
    climax_gray_fixture.volume = original_volume
    climax_gray_fixture._invert_switch_change()
    assert numpy.array_equal(climax_gray_fixture.volume, original_volume)
    climax_gray_fixture._invert_switch_change()
    assert numpy.array_equal(climax_gray_fixture.volume, original_volume)
    climax_gray_fixture._auto_contrast_pressed()
    assert climax_gray_fixture.vmin_slider.value == climax.mode(climax_gray_fixture.image_data[climax_gray_fixture.curslice,:,:].ravel())[0]
    assert climax_gray_fixture.vmax_slider.value == int(numpy.percentile(climax_gray_fixture.image_data[climax_gray_fixture.curslice,:,:], 99))
    
    climax_gray_fixture.volume = numpy.concatenate((climax_gray_fixture.volume, climax_gray_fixture.volume, climax_gray_fixture.volume), axis=1)
    climax_gray_fixture.volume = numpy.concatenate((climax_gray_fixture.volume, climax_gray_fixture.volume), axis=0)
    assert climax_gray_fixture.volume.shape == (2, 3, 5, 150, 30)
    climax_gray_fixture.color = climax_gray_fixture.volume[0]
    climax_gray_fixture.slices = climax_gray_fixture.color[0]
    climax_gray_fixture.pix_val_min_max = [numpy.min(climax_gray_fixture.color), numpy.max(climax_gray_fixture.color)]
    climax_gray_fixture.image_data = numpy.transpose(climax_gray_fixture.slices, climax.orientations[climax_gray_fixture.view_plane])
    climax_gray_fixture.display_slice(True, 0)
    climax_gray_fixture.time_slider.value = 1
    assert not climax_gray_fixture._time_slider_change()
    climax_gray_fixture.time_slider.value = 0
    assert not climax_gray_fixture._time_slider_key()
    climax_gray_fixture.time_slider.value = 1
    climax_gray_fixture.continuous_update = False
    assert not climax_gray_fixture._time_slider_click()
    climax_gray_fixture.channel_slider.value = 1
    climax_gray_fixture.continuous_update = True
    assert not climax_gray_fixture._channel_slider_change()
    climax_gray_fixture.channel_slider.value = 0
    assert not climax_gray_fixture._channel_slider_key()
    climax_gray_fixture.channel_slider.value = 1
    climax_gray_fixture.continuous_update = False
    assert not climax_gray_fixture._channel_slider_click()
    climax_gray_fixture.continuous_update = True

@pytest.mark.parametrize(["filename"], [("file",), ("file.tif",), ("file.jpg",), ("file.jpeg",), ("file.png",), ("file.tiff",), ("file.bmp",), ("file.TIF",), ("file.JPG",), ("file.JPEG",), ("file.PNG",), ("file.TIFF",), ("file.BMP",), ("file.name.with.dots.png",), ("file.name.with.dots",)])
def test_climax_set_extension(filename):
    assert climax.set_extension(filename, ".tif") == f"{os.path.splitext(filename)[0]}.tif"
