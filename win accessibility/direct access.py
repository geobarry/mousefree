"""
This module will be the only module to access winui.
Every function in this module will be wrapped in a try-finally block to prevent
multiple simultaneous retrievals.
"""
from talon import Module, ui, Context, clip, ctrl, cron, actions, canvas, screen, settings
from talon.windows import ax as ax, ui as winui
from io import StringIO
from contextlib import redirect_stdout
import io

retrieving = False

mod = Module()

@mod.action_class
class Actions:
    def set_winax_retrieving(state: bool = True):
        """Used this to prevent windows accessibility freezes"""
        global retrieving
        retrieving = state
    def winax_retrieving():
        """if true, you should not request a focused element because we are probably waiting for windows to respond to a previous request"""
        global retrieving
        return retrieving
    def safe_focused_element():
        """This is intended to be a safe way to obtain the currently focused element. Will return none if unable to retrieve."""
        global retrieving
        if retrieving:
            print(f"FUNCTION safe_focused_element could not retrieve element because another retrieval is in process")
            return None
        else:
            retrieving = True
            try:
                el = winui.focused_element()
                return el
            except Exception as error:
                print("FUNCTION safe_focused_element could not retrieve element due to error")
                print(f'error: {error}')
                print("Attempting to retrieve from generic UI")
                try:
                    el = ui.focused_element()
                    return el
                except Exception as error:
                    print("Retrieval from generic UI also raised an error")
                    print(f'error: {error}')
                return None
            finally:
                retrieving = False
    def winax_main_screen():
        """retrieves the main screen from windows UI"""
        global retrieving
        if retrieving:
            print("FUNCTION winax_main_screen: unable to retrieve element because another retrieval is in process")
        else:
            retrieving = True
            try:
                return winui.main_screen()
            except Exception as error:
                print(f"FUNCTION winax_main_screen encountered an error:\n {error}")
            finally:
                retrieving = False
    def act_on_element(el: ax.Element, action: str, delay_after_ms: int=0):
        """Perform action on element. Get actions from {user.ui_action}"""
        if not el:
            return 
        global retrieving
        if retrieving:
            print("FUNCTION el_prop_val: unable to retrieve element because another retrieval is in process")
        else:
            retrieving = True
            try:
                action = action.lower()
                if action in ["click","right-click","double-click"]:
                    loc = actions.user.element_location(el)
                    if loc != None:            
                        if delay_after_ms > 0:
                            actions.user.slow_mouse(loc.x,loc.y,delay_after_ms)
                            actions.sleep(f"{delay_after_ms + 75}ms")
                        else:
                            ctrl.mouse_move(loc.x,loc.y)
                        if action == "click":
                            ctrl.mouse_click()
                        elif action == "right-click":
                            ctrl.mouse_click(1)
                        elif action == "double-click":
                            ctrl.mouse_click(times = 2)
                    else:
                        print(f"Error in accessibility.py function act_on_element: Element has no location.")
                        return 
                elif action == "hover":
                    loc = actions.user.element_location(el)
                    if loc != None:    
                        actions.user.slow_mouse(loc.x,loc.y,delay_after_ms)
                    else:
                        print(f"Error in accessibility.py function act_on_element: Element has no location.")
                elif action == "highlight":
                    actions.user.highlight_element(el)
                elif action == "label":
                    actions.user.highlight_element(el,el.name)
                elif action == "select":
                    if "SelectionItem" in el.patterns:
                        el.selectionitem_pattern.select()
                    elif "LegacyIAccessible" in el.patterns:
                        el.legacyiaccessible_pattern.select(1)
                    else:
                        print(f"Error in accessibility.py function act_on_element: Element cannot be selected.")
                elif action == "invoke":
                    if "Invoke" in el.patterns:
                        el.invoke_pattern.invoke()
                    else:
                        print(f"Error in accessibility.py function act_on_element: Element cannot be invoked.")
                elif action == "toggle":
                    if "Toggle" in el.patterns:
                        el.toggle_pattern.toggle()
                elif action == "expand":
                    if "ExpandCollapse" in el.patterns:
                        el.expandcollapse_pattern.expand()
                elif action == "collapse":
                    if "ExpandCollapse" in el.patterns:
                        el.expandcollapse_pattern.collapse()
                elif action == "scroll_into_view":
                    if "ScrollItem" in el.patterns:
                        el.scrollitem_pattern.scroll_into_view()
            except Exception as error:
                print(f"Error in function act_on_element:\n{error}")
            finally:
                retrieving = False
    def set_el_prop_val(el: ax.Element, prop_name: str, val: str):
        """Attempts to set the given property value of the given element"""
        if not el:
            return 
        if actions.user.winax_retrieving():
            return 
        actions.user.set_winax_retrieving(True)
        try:
            if "VirtualizedItem" in el.patterns:
                el.virtualizeditem_pattern.realize()
            if prop_name == "value":
                if "Value" in el.patterns:
                    pattern = el.value_pattern
                    pattern.value = val
            if prop_name == "text":
                if "Text" in el.patterns:
                    pattern = el.text_pattern
                    pattern.text = val
        except:
            return 
        finally:
            actions.user.set_winax_retrieving(False)
            return True
    def el_prop_val(el: ax.Element, prop_name: str, as_text: bool = False):
        """Returns the property value or None if the property value cannot be retrieved"""
        if not el:
            return 
        global retrieving
        if retrieving:
            print("FUNCTION el_prop_val: unable to retrieve element because another retrieval is in process")
        else:
            retrieving = True
            try:
                # handle virtualized elements
                if "VirtualizedItem" in el.patterns:
                    el.virtualizeditem_pattern.realize()
                if prop_name.lower() == "name":
                    return el.name
                elif prop_name.lower() == "pid":
                    return el.pid
                elif prop_name.lower() == "control_type":
                    return el.control_type
                elif prop_name.lower() == "localized_control_type":
                    return el.localized_control_type
                elif prop_name.lower() == "accelerator_key":
                    return el.accelerator_key
                elif prop_name.lower() == "access_key":
                    return el.access_key
                elif prop_name.lower() == "has_keyboard_focus":
                    return el.has_keyboard_focus
                elif prop_name.lower() == "is_keyboard_focusable":
                    return el.is_keyboard_focusable
                elif prop_name == "is_enabled":
                    return el.is_enabled
                elif prop_name.lower() == "class_name":
                    return el.class_name
                elif prop_name.lower() == "automation_id":
                    return el.automation_id
                elif prop_name.lower() == "printout":
                    s = StringIO()               
                    with redirect_stdout(s):
                        print(el)
                    x = s.getvalue().strip().replace("<","").replace(">","") 
                    return x                
                elif prop_name.lower() == "help_text":
                    return el.help_text
                elif prop_name.lower() == "culture":
                    return el.culture
                elif prop_name.lower() == "is_control_element":
                    return el.is_control_element
                elif prop_name.lower() == "is_content_element":
                    return el.is_content_element
                elif prop_name.lower() == "is_password":
                    return el.is_password
                elif prop_name.lower() == "window_handle":
                    return el.window_handle
                elif prop_name.lower() == "item_type":
                    return el.item_type
                elif prop_name.lower() == "is_offscreen":
                    return el.is_offscreen
                elif prop_name.lower() == "clickable_point":
                    if as_text:
                        loc = el.clickable_point
                        return f"x: {loc.x}   y: {loc.y}"
                    else:
                        return el.clickable_point
                elif prop_name.lower() == "children":
                    children = el.children
                    if children == None:
                        if as_text:
                            return str(None)
                        else:
                            return 0
                    elif as_text:
                        return str(len(children))
                    else:
                        return children
                elif prop_name.lower() == "item_status":
                    return el.item_status
                elif prop_name.lower() == "patterns":
                    r = el.patterns
                    if as_text:
                        r = str(r).replace("[","").replace("]","")
                    return r
                elif prop_name.lower() == "described_by":
                    return el.is_described_by
                elif prop_name.lower() == "flows_to":
                    return el.flows_to
                elif prop_name.lower() == "provider_description":
                    return el.provider_description
                elif prop_name.lower() == "rect":
                    return el.rect
                elif prop_name.lower() == "rect.x":
                    rect = el.rect
                    if rect:
                        return el.rect.x
                elif prop_name.lower() == "rect.y":
                    rect = el.rect
                    if rect:
                        return el.rect.y
                elif prop_name.lower() == "rect.width":
                    rect = el.rect
                    if rect:
                        return el.rect.width
                elif prop_name.lower() == "rect.height":
                    rect = el.rect
                    if rect:
                        return el.rect.height
                elif prop_name.lower() == "value":
                    if "Value" in el.patterns:
                        return el.value_pattern.value
                elif prop_name.lower() == "value.is_read_only":
                    if "Value" in el.patterns:
                        return el.value_pattern.is_read_only
                elif prop_name.lower() == "legacy.value":
                    if "LegacyIAccessible" in el.patterns:
                        return el.legacyiaccessible_pattern.value
                elif prop_name.lower() == "legacy.state":
                    if "LegacyIAccessible" in el.patterns:
                        return el.legacyiaccessible_pattern.state
                elif prop_name.lower() == "legacy.selection":
                    if "LegacyIAccessible" in el.patterns:
                        return el.legacyiaccessible_pattern.selection
                elif prop_name.lower() == "legacy.name":
                    if "LegacyIAccessible" in el.patterns:
                        return el.legacyiaccessible_pattern.name
                elif prop_name.lower() == "legacy.description":
                    if "LegacyIAccessible" in el.patterns:
                        return el.legacyiaccessible_pattern.description
                elif prop_name.lower() == "text":
                    if "Text" in el.patterns:
                        text_range = el.text_pattern.document_range
                        return text_range.text
                    else:
                        if as_text:
                            return ''
                        else:
                            return None
                elif prop_name.lower() == "parent":
                    return el.parent.name if as_text else el.parent
            except Exception as error:
                print(f'error: {error}')
                if as_text:
                    return ''
                else:
                    return  None
            finally:
                retrieving = False

