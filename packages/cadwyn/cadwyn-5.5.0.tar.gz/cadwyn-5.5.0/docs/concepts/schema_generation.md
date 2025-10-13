# Schema generation

Cadwyn automatically generates versioned schemas and everything related to them from HEAD version at runtime -- no actual code is being generated. These versioned schemas will be automatically used in requests and responses for [versioned API routes](./main_app.md#main-app).

## Rendering schemas

When you have many versions and schemas, it is quite challenging to know what validators, fields, and other attributes are defined on each schema in any specific version. To address this issue, there is a way to **render** the generated pydantic models and enums as code using the command-line interface.

**NOTICE** that `cadwyn render` does not guarantee rendering correct schemas. It is going to be a close enough approximation for manual validation. However, it is not yet ready to be used for production code generation. For example, it doesn't handle schema renamings in class `__bases__` yet.

### Rendering a module

Here's a way to render the entire module with the schemas:

```bash
cadwyn render module data.schemas --app=main:app --version=2024-05-26
```
<!-- TODO: Add an option to use a callable instead of a variable -->
This command will print to stdout what the schemas would look like in version 2024-05-26 if they were written by hand instead of generated at runtime by Cadwyn. This command takes the schemas from `data/schemas.py` module and knows what the schemas would look like based on the version changes from `Cadwyn` app instance named `app` and located in `main.py`.

### Rendering a single model

Here's a way to render a single pydantic model or enum with the schemas:

```bash
cadwyn render model data.schemas:UserCreateRequest --app=main:app --version=2024-05-26
```

This command will print to stdout what the `UserCreateRequest` schema would look like in version 2024-05-26 if it was written by hand instead of generated at runtime by Cadwyn. This command takes the `UserCreateRequest` schema from `data/schemas.py` module and knows what the schema would look like based on the version changes from `Cadwyn` app instance named `app` and located in `main.py`.

## Generating schemas without FastAPI

Cadwyn is capable of generating versioned schemas from its version changes even without FastAPI:

```python
import cadwyn
from cadwyn.schema_generation import generate_versioned_models
from my_versions import version_bundle, MyVersionedSchema

schema_generators = generate_versioned_models(version_bundle)
MyVersionedSchemaFrom2025 = schema_generators["2025-11-16"][MyVersionedSchema]
```
