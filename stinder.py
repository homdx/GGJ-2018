import os, re, random

import stinder_profile as profile

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.carousel import Carousel
from kivy.uix.widget import Widget
from kivy.uix.button import Button
from kivy.uix.image import Image as BaseImage
from kivy.core.window import Window
from kivy.core.audio import SoundLoader

HEADSHOTS = {}
GENDER = {
    '0': 'unisex',
    '1': 'male',
    '2': 'female',
}

class rootWidget(BoxLayout):
    def __init__(self, **kwargs):
        super(rootWidget, self).__init__(**kwargs)

    def clear_windows(self):
        for child in self.children:
            self.remove_widget(child)

    def run_game(self):
        # build head shot file list
        match = re.compile(r'([0-9]+)_([0-9]+)_.*\.png')
        for filename in os.listdir('images'):
            m = match.match(filename)
            if m:
                index = int(m.group(1))
                gender = GENDER[m.group(2)]
                if index not in HEADSHOTS:
                    HEADSHOTS[index] = {}
                    HEADSHOTS[index]['male'] = []
                    HEADSHOTS[index]['female'] = []
                if gender == 'male' or gender == 'unisex':
                    HEADSHOTS[index]['male'].append({
                        'filename':'images/%s' % filename,
                })
                if gender == 'female' or gender == 'unisex':
                    HEADSHOTS[index]['female'].append({
                        'filename':'images/%s' % filename,
                })

        root = BetterBoxLayout(orientation='vertical')
        self.bio = TextBox(text="" , markup=True, font_size='20sp')

        self.carousel = BestCarousel(self.bio,
                direction='right', min_move=0.4, loop=True)

        root.add_widget(self.carousel)

        bio = BetterBoxLayout(orientation='vertical')

        root.add_widget(bio)

        bio.add_widget(self.bio)

        self.clear_windows()

        self.add_widget(root)

class Image(BaseImage):
    def __init__(self, blank=False, allow_stretch=True, keep_ratio=True, **kwargs):
        super(Image, self).__init__(allow_stretch=allow_stretch,
                keep_ratio=keep_ratio, **kwargs)
        # prevent interpolation when we scale up the image
        self.texture.min_filter = 'nearest'
        self.texture.mag_filter = 'nearest'
        # deal with blanking the entire image
        if blank:
            self._blank()

    def _blank(self):
        """
        blank the entire image
        """
        pixels1 = bytearray(self.texture.pixels)
        for i in range(0, len(pixels1), 4):
            pixels1[i] = 255
            pixels1[i+1] = 255
            pixels1[i+2] = 255
            pixels1[i+3] = 255
        self.texture.blit_buffer(pixels1, colorfmt=self.texture.colorfmt,
                bufferfmt=self.texture.bufferfmt)

    def blit_img(self, img):
        """
        blit image onto this image
        """
        pixels1 = bytearray(self.texture.pixels)
        pixels2 = bytearray(img.texture.pixels)

        for i in range(0, len(pixels2), 4):
            if pixels2[i] == 0 and pixels2[i+1] == 0 and pixels2[i+2] == 0 \
                    and pixels2[i+3] != 255:
                continue
            pixels1[i] = pixels2[i]
            pixels1[i+1] = pixels2[i+1]
            pixels1[i+2] = pixels2[i+2]
            pixels1[i+3] = 255

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

        # update bio data
        self.bio_data = profile.generate_bio()
        self.bio.text = "[color=000000]%s[/color]" % \
                                profile.format_bio(self.bio_data)

        # blank image
        image1 = Image(source='images/blank.png', blank=True)

        # build avatar
        for layer, index in enumerate(sorted(HEADSHOTS.keys())):
            options = len(HEADSHOTS[index][self.bio_data['gender']])
            if options == 0:
                continue
            item = random.randrange(options)
            filename = HEADSHOTS[index][self.bio_data['gender']][item]['filename']
            image1.blit_img(Image(source=filename))

        return image1

    def _next_item(self):
        if len(self.slides) < 3:
            # game isn't ready yet
            return
        if self.index == 2:
            self.good_swipe = SoundLoader.load('assets/audio/oh_yeah_1.wav')
            self.good_swipe.play()
        elif self.index == 0:
            self.bad_swipe = SoundLoader.load('assets/audio/boo_1.wav')
            self.bad_swipe.play()

        # load next headshot
        image = self._load_headshot()
        self.update_widget(1, image)

        # reset to slide 1
        self.index = 1

    def __init__(self, bio, **kwargs):

        # save bio widget for later updating
        self.bio = bio

        # load the audio files
        self.swiping_music = SoundLoader.load('assets/audio/swiping_music.mp3')
        self.swiping_music.loop = True
        self.swiping_music.volume = 0.2
        self.swiping_music.play()
        self.good_swipe = SoundLoader.load('assets/audio/oh_yeah_1.wav')
        self.bad_swipe = SoundLoader.load('assets/audio/boo_1.wav')

        # call the superclass init function
        super(BestCarousel, self).__init__(**kwargs)

        # load the bio content options into the module
        profile.load_bio_content()

        # set up the slide widgets in the carousel
        self.add_widget(Image(source='images/Button_Cross.png'))
        self.add_widget(Image(source='images/blank.png', blank=True))
        self.add_widget(Image(source='images/Button_Heart.png'))
        self.index = 1

class StartSplash(Image):
    def __init__(self, **kwargs):
        super(StartSplash, self).__init__(**kwargs)

class BetterBoxLayout(BoxLayout):
    pass

class StartGameButton(Button):
    def on_press(self):
        window = self.get_root_window()
        root = window.children[0]
        root.run_game()

class TextBox(Label):
    pass

class StinderApp(App):

    def build(self):
        root = rootWidget()

        start_splash = StartSplash(source="images/STinder.png")

        Window.size = (Window.height / 2, Window.height)

        # set the background to white
        Window.clearcolor = (1, 1, 1, 0)

        root.add_widget(start_splash)

        return root
