#define PY_SSIZE_T_CLEAN
#include <Python.h>

#include <libgetargv.h>
#include <stdbool.h>

static PyObject *GetargvError;

static PyObject *getargv_as_bytes(PyObject *self, PyObject *args) {
  pid_t pid;
  uint32_t skip = 0;
  bool nuls = false;

  if (!PyArg_ParseTuple(args, "i|Ip", &pid, &skip, &nuls)) {
    return NULL;
  }

  struct GetArgvOptions options = {.pid = pid, .nuls = nuls, .skip = skip};

  struct ArgvResult result;

  if (!get_argv_of_pid(&options, &result)) {
    PyErr_SetFromErrno(GetargvError);
    return NULL;
  }

  // When memory buffers are passed as parameters to supply data to build
  // objects, as for the y# format, the required data is copied. Buffers
  // provided by the caller are never referenced by the objects created by
  // Py_BuildValue(). In other words, if your code invokes malloc() and passes
  // the allocated memory to Py_BuildValue(), your code is responsible for
  // calling free() for that memory once Py_BuildValue() returns.

  PyObject *s = Py_BuildValue("y#", result.start_pointer,
                              result.end_pointer - result.start_pointer + 1);
  free_ArgvResult(&result);

  return s; // handles s == NULL implicitly
}

static PyObject *getargv_as_list(PyObject *self, PyObject *args) {
  pid_t pid;

  if (!PyArg_ParseTuple(args, "i", &pid)) {
    return NULL;
  }

  struct ArgvArgcResult result;

  if (!get_argv_and_argc_of_pid(pid, &result)) {
    PyErr_SetFromErrno(GetargvError);
    return NULL;
  }

  // When memory buffers are passed as parameters to supply data to build
  // objects, as for the y format, the required data is copied. Buffers
  // provided by the caller are never referenced by the objects created by
  // Py_BuildValue(). In other words, if your code invokes malloc() and passes
  // the allocated memory to Py_BuildValue(), your code is responsible for
  // calling free() for that memory once Py_BuildValue() returns.

  PyObject *lst = PyList_New(result.argc);
  if (lst) {
    for (size_t i = 0; i < result.argc; i++) {
      PyObject *s = Py_BuildValue("y", result.argv[i]);
      if (s) {
        PyList_SET_ITEM(lst, i, s); // s now owned by lst
      } else {
        Py_DECREF(lst); // releases owned elements too
        break;
      }
    }
  }

  free_ArgvArgcResult(&result);

  return lst; // handles lst == NULL implicitly
}

static PyMethodDef GetargvMethods[] = {
    {"as_bytes", getargv_as_bytes, METH_VARARGS,
     "Returns the arguments of a pid as a bytes object.\n\
\n\
            Parameters:\n\
                    pid (int): An integer PID\n\
                    skip (int): How many leading arguments to skip past\n\
                    nuls (bool): Whether to convert nuls to spaces for human readability\n\
\n\
            Returns:\n\
                    args (bytes): Binary string of the PID's args\n\
"},
    {
        "as_list", getargv_as_list, METH_VARARGS,
        "Returns the arguments of a pid as an list of bytes objects.\n\
\n\
            Parameters:\n\
                    pid (int): An integer PID\n\
\n\
            Returns:\n\
                    args (list[bytes]): List of the PID's args as binary strings\n\
"},
    {NULL, NULL, 0, NULL} /* Sentinel */
};

static struct PyModuleDef _getargvmodule = {
    PyModuleDef_HEAD_INIT,
    "_getargv", /* name of module */
    "Obtain binary string representations of the arguments of other PIDs.\n\
\n\
On macOS you must use the KERN_PROCARGS2 sysctl to obtain other procs' args,\n\
however the returned representation is badly documented and a naive approach\n\
doesn't deal with leading empty args. libgetargv parses the results of the\n\
sysctl correctly, and this module provides Python bindings to libgetargv.\n\
\n\
Classes:\n\
\n\
    error\n\
\n\
Functions:\n\
\n\
    as_bytes(pid, skip, nuls) -> bytes\n\
    as_list(pid) -> list[bytes]\n\
",
    -1, // size of per-interpreter state of the module, or -1 if the module keeps state in global variables. (our GetargvError is a global variable I think, though that might just be the definition).
    GetargvMethods};

PyMODINIT_FUNC PyInit__getargv(void) {
  PyObject *m = PyModule_Create(&_getargvmodule);

  if (m == NULL)
    return NULL;

  GetargvError = PyErr_NewException("_getargv.error", NULL, NULL);
  Py_XINCREF(GetargvError);
  if (PyModule_AddObject(m, "error", GetargvError) < 0) {
    Py_XDECREF(GetargvError);
    Py_CLEAR(GetargvError);
    Py_DECREF(m);
    return NULL;
  }

  return m;
}
