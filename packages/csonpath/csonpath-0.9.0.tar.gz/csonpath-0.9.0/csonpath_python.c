#include <Python.h>

#define CSONPATH_JSON PyObject *

#define CSONPATH_NULL Py_None

#define CSONPATH_GET csonpath_python_get

#define CSONPATH_AT csonpath_python_at

#define CSONPATH_REMOVE(o) Py_XDECREF(o)

#define CSONPATH_NEW_OBJECT() PyDict_New()

#define CSONPATH_NEW_ARRAY() PyList_New(0)

#define CSONPATH_IS_OBJ(o) PyDict_Check(o)

#define CSONPATH_IS_ARRAY(o) PyList_Check(o)

#define CSONPATH_IS_STR(o) PyUnicode_Check(o)

#define CSONPATH_IS_NUM(o) PyLong_Check(o)

#define CSONPATH_GET_STR(obj)			\
    PyUnicode_AsUTF8(obj)

#define CSONPATH_DECREF(obj)			\
  Py_DECREF(obj);
  

#define CSONPATH_GET_NUM(obj)			\
    PyLong_AsLong(obj)

#define CSONPATH_EQUAL_NUM(obj, to_cmp)		\
    ({						\
	_Bool r = 0;				\
	if (PyLong_Check(obj)) {		\
	    r = PyLong_AsLong(obj) == to_cmp;	\
	}					\
	r;					\
    })

#define CSONPATH_EQUAL_STR(obj, to_cmp)	({			\
    _Bool r = 0;						\
      if (PyUnicode_Check(obj))	{				\
	const char *py_str = PyUnicode_AsUTF8(obj);		\
	r = !strcmp(py_str, to_cmp);				\
      }								\
      r;							\
    })

#define CSONPATH_FORMAT_EXCEPTION(ARGS...)	\
    PyErr_Format(PyExc_ValueError, ARGS)

#define CSONPATH_EXCEPTION(ARGS...)		\
    PyErr_Format(PyExc_ValueError, ARGS);	\
    return -1;

#define CSONPATH_CALLBACK PyObject *

#define CSONPATH_CALLBACK_DATA PyObject *

#define CSONPATH_CALL_CALLBACK(callback, ctx, child_info, tmp, udata) do { \
	PyObject *arglist;						\
	if (child_info->type == CSONPATH_STR)				\
	    arglist = Py_BuildValue("(OsOO)", ctx, child_info->key, tmp, udata); \
	else								\
	    arglist = Py_BuildValue("(OiOO)", ctx, child_info->idx, tmp, udata); \
	PyObject_CallObject(callback, arglist);				\
	Py_DECREF(arglist);						\
    } while (0)

/* assuming each modification of the object need to go out of the loop */
#define CSONPATH_NEED_FOREACH_REDO(o)	1

#define CSONPATH_REMOVE_CHILD(obj, child_info)				\
  if (child_info.type == CSONPATH_INTEGER) {				\
    PyList_SetSlice(obj, child_info.idx, child_info.idx + 1, NULL);	\
  } else if (child_info.type == CSONPATH_STR) {				\
    PyDict_DelItemString(obj, child_info.key);				\
  }

#define CSONPATH_ARRAY_APPEND(list, el) PyList_Append(list, el)

/* I don't think incrref is needed with python */
#define CSONPATH_ARRAY_APPEND_INCREF(array, el) ({	\
      PyList_Append(array, el);				\
    })

static int pydict_try_setitemstring(PyObject *obj,  const char * const at, PyObject *el)
{
    if (!PyDict_Check(obj)) {
	PyErr_Format(PyExc_ValueError, "Unable to follow path (%s): Dict expected", at);
	return -1;
    }
    PyDict_SetItemString(obj, at, el);
    return 1;
}

static int python_set_or_insert_item(PyObject *array,  Py_ssize_t at, PyObject *el)
{
    if (!PyList_Check(array)) {
	PyErr_Format(PyExc_ValueError, "Unable to follow path: List expected");
	return -1;
    }
    Py_ssize_t s = PyList_Size(array);
    if (at >= s) {
	for (;s < at; ++s)
	    PyList_Insert(array, s, Py_None);

	PyList_Insert(array, at, el);
    } else {
	Py_INCREF(el);
	if (PyList_SetItem(array, at, el) < 0)
	  Py_DECREF(el);
    }
    return 1;
}

#define CSONPATH_APPEND_AT(array, at, el)			\
    _Generic((at),						\
	     int: python_set_or_insert_item,			\
	     unsigned int: python_set_or_insert_item,		\
	     long: python_set_or_insert_item,			\
	     unsigned long: python_set_or_insert_item,		\
	     long long: python_set_or_insert_item,		\
	     unsigned long long: python_set_or_insert_item,	\
	     const char *: pydict_try_setitemstring,		\
	     char *: pydict_try_setitemstring			\
	) (array, at, el)


#define CSONPATH_ARRAY_CLEAR(o) PyList_Clear(o)

#define CSONPATH_OBJ_CLEAR(o) PyDict_Clear(o)

#define CSONPATH_FOREACH_ARRAY(obj, child, idx)				\
    for (intptr_t array_len = PyList_Size(obj), idx = 0;		\
	 ({int r = idx < array_len; if (r) child = PyList_GetItem(obj, idx); r;}); ++idx)

#define CSONPATH_FOREACH_OBJ(obj, child, key)				\
    for (Py_ssize_t pos_ = 0; ({					\
		PyObject *key_;						\
		_Bool r = PyDict_Next(obj, &pos_, &key_, &child);	\
		if (r) key = PyUnicode_AsUTF8AndSize(key_, NULL);	\
		r;							\
	    });)

#define CSONPATH_FOREACH_EXT(obj, el, code, key_idx)			\
  if (PyDict_Check(obj)) {						\
    PyObject *key_;							\
    Py_ssize_t pos_ = 0;						\
    while (PyDict_Next(obj, &pos_, &key_, &el)) {			\
      const char *key_idx = PyUnicode_AsUTF8AndSize(key_, NULL);	\
      (void)key_idx;							\
      code								\
	}								\
  } else if (PyList_Check(obj)) {					\
    int array_len_ = PyList_Size(obj);					\
    for (intptr_t key_idx = 0; key_idx < array_len_; ++key_idx) {	\
      el = PyList_GetItem(obj, key_idx);				\
      code								\
	}								\
  }


static PyObject *csonpath_python_get(PyObject *obj, const char *key) {
    if (PyDict_Check(obj)) {
        PyObject *value = PyDict_GetItemString(obj, key);
        return value ? value : Py_None;
    }
    return Py_None;
}

static PyObject *csonpath_python_at(PyObject *obj, int at) {
    if (PyList_Check(obj)) {
        if (at >= 0 && at < PyList_Size(obj)) {
            PyObject *item = PyList_GetItem(obj, at);
            return item ? item : Py_None;
        }
    }
    return Py_None;
}

#include "csonpath.h"

typedef struct {
    PyObject_HEAD
    struct csonpath *cp;
} PyCsonPathObject;

#define CAPSULE_NAME "csonpath_capsule"

#define BAD_ARG() ({fprintf(stderr, "bad argument\n"); PyErr_BadArgument(); return NULL;})


static PyObject *PyCsonPath_new(PyTypeObject *subtype, PyObject* args,
				PyObject* dont_care)
{
  PyCsonPathObject *self = (PyCsonPathObject *)subtype->tp_alloc(subtype, 0);
  const char *s;

  if (!self)
    BAD_ARG();

  if (!PyArg_ParseTuple(args, "s", &s))
    BAD_ARG();

  struct csonpath *ret = malloc(sizeof *ret);
  if (!self)
    return PyErr_NoMemory();

  if (csonpath_init(ret, s) < 0)
    return PyErr_NoMemory();

  if (csonpath_compile(ret) < 0) {
    char *error = ret->compile_error;
    PyErr_Format(PyExc_ValueError, "compilation fail %s", error ? error : "(unknow error)");
    csonpath_destroy(ret);
    return NULL;
  }
  self->cp = ret;

  return (PyObject *)self;
}

static PyObject *find_all(PyCsonPathObject *self, PyObject* args)
{
    PyObject *json;

    if (!PyArg_ParseTuple(args, "O", &json))
	BAD_ARG();
    PyObject *ret = csonpath_find_all(self->cp, json);
    return ret;
}

static PyObject *find_first(PyCsonPathObject *self, PyObject* args)
{
    PyObject *json;

    if (!PyArg_ParseTuple(args, "O", &json))
	BAD_ARG();
    PyObject *ret = csonpath_find_first(self->cp, json);
    Py_INCREF(ret);
    return ret;
}

static PyObject *print_instructions(PyCsonPathObject *self, PyObject *args, PyObject *kwds)
{
    csonpath_print_instruction(self->cp);
    return Py_None;
}

static PyObject *callback(PyCsonPathObject *self, PyObject* args)
{
    PyObject *json, *callback, *udata = Py_None;

    if (!PyArg_ParseTuple(args, "OO|O", &json, &callback, &udata))
	BAD_ARG();
    int ret = csonpath_callback(self->cp, json, callback, udata);
    return PyLong_FromLong(ret);
}

static PyObject *do_remove(PyCsonPathObject *self, PyObject* args)
{
  PyObject *json;

  if (!PyArg_ParseTuple(args, "O", &json))
    BAD_ARG();
  int ret = csonpath_remove(self->cp, json);
  return PyLong_FromLong(ret);
}

static PyObject *update_or_create(PyCsonPathObject *self, PyObject* args)
{
  PyObject *json;
  PyObject *value;

  if (!PyArg_ParseTuple(args, "OO", &json, &value))
    BAD_ARG();
  int ret = csonpath_update_or_create(self->cp, json, value);
  if (ret < 0)
      return NULL;
  return PyLong_FromLong(ret);
}

static PyObject *update_or_create_callback(PyCsonPathObject *self, PyObject* args)
{
    PyObject *json, *callback, *udata = Py_None;

    if (!PyArg_ParseTuple(args, "OO|O", &json, &callback, &udata))
	BAD_ARG();
    int ret = csonpath_update_or_create_callback(self->cp, json, callback, udata);
    return PyLong_FromLong(ret);
}

static void PyCsonPath_dealloc(PyCsonPathObject *self) {
  if (self->cp) {
    csonpath_destroy(self->cp);
    free(self->cp);
  }
  Py_TYPE(self)->tp_free((PyObject *)self);
}


static PyObject *PyCsonPath_set_path(PyCsonPathObject *self, PyObject* args) {
    const char *new_path;
    if (!PyArg_ParseTuple(args, "s", &new_path))
      return Py_False;
    if (!new_path) return Py_False;

    csonpath_set_path(self->cp, new_path);
    return Py_True;
}

static PyMethodDef csonpath_py_method[] = {
    {"set_path", (PyCFunction)PyCsonPath_set_path, METH_VARARGS, "set_path"},
    {"callback", (PyCFunction)callback, METH_VARARGS, "callback"},
    {"print_instructions", (PyCFunction)print_instructions, METH_NOARGS, "print_instructions"},
    {"update_or_create_callback", (PyCFunction)update_or_create_callback, METH_VARARGS, "update_or_create_callback"},
    {"find_first", (PyCFunction)find_first, METH_VARARGS, "find first elems"},
    {"find_all", (PyCFunction)find_all, METH_VARARGS, "find all elems, if one found, pout it in an array"},
    {"remove", (PyCFunction)do_remove, METH_VARARGS, "remove all elems found"},
    {"update_or_create", (PyCFunction)update_or_create, METH_VARARGS, "update or create"},
    {NULL, NULL, 0, NULL}
};

static PyTypeObject PyCsonPathType = {
    PyVarObject_HEAD_INIT(NULL, 0)
    .tp_name = "csonpath.CsonPath",
    .tp_basicsize = sizeof(PyCsonPathObject),
    .tp_dealloc = (destructor)PyCsonPath_dealloc,
    .tp_flags = Py_TPFLAGS_DEFAULT,
    .tp_methods = csonpath_py_method,
    .tp_new = PyCsonPath_new
};

static struct PyModuleDef csonpath_py_mod = {
    PyModuleDef_HEAD_INIT,
    "csonpath",
    NULL,
    -1,
    NULL
};

PyMODINIT_FUNC PyInit_csonpath(void) {
  PyObject *m;
  if (PyType_Ready(&PyCsonPathType) < 0)
    return NULL;

  m = PyModule_Create(&csonpath_py_mod);
  if (!m) return NULL;

  PyModule_AddObject(m, "CsonPath", (PyObject *)&PyCsonPathType);

  return m;
}
