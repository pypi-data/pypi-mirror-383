# slider widget tests.
# for coverage, run:
# cpython -m coverage run -m pytest -vs
# or if you want to include branches:
# python -m coverage run --branch -m pytest -vs
# followed by:
# python -m coverage report -m


import numpy

from climax._renderer import Renderer
from climax._imagepanel import ImagePanel
from climax.climax_rs import _colour_strings_with_newlines_rust


def test_halfcell_renderer_basic():
    img = numpy.zeros((4, 4), dtype=int)
    renderer = Renderer(img)
    segments = renderer.render(None)
    assert segments  # Should produce some segments

def test_halfcell_renderer_with_fixture():
    image = numpy.random.rand(100, 100)
    impanel = ImagePanel(image)
    segments = impanel.renderer.render(None)
    assert segments  # Should produce some segments
    assert len(segments) == (image.shape[0] * image.shape[1] // 2) + (image.shape[0] // 2)  # Each row is half-height and separated by a carriage return character.

def test_halfcell_renderer_with_empty_image():
    image = numpy.zeros((0, 0), dtype=int)  # Empty image
    renderer = Renderer(image)
    segments = renderer.render(None)
    assert segments == []  # Should produce no segments for an empty image

def test_get_color_basic():
    image = numpy.asarray([[0, 20], [60, 80], [240, 255]], dtype=int)  # Example image
    impanel = ImagePanel(image, cmap='gray')
    renderer = Renderer(impanel.map_image(image), rgb_lookup=impanel.rgb_lookup)
    segments = renderer.render(None)
    assert segments[0].style.bgcolor[0] == impanel.rgb_lookup[0]
    assert segments[0].style.color[0] == impanel.rgb_lookup[60]

def test_segment_generation_python():
    image = numpy.asarray([[0, 20], [60, 80]], dtype=int)  # Example image
    impanel = ImagePanel(image, cmap='gray')
    renderer = Renderer(impanel.map_image(image), rgb_lookup=impanel.rgb_lookup)
    
    segments_rust = _colour_strings_with_newlines_rust(renderer.image, impanel.rgb_lookup)
    segments_python = renderer._colour_strings_with_newlines_python()
    assert all(s==t for s, t in zip(segments_rust, segments_python))  # Both methods should produce the same segments
