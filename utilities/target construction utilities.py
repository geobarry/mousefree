from talon import Context,Module,actions,clip,ui
from talon.windows import ax as ax, ui as winui
import subprocess
import re
import os
mod = Module()

#ctx = Context()

def number_to_words(number_str):
    """Converts a string of numbers to its written form."""

    units = ["", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine"]
    teens = ["ten", "eleven", "twelve", "thirteen", "fourteen", "fifteen", "sixteen", "seventeen", "eighteen", "nineteen"]
    tens = ["", "ten", "twenty", "thirty", "forty", "fifty", "sixty", "seventy", "eighty", "ninety"]

    def convert_two_digits(number):
        if number == 0:
            return ""
        elif number < 10:
            return units[number]
        elif number < 20:
            return teens[number - 10]
        else:
            return tens[number // 10] + (" " + units[number % 10] if number % 10 != 0 else "")

    def convert_three_digits(number):
        if number == 0:
            return ""
        elif number < 100:
            return convert_two_digits(number)
        else:
            return units[number // 100] + " hundred" + (" " + convert_two_digits(number % 100) if number % 100 != 0 else "")

    number = int(number_str)
    if number == 0:
        return "zero"

    result = ""
    if number < 0:
        result = "negative "
        number = abs(number)

    billions = number // 1000000000
    millions = (number % 1000000000) // 1000000
    thousands = (number % 1000000) // 1000
    hundreds = number % 1000

    if 0 < billions < 1000:
        result += convert_three_digits(billions) + " billion "
    if millions > 0:
        result += convert_three_digits(millions) + " million "
    if thousands > 0:
        result += convert_three_digits(thousands) + " thousand "
    if hundreds > 0:
        result += convert_three_digits(hundreds)

    return result.strip()

def number_variations(n_str: str):
    """Returns a list of lists of number strings that can represent the input number"""
    if len(n_str) > 2:
        return [[n_str]] + [x + [n_str[-2:]] for x in number_variations(n_str[:-2])]
    else:
        return [[n_str]]

def variations(words_and_numbers: list):
    """Returns variations of word and number list, converting numbers into words"""
    idx = next((i for i in range(len(words_and_numbers)) if words_and_numbers[i].isnumeric()),None)
    if idx == None:
        return [words_and_numbers]
    else:
        r = []
        n = words_and_numbers[idx]
        if len(n) == 4:
            num_variations = [[n],[n[:2],n[2:]]]
        else:
            num_variations = [[n]]
        # get variations by splitting into 2-digit pieces
        num_variations = number_variations(n)
        # add variation with all single digits
        last_variation = [x for x in n]
        num_variations += [last_variation]
        for number_list in num_variations:
            number_words = [number_to_words(x) for x in number_list]
            word_list = words_and_numbers[:idx] + number_words + words_and_numbers[idx+1:]
            spoken_form_list = variations(word_list)
            r += spoken_form_list

        return r


@mod.action_class
class Actions:
    def text_to_spoken_forms(text_list: list, max_words: int = 5):
        """returns a dictionary of spoken_form: id"""
        print(f"FUNCTION: text_to_spoken_forms")
        r = {}
        for i in range(len(text_list)):
            # Create spoken forms of first word or first and second word
            # (maybe this can be changed to accept any number of words)
            # (maybe also could be improved to accept numbers)
            # add full t to dictionary
            t = text_list[i]
            t = re.sub(r"[^a-zA-Z0-9]+"," ",t)
            # split into single words or numbers
            singles = re.findall(r"\d+|\w+",t)
            # get variations on above including different spoke in forms for numbers 
            number_variations = variations(singles)
            # singles = [number_to_words(x) if x.isnumeric() else x for x in singles]
            for variation in number_variations:
                for j in range(max(max_words,len(variation))):
                    x = " ".join(variation[:j+1])
                    if not x in r:
                        r[x] = i  
        return r
