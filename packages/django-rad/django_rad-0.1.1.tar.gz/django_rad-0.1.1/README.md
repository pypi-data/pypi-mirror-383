Here’s your content converted into clean Markdown format:

````markdown
# django-rad

**django-rad** is a Django app that helps in the creation of APIs, which is somewhat a mix of **Django Ninja** and **Django Rest Framework**.

## Quick Start

1. **Add `rad` to your `INSTALLED_APPS` setting**:

```python
INSTALLED_APPS = [
    ...,
    "rad",
]
````

2. **Include the router in your `urls.py`** so that all controllers are registered:

```python
from django_rad.routers import route

path("api/", route.api.urls())
```

3. **Create a `controllers.py`** or write the controller in `views.py`:

```python
from django_rad.controllers import ApiController

class IndexController(ApiController):
    @route.api.get("/")
    def index(self, request):
        return self.response({"message": "hello world"})
```

```

If you want, I can also make it **even more structured and beginner-friendly** with headings, code blocks, and notes. Do you want me to do that?
```
