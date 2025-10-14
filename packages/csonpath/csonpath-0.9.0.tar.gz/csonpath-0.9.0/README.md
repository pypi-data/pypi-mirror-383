# csonpath

> that's not my path, that's not your path, but csonpath

[![Project Sandbox](https://docs.outscale.com/fr/userguide/_images/Project-Sandbox-yellow.svg)](https://docs.outscale.com/en/userguide/Open-Source-Projects.html)

**csonpath** is a partial [JSONPath](https://goessner.net/articles/JsonPath/) implementation in C, with Python bindings. It allows you to query, update, and remove data from JSON objects using path expressions.

## 🌐 Links

- Project website: https://github.com/outscale/csonpath
- Join our community on [Discord](https://discord.gg/HUVtY5gT6s)


## 📄 Table of Contents

- [Overview](#-overview)
- [Requirements](#-requirements)
- [Installation](#-installation)
- [Configuration](#-configuration)
- [Usage](#-usage)
- [Examples](#-examples)
- [License](#-license)
- [Contributing](#-contributing)


## 🚀 Features

### jsonpath
- support simple path like ex: `"$.a[3]["oui"]`
- support `..`: `"$..non`
- support `[*]`: `"$.array[*].obj[*].field"`
- support filters:
  - with `>` or `<`: `"$.obj[?field > 123]"`
  - with `=` or '!=': `"$.obj[?field != "123"]"`
  - with regex, using POSIX regcom: `"$.obj[?.field ~= "123"]"`
  - with `&`: `"$.obj[?field != "123" & second = 1]"`
- support `|`: `"$.obj | $.otherobj"`
### Functions
- **Find First**: Retrieve the first value matching a path.
- **Find All**: Retrieve all values matching a path.
- **Update or Create**: Update values or create new ones according to the path.
- **Remove**: Remove values matching a path.
- **Update or Create Callback**: Update values or create new ones according to the path, using a user-define callback.
- **Callback**: Call a callback according to the path.
- **Supports both C (using json-c) and Python objects.**

## ✅ Getting Started

### Prerequisites

- C compiler (gcc/clang)
- [json-c](https://github.com/json-c/json-c) library for C usage
- Python 3.x (for Python bindings)

### Build

To build the C tests and examples:

```sh
make
```

### Usage (json-c)

See examples in [`tests/json-c/get-a.c`](tests/json-c/get-a.c):

```c
#include "csonpath_json-c.h"

const char *json_str = "{ \"a\": \"value\", \"array\": [1,2,3] }";
struct csonpath p;
struct json_object *jobj = json_tokener_parse(json_str);
struct json_object *ret;

csonpath_init(&p, "$.a");
ret = csonpath_find_first(&p, jobj);
// ret now points to "value"
```

#### Avaible functions:
```C
int csonpath_init(struct csonpath cjp[static 1], const char path[static 1])
```
init a csonpath struct

```C
int csonpath_set_path(struct csonpath cjp[static 1], const char path[static 1])
```
change the path of a struct

```C
int csonpath_compile(struct csonpath cjp[static 1])
```
compile the path, doesn't need to be called before using it, but can be useful to catch error earlyer.
```C
void csonpath_print_instruction(struct csonpath cjp[static 1])
```
print all instructions once compiled
```C
struct json_object *csonpath_find_first(struct csonpath cjp[static 1], struct json_object *json);
```
Retrieve the first value matching a path
```C
struct json_object *csonpath_find_all(struct csonpath cjp[static 1], struct json_object *json);
```
Retrieve all values matching a path, return need to be free using `json_object_put`
```C
struct json_object *csonpath_remove(struct csonpath cjp[static 1], struct json_object *json);
```
Remove all matching elements from json
```C
struct json_object *csonpath_update_or_create(struct csonpath cjp[static 1], struct json_object *json, struct json_object *new_val)
```
update and push new_val, in json.
```C
struct json_object *csonpath_callback(struct csonpath cjp[static 1], struct json_object *json, json_c_callback callback, void *userdata)
```
call `callback` on each value matching path
```C
struct json_object *csonpath_update_or_create_callback(struct csonpath cjp[static 1], struct json_object *json, json_c_callback callback, void *userdata)
```
like callback, but update json base on the path, along the way.

### Usage (Python)

#### Example
```python
import csonpath

d = { "a": "value", "array": [1,2,3] }
o = csonpath.CsonPath("$.a")
print(o.find_first(d))  # Output: "value"
```

#### Avaible methodes:
- `CsonPath(path)`: create a new csonpath object.
- `OBJ.find_first(self, json)`: take a json, return first found occurrence.
- `OBJ.find_all(self, json)`: take a json, return all found occurrence in a list.
- `OBJ.remove(self, json)`: take a json, remove all found occurrence from it.
- `OBJ.update_or_create(self, json, value)`: take a json, replace all found occurrence from it, by the value, if doesn't found something, create it.
- `OBJ.update_or_create_callback(self, json, callback, callback_data)`: take a json, if it doesn't find a parent object, create it, then it calls a callback.
- `OBJ.callback(self, json, callback, callback_data)`: take a json, call a callback, an all occurrence.

`callback` is a function that take 4 arguments: `parent`, `idx`, `cur_value` and `callback_data`

Check [`tests`](tests/python/) for more examples

### Backends and Direct Usage

csonpath is inspired by JSONPath, but is designed to be backend-agnostic: it can work with any C library or environment that manipulates array, object, and scalar types—not just JSON. Out of the box, backends for Python and json-c are provided, but you can create your own backend for other formats such as YAML, or any custom data structure.

To use csonpath with a different data type or library, simply define the required macros and types in a header file (similar to `csonpath_json-c.h` or `csonpath_python.c`), then include your backend header before `csonpath.h`. This approach allows you to adapt csonpath for manipulating data in any format that supports array/object semantics, giving you full flexibility beyond just JSON.

## Directory Structure

- `csonpath.h`, `csonpath_do.h` - Main implementation files
- `csonpath_json-c.h` - Json-C implementation, use it by including "csonpath_json-c.h" directly in your source
- `csonpath_python.c` - python implementation, use it like a python lib (so `pip install .`)
- `tests/` - Contains tests
- `bench/` - Some benchmarks

## 🤝 Contributing

We welcome contributions!

Please read our [Contributing Guidelines](CONTRIBUTING.md) and [Code of Conduct](CODE_OF_CONDUCT.md) before submitting a pull request.

Feel free to open issues or pull requests!

## 📜 License
BSD 3-Clause. See [LICENSE](LICENSE).
