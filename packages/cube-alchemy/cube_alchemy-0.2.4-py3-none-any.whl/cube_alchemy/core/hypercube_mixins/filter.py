import logging
from typing import Dict, List, Any
import pandas as pd

class Filter:

    def filter(
        self,
        criteria: Dict[str, List[Any]],
        context_state_name: str = 'Default',
        is_reset: bool = False,
        save_state: bool = True
    ) -> bool:
        """
        Applies filters to the DataFrame and updates the state.
        """
        if context_state_name == 'Unfiltered':
            raise ValueError("Cannot use 'Unfiltered' state name to change filter state. Please use a different state name.")

        self.context_states[context_state_name] = self._fetch_and_filter(context_state_name=context_state_name, filter_criteria=criteria)

        if not is_reset:
            self._truncate_filter_history(context_state_name=context_state_name)
            self.filter_pointer[context_state_name] += 1

        if save_state:
            self.applied_filters[context_state_name].append({"op": 'add', "criteria": criteria})

        
        return True
    
    def remove_filter(
        self,
        dimensions: List[str],        
        context_state_name: str = 'Default',
        is_reset: bool = False
    ) -> bool:

        if context_state_name == 'Unfiltered':
            raise ValueError("Cannot use 'Unfiltered' state. Please use a different state name.")
        
        # Get all current filters up to the pointer
        current_filters = self.get_filters(0, context_state_name = context_state_name)

        new_filter_set = {k: v for k, v in current_filters.items() if k not in dimensions}
        
        self.context_states[context_state_name] = self.context_states['Unfiltered'].copy()
        self.filter(
            new_filter_set,
            context_state_name=context_state_name,
            is_reset=is_reset,
            save_state=False,
        )

        self.applied_filters[context_state_name].append({"op": 'remove', "dimensions": dimensions})

        return True
    
    def reset_filters(
        self,
        direction: str = 'backward',
        context_state_name: str = 'Default'
    ) -> bool:

        if context_state_name == 'Unfiltered':
            raise ValueError("Cannot use 'Unfiltered' state. Please use a different state name.")
        
        if direction == 'backward':
            self.context_states[context_state_name] = self.context_states['Unfiltered'].copy()
            self.filter_pointer[context_state_name] -= 1
            self.filter(
                self.get_filters(0, context_state_name=context_state_name),
                context_state_name=context_state_name,
                is_reset=True,
                save_state=False,
            )  # resets are not saved as a new state
        elif direction == 'forward':
            if self.filter_pointer[context_state_name] == len(self.applied_filters[context_state_name]):
                return False
            self.filter_pointer[context_state_name] += 1
            next_filter = self.applied_filters[context_state_name][self.filter_pointer[context_state_name] - 1] # maybe I should have used the pointer index to match the list index, it is one more for now
            if next_filter['op'] == 'add':
                self.filter(
                    next_filter['criteria'],
                    context_state_name=context_state_name,
                    is_reset=True,
                    save_state=False,
                )
            else:
                self.context_states[context_state_name] = self.context_states['Unfiltered'].copy()
                self.filter(
                    self.get_filters(0, context_state_name=context_state_name),
                    context_state_name=context_state_name,
                    is_reset=True,
                    save_state=False,
                )

        elif direction == 'all':
            dimensions = []
            for dim in self.get_filters(0, context_state_name = context_state_name):
                dimensions.append(dim)

            self._truncate_filter_history(context_state_name = context_state_name)
            self.filter_pointer[context_state_name] += 1

            self.applied_filters[context_state_name].append({"op": 'remove', "dimensions": dimensions})

            self.context_states[context_state_name] = self.context_states['Unfiltered'].copy()
        else:
            raise ValueError("Invalid direction. Use 'backward', 'forward', or 'all'.")



        return True
    
    def get_filters(
        self,
        off_set: int = 0,
        context_state_name: str = 'Default'
    ) -> Dict[str, List[Any]]:

        #current position is off_set = 0
        position = self.filter_pointer[context_state_name] + off_set
        current_filters = self.applied_filters[context_state_name][:position]

        filters_state = {}
        for filter in current_filters:
            if filter['op'] == 'add':
                for dim, vals in filter['criteria'].items():
                    # Overwrite the dimension with the new values
                    filters_state[dim] = list(vals)
            elif filter['op'] == 'remove':
                for dim in filter['dimensions']:
                    if dim in filters_state:
                        del filters_state[dim]
        return filters_state
    
    def get_filtered_dimensions(
        self,
        off_set: int = 0,
        context_state_name: str = 'Default'
    ) -> List[str]:
        if context_state_name == 'Unfiltered':
            raise ValueError("Cannot use 'Unfiltered' state. Please use a different state name.")
        
        """
        Returns a list of currently filtered dimensions (keys) only, not their values.
        """
        position = self.filter_pointer[context_state_name] + off_set
        current_filters = self.applied_filters[context_state_name][:position]
        filtered_dimensions = []
        for filter in current_filters:
            if filter['op'] == 'add':
                for dim in filter['criteria'].keys():
                    filtered_dimensions.append(dim)
            elif filter['op'] == 'remove':
                for dim in filter['dimensions']:
                    if dim in filtered_dimensions:
                        filtered_dimensions = [d for d in filtered_dimensions if d != dim]
        # Only keep the last occurrence of each dimension (preserve order, no duplicates)
        seen = set()
        result = []
        for dim in reversed(filtered_dimensions):
            if dim not in seen:
                seen.add(dim)
                result.insert(0, dim)
        return result
    
    def set_context_state(
        self,
        context_state_name: str,
        base_context_state_name: str = 'Unfiltered'
    ) -> bool:
        if context_state_name == 'Unfiltered':
            raise ValueError("Cannot use 'Unfiltered' state name. Please use a different state name.")
        try:
            self.context_states[context_state_name] = self.context_states[base_context_state_name].copy()
            self.applied_filters[context_state_name]  =  [] 
            self.filter_pointer[context_state_name]  = 0 
            return True
        except Exception as e:
            self.log().error("Error setting state '%s': %s", context_state_name, e)
            return False
    
    def _truncate_filter_history(
        self,
        context_state_name: str = 'Default'
    ) -> bool:
        if context_state_name == 'Unfiltered':
            raise ValueError("Cannot use 'Unfiltered' state. Please use a different state name.")
        
        # truncate index if pointer is not at the end (re-writes the applied filters)
        if self.filter_pointer[context_state_name] < len(self.applied_filters[context_state_name]):
            self.applied_filters[context_state_name] = self.applied_filters[context_state_name][:self.filter_pointer[context_state_name]]
        return True
    