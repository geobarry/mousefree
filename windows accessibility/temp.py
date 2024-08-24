from talon import Module, ui, Context, ctrl
mod = Module()
@mod.action_class
class Actions:
    def click_focused():
        """attempts to click on the currently focused element"""
        el = ui.focused_element()
        try: # try clickable point property
            pt = el.clickable_point
        except:
            try: # try rectangle
                rect = el.rect
                pt = Point2d(rect.x + int(rect.width/2),rect.y + int(rect.height/2))
            except:
                print("accessibility: element_location: NO LOCATION FOUND :(")
        if pt:
            ctrl.mouse_move(pt.x,pt.y)
            ctrl.mouse_click()
