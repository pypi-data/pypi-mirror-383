/*
 * Copyright (c) 2025, Alexander Kirchhoff
 *
 * Redistribution and use in source and binary forms, with or without
 * modification, are permitted provided that the following conditions are met:
 *
 * 1. Redistributions of source code must retain the above copyright notice,
 *    this list of conditions and the following disclaimer.
 *
 * 2. Redistributions in binary form must reproduce the above copyright notice,
 *    this list of conditions and the following disclaimer in the documentation
 *    and/or other materials provided with the distribution.
 *
 * 3. Neither the name of the copyright holder nor the names of its
 *    contributors may be used to endorse or promote products derived from
 *    this software without specific prior written permission.
 *
 * THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
 * AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
 * IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
 * ARE DISCLAIMED.  IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
 * LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
 * CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
 * SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
 * INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
 * CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
 * ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
 * POSSIBILITY OF SUCH DAMAGE.
*/
/* SPDX-License-Identifier: BSD-3-Clause */

#include <Python.h>

#define WHITE_DECL static
#include "white.c"

typedef struct WhiteObject {
	PyObject_HEAD
	struct white_state white_state;
} WhiteObject;

static PyObject *White_new(PyTypeObject *type, PyObject *args, PyObject *kwds) {
	WhiteObject *self;
	self = (WhiteObject *) type->tp_alloc(type, 0);
	if (self != NULL) {
		white_init(&self->white_state);
	}
	return (PyObject *) self;
}

static PyObject *White_feed(WhiteObject *self, PyObject *data) {
	Py_buffer view;
	if (PyObject_GetBuffer(data, &view, PyBUF_SIMPLE) == -1)
		return NULL;
	if (view.len > UINT32_MAX) {
		PyBuffer_Release(&view);
		PyErr_SetString(PyExc_OverflowError, "Data too long");
		return NULL;
	}
	const uint8_t *start = view.buf;
	const uint8_t *result = white_step(
		&self->white_state, start, (uint32_t) view.len);
	size_t offset = result == NULL ? 0 : result - start;
	PyBuffer_Release(&view);
	if (result == NULL) {
		white_init(&self->white_state);
		PyErr_SetString(PyExc_ValueError, "Invalid MessagePack message");
		return NULL;
	}
	if (white_done(&self->white_state)) {
		white_init(&self->white_state);
		return PyLong_FromSize_t(offset);
	}
	Py_RETURN_NONE;
}

static PyMethodDef White_methods[] = {
	{"feed", (PyCFunction) White_feed, METH_O, NULL},
	{NULL}
};

static PyTypeObject WhiteType = {
	PyVarObject_HEAD_INIT(NULL, 0)
	.tp_name = "_white.White",
	.tp_basicsize = sizeof(WhiteObject),
	.tp_flags = Py_TPFLAGS_DEFAULT,
	.tp_new = White_new,
	.tp_methods = White_methods,
};

static struct PyModuleDef whitemodule = {
	PyModuleDef_HEAD_INIT,
	"_white",
	NULL,
	-1
};

PyMODINIT_FUNC PyInit__white(void) {
	if (PyType_Ready(&WhiteType) == -1) return NULL;
	PyObject *m = PyModule_Create(&whitemodule);
	if (m == NULL) return NULL;
	Py_INCREF(&WhiteType);
	if (PyModule_AddObject(m, "White", (PyObject *) &WhiteType) == -1) {
		Py_DECREF(&WhiteType);
		Py_DECREF(m);
		return NULL;
	}
	return m;
}
