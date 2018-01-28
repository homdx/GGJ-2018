import os, re, random

import stinder_profile as profile

from kivy.app import App
from kivy.clock import Clock
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

good_swipe = []
bad_swipe = []
swiping_loop = None
transition_music = None
menu_music = None
wilhelm = None

class rootWidget(BoxLayout):
    def __init__(self, **kwargs):
        super(rootWidget, self).__init__(**kwargs)

    def update_score(self):
        self.score_w.text = "[color=000000]Score: %s[/color]" % self.score

    def new_score(self):
        self.score = 0
        self.update_score()

    def increase_score(self):
        self.score += 1
        self.update_score()

    def decrease_timer(self, dt):
        self.timer_value -= 1
        self.timer.text = "[color=000000]Seconds Remaining: %s[/color]" % self.timer_value
        if self.timer_value == 0:
            self.show_splash()

    def new_timer(self):
        self.timer_value = 120

    def clear_windows(self):
        Clock.unschedule(self.decrease_timer)
        if swiping_loop != None:
            def a():
                pass
            swiping_loop.on_stop = a
            swiping_loop.stop()
        if menu_music != None:
            menu_music.stop()

        for child in self.children:
            self.remove_widget(child)

    def show_splash(self):
        self.clear_windows()

        start_splash = StartSplash(source="images/Title.png")


        self.add_widget(start_splash)

    def show_victory(self):
        self.clear_windows()

        self.add_widget(StartSplash(source="images/Victory.png"))

    def lose_screen(self, sti):
        self.clear_windows()

        self.add_widget(LoseScreen(sti))

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

        self.clear_windows()

        game = Game(orientation='vertical')

        b = BetterBoxLayout(orientation='horizontal', size_hint=(1, 0.05))

        self.timer = TextBox(text="",
                markup=True, font_size='20sp')
        b.add_widget(self.timer)

        self.score_w = TextBox(text="", markup=True, font_size='20sp')
        b.add_widget(self.score_w)

        # Initialise score and timer
        self.new_timer()
        self.new_score()

        game.add_widget(b)

        self.bio = TextBox(text="" , markup=True, font_size='20sp')

        carousel = BestCarousel(self.bio,
                direction='right', min_move=0.4, loop=True)
        game.add_widget(carousel)
        carousel.index = 1

        bio = BetterBoxLayout(orientation='vertical')

        game.add_widget(bio)

        bio.add_widget(self.bio)



        # Start decreasing the timer every 1 second
        self.clock = Clock.schedule_interval(self.decrease_timer, 1)

        self.add_widget(game)

class Image(BaseImage):
    def __init__(self, blank=False, allow_stretch=True, keep_ratio=True, **kwargs):
        super(Image, self).__init__(allow_stretch=allow_stretch,
                keep_ratio=keep_ratio, **kwargs)
        # prevent interpolation when we scale up the image
        if self.texture != None:
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

    def play_loop_music(self):
        global swiping_loop
        swiping_loop.volume = 0.1
        swiping_loop.play()

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

        #print easter_egg ronnie
        if self.bio_data['gender'] == 'ronnie':
            image1 = Image(source='images/ronnie.jpg')
            return image1

        #print easter_egg putin
        if self.bio_data['gender'] == 'putin':
            image1 = Image(source='images/putin.jpg')
            return image1

        # build avatar
        for layer, index in enumerate(sorted(HEADSHOTS.keys())):
            if index > 50:
                if random.randrange(0, 10) > 0:
                    continue
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
        global good_swipe, bad_swipe
        if self.index == 0:
            # ACCEPT
            window = self.get_root_window()
            if window == None:
                print("WARNING: This shouldn't happen :(")
                return
            root = window.children[0]
            if len(self.bio_data['sti_list']) > 0:
                # BAD, LOST GAME
                wilhelm.play()
                sti = random.choice(self.bio_data['sti_list'])
                root.lose_screen(sti)
                return
            else:
                # GOOD
                random.choice(good_swipe).play()
                root.increase_score()
                if root.score == 1:
                    root.show_victory()
                    return
        elif self.index == 2:
            # DECLINE
            random.choice(bad_swipe).play()

        # load next headshot
        image = self._load_headshot()
        self.update_widget(1, image)

        # reset to slide 1
        self.index = 1

    def __init__(self, bio, **kwargs):

        # save bio widget for later updating
        self.bio = bio

        # load the moosic
        global menu_music, transition_music, swiping_loop
        swiping_loop = SoundLoader.load('assets/audio/swiping_loop.wav')
        swiping_loop.loop = False
        swiping_loop.volume = 0.2
        swiping_loop.on_stop = self.play_loop_music
        transition_music = SoundLoader.load('assets/audio/loop_transition.wav')
        transition_music.loop = False
        transition_music.volume = 0.1
        transition_music.on_stop = self.play_loop_music

        # stop the menu music
        menu_music.stop()

        # play the transition music
        transition_music.play()
        while transition_music.get_pos() < 2.42:
            pass
        swiping_loop.play()

        # Load the audio effects
        global good_swipe, bad_swipe, wilhelm
        good_swipe.append(SoundLoader.load('assets/audio/oh_yeah_1.wav'))
        good_swipe.append(SoundLoader.load('assets/audio/oh_yeah_2.wav'))
        good_swipe.append(SoundLoader.load('assets/audio/oh_yeah_3.wav'))
        good_swipe.append(SoundLoader.load('assets/audio/oh_yeah_4.wav'))
        good_swipe.append(SoundLoader.load('assets/audio/oh_yeah_5.wav'))
        good_swipe.append(SoundLoader.load('assets/audio/oh_yeah_6.wav'))
        good_swipe.append(SoundLoader.load('assets/audio/oh_yeah_7.wav'))
        good_swipe.append(SoundLoader.load('assets/audio/oh_yeah_8.wav'))
        bad_swipe.append(SoundLoader.load('assets/audio/boo_1.wav'))
        bad_swipe.append(SoundLoader.load('assets/audio/boo_2.wav'))
        bad_swipe.append(SoundLoader.load('assets/audio/boo_3.wav'))
        bad_swipe.append(SoundLoader.load('assets/audio/boo_4.wav'))
        bad_swipe.append(SoundLoader.load('assets/audio/boo_5.wav'))
        bad_swipe.append(SoundLoader.load('assets/audio/boo_6.wav'))
        bad_swipe.append(SoundLoader.load('assets/audio/boo_7.wav'))
        bad_swipe.append(SoundLoader.load('assets/audio/boo_8.wav'))
        bad_swipe.append(SoundLoader.load('assets/audio/boo_9.wav'))
        bad_swipe.append(SoundLoader.load('assets/audio/boo_10.wav'))
        wilhelm = SoundLoader.load('assets/audio/wilhelm.wav')

        # call the superclass init function
        super(BestCarousel, self).__init__(**kwargs)

        # load the bio content options into the module
        profile.load_bio_content()

        # set up the slide widgets in the carousel
        self.add_widget(Image(source='images/Button_Heart_1.png'))
        self.add_widget(Image(source='images/blank.png', blank=True))
        self.add_widget(Image(source='images/Button_Cross_1.png'))

# helper widgets

class BetterBoxLayout(BoxLayout):
    pass

class TextBox(Label):
    pass

# the widget the game runs in

class Game(BetterBoxLayout):
    pass

# the splash widget

class StartSplash(Image):
    def __init__(self, **kwargs):
        super(StartSplash, self).__init__(**kwargs)
        global menu_music
        menu_music = SoundLoader.load('assets/audio/menu_music.mp3')
        menu_music.volume = 0.1
        menu_music.play()

    def on_touch_up(self, val):
        super(StartSplash, self).on_touch_up(val)
        window = self.get_root_window()
        root = window.children[0]
        root.run_game()

# the loss widget

class LoseScreen(BetterBoxLayout):
    def __init__(self, sti, **kwargs):
        super(LoseScreen, self).__init__(**kwargs)
        lose_reason = """Oh no, that person has an STI:

%s

%s""" % sti
        txt = TextBox(text="[color=000000]%s[/color]" % lose_reason,
                markup=True, font_size='20sp', pos_hint={'y': 0.5, 'centre_x':0.3})
        self.add_widget(txt)

    def on_touch_up(self, val):
        super(LoseScreen, self).on_touch_up(val)
        window = self.get_root_window()
        root = window.children[0]
        root.show_splash()

# app start class

class StinderApp(App):

    def build(self):
        root = rootWidget()

        Window.size = (400, 800)

        # set the background to white
        Window.clearcolor = (1, 1, 1, 0)

        root.show_splash()

        return root
