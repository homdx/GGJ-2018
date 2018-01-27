import os, re, random

import profile

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.carousel import Carousel
from kivy.uix.widget import Widget
from kivy.uix.image import Image as BaseImage
from kivy.core.window import Window

HEADSHOTS = {}
GENDER = {
    '0': 'Unisex',
    '1': 'Male',
    '2': 'Female',
}

class Image(BaseImage):
    def __init__(self, allow_stretch=True, keep_ratio=True, **kwargs):
        super(Image, self).__init__(allow_stretch=allow_stretch,
                keep_ratio=keep_ratio, **kwargs)
        # prevent interpolation when we scale up the image
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

        tex = img.texture
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

    def _load_headshot(self):

        image1 = None

        #print("stack")
        for layer, index in enumerate(sorted(HEADSHOTS.keys())):
            #XXX DEBUG
            #if layer == 1:
            #    break
            item = random.randrange(len(HEADSHOTS[index]))
            #print(HEADSHOTS[index][item]['filename'])
            if layer == 0:
                image1 = Image(source=HEADSHOTS[index][item]['filename'])
            else:
                image1.blit_img(
                        Image(source=HEADSHOTS[index][item]['filename']))

        for i in self.children:
            print(i)
            for j in i.children:
                print(j)

        return image1

    def _next_item(self):
        if len(self.slides) < 3:
            # game isn't ready yet
            print("SKIP")
            return
        image = self._load_headshot()
        self.update_widget(self.index, image)
        index= self.index
        if index -1 < 0:
            index = 2
        else:
            index = index -1
        self.update_widget(index, Image(source='images/Button_Cross.png'))
        if index -1 < 0:
            index = 2
        else:
            index = index -1
        self.update_widget(index, Image(source='images/Button_Heart.png'))

    def __init__(self, **kwargs):
        print("__init__")
        super(BestCarousel, self).__init__(**kwargs)
        image = self._load_headshot()
        self.add_widget(Image(source='images/Button_Cross.png'))
        self.add_widget(image)
        self.add_widget(Image(source='images/Button_Heart.png'))
        self.index = 1

class TextBox(Label):
    pass

class StinderApp(App):

    def build(self):

        # load the bios
        profile.load_bio_content()

        # build head shot file list
        match = re.compile(r'([0-9]+)_([0-9]+)_.*\.png')
        for filename in os.listdir('images'):
            m = match.match(filename)
            if m:
                index = int(m.group(1))
                if index not in HEADSHOTS:
                    HEADSHOTS[index] = []
                HEADSHOTS[index].append({
                    'filename':'images/%s' % filename,
                    'gender':GENDER[m.group(2)]
                })

        print(HEADSHOTS)

        # set the background to white
        Window.clearcolor = (1, 1, 1, 0)

        Window.size = (Window.height / 2, Window.height)

        root = BoxLayout(orientation='vertical')

        self.carousel = BestCarousel(
                direction='right', min_move=0.4, loop=True)

        root.add_widget(self.carousel)

        bio = BoxLayout(orientation='vertical')

        root.add_widget(bio)

        bio_data = profile.generate_bio()
        print(bio_data['name'])
        self.bio = TextBox(text="[color=000000]%s[/color]" %
            profile.format_bio(bio_data), markup=True, font_size='20sp')

        bio.add_widget(self.bio)

        return root

