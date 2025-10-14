
#rango.generics.py
from fastapi import HTTPException, Query
from fastapi.responses import JSONResponse
from .serializers import ModelSerializer
from tortoise import fields
from typing import Any
from typing import List, Optional
import logging

logger = logging.getLogger(__name__)

class ListCreateView:
    model = None
    serializer_class = None
    prefetch_related = []  # List of related fields to prefetch
    select_related = []    # List of foreign key fields to select_related

    # ---- Helpers to detect field kinds without importing internal classes ----
    def _get_model_field(self, field_name: str):
        return getattr(self.model, "_meta").fields_map.get(field_name)

    def _is_fk_field(self, field_obj: Any) -> bool:
        # Tortoise uses ForeignKeyFieldInstance for FK descriptors in _meta.fields_map
        return bool(field_obj) and field_obj.__class__.__name__.endswith("ForeignKeyFieldInstance")

    def _is_m2m_field(self, field_obj: Any) -> bool:
        # Tortoise uses ManyToManyFieldInstance for M2M descriptors in _meta.fields_map
        return bool(field_obj) and field_obj.__class__.__name__.endswith("ManyToManyFieldInstance")

    def _is_text_field(self, field_obj: Any) -> bool:
        name = getattr(field_obj.__class__, "__name__", "")
        return name in ("CharField", "TextField")

    # ----------------------------
    # Extensibility hooks (override in subclasses)
    # ----------------------------
    def get_base_queryset(self):
        return self.model.all()

    def get_queryset(self, request):
        return self.get_base_queryset()

    async def filter_queryset(self, request, queryset):
        return queryset

    def serialize(self, objects, many: bool):
        return self.serializer_class(objects, many=many).data

    async def before_create(self, request, data: dict) -> dict:
        return data

    async def perform_create(self, validated_data: dict):
        # Default: create handling relations
        return await self._create_with_relations(validated_data)

    async def after_create(self, request, obj):
        return obj

    async def get(self, request):
        """Get list of objects with optional filtering and pagination."""
        # Parse query parameters
        page = int(request.query_params.get('page', 1))
        page_size = int(request.query_params.get('page_size', 100))
        search = request.query_params.get('search', None)
        
        # Build query
        query = self.get_queryset(request)
        
        # Apply select_related for foreign keys
        if self.select_related:
            query = query.select_related(*self.select_related)
        
        # Apply prefetch_related for many-to-many and reverse foreign keys
        if self.prefetch_related:
            query = query.prefetch_related(*self.prefetch_related)
        
        # Apply search if provided and additional filtering
        if search:
            query = await self._apply_search(query, search)
        query = await self.filter_queryset(request, query)
        
        # Apply pagination
        offset = (page - 1) * page_size
        objects = await query.offset(offset).limit(page_size)
        
        # Serialize with proper foreign key handling
        return JSONResponse({
            'results': self.serialize(objects, many=True),
            'page': page,
            'page_size': page_size,
            'count': len(objects)
        })

    async def post(self, request):
        """Create a new object with foreign key validation."""
        data = await request.json()
        
        # Hooks + validation
        data = await self.before_create(request, data)
        await self._validate_foreign_keys(data)
        
        serializer = self.serializer_class(data=data)
        if serializer.is_valid():
            # Create the object (overrideable)
            obj = await self.perform_create(serializer.validated_data)
            obj = await self.after_create(request, obj)
            
            # Fetch the created object with relations for serialization
            obj_with_relations = await self._get_object_with_relations(obj.id)
            return JSONResponse(self.serializer_class(obj_with_relations).data, status_code=201)
        
        raise HTTPException(status_code=400, detail=serializer.errors)

    async def _apply_search(self, query, search_term: str):
        """Apply search functionality to the query."""
        # This is a basic implementation - can be overridden in subclasses
        # Look for text fields to search in
        search_fields = []
        for field_name, field in self.model._meta.fields_map.items():
            if self._is_text_field(field):
                search_fields.append(field_name)
        
        if search_fields:
            # Create OR conditions for search
            from tortoise.expressions import Q
            search_conditions = Q()
            for field in search_fields:
                search_conditions |= Q(**{f"{field}__icontains": search_term})
            query = query.filter(search_conditions)
        
        return query

    async def _validate_foreign_keys(self, data: dict):
        """Validate that foreign key references exist."""
        for field_name, field_value in data.items():
            # support both "category" and "category_id"
            base_name = field_name[:-3] if field_name.endswith("_id") else field_name
            model_field = self._get_model_field(base_name)

            if self._is_fk_field(model_field) and field_value is not None:
                # Check if the referenced object exists
                related_model = model_field.related_model
                if isinstance(field_value, dict) and 'id' in field_value:
                    field_value = field_value['id']
                
                exists = await related_model.filter(id=field_value).exists()
                if not exists:
                    raise HTTPException(
                        status_code=400, 
                        detail=f"Related object with id {field_value} does not exist for field {base_name}"
                    )

    async def _create_with_relations(self, validated_data: dict):
        """Create object and handle many-to-many relations."""
        # Separate many-to-many fields
        many_to_many_data = {}
        regular_data = {}
        
        for field_name, value in validated_data.items():
            base_name = field_name[:-3] if field_name.endswith("_id") else field_name
            model_field = self._get_model_field(base_name)

            if self._is_m2m_field(model_field):
                many_to_many_data[base_name] = value
            elif self._is_fk_field(model_field):
                fk_id = value['id'] if isinstance(value, dict) and 'id' in value else value
                regular_data[f"{base_name}_id"] = fk_id
            else:
                regular_data[field_name] = value
        
        # Create the object
        obj = await self.model.create(**regular_data)
        
        # Handle many-to-many relationships
        for field_name, related_ids in many_to_many_data.items():
            if related_ids:
                related_field = getattr(obj, field_name)
                await related_field.add(*related_ids)
        
        return obj

    async def _get_object_with_relations(self, obj_id: int):
        """Get object with all relations prefetched."""
        query = self.model.filter(id=obj_id)
        
        if self.select_related:
            query = query.select_related(*self.select_related)
        
        if self.prefetch_related:
            query = query.prefetch_related(*self.prefetch_related)
        
        return await query.first()


class RetrieveUpdateDeleteView:
    model = None
    serializer_class = None
    prefetch_related = []  # List of related fields to prefetch
    select_related = []    # List of foreign key fields to select_related

    # ----------------------------
    # Extensibility hooks (override in subclasses)
    # ----------------------------
    # Helpers (duplicated from ListCreateView for isolation)
    def _get_model_field(self, field_name: str):
        return getattr(self.model, "_meta").fields_map.get(field_name)

    def _is_fk_field(self, field_obj: Any) -> bool:
        return bool(field_obj) and field_obj.__class__.__name__.endswith("ForeignKeyFieldInstance")

    def _is_m2m_field(self, field_obj: Any) -> bool:
        return bool(field_obj) and field_obj.__class__.__name__.endswith("ManyToManyFieldInstance")

    async def get_object(self, request, id: int):
        return await self._get_object_with_relations(id)

    async def before_update(self, request, obj, data: dict) -> dict:
        return data

    async def perform_update(self, obj, validated_data: dict):
        await self._update_with_relations(obj, validated_data)
        return obj

    async def after_update(self, request, obj):
        return obj

    async def before_delete(self, request, obj):
        return None

    async def perform_delete(self, obj):
        await obj.delete()

    async def after_delete(self, request, obj_id: int):
        return None

    async def get(self, request, id: int):
        """Retrieve a single object with relations."""
        obj = await self.get_object(request, id)
        if not obj:
            raise HTTPException(status_code=404, detail="Not found")
        return JSONResponse(self.serializer_class(obj).data)

    async def put(self, request, id: int):
        """Update an object with foreign key validation."""
        obj = await self.model.filter(id=id).first()
        if not obj:
            raise HTTPException(status_code=404, detail="Not found")
        
        data = await request.json()
        # Hooks + validation
        data = await self.before_update(request, obj, data)
        await self._validate_foreign_keys(data)
        
        serializer = self.serializer_class(data=data, instance=obj)
        if serializer.is_valid():
            # Update (overrideable)
            obj = await self.perform_update(obj, serializer.validated_data)
            obj = await self.after_update(request, obj)
            
            # Fetch the updated object with relations for serialization
            obj_with_relations = await self._get_object_with_relations(obj.id)
            return JSONResponse(self.serializer_class(obj_with_relations).data)
        
        raise HTTPException(status_code=400, detail=serializer.errors)

    async def patch(self, request, id: int):
        """Partial update of an object."""
        obj = await self.model.filter(id=id).first()
        if not obj:
            raise HTTPException(status_code=404, detail="Not found")
        
        data = await request.json()
        # Hooks + validation
        data = await self.before_update(request, obj, data)
        await self._validate_foreign_keys(data)
        
        serializer = self.serializer_class(data=data, instance=obj, partial=True)
        if serializer.is_valid():
            obj = await self.perform_update(obj, serializer.validated_data)
            obj = await self.after_update(request, obj)
            
            # Fetch the updated object with relations for serialization
            obj_with_relations = await self._get_object_with_relations(obj.id)
            return JSONResponse(self.serializer_class(obj_with_relations).data)
        
        raise HTTPException(status_code=400, detail=serializer.errors)

    async def delete(self, request, id: int):
        """Delete an object."""
        obj = await self.model.filter(id=id).first()
        if not obj:
            raise HTTPException(status_code=404, detail="Not found")
        await self.before_delete(request, obj)
        await self.perform_delete(obj)
        await self.after_delete(request, id)
        return JSONResponse({"detail": "Deleted"})

    async def _validate_foreign_keys(self, data: dict):
        """Validate that foreign key references exist."""
        for field_name, field_value in data.items():
            # support both "field" and "field_id"
            base_name = field_name[:-3] if field_name.endswith("_id") else field_name
            model_field = self._get_model_field(base_name)

            if self._is_fk_field(model_field) and field_value is not None:
                related_model = model_field.related_model
                if isinstance(field_value, dict) and 'id' in field_value:
                    field_value = field_value['id']
                exists = await related_model.filter(id=field_value).exists()
                if not exists:
                    raise HTTPException(
                        status_code=400,
                        detail=f"Related object with id {field_value} does not exist for field {base_name}"
                    )

    async def _update_with_relations(self, obj, validated_data: dict):
        """Update object and handle many-to-many relations."""
        # Separate many-to-many fields
        many_to_many_data = {}
        regular_data = {}
        
        for field_name, value in validated_data.items():
            base_name = field_name[:-3] if field_name.endswith("_id") else field_name
            model_field = self._get_model_field(base_name)

            if self._is_m2m_field(model_field):
                many_to_many_data[base_name] = value
            elif self._is_fk_field(model_field):
                fk_id = value['id'] if isinstance(value, dict) and 'id' in value else value
                regular_data[f"{base_name}_id"] = fk_id
            else:
                regular_data[field_name] = value
        
        # Update regular fields
        for field_name, value in regular_data.items():
            setattr(obj, field_name, value)
        await obj.save()
        
        # Handle many-to-many relationships
        for field_name, related_ids in many_to_many_data.items():
            related_field = getattr(obj, field_name)
            # Clear existing relations and add new ones
            await related_field.clear()
            if related_ids:
                await related_field.add(*related_ids)

    async def _get_object_with_relations(self, obj_id: int):
        """Get object with all relations prefetched."""
        query = self.model.filter(id=obj_id)
        
        if self.select_related:
            query = query.select_related(*self.select_related)
        
        if self.prefetch_related:
            query = query.prefetch_related(*self.prefetch_related)
        
        return await query.first()
