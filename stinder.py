from kivy.app import App
from kivy.uix.carousel import Carousel
from kivy.uix.widget import Widget
from kivy.uix.image import Image as BaseImage
from kivy.core.window import Window

class Image(BaseImage):
    def __init__(self, allow_stretch=True, keep_ratio=True, **kwargs):
        super(Image, self).__init__(allow_stretch=allow_stretch,
                keep_ratio=keep_ratio, **kwargs)
        self.texture.min_filter = 'nearest'
        self.texture.mag_filter = 'nearest'

    def blit_img(self, img):
        """
        blit image onto this image
        """
        pixels1 = bytearray(self.texture.pixels)
        pixels2 = bytearray(img.texture.pixels)
        for i, v in enumerate(pixels2):
            if v != 0:
                pixels1[i] = v

        tex = self.texture
        self.texture.blit_buffer(pixels1, colorfmt=tex.colorfmt,
                bufferfmt=tex.bufferfmt)

class BestCarousel(Carousel):
    def on_touch_up(self, obj):
        super(BestCarousel, self).on_touch_up(obj)

    def on_index(self, *args):
        super(BestCarousel, self).on_index(*args)
        self._next_item()

    def update_widget(self, index, widget):

        # get the old widget from this index
        old_widget = self.slides[index]

        # get the slide holding this object
        slide = old_widget.parent

        # remove the old widget from the slide
        slide.remove_widget(old_widget)

        # add the new widget to the slide
        slide.add_widget(widget)

        # and replace the widget in the slides list
        self.slides[index] = widget

    def _load_image(self, src):

        image1 = Image(source=src)

        image2 = Image(source="images/10_1_Face_Tan.png")

        image1.blit_img(image2)

        return image1

    def _next_item(self, init=False):
        if len(self.slides) < 2:
            # game isn't ready yet
            return
        for index in range(len(self.slides)):
            if init == False and index == self.index:
                continue
            image = self._build_headshot()
            self.update_widget(index, image)

    def _build_headshot(self):
        src = "images/0_1_Shirt_Blue.png"
        image = self._load_image(src)
        return image

    def __init__(self, **kwargs):
        print("__init__")
        super(BestCarousel, self).__init__(**kwargs)
        while len(self.slides) < 2:
            src = "images/Hulk Hogan.png"
            image = self._load_image(src)
            self.add_widget(image)
        self._next_item(init=True)

class StinderApp(App):

    def build(self):

        # set the background to white
        Window.clearcolor = (1, 1, 1, 1)

        # start BestCarousel
        self.carousel = BestCarousel(
                direction='right', min_move=0.1, loop=True)

        return self.carousel

