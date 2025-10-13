# Django Structured JSON Field [![PyPI](https://img.shields.io/pypi/v/django-structured-json-field?style=flat-square)](https://pypi.org/project/django-structured-json-field) ![Codecov](https://img.shields.io/codecov/c/github/bnznamco/django-structured-field?style=flat-square&logo=codecov&logoSize=auto&cacheSeconds=0) ![GitHub Workflow Status](https://img.shields.io/github/actions/workflow/status/lotrekagency/django-structured-field/ci.yml?style=flat-square) [![GitHub](https://img.shields.io/github/license/lotrekagency/django-structured-field?style=flat-square)](./LICENSE) [![Docs](https://img.shields.io/badge/docs-online-brightgreen?style=flat-square)](https://bnznamco.github.io/django-structured-field/)


<br>
<br>
<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="docs/.vuepress/public/images/logo-dark.svg" width="200">
    <source media="(prefers-color-scheme: light)" srcset="docs/.vuepress/public/images/logo.svg" width="200">
    <img alt="Django Structured JSON Field logo" src="docs/.vuepress/public/images/logo.svg" width="200">
  </picture>
</p>
<br>
<br>
<br>
<br>



This is a Django field that allows you to declare the structure of a JSON field and validate it.

## Features

- Define the structure of a JSON field using Pydantic models
- Validate the JSON field against the defined structure
- Use relationships between models inside the JSON field 🤯
- Easily integrate with Django Rest Framework serializers
- Admin editor for the JSON field with autocomplete search for related models 👀


## Documentation

Check out our [documentation](https://bnznamco.github.io/django-structured-field/) for detailed guides and examples on:

- Installation and basic usage
- Working with relationships
- Admin integration
- REST Framework integration
- Caching
- Settings configuration



## Installation

```bash
pip install django-structured-json-field
```

## Usage

```python
from django.db import models
from structured.fields import StructuredJSONField
from structured.pydantic.models import BaseModel

# Define this schema as you would do with a Pydantic model
class MySchema(BaseModel):
    name: str
    age: int = None

def init_data():
    return MySchema(name='')

# Create a model with a StructuredJSONField with the schema you defined
class MyModel(models.Model):
    structured_data = StructuredJSONField(schema=MySchema, default=init_data)

```

## Relationships

This field supports relationships between models, you can define them in your schema and they will be treated as normal django relationships. It also supports recursive schemas.

### Recursion

You can define recursive schemas by declaring the attribute type as a string:

```python
from typing import Optional, List

class MySchema(BaseModel):
    name: str
    age: int = None
    parent: Optional['MySchema'] = None
    relateds: List['MySchema'] = []
```

### Foreign Keys

You can also define model relationships in your schema:

```python
from structured.pydantic.fields import ForeignKey

class MySchema(BaseModel):
    name: str
    age: int = None
    fk_field: ForeignKey['MyModel'] = None
```

This will treat the parent field as a normal django ForeignKey.

#### Tip:

You can omit the `ForeignKey` field and just use the model class as the type annotation:

```python
class MySchema(BaseModel):
    name: str
    age: int = None
    fk_field: MyModel = None
```

the field will still be treated as a ForeignKey if the type annotation is a subclass of django `models.Model`.

### ManyToMany

If you need a ManyToMany relationship, you can use the `QuerySet` field:

```python
from structured.pydantic.fields import QuerySet

class MySchema(BaseModel):
    name: str
    age: int = None
    parents: QuerySet['MyModel']
```

`QuerySet` fields will generate a django object manager that will allow you to query the related objects as you would do with a normal django `QuerySet`.

```python
instance = MySchema(name='test', age=10, parents=MyModel.objects.all())
# You can filter the queryset
instance.parents.filter(name='test')
# You can count the queryset
instance.parents.count()
# You can get the first element of the queryset, etc...
instance.parents.first()
```

### Admin integration

The field is integrated with the Django admin, you can use the autocomplete search to select the related models. To allow the autocomplete search you need to include structured.urls in your urls.py file:

```python
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('structured.urls')),
]
```

### Rest Framework integration

You can easily integrate structured fields with Django Rest Framework serializers, just use the `StructuredModelSerializer` as the base class for your serializer:

```python
from rest_framework import serializers
from structured.contrib.rest_framework import StructuredModelSerializer

class MyModelSerializer(StructuredModelSerializer):
    class Meta:
        model = MyModel
        fields = '__all__'
```

Errors generated by pydantic validation will be automatically translated to DRF errors.


### Cache

To prevent the field from making multiple identical queries a caching technique is used. The cache is still a work in progress, please open an issue if you find any problem.
Actually the cache covers all the relations inside a StructuredJSONField, optimizing the queries during the serialization process.

#### Cache engine progress:

- [x] Shared cache between `ForeignKey` fields and `QuerySet` fields
- [x] Shared cache through nested schemas
- [x] Shared cache through nested lists of schemas
- [ ] Shared cache between all `StructuredJSONFields` in the same instance
- [ ] Shared cache between multiple instances of the same model
- [ ] Cache invalidation mechanism

## Settings

You can manage structured field behaviour modifying the `STRUCTURED_FIELD` setting in your `settings.py` file. Here a list of the available settings and their default values:

```python
STRUCTURED_FIELD = {
    'CACHE':{
        'ENABLED': True,
        'SHARED': False # ⚠️ EXPERIMENTAL: this enables a thread-shared cache, it's not recommended to use it in production.
    },
}
```

## Contributing

The project is open to contributions, just open an issue or a PR.

### Running tests

```bash
pip install -r requirements-dev.txt
make test
```

### Running test app

```bash
pip install -r requirements-dev.txt
python manage.py migrate
python manage.py runserver
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details
