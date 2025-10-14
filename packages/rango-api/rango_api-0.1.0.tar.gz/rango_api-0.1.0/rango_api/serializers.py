#rango/serializers.py

from pydantic import BaseModel
from typing import List, Any, Optional, Dict, Union
from tortoise import fields
from typing import Any
from tortoise.models import Model

class ModelSerializer:
    """Enhanced serializer for Rango models with foreign key support."""
    
    def __init__(self, instance=None, data=None, many=False, context=None):
        self.instance = instance
        self.initial_data = data
        self.many = many
        self.context = context or {}
        self.validated_data = {}
        self.errors = {}

    @property
    def data(self):
        if self.instance is None:
            return None
        if self.many:
            return [self._serialize(obj) for obj in self.instance]
        return self._serialize(self.instance)

    def is_valid(self):
        if not self.initial_data:
            self.errors = {"detail": "No data provided"}
            return False
        
        self.validated_data = {}
        self.errors = {}
        
        # Get model class from Meta or instance
        model_class = getattr(self.Meta, 'model', None) if hasattr(self, 'Meta') else None
        if not model_class and self.instance and not self.many:
            model_class = type(self.instance)
        
        if not model_class:
            self.validated_data = self.initial_data
            return True
        
        # Validate each field
        for field_name, field_value in self.initial_data.items():
            try:
                validated_name, validated_value = self._validate_field(model_class, field_name, field_value)
                self.validated_data[validated_name] = validated_value
            except Exception as e:
                self.errors[field_name] = str(e)
        
        return len(self.errors) == 0

    # ---- Helpers to detect field kinds without importing internal classes ----
    def _get_model_field(self, model_class: Any, field_name: str):
        return getattr(model_class, "_meta").fields_map.get(field_name)

    def _is_fk_field(self, field_obj: Any) -> bool:
        return bool(field_obj) and field_obj.__class__.__name__.endswith("ForeignKeyFieldInstance")

    def _is_m2m_field(self, field_obj: Any) -> bool:
        return bool(field_obj) and field_obj.__class__.__name__.endswith("ManyToManyFieldInstance")

    def _validate_field(self, model_class, field_name: str, field_value):
        """Validate a single field, handling foreign keys and many-to-many.
        Returns a tuple of (validated_field_name, validated_value).
        """
        base_name = field_name[:-3] if field_name.endswith("_id") else field_name
        model_field = self._get_model_field(model_class, base_name)
        if not model_field:
            return field_name, field_value

        # Foreign key: normalize to <field>_id
        if self._is_fk_field(model_field):
            if field_value is None:
                return f"{base_name}_id", None
            fk_id = field_value
            if isinstance(field_value, dict) and 'id' in field_value:
                fk_id = field_value['id']
            return f"{base_name}_id", fk_id

        # Many-to-many: normalize list of ids
        if self._is_m2m_field(model_field):
            if field_value is None:
                return base_name, []
            if isinstance(field_value, list):
                ids = [item['id'] if isinstance(item, dict) and 'id' in item else item for item in field_value]
                return base_name, ids
            return base_name, field_value

        # Regular field
        return field_name, field_value

    def _serialize(self, obj):
        """Serialize an object with foreign key support."""
        # Get fields from the Meta class if it exists
        if hasattr(self, 'Meta') and hasattr(self.Meta, 'fields'):
            fields_to_serialize = self.Meta.fields
        else:
            # Fallback to all model fields
            fields_to_serialize = [field for field in dir(obj) if not field.startswith('_') and not callable(getattr(obj, field))]
        
        result = {}
        model_class = type(obj)
        
        for field_name in fields_to_serialize:
            if not hasattr(obj, field_name):
                continue
                
            value = getattr(obj, field_name)
            # Handle foreign key and many-to-many relationships
            model_field = self._get_model_field(model_class, field_name)

            if self._is_fk_field(model_field):
                if value is not None:
                    if hasattr(value, '_meta'):
                        result[field_name] = self._serialize_related_object(value)
                    else:
                        result[field_name] = value
                else:
                    result[field_name] = None
            elif self._is_m2m_field(model_field):
                if hasattr(value, '__iter__') and not isinstance(value, str):
                    result[field_name] = [self._serialize_related_object(item) for item in value]
                else:
                    result[field_name] = value
            else:
                result[field_name] = self._serialize_value(value)
        
        return result

    def _serialize_related_object(self, obj):
        """Serialize a related object (foreign key or many-to-many)."""
        if obj is None:
            return None
        
        # Check if there's a nested serializer defined
        nested_serializer_class = getattr(self.Meta, 'nested_serializers', {}).get(type(obj).__name__)
        
        if nested_serializer_class:
            nested_serializer = nested_serializer_class(instance=obj)
            return nested_serializer.data
        else:
            # Default serialization for related objects
            return {
                'id': getattr(obj, 'id', None),
                'str': str(obj) if hasattr(obj, '__str__') else None
            }

    def _serialize_value(self, value):
        """Serialize a primitive value."""
        if value is None:
            return None
        elif hasattr(value, 'isoformat'):  # Handle datetime objects
            return value.isoformat()
        elif isinstance(value, (str, int, float, bool, list, dict)):
            return value
        else:
            return str(value)


class NestedModelSerializer(ModelSerializer):
    """Serializer for nested objects with foreign key relationships."""
    
    def __init__(self, instance=None, data=None, many=False, context=None, depth=1):
        self.depth = depth
        super().__init__(instance, data, many, context)
    
    def _serialize_related_object(self, obj):
        """Enhanced serialization for nested objects."""
        if obj is None:
            return None
        
        if self.depth <= 0:
            return {'id': getattr(obj, 'id', None)}
        
        # Recursively serialize with reduced depth
        nested_serializer = NestedModelSerializer(
            instance=obj, 
            depth=self.depth - 1,
            context=self.context
        )
        return nested_serializer.data
