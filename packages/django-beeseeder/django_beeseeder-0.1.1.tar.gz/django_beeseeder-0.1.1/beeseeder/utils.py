from django.db.models import fields
from django.conf import settings

class ModelItem:
    exclude_model_field_names =['group', "user_permissions"]
    def __init__(self, model, record_count=50):
        self.model = model
        self.related_model_names = (
            []
        )  # will contain all the external model names that are related to the current model

        self.model_schema = self.get_model_schema()
        self.model_name = self.model_schema["name"]
        self.record_count = record_count

    def __str__(self):
        return f"{self.model.__name__}"

    def get_model_schema(self):
        schema = {}
        model_name = self.model._meta.app_label + "." + self.model.__name__
        schema["name"] = model_name
        schema["fields"] = []

        for field in self.model._meta.get_fields():
            # `field.concrete` checks if the field directly corresponds to a database column.
            if not field.concrete:
                continue
            
            if field.name in self.exclude_model_field_names:
                continue
            
            field_info = {
                "type": field.get_internal_type(),
                "is_relation": field.is_relation,
                "name": field.name,
            }
           
            
            # Extra details for regular fields
            if hasattr(field, "max_length") and field.max_length:
                field_info["max_length"] = field.max_length
            if hasattr(field, "null"):
                field_info["null"] = field.null
            if hasattr(field, "blank"):
                field_info["blank"] = field.blank
            if hasattr(field, "unique"):
                field_info["unique"] = field.unique
            
            
            if hasattr(field, "choices"):
                if field.choices is not None and field.choices != fields.NOT_PROVIDED:

                    field_info["choices"] = field.choices[:10]
            
            if hasattr(field, "default"):
                default_value = field.default
                if default_value is not None and default_value != fields.NOT_PROVIDED:
                    if callable(default_value):
                        default_value = default_value()
                        field_info["default"] = default_value
                    else:
                        field_info["default"] = default_value
            
            if hasattr(field, "help_text"):
                field_info["help_text"] = field.help_text

            if field.is_relation:
                if field.related_model._meta.app_label in settings.SEED_APPS:
                    related_model_name = (
                        f"{field.related_model._meta.app_label}.{field.related_model.__name__}"
                        if field.related_model
                        else None
                    )  # produces something like 'auth.User'

                    if related_model_name not in self.related_model_names:
                        self.related_model_names.append(related_model_name)
                    field_info["related_model"] = related_model_name

                
            schema["fields"].append(field_info)
            schema["related_model_names"] = self.related_model_names
        return schema