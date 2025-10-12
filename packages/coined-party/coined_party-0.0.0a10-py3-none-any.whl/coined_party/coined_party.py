# imports
import random
import sys
import time
import os

# Variables
coins = 0
presence = "games_lounge"     # Variable that sets presence to games_lounge so no errors can occur
x = 0     # Variable that makes something happen only the first time the code is run
name = ""

'''   -------------------------------- Functions --------------------------------   '''

# Function that determines location based off user input
def whereTo():
    # Globalizing Variables
    global presence, ask

    # Checking presence and deciding which text to print
    if presence == "games_lounge":
        ask = input("\nPress enter to proceed to game, press 1, then enter to return to Games Lounge.\n")
    elif presence == "inGame":
        ask = input("\nPress enter to play again, press 1, then enter to return to Games Lounge.\n")

    # Checking answer and determining next location
    if ask == "":
        pass
    elif ask == "1":
        games_lounge(name)
    else:
        print("\n\n\nInvalid, heading back to Games Lounge.")
        games_lounge(name)
...

# Function that acts as a main menu, where users can decide which game to play
def games_lounge(name):
    # Globalizing Variables
    global presence, coins, negativeCoins

    # Making sure coins never go below 0
    if coins < 0:
        coins = 0
    else:
        pass
    ...

    # Loading games lounge

    # Creating fun games lounge entrance
    if presence == "inGame":
        print("Heading back to Games Lounge...")
        time.sleep(1)
        print("Locating Games Lounge...")
        time.sleep(1)

        notFound = random.randint(1, 10)
        if notFound == 7:
            print("Games Lounge not found...")
            time.sleep(1)
            print("Just kidding...")
        else:
            print("Games Lounge found...")
        time.sleep(1)

        print("Entering Games Lounge...")
        time.sleep(2)
    else:
        pass

    # Setting presence according to current location
    presence = "games_lounge"

    # Welcoming user
    selectedGame = input(f"\n\nWelcome {name}, your coin count is currently {coins}. "
          f"\nWhat do you wish to play? Press 1 for Look away, "
          f"\npress 2 for Slot Machine, press 3 for Pig. "
          f"\nTo view rules for each game, choose the game, "
          f"\nand there'll be an option to head back to the games lounge."
          f"\nIf you wish to quit the game, press Q: ")

    # Deciding which game to go to based off user input
    if selectedGame == "1":
        look_away_rules()
    elif selectedGame == "2":
        slot_machine_rules()
    elif selectedGame == "3":
        pig_dice_rules()

    # Exiting game
    elif selectedGame == "q" or selectedGame == "Q":
        areYouSure = input("Are you sure you want to exit the game? "
                           "\nYou will lose all your progress. (Y/N) ")
        if areYouSure == "Y" or areYouSure == "y":
            print("\n\n...Quitting program...")
            time.sleep(2)
            print("\n\nThanks for playing! 👋")
            time.sleep(1)
            sys.exit()
        elif areYouSure == "N" or areYouSure == "n":
            games_lounge(name)

    # Restarting game
    elif selectedGame == "r" or selectedGame == "R":
        areYouSure = input("Are you sure you want to restart the game? "
                           "\nYou will lose all your progress. (Y/N) ")
        if areYouSure == "Y":
            print("\n\n...Restarting program...")
            time.sleep(1)
            os.execl(sys.executable, sys.executable, *sys.argv)
        elif areYouSure == "N":
            games_lounge(name)

    # Punishing user for being stupid
    else:
        print(f"{selectedGame} does not exist, \n"
              f"you lost aura for that; and coins for that matter.")
        negativeCoins = int(random.randint(1, 20))
        time.sleep(1)
        ...

        if coins > negativeCoins:
            coins = 0
        elif coins <= negativeCoins:
            # Being a bully
            if negativeCoins == 20:
                print("Wow! You're unlucky as hell. You lost the max amount you could've lost.")
                coins -= negativeCoins
            else:
                coins -= negativeCoins
        time.sleep(1)
        ...
    ...

    # Restarting games_lounge() if user input was invalid
    games_lounge(name)
...

# Function that displays rules to game, and grabs user input to be used in look_away()
def look_away_rules():
    # Globalizing variables
    global presence

    # Setting presence to Games Lounge because play again is an option, and whereTo()
    # text output should be according to location
    presence = "games_lounge"

    # Game 1 rules
    print("\n\nLook away! The rules to the game are simple. \n"
          "You are going to play against two bots, one named GPT, and the other LLaMA. \n"
          "Then, you choose a direction, either up, down, left, or right. \n"
          "If any of the bots look in the same direction as you, you lose =( \n"
          "If you look in a different direction than them, you WIN =D \n"
          "To look towards a specific direction, we use numbers: \n"
          "1 = up \n2 = down \n3 = left \n4 = right \nUse this as a cheat sheet."
          "\n\n")

    # Checking whether to proceed
    whereTo()

    # Setting presence to inGame
    presence = "inGame"

    # Starting Game 1
    print("Without further ado, let's BEGIN!")

    # Loops that makes sure inputs are valid
    for i in range(100000):
        move1 = int(input("Please choose a direction for round 1: "))
        if move1 != 1 and move1 != 2 and move1 != 3 and move1 != 4:
            print(f"{move1} is not a valid direction, please be smart.\n")
            time.sleep(0.8)
        else:
            break
    time.sleep(0.7)

    for i in range(100000):
        move2 = int(input("Thank you! Now, please choose a direction for round 2: "))
        if move2 != 1 and move2 != 2 and move2 != 3 and move2 != 4:
            print(f"{move2} is not a valid direction, please be smart.\n")
            time.sleep(0.8)
        else:
            break
    time.sleep(0.7)

    for i in range(100000):
        move3 = int(input("Thank you! Lastly, please choose a direction for round 3: "))
        if move3 != 1 and move3 != 2 and move3 != 3 and move3 != 4:
            print(f"{move3} is not a valid direction, please be smart.\n")
            time.sleep(0.8)
        else:
            break

    # Deriving 1
    look_away(move1, move2, move3)
    time.sleep(2)

    # Asking user where to go next
    whereTo()
    look_away_rules()
...

# Function that runs Look Away game
def look_away(round1, round2, round3):
    # Globalizing variables
    global coins

    # Variables
    score = 0
    round1 = int(round1)
    round2 = int(round2)
    round3 = int(round3)
    ...

    # --- AI Bot 1 (GPT) ---
    GPT_AImove1 = random.randint(1,4)
    GPT_AImove2 = random.randint(1,4)
    GPT_AImove3 = random.randint(1,4)
    ...

    # --- AI Bot 2 (LLaMA) ---
    LLaMA_AImove1 = random.randint(1,4)
    LLaMA_AImove2 = random.randint(1,4)
    LLaMA_AImove3 = random.randint(1,4)
    ...

    # Round 1 - Preparations
    print("Round 1, Begin!")
    print("Calculating GPT move...")
    time.sleep(0.8)
    print("Calculating LLaMA move...")
    time.sleep(0.8)

    # Round 1 - Comparisons
    if round1 == GPT_AImove1 or round1 == LLaMA_AImove1:
        winner = "Bot"
    else:
        winner = "Player"

    # Printing round results and winner
    print(f"GPT: {GPT_AImove1}, "
          f"LLaMA: {LLaMA_AImove1}, "
          f"Player: {round1}, "
          f"Winner: {winner} \n")
    ...

    # Round 2 - Preparations
    print("Round 2, Begin!")
    print("Calculating GPT move...")
    time.sleep(0.8)
    print("Calculating LLaMA move...")
    time.sleep(0.8)

    # Round 2 - Comparisons
    if round2 == GPT_AImove2 or round2 == LLaMA_AImove2:
        winner = "Bot"
    else:
        winner = "Player"

    # Printing round results and winner
    print(f"GPT: {GPT_AImove2}, "
          f"LLaMA: {LLaMA_AImove2}, "
          f"Player: {round2}, "
          f"Winner: {winner} \n")
    ...

    # Round 3 - Preparations
    print("Round 3, Begin!")
    print("Calculating GPT move...")
    time.sleep(0.8)
    print("Calculating LLaMA move...")
    time.sleep(0.8)

    # Round 3 - Comparisons
    if round3 == GPT_AImove3 or round3 == LLaMA_AImove3:
        winner = "Bot"
    else:
        winner = "Player"

    # Printing round results and winner
    print(f"GPT: {GPT_AImove3}, "
          f"LLaMA: {LLaMA_AImove3}, "
          f"Player: {round3}, "
          f"Winner: {winner} \n")
    ...

    # Calculating Score
    if GPT_AImove1 == round1 or LLaMA_AImove1 == round1:
        if GPT_AImove2 == round2 or LLaMA_AImove2 == round2:
            if GPT_AImove3 == round3 or LLaMA_AImove3 == round3:
                score += 0
            elif GPT_AImove3 != round3 and LLaMA_AImove3 != round3:
                score += 10
            ...
        elif GPT_AImove2 != round2 and LLaMA_AImove2 != round2:
            if GPT_AImove3 == round3 or LLaMA_AImove3 == round3:
                score += 10
            elif GPT_AImove3 != round3 and LLaMA_AImove3 != round3:
                score += 20
            ...
        ...
    elif GPT_AImove1 != round1 and LLaMA_AImove1 != round1:
        if GPT_AImove2 == round2 or LLaMA_AImove2 == round2:
            if GPT_AImove3 == round3 or LLaMA_AImove3 == round3:
                score += 10
            elif GPT_AImove3 != round3 and LLaMA_AImove3 != round3:
                score += 20
            ...
        elif GPT_AImove2 != round2 and LLaMA_AImove2 != round2:
            if GPT_AImove3 == round3 or LLaMA_AImove3 == round3:
                score += 20
            elif GPT_AImove3 != round3 and LLaMA_AImove3 != round3:
                score += 30
            ...
        ...
    ...

    # Printing out final coin amount
    print(f"Total coins: {score}\n")
    time.sleep(1.25)

    # Directing deposit of final coins to bank
    coins += score
...

# Function that displays rules to game, and grabs user input to be used in slot_machine()
def slot_machine_rules():
    # Globalizing variables
    global presence, bet

    # Setting presence to games_lounge because play again is an option, and whereTo()
    # text output should be according to location
    presence = "games_lounge"

    # Game 2 rules
    print("\n\nTime for the SECOND game! Slot Machine! Here are the rules: \n"
          "You give your bet, and a randomized slot machine will display three \n"
          "emojis. If the emojis are all different, you get nothing. If two of the \n"
          "emojis are the same, your bet will double. Lastly, if all three of the \n"
          "emojis are the same, your bet will QUINTIPLE!")

    # Checking whether to proceed
    whereTo()

    # Setting presence to inGame
    presence = "inGame"

    # Making sure user doesn't go into debt
    if coins == 0:
        print("Damn, you broke as hell. Get back to the games \n"
              "lounge, and come back when you actually have bread.\n\n")
        games_lounge(name)
    else:
        pass
    ...

    # Starting Game 2

    # Making sure user doesn't get addicted to gambling
    for i in range(10000000):
        bet = int(input("\nLet's begin! I need to know first, how much will you be betting today? "))
        if bet > coins:
            print("You do not have enough coins! Please choose a lower amount, brokie.")
        elif bet <= coins:
            break
    time.sleep(0.7)

    # Deriving 2
    slot_machine(bet)
    time.sleep(2)

    # Asking user where to go next
    whereTo()
    slot_machine_rules()
...

# Function that runes Slot Machine game
def slot_machine(bet):
    # Globalizing variables
    global coins

    # Subtracting bet from coins
    coins -= bet
    print(f"Your coin count is now {coins}")

    # Randomizing slots
    slot1 = random.randint(1, 4)
    slot2 = random.randint(1, 4)
    slot3 = random.randint(1, 4)
    ...

    # Assigning emoji to Slot 1 based off random number
    if slot1 == 1:
        slot1 = "🤪"
    elif slot1 == 2:
        slot1 = "😍"
    elif slot1 == 3:
        slot1 = "😭"
    elif slot1 == 4:
        slot1 = "😁"
    else:
        print("invalid")
        slot_machine(bet)
    ...

    # Assigning emoji to Slot 2 based off random number
    if slot2 == 1:
        slot2 = "🤪"
    elif slot2 == 2:
        slot2 = "😍"
    elif slot2 == 3:
        slot2 = "😭"
    elif slot2 == 4:
        slot2 = "😁"
    else:
        print("invalid")
        slot_machine(bet)
    ...

    # Assigning emoji to Slot 3 based off random number
    if slot3 == 1:
        slot3 = "🤪"
    elif slot3 == 2:
        slot3 = "😍"
    elif slot3 == 3:
        slot3 = "😭"
    elif slot3 == 4:
        slot3 = "😁"
    else:
        print("invalid")
    ...

    # Determining score
    if (slot1 == slot2 or slot1 == slot3 or slot2 == slot3) and not(slot1 == slot2 and slot1 == slot3):
        bet *= 2
    elif slot1 == slot3 and slot1 == slot3:
        bet *= 5
    else:
        bet = 0

    # Informing user of their bad financial decision
    print(f"{slot1} {slot2} {slot3},  {bet}")
    coins += bet
...

# Function that displays rule to game, and grabs user input to be used in pig_dice()
def pig_dice_rules():
    # Globalizing variables
    global presence, x

    # Setting presence to Games Lounge because play again is an option, and whereTo()
    # text output should be according to location
    presence = "games_lounge"

    # Game 3 rules
    print("\n\nThis is a risk-it-all game, so be prepared! "
          "\nThe rules to the game can't be any simpler:\n"
          "You choose a threshold. A couple of dice are rolled repeatedly and \n"
          "added together. The game ends when; the added value increases beyond \n"
          "the threshold, this is where you win; a 1 is rolled, this is where you lose; \n"
          "or two 1s are rolled, this is where you catastrophically lose.")

    # Checking whether to proceed
    whereTo()

    # Setting presence to inGame
    presence = "inGame"

    # Starting Final Game

    # Grabbing threshold from user
    threshold = int(input("\nPlease choose a threshold: "))

    # Displaying cringey entrance only the first time the code is run
    if x == 0:
        # Making an intimidating entrance (or cringey, depending on your aura level)
        for i in ("tHaNnk =oU FOr ThE t_rEshOLd"):
            print(i, end="")
            time.sleep(0.25)
        for i in ("\nGoOd l_uCk!!?!??\n"):
            print(i, end="")
            time.sleep(0.25)
        x += 1
    else:
        pass
    time.sleep(1)

    # Deriving 3
    pig_dice(threshold)
    time.sleep(2)

    # Asking user where to go next
    whereTo()
    pig_dice_rules()
...

# Function that runs Pig game
def pig_dice(threshold):
    # Globalizing variables
    global coins, status

    # Generating Dice and rolls list [illegal]
    diceTotal = 0
    roll1 = []
    roll2 = []

    # Repeating dice rolls until; a 1 is rolled; or the threshold is reached
    for _ in range(10000):
        dice1 = random.randint(1, 6)
        dice2 = random.randint(1, 6)
        diceTotal = diceTotal + dice1 + dice2
        roll1 += [dice1]
        roll2 += [dice2]

        # Checking if any 1s were rolled and displaying result
        if dice1 == 1 or dice2 == 1:

            # Checking whether loss was catastrophic or just a heart attack
            if dice1 == 1 and dice2 == 1:
                status = "Catastrophic Loss"
                diceTotal = -1
                break
            else:
                status = "Loss"
                diceTotal = 0
                break
            ...

        elif diceTotal >= threshold:
            status = "Win"
            break
        elif diceTotal < threshold:
            status = "Proceed"
            continue
        else:
            print("invalid")
            break
    ...

    # Generating Output
    print("\nRolls:", end=" ")

    # Grabbing results from saved list to have them displayed
    for i in range(len(roll1)):
        print(f"({roll1[i]}, {roll2[i]}),", end=" ")
    if status == "Win":
        print(f"{status}, ({diceTotal} coins).")
    else:
        print(status)
    ...

    # Points Return
    print(f"Points: {diceTotal}.")

    # Finding new coin count
    if diceTotal >= 0:
        coins += diceTotal
    elif diceTotal -1:
        coins = 0
    else:
        print("You have somehow found a way to break the code, even though it's been\n"
              "written by the best programmer in the world. \n"
              "Here, take this. you've earned it.")
        coins = 99999999999
...

# Signature function
def printSignature():
    signatureName = "Yoosif Alquwatly"
    program = "Engineering 1 | McMaster University"
    print(f"{signatureName} \n"
          f"{program} \n"
          f"\n\n")
...

'''   ---------------------------------- Code ----------------------------------   '''
# Kickstarting code
def runGame():
    global name

    # Signature
    printSignature()

    # Welcome Message
    print("Welcome to Coined Party! \n"
          "It's time for YOU to play some party GAMES! Here are the rules: \n"
          "You'll get to play the following games: \n"
          "    - Look Away \n"
          "    - Slot Machine \n"
          "    - Pig \n"
          "The objective is to gather as many coins as you can by the end of the party!"
          "\n\n")
    ...

    # Only activates code when it's the main file; not when imported
    try:
        # Asking user for personal information, so I can access their bank account
        name = input("Firstly, please enter your name: ")

        # Booting up the game
        games_lounge(name)

    # Removing error when user ends program
    except KeyboardInterrupt:
        print("\n\n...Quitting program...")
        time.sleep(2)
        print("\n\nThanks for playing! 👋")
        time.sleep(1)

runGame()