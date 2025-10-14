from typing import (
    Any,
    Iterable,
    List,
    Type,
    TypeVar,
    get_type_hints,
    Dict,
    get_origin,
    get_args,
)
from pydantic import BaseModel, ConfigDict
from django.db import models

SerializerType = TypeVar("SerializerType", bound="BaseSerializer")


class BaseSerializer(BaseModel):
    model_config = ConfigDict(from_attributes=True, arbitrary_types_allowed=True)

    @classmethod
    def serialize(
        cls: Type[SerializerType], instance: models.Model, **kwargs: Any
    ) -> Dict[str, Any]:
        """
        Automatically serialize Django model instance, including related fields
        if a serializer is defined for the field type.
        """
        data: Dict[str, Any] = {}
        hints = get_type_hints(cls)

        for field, field_type in hints.items():
            # Skip special fields
            if field.startswith("_") or field == "model_config":
                continue

            value = getattr(instance, field, None)

            # Nested serializer for ForeignKey/OneToOne
            if value is not None and isinstance(value, models.Model):
                try:
                    if issubclass(field_type, BaseSerializer):
                        data[field] = field_type.serialize(value)
                        continue
                except TypeError:
                    pass

            # Handle ManyToMany with serializer hints
            if isinstance(value, models.Manager):
                origin = get_origin(field_type)
                if origin == list:
                    args = get_args(field_type)
                    if args and issubclass(args[0], BaseSerializer):
                        data[field] = [args[0].serialize(obj) for obj in value.all()]
                    else:
                        data[field] = list(value.values())
                    continue

            data[field] = value

        return data

    @classmethod
    def serialize_many(
        cls: Type[SerializerType], queryset: Iterable[models.Model], **kwargs: Any
    ) -> List[Dict[str, Any]]:
        """
        Serialize a list/queryset of Django model instances.
        """
        return [cls.serialize(obj, **kwargs) for obj in queryset]


class ModelSerializer(BaseSerializer):
    """
    ModelSerializer with optional fields, exclusions, and nested serializers.

    Example:
        class ArticleSerializer(ModelSerializer):
            author: UserSerializer  # type hint for nested serialization

            class Meta:
                model = Article
                fields = ['id', 'title', 'author']  # optional
                exclude = ['created_at']  # optional
                depth = 0  # optional, for auto-nesting
    """

    @classmethod
    def get_meta(cls) -> Type:
        if not hasattr(cls, "Meta"):
            raise ValueError(f"{cls.__name__} requires a `Meta` inner class.")
        meta = cls.Meta
        if not hasattr(meta, "model"):
            raise ValueError(f"{cls.__name__}.Meta requires a `model` attribute.")
        return meta

    @classmethod
    def serialize(
        cls: Type[SerializerType], instance: models.Model, **kwargs: Any
    ) -> Dict[str, Any]:
        meta = cls.get_meta()
        model = meta.model
        hints = get_type_hints(cls)
        data: Dict[str, Any] = {}

        include_fields: List[str] | None = getattr(meta, "fields", None)
        exclude_fields: List[str] = getattr(meta, "exclude", [])
        depth: int = getattr(meta, "depth", 0)

        for field in model._meta.get_fields():
            name = field.name

            # Skip reverse relations unless explicitly included
            if field.auto_created and not field.concrete:
                if not include_fields or name not in include_fields:
                    continue

            # Apply fields/exclude logic
            if include_fields and name not in include_fields:
                continue
            if exclude_fields and name in exclude_fields:
                continue

            try:
                value = getattr(instance, name, None)
            except Exception:
                # Skip fields that raise exceptions (e.g., reverse relations)
                continue

            # Nested serializer via type hints (highest priority)
            if name in hints:
                hint = hints[name]

                # Single nested serializer
                try:
                    if isinstance(value, models.Model) and issubclass(
                        hint, BaseSerializer
                    ):
                        data[name] = hint.serialize(value)
                        continue
                except TypeError:
                    pass

                # ManyToMany with serializer
                if isinstance(value, models.Manager):
                    origin = get_origin(hint)
                    if origin == list:
                        args = get_args(hint)
                        if args:
                            try:
                                if issubclass(args[0], BaseSerializer):
                                    data[name] = [
                                        args[0].serialize(obj) for obj in value.all()
                                    ]
                                    continue
                            except TypeError:
                                pass

            # ForeignKey / OneToOne - return nested dict or pk
            if isinstance(field, (models.ForeignKey, models.OneToOneField)):
                if value is None:
                    data[name] = None
                elif depth > 0:
                    # Auto-nest if depth is set
                    data[name] = {
                        "id": value.pk,
                        **{
                            f.name: getattr(value, f.name)
                            for f in value._meta.fields
                            if not isinstance(
                                f, (models.ForeignKey, models.ManyToManyField)
                            )
                        },
                    }
                else:
                    data[name] = value.pk
                continue

            # ManyToMany - return list of pks or nested dicts
            if isinstance(field, models.ManyToManyField):
                if isinstance(value, models.Manager):
                    if depth > 0:
                        data[name] = list(value.values("id"))
                    else:
                        data[name] = list(value.values_list("id", flat=True))
                else:
                    data[name] = []
                continue

            # Regular field
            if isinstance(field, models.Field):
                data[name] = value

        return data


# Usage:
# book = Book.lobjects.get(id=1)
# data = BookSerializer.serialize(book)
#
# books = Book.objects.all()
# data_list = BookSerializer.serialize_many(books)
