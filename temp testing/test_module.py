from talon import Context,Module,actions

ctx = Context()

@ctx.dynamic_list("user.turnip_salad")
def turnip_salad(spoken_form) -> dict[str,str]:
    # NOTE: It looks like you are not allowed to call an action from inside a dynamic list in another module
    print(f"FUNCTION turnip_salad")
#    actions.user.add_salad_dressing()
    dynamic_output = {"turnip":"salad"}
    return dynamic_output

mod = Module()

mod.list("turnip_salad","dummy list")
@mod.action_class
class Actions:
    def add_salad_dressing():
        """dummy function for testing"""
        print("Mixing some oil in vinegar...")
        return 

