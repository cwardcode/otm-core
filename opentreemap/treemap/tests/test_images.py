# -*- coding: utf-8 -*-


from PIL import Image

from treemap.images import save_uploaded_image
from treemap.tests import LocalMediaTestCase, media_dir


class SaveImageTest(LocalMediaTestCase):
    @media_dir
    def test_rotates_image(self):
        sideways_file = self.load_resource('tree_sideways.jpg')

        img_file, __ = save_uploaded_image(sideways_file, 'test')

        expected_width, expected_height = Image.open(sideways_file).size
        actual_width, actual_height = Image.open(img_file).size
        self.assertAlmostEqual(expected_width, actual_height, delta=1)
        self.assertAlmostEqual(expected_height, actual_width, delta=1)
