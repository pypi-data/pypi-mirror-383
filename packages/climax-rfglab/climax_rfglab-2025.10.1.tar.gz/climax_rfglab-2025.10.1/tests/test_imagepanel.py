# slider widget tests.
# for coverage, run:
# cpython -m coverage run -m pytest -vs
# or if you want to include branches:
# python -m coverage run --branch -m pytest -vs
# followed by:
# python -m coverage report -m

import numpy
import pytest
from textual.events import MouseMove

from climax.climax  import climax
from climax._imagepanel import ImagePanel


pytest_plugins = ('pytest_asyncio',)


def test_imagepanel_basic():
    # Test basic initialization of ImagePanel
    image = numpy.random.randint(0, 256, (100, 100), dtype=numpy.uint8)  # Create a random grayscale image
    panel = ImagePanel(image)
    assert panel is not None
    assert panel.image is not None  # No image loaded initially
    assert panel.zoom_factor == 1.0  # Default zoom level

def test_imagepanel_rendering():
    # Test rendering functionality of ImagePanel
    image = numpy.random.randint(0, 256, (100, 100), dtype=numpy.uint8)  # Create a random grayscale image
    panel = ImagePanel(image)
    
    rendered_output = panel.render()  # Call the render method
    assert rendered_output is not None  # Should produce some output

@pytest.mark.parametrize(["x", "y"], [(10, 20), (50, 50), (99, 99), (0, 0), (25, 75), (200, 200)])  # image coordinates
@pytest.mark.asyncio
async def test_imagepanel_mousemove(x, y):
    app = climax()

    # Test mouse move event handling
    image = numpy.random.randint(0, 256, (100, 100), dtype=numpy.uint8)  # Create a random grayscale image
    app.volume = numpy.expand_dims(image, axis=(0, 1, 2))
    app.color = app.volume[0]
    app.slices = app.color[0]
    app.image_data = numpy.transpose(app.slices, climax.orientations[app.view_plane])
    app.display_slice(True, 0)

    async with app.run_test() as pilot:
        event = MouseMove(app.image_panel, x=int(round(x*app.image_panel.zoom_factor*app.image_panel.renderer_xscale)), y=int(round(y*app.image_panel.zoom_factor*app.image_panel.renderer_yscale)), screen_x=int(round(x*app.image_panel.zoom_factor*app.image_panel.renderer_xscale)), screen_y=int(round(y*app.image_panel.zoom_factor*app.image_panel.renderer_yscale)), delta_x=0, delta_y=0, button=None, shift=False, ctrl=False, meta=False)
        app.image_panel.post_message(event)
        await pilot.pause(0.1)
        
        col, row = int(event.x / (app.image_panel.zoom_factor*app.image_panel.renderer_xscale)), int(event.y / (app.image_panel.zoom_factor * app.image_panel.renderer_yscale))

        if col < image.shape[1] and row < image.shape[0]-1:
            assert app.image_panel.tooltip==f"(x={col},y={row}:{row+1})={image[row,col]}:{image[row+1,col]}, {app.image_panel.zoom_factor}x"
        else :
            assert app.image_panel.tooltip is None

def test_imagepanel_getrgb():
    image = numpy.asarray([[0, 20], [240, 255]], dtype=int)  # Example image. Use the 8-bit range up to avoid issues with scaling.
    impanel = ImagePanel(image, cmap='gray')
    rgb = impanel.get_rgb()
    assert rgb.shape == (3, image.shape[0], image.shape[1])  # Should return an RGB array with the correct shape
    assert (rgb[:, 0, 0] == [0, 0, 0]).all()  # First pixel should be black
    assert (rgb[:, 1, 0] == [240, 240, 240]).all()  # Second pixel should match the gray value
    assert (rgb[:, 0, 1] == [20, 20, 20]).all()  # Third pixel should match the gray value
    assert (rgb[:, 1, 1] == [255, 255, 255]).all()  # Fourth pixel should match the gray value

@pytest.mark.parametrize(["min", "max"], [(50, 200), (50, 50)])  # image coordinates
def test_imagepanel_stretch(min, max):
    image = numpy.asarray([[0, 20], [240, 255]], dtype=int)  # Example image
    impanel = ImagePanel(image, cmap='gray')
    stretched = impanel.stretch(image, minimum=min, maximum=max)
    assert stretched.min() == min  # Minimum value should be stretched to min
    assert stretched.max() == max  # Maximum value should be stretched to max
