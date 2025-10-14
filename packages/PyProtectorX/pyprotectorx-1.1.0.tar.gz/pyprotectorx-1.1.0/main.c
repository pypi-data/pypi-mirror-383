/* PyProtectorX v1.1.0 - Ultimate Python Code Protection
 * 
 * Copyright (c) 2025 Zain Alkhalil (VIP). All Rights Reserved.
 * 
 * Website: https://pyprotector.netlify.app
 * GitHub: https://github.com/vipty1
 */

#include <Python.h>
#include <structmember.h>
#include <marshal.h>
#include <compile.h>
#include <string.h>

#define VERSION "1.1.0"
#define COPYRIGHT "PyProtectorX v1.1.0 - Copyright (c) 2025 Zain Alkhalil (VIP)"

// Platform detection
#if defined(__x86_64__) || defined(_M_X64)
    #define ARCH_NAME "x86-64"
#elif defined(__i386__) || defined(_M_IX86)
    #define ARCH_NAME "x86"
#elif defined(__aarch64__) || defined(_M_ARM64)
    #define ARCH_NAME "ARM64"
#elif defined(__arm__) || defined(_M_ARM)
    #define ARCH_NAME "ARM32"
#else
    #define ARCH_NAME "Generic"
#endif

#if defined(_WIN32) || defined(_WIN64)
    #define OS_NAME "Windows"
#elif defined(__linux__)
    #define OS_NAME "Linux"
#elif defined(__APPLE__)
    #define OS_NAME "macOS"
#else
    #define OS_NAME "Unknown"
#endif

// Watermark
#define WATERMARK_SIZE 13
static const unsigned char WATERMARK[] = "pyprotectorx";

// Magic seeds
#define SEED1 0x50795078
#define SEED2 0x58746563
#define SEED3 0x746F7230
#define SEED4 0x33303030

// XorShift128 PRNG
static unsigned int xorshift128(unsigned int* state) {
    unsigned int t = state[3];
    t ^= t << 11;
    t ^= t >> 8;
    state[3] = state[2]; state[2] = state[1]; state[1] = state[0];
    state[0] = state[0] ^ (state[0] >> 19) ^ t ^ (t >> 8);
    return state[0];
}

// Generate key
static PyObject* gen_key(const char* seed, Py_ssize_t len, unsigned int salt) {
    unsigned char* key = (unsigned char*)PyMem_Malloc(len);
    if (!key) return PyErr_NoMemory();
    
    size_t seed_len = strlen(seed);
    unsigned int st[4] = {salt ^ SEED1, salt ^ SEED2, salt ^ SEED3, salt ^ SEED4};
    
    for (Py_ssize_t i = 0; i < len; i++) {
        unsigned int r = xorshift128(st);
        key[i] = seed[i % seed_len] ^ (r >> 8) ^ (r >> 16) ^ (r >> 24) ^ 
                 WATERMARK[i % WATERMARK_SIZE] ^ ((i * 0x79) & 0xFF);
    }
    
    PyObject* res = PyBytes_FromStringAndSize((char*)key, len);
    memset(key, 0, len);
    PyMem_Free(key);
    return res;
}

// Multi-layer encryption
static PyObject* encrypt(PyObject* self, PyObject* args) {
    Py_buffer data_buf, key_buf;
    if (!PyArg_ParseTuple(args, "y*y*", &data_buf, &key_buf)) return NULL;
    
    if (key_buf.len == 0) {
        PyErr_SetString(PyExc_ValueError, "Invalid key");
        PyBuffer_Release(&data_buf);
        PyBuffer_Release(&key_buf);
        return NULL;
    }
    
    unsigned char* res = (unsigned char*)PyMem_Malloc(data_buf.len);
    if (!res) {
        PyBuffer_Release(&data_buf);
        PyBuffer_Release(&key_buf);
        return PyErr_NoMemory();
    }
    
    unsigned char* data = (unsigned char*)data_buf.buf;
    unsigned char* key = (unsigned char*)key_buf.buf;
    unsigned int st[4] = {SEED1, SEED2, SEED3, SEED4};
    
    // Layer 1: XOR with key
    for (Py_ssize_t i = 0; i < data_buf.len; i++)
        res[i] = data[i] ^ key[i % key_buf.len];
    
    // Layer 2: PRNG stream
    for (Py_ssize_t i = 0; i < data_buf.len; i++) {
        if (i % 16 == 0) {
            unsigned int r = xorshift128(st);
            res[i] ^= (r >> 8) & 0xFF;
        } else {
            res[i] ^= (st[0] >> ((i % 4) * 8)) & 0xFF;
        }
    }
    
    // Layer 3: Watermark
    for (Py_ssize_t i = 0; i < data_buf.len; i++)
        res[i] ^= WATERMARK[i % WATERMARK_SIZE];
    
    // Layer 4: Position
    for (Py_ssize_t i = 0; i < data_buf.len; i++)
        res[i] ^= (i * 0x79) & 0xFF;
    
    PyObject* result = PyBytes_FromStringAndSize((char*)res, data_buf.len);
    memset(res, 0, data_buf.len);
    PyMem_Free(res);
    PyBuffer_Release(&data_buf);
    PyBuffer_Release(&key_buf);
    return result;
}

// Compression
static PyObject* compress(PyObject* self, PyObject* args) {
    PyObject *data, *zlib, *func, *level, *result;
    if (!PyArg_ParseTuple(args, "O", &data)) return NULL;
    
    zlib = PyImport_ImportModule("zlib");
    if (!zlib) return NULL;
    func = PyObject_GetAttrString(zlib, "compress");
    Py_DECREF(zlib);
    if (!func) return NULL;
    
    level = PyLong_FromLong(9);
    result = PyObject_CallFunctionObjArgs(func, data, level, NULL);
    Py_DECREF(func);
    Py_DECREF(level);
    return result;
}

static PyObject* decompress(PyObject* self, PyObject* args) {
    PyObject *data, *zlib, *func, *result;
    if (!PyArg_ParseTuple(args, "O", &data)) return NULL;
    
    zlib = PyImport_ImportModule("zlib");
    if (!zlib) return NULL;
    func = PyObject_GetAttrString(zlib, "decompress");
    Py_DECREF(zlib);
    if (!func) return NULL;
    
    result = PyObject_CallFunctionObjArgs(func, data, NULL);
    Py_DECREF(func);
    return result;
}

// Dumps
static PyObject* dumps(PyObject* self, PyObject* args) {
    const char* src;
    if (!PyArg_ParseTuple(args, "s", &src)) return NULL;
    
    PyObject *compiled = Py_CompileString(src, "<pyprotectorx>", Py_file_input);
    if (!compiled) return NULL;
    
    PyObject *marshaled = PyMarshal_WriteObjectToString(compiled, Py_MARSHAL_VERSION);
    Py_DECREF(compiled);
    if (!marshaled) return NULL;
    
    PyObject *compressed = compress(NULL, Py_BuildValue("(O)", marshaled));
    Py_DECREF(marshaled);
    if (!compressed) return NULL;
    
    unsigned int salt = SEED2 ^ SEED3 ^ 0xDEADBEEF;
    PyObject *key = gen_key("PyProtectorX_2025", PyBytes_GET_SIZE(compressed), salt);
    if (!key) {
        Py_DECREF(compressed);
        return NULL;
    }
    
    PyObject *encrypted = encrypt(NULL, Py_BuildValue("(OO)", compressed, key));
    Py_DECREF(compressed);
    Py_DECREF(key);
    if (!encrypted) return NULL;
    
    PyObject *base64 = PyImport_ImportModule("base64");
    if (!base64) {
        Py_DECREF(encrypted);
        return NULL;
    }
    PyObject *b64func = PyObject_GetAttrString(base64, "b64encode");
    Py_DECREF(base64);
    if (!b64func) {
        Py_DECREF(encrypted);
        return NULL;
    }
    
    PyObject *encoded = PyObject_CallFunctionObjArgs(b64func, encrypted, NULL);
    Py_DECREF(b64func);
    Py_DECREF(encrypted);
    return encoded;
}

// Loads
static PyObject* loads(PyObject* self, PyObject* args) {
    PyObject *encoded;
    if (!PyArg_ParseTuple(args, "O", &encoded)) return NULL;
    
    PyObject *base64 = PyImport_ImportModule("base64");
    if (!base64) return NULL;
    PyObject *b64func = PyObject_GetAttrString(base64, "b64decode");
    Py_DECREF(base64);
    if (!b64func) return NULL;
    
    PyObject *encrypted = PyObject_CallFunctionObjArgs(b64func, encoded, NULL);
    Py_DECREF(b64func);
    if (!encrypted) return NULL;
    
    unsigned int salt = SEED2 ^ SEED3 ^ 0xDEADBEEF;
    PyObject *key = gen_key("PyProtectorX_2025", PyBytes_GET_SIZE(encrypted), salt);
    if (!key) {
        Py_DECREF(encrypted);
        return NULL;
    }
    
    PyObject *decrypted = encrypt(NULL, Py_BuildValue("(OO)", encrypted, key));
    Py_DECREF(encrypted);
    Py_DECREF(key);
    if (!decrypted) return NULL;
    
    PyObject *decompressed = decompress(NULL, Py_BuildValue("(O)", decrypted));
    Py_DECREF(decrypted);
    if (!decompressed) return NULL;
    
    PyObject *code_obj = PyMarshal_ReadObjectFromString(
        PyBytes_AS_STRING(decompressed), PyBytes_GET_SIZE(decompressed));
    Py_DECREF(decompressed);
    return code_obj;
}

// Run
static PyObject* run(PyObject* self, PyObject* args) {
    PyObject *encoded;
    if (!PyArg_ParseTuple(args, "O", &encoded)) return NULL;
    
    PyObject *code = loads(NULL, Py_BuildValue("(O)", encoded));
    if (!code) return NULL;
    
    PyObject *main = PyImport_AddModule("__main__");
    if (!main) {
        Py_DECREF(code);
        return NULL;
    }
    
    PyObject *dict = PyModule_GetDict(main);
    if (!dict) {
        Py_DECREF(code);
        return NULL;
    }
    
    PyObject *result = PyEval_EvalCode(code, dict, dict);
    Py_DECREF(code);
    return result;
}

// System info
static PyObject* get_info(PyObject* self, PyObject* args) {
    PyObject* info = PyDict_New();
    if (!info) return NULL;
    
    PyDict_SetItemString(info, "version", PyUnicode_FromString(VERSION));
    PyDict_SetItemString(info, "architecture", PyUnicode_FromString(ARCH_NAME));
    PyDict_SetItemString(info, "os", PyUnicode_FromString(OS_NAME));
    PyDict_SetItemString(info, "is_64bit", PyBool_FromLong(sizeof(void*) == 8));
    
    return info;
}

// Methods
static PyMethodDef methods[] = {
    {"dumps", dumps, METH_VARARGS, "Encrypt Python code"},
    {"loads", loads, METH_VARARGS, "Decrypt Python code"},
    {"Run", run, METH_VARARGS, "Execute encrypted code"},
    {"get_system_info", get_info, METH_NOARGS, "Get system info"},
    {"compress", compress, METH_VARARGS, "Compress data"},
    {"decompress", decompress, METH_VARARGS, "Decompress data"},
    {NULL, NULL, 0, NULL}
};

// Module
static struct PyModuleDef module = {
    PyModuleDef_HEAD_INIT,
    "PyProtectorX",
    COPYRIGHT,
    -1,
    methods
};

// Init
PyMODINIT_FUNC PyInit_PyProtectorX(void) {
    PyObject* m = PyModule_Create(&module);
    if (!m) return NULL;
    
    PyModule_AddStringConstant(m, "__version__", VERSION);
    PyModule_AddStringConstant(m, "__copyright__", COPYRIGHT);
    PyModule_AddStringConstant(m, "__author__", "PyProtectorX Team");
    PyModule_AddStringConstant(m, "__website__", "https://pyprotectorx.netlify.app");
    
    return m;
}