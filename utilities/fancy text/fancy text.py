from talon import Context, Module, actions, settings
ctx = Context()
mod = Module()

mod.list("fancy_punctuation","Punctuation spoken forms for fancy text.")
mod.mode("fancy_dictation","An attempt to allow control of formatting & punctuation within a dictation mode.")


@mod.capture(rule="{user.fancy_punctuation} | <user.formatters> <user.text> (close|end) <user.formatters> | word <user.word> | <user.text>")
def fancy_unit(m) -> str:
    """A target to navigate to. Returns a regular expression."""
    if hasattr(m, "fancy_punctuation"):
        return m.fancy_punctuation
    elif hasattr(m,"format_text"):
        return m.format_text
    elif hasattr(m,"word"):
        return m.word
    elif hasattr(m,"formatters"):
        print("something is happening...")
        return actions.user.formatted_text(m.text,m.formatters)
    else:
        return m.text

@mod.action_class
class Actions:
    def fancy_text(text_list: list, capitalize_first_word: bool = True, capitalize_after_quotes: bool = False):
        """Inserts a combination of text and punctuation"""
        p = ""
        parity = {}
        parity['"'] = 1
        parity["'"] = 1
        parity["caps"] = 1
        for i in range(len(text_list)):
            t = text_list[i]
            # punctuation that comes in pairs - better if these could all be implemented as formatters like dub string,
            if t in ["'",'"']:
                if parity[t] == 1:
                    if i == 0:
                        p += t
                    else:
                        p += " " + t
                else:
                    p += t
                parity[t] = parity[t] - 1
                parity["caps"] = 1
            # punctuation that never has a space before it
            elif t in [",","...",":",";",")","}","]"]:
                p += t
            # punctuation that never has a space before it and indicates the next word should be capitalized
            elif t in [".", "?", "!"]:
                p += t
                parity["caps"] = 1
            elif parity["caps"] == 1:
                if capitalize_first_word and i == 0:
                    p += t[0].upper() + t[1:]
                elif capitalize_after_quotes and text_list[i-1] in ['"',"'"]:
                    p += t[0].upper() + t[1:]
                else:
                    p += t
                parity["caps"] = -1
            elif i > 1 and text_list[i-1] in ["#","$","(","[","{"]:
                p += t
            else:
                p += " " + t
        p += " "
        print(f'p: {p}')
        actions.insert(p)
        
