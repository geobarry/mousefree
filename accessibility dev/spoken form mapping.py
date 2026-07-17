from talon import Module, actions

mod=Module()

@mod.action_class
class GenericMappingsActions:

    def create_spoken_form_mappings(name_obj_list: list[tuple[str, object]]) -> tuple[dict, dict]:
        """Returns spoken-form dict and spoken_form→obj_list mapping.
        
        Input: list of (name, obj) pairs. Duplicate names allowed.
        Output:
          spoken_form_dict: spoken_form → spoken_form
          obj_dict: spoken_form → [objects]
        """
        # STANDARD USAGE - INSIDE DYNAMIC LIST FUNCTION:
        #   obtain list of (name, obj) tuples
        #   create global obj_dict
        #   spoken_form_dict,obj_dict = actions.user.create_spoken_form_mappings(name_dict)
        #   return spoken_form_dict
        # Then use obj_dict in action with dynamic list input argument
        # Spoken forms will be created for each name
        # The output spoken_form_dict contains spoken forms; keys and values are identical
        # The output obj_dict keys will be spoken forms and values will be lists of associated objects
        # In the output, the same object may be associated with multiple spoken forms
        
        # 1. spoken_form → [names]
        spoken_form_name_dict = {}
        for name, obj in name_obj_list:
            sf_map = actions.user.create_spoken_forms_from_list([name])
            for spoken_form in sf_map.keys():
                spoken_form_name_dict.setdefault(spoken_form, []).append(name)

        # 2. spoken_form → [objects]
        obj_dict = {}
        for spoken_form, names in spoken_form_name_dict.items():
            for name, obj in name_obj_list:
                if name in names:
                    obj_dict.setdefault(spoken_form, []).append(obj)

        # 3. spoken_form → spoken_form (for Talon dynamic list)
        spoken_form_dict = {sf: sf for sf in spoken_form_name_dict.keys()}

        return spoken_form_dict, obj_dict

        
        
        