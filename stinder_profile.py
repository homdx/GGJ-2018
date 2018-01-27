import json
import random

STI_CHANCE = 10

likes_list = []
dislikes_list = []
quotes_quips_lyrics_list = []
jobs_list = []
looking_for_list = []
songs_list = []
male_names_list = []
female_names_list = []

def has_sti():
    if random.randint(1,100) <= STI_CHANCE:
        return True
    else:
        return False

# Load all bio content from the json files
def load_bio_content():
    # Load male names
    with open("assets/bio/male_names.json", "r") as fd:
        global male_names_list
        male_names_list = json.load(fd)
    # Load female names
    with open("assets/bio/female_names.json", "r") as fd:
        global female_names_list
        female_names_list = json.load(fd)
    # Load likes
    with open("assets/bio/likes.json", "r") as fd:
        global likes_list
        likes_list = json.load(fd)
    # Load dislikes
    with open("assets/bio/dislikes.json", "r") as fd:
        global dislikes_list
        dislikes_list = json.load(fd)
    # Load quotes, lyrics, and quips
    with open("assets/bio/quotes_quips_lyrics.json", "r") as fd:
        global quotes_quips_lyrics_list
        quotes_quips_lyrics_list = json.load(fd)
    # Load jobs
    with open("assets/bio/jobs.json", "r") as fd:
        global jobs_list
        jobs_list = json.load(fd)
    # Load 'looking for' list
    with open("assets/bio/looking_for.json", "r") as fd:
        global looking_for_list
        looking_for_list = json.load(fd)
    # Load songs list
    with open("assets/bio/songs.json", "r") as fd:
        global songs_list
        songs_list = json.load(fd)

# Generate and return a new bio
def generate_bio():
    my_bio = {
        'sti_list': []
    }

    # Generate a gender
    my_bio['gender'] = random.choice(["male", "female"])

    # Generate a name based on the gender
    if my_bio['gender'] == "male":
        my_bio['name'] = random.choice(male_names_list)
    else:
        my_bio['name'] = random.choice(female_names_list)

    # Generate an age
    my_bio['age'] = random.randint(18,60)

    # Generate a likes list
    global likes_list
    my_bio['likes'] = []
    while len(my_bio['likes']) != 3:
        unique = False
        if has_sti():
            while not unique:
                new_like = random.choice(likes_list['sti'])
                if new_like[0] not in my_bio['likes']:
                    unique = True
                    my_bio['likes'].append(new_like[0])
                    my_bio['sti_list'].append(("Likes %s" % new_like[0], new_like[1]))
        else:
            while not unique:
                new_like = random.choice(likes_list['clean'])
                if new_like not in my_bio['likes']:
                    unique = True
                    my_bio['likes'].append(new_like)

    # Generate a dislikes list
    global dislikes_list
    my_bio['dislikes'] = []
    while len(my_bio['dislikes']) != 2:
        unique = False
        if has_sti():
            while not unique:
                new_dislike = random.choice(dislikes_list['sti'])
                if new_dislike[0] not in my_bio['dislikes'] and new_dislike[0] not in my_bio['likes']:
                    unique = True
                    my_bio['dislikes'].append(new_dislike[0])
                    my_bio['sti_list'].append(("Dislikes %s" % new_dislike[0], new_dislike[1]))
        else:
            while not unique:
                new_dislike = random.choice(dislikes_list['clean'])
                if new_dislike not in my_bio['dislikes'] and new_dislike not in my_bio['likes']:
                    unique = True
                    my_bio['dislikes'].append(new_dislike)

    # Generate a random quote, lyric, or quip
    global quotes_quips_lyrics_list
    if has_sti():
        quote_quip_lyric = random.choice(quotes_quips_lyrics_list['sti'])
        my_bio['quote_quip_lyric'] = quote_quip_lyric[0]
        my_bio['sti_list'].append(("Their profile said '%s'" % quote_quip_lyric[0], quote_quip_lyric[1]))
    else:
        my_bio['quote_quip_lyric'] = random.choice(quotes_quips_lyrics_list['clean'])

    # Generate a current and dream job
    global jobs_list
    if has_sti():
        job = random.choice(jobs_list['sti'])
        my_bio['current_job'] = job[0]
        my_bio['sti_list'].append(("Their profession was '%s'" % job[0],job[1]))
    else:
        my_bio['current_job'] = random.choice(jobs_list['clean'])

    # Make sure the dream job isn't the same as the current job
    my_bio['dream_job'] = None
    while my_bio['dream_job'] == None:
        if has_sti():
            new_job = random.choice(jobs_list['sti'])
            if new_job[0] != my_bio['current_job']:
                my_bio['dream_job'] = new_job[0]
        else:
            new_job = random.choice(jobs_list['clean'])
            if new_job != my_bio['current_job']:
                my_bio['dream_job'] = new_job

    # Generate a 'looking for'
    global looking_for_list
    if has_sti():
        looking_for = random.choice(looking_for_list['sti'])
        my_bio['looking_for'] = looking_for[0]
        my_bio['sti_list'].append(("They were looking for %s" % looking_for[0], looking_for[1]))
    else:
        my_bio['looking_for'] = random.choice(looking_for_list['clean'])

    # Generate a favourite song
    global songs_list
    my_bio['fav_song'] = random.choice(songs_list['clean'])

    # Return the new bio
    return my_bio

def format_bio(bio):
    # Profile header: name, age, job
    out = ""
    out += "%s, %d\n" % (bio['name'], bio['age'])
    out += (bio['current_job'])
    out += ("\n\n")

    # Profile body
    if "likes" in bio:
        out += ("I'm into %s, %s, and %s\n" % tuple(bio['likes']))
        out += ("Swipe left if you're into %s or %s\n" % tuple(bio['dislikes']))
    if "dream_job" in bio:
        out += ("My dream job is to be a %s\n" % bio['dream_job'])
        out += ("\n")
    if "looking_for" in bio:
        out += ("Looking for %s\n" % bio['looking_for'])
        out += ("\n")
    if "quote_quip_lyric" in bio:
        out += (bio['quote_quip_lyric'])
        out += ("\n")

    return out

if __name__ == "__main__":
    load_bio_content()
    bio = generate_bio()

    # Profile header: name, age, job
    print("%s, %d, (%s)" % (bio['name'], bio['age'], bio['gender']))
    print(bio['current_job'])
    print("")

    # Profile body
    if "likes" in bio:
        print("I'm into %s, %s, and %s" % tuple(bio['likes']))
        print("Swipe left if you're into %s or %s" % tuple(bio['dislikes']))
    if "dream_job" in bio:
        print("My dream job is to be a %s" % bio['dream_job'])
    if "looking_for" in bio:
        print("Looking for %s" % bio['looking_for'])
    if "quote_quip_lyric" in bio:
        print(bio['quote_quip_lyric'])

    print("")
    if len(bio['sti_list']) == 0:
        print("no STI!")
    else:
        my_sti = random.choice(bio['sti_list'])
        print("Has an STI: %s (%s)" % (my_sti[0], my_sti[1]))
