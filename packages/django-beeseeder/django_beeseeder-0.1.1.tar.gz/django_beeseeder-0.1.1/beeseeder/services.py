from collections import OrderedDict
from beeseeder.utils import ModelItem


def order_models_by_dependency(model_items: list[ModelItem]):
    #TODO: check if there is a way to optimize this function
    
    # ordered model items
    omi = OrderedDict() 
    def enforce_order(sub_model_items: list[ModelItem]):
        for model_item in sub_model_items:

            if len(model_item.related_model_names) >= 0:
                related_model_items = list(
                    filter(
                        lambda x: x.model_name in model_item.related_model_names,
                        model_items,
                    )
                )

                added_count = len(
                    [x for x in model_item.related_model_names if x in omi]
                )

                if added_count == len(model_item.related_model_names):
                    if model_item.model_name not in omi:
                        omi[model_item.model_name] = model_item
                else:
                    enforce_order(related_model_items)
            else:
                if model_item.model_name not in omi:
                    omi[model_item.model_name] = model_item

    while len(omi) < len(model_items):
        enforce_order(model_items)

    return omi.values()