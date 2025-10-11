import rweintr_wordgame
from rweintr_wordgame import wordgame

def main():
    '''Guess a random word letter by letter'''

    name=input("Please enter your name\n")
    print("Welcome " + name + " to the RWEINTR Guess the Word game version " + rweintr_wordgame.__version__)

    level=input("Choose difficulty level 1(Easy) 2(Medium (default)) 3(Difficult): ")
    # difficulty level determines number of guesses user is allowed
    num_guesses = wordgame.set_game_level(level)
    print("You have ",num_guesses," guesses.")
    print("You can quit anytime by entering Q")

    #choose a random generated word
    game_word=wordgame.choose_game_word(level)
    #print (game_word)

    guess_word=wordgame.init_guess_word(game_word)

    #Guess the word in a configurable number of tries and test for success
    guess_successful, guesses = wordgame.guess_the_word(game_word,guess_word,num_guesses)
    if guess_successful == "Quit":
        return
    elif guess_successful:
        print(name," congrats you guessed the word ", game_word," in ",guesses, " guess(es)")
    else:
        print(name," better luck next time, the word was  ", game_word)

if __name__ == "__main__":
    main()