import time
from itertools import combinations
import random

from tqdm import tqdm


# Given helper functions and additional required functions
def create_deck():
    suits = ['♠', '♥', '♣', '♦']
    values = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
    deck = [f'{suit}{value}' for suit in suits for value in values]
    random.shuffle(deck)
    return deck

def card_value(card):
    values = {'2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9, '10': 10, 'J': 11, 'Q': 12, 'K': 13, 'A': 14}
    return values[card[1:]]

def card_suit(card):
    return card[0]

def is_straight(ranks):
    if len(set(ranks)) != 5:
        return False
    return max(ranks) - min(ranks) == 4 or set(ranks) == {2, 3, 4, 5, 14}

def hand_rank(hand):
    ranks = sorted((card_value(card) for card in hand), reverse=True)
    suits = [card_suit(card) for card in hand]
    is_flush = len(set(suits)) == 1
    straight = is_straight(ranks)
    if straight and is_flush:
        return (8 if min(ranks) != 10 else 9, ranks, hand)
    rank_counts = sorted(((ranks.count(rank), rank) for rank in set(ranks)), reverse=True)
    score, high_cards = zip(*rank_counts)
    if score == (4, 1):
        return (7, high_cards, hand)
    if score == (3, 2):
        return (6, high_cards, hand)
    if is_flush:
        return (5, ranks, hand)
    if straight:
        return (4, ranks, hand)
    if score == (3, 1, 1):
        return (3, high_cards, hand)
    if score == (2, 2, 1):
        return (2, high_cards, hand)
    if score == (2, 1, 1, 1):
        return (1, high_cards, hand)
    return (0, ranks, hand)

# Implementation of the hands_potential function
def hands_potential(current_cards):
    # Initialize the probabilities dictionary for each hand type
    hand_types = ["High Card", "One Pair", "Two Pairs", "Three of a Kind", "Straight", "Flush", "Full House", "Four of a Kind", "Straight Flush", "Royal Flush"]
    probabilities = {hand_type: 0 for hand_type in hand_types}
    total_combinations = 0
    best_hand = ("", [], [])

    # Create a deck and remove current cards from it
    deck = create_deck()
    deck = [card for card in deck if card not in current_cards]

    # Determine the number of cards to draw to make a hand of 7 cards
    draw_count = 7 - len(current_cards)

    # Generate all possible hands
    possible_hands = combinations(deck, draw_count) if draw_count > 0 else [tuple(current_cards)]
    # print('There are ', len(list(possible_hands)), ' possible hands')

    for possible_hand in possible_hands:
        hand = list(possible_hand) + current_cards
        if len(hand) == 7:
            # Find all combinations of 5 cards from the 7 to evaluate the best possible hand
            best_comb_hand = max([hand_rank(list(comb)) for comb in combinations(hand, 5)], key=lambda x: x[0])
            probabilities[hand_types[best_comb_hand[0]]] += 1
            total_combinations += 1
            # Update best hand if current is better

            if not best_hand[0] or best_comb_hand > hand_rank(best_hand[2]):
                best_hand = (hand_types[best_comb_hand[0]], best_comb_hand[1], best_comb_hand[2])

    # Calculate probabilities
    for hand_type in probabilities:
        probabilities[hand_type] = probabilities[hand_type] / total_combinations if total_combinations else 0

    # Organize probabilities into the specified format
    probabilities_list = [[hand_type, prob] for hand_type, prob in probabilities.items()]

    # Prepare the output dictionary
    output = {
        "probability": probabilities_list,
        "best_hand": [best_hand[0], ', '.join(map(str, best_hand[1]))]
    }

    return output


# Example usage with current cards
current_cards = ['♠A', '♥2', '♠3', '♣10', '♠K']
# current_cards = ['♠A', '♥2']
#
# start = time.time()
# result = hands_potential(current_cards)
# end = time.time()
# print('time cost', end - start)
# print()
#
# print('Your card is: ', ','.join(current_cards))
# print('The probability is: ')
# print('\n'.join([item[0]+', '+"{:.2f}%".format(item[1] * 100) for item in result['probability']]))

# deck = create_deck()
# all_starting_hands = list(combinations(deck, 2))
#
# results = []
#
# for hand in tqdm(all_starting_hands):
#     probabilities = hands_potential(list(hand))
#     results.append({
#         'hand': hand,
#         'probabilities': probabilities
#     })
#
# deck = create_deck()
# all_starting_hands = list(combinations(deck, 2))
