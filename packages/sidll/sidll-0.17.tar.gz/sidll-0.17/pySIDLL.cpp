#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <pybind11/stl_bind.h>
#include <variant>
#include "SIDLL.h"

namespace py = pybind11;

using MyVariant = variant<int, double, long, const char*, string, tuple<int, int>, tuple<int, int, int>, tuple<double, double>, tuple<double, double, double>, tuple<std::string, std::string>, tuple <std::string, std::string, std::string>>;

PYBIND11_MODULE(sidll,m) {
	
	py::class_<SIDLL>(m, "SIDLL")
		.def(py::init<>())
		.def("getLength", &SIDLL::getLength)
		.def("insertNode", &SIDLL::insertNode, py::call_guard<py::gil_scoped_release>())
		.def("deleteNode", &SIDLL::deleteNode, py::call_guard<py::gil_scoped_release>())
		.def("keyExists", &SIDLL::keyExists, py::call_guard<py::gil_scoped_release>())
		.def("getValue", &SIDLL::getValue, py::arg("key"), py::arg("relativeIndex") = 0, py::call_guard<py::gil_scoped_release>())
		.def("_insert", &SIDLL::_insert, py::call_guard<py::gil_scoped_release>())
		.def("_delete", &SIDLL::_delete, py::call_guard<py::gil_scoped_release>())
		.def("_findNode", &SIDLL::_findNode, py::call_guard<py::gil_scoped_release>())
		.def("_findNodeFromHead", &SIDLL::_findNodeFromHead, py::call_guard<py::gil_scoped_release>())
		.def("_findPointer", &SIDLL::_findPointer, py::call_guard<py::gil_scoped_release>())
		.def("_insertPointer", &SIDLL::_insertPointer, py::call_guard<py::gil_scoped_release>())
		.def("_insertPointerInBetween", &SIDLL::_insertPointerInBetween, py::call_guard<py::gil_scoped_release>())
		.def("_deletePointerWithCheck", &SIDLL::_deletePointerWithCheck, py::call_guard<py::gil_scoped_release>())
		.def("_repointPointer", &SIDLL::_repointPointer, py::call_guard<py::gil_scoped_release>())
		.def("setInterpointerDistance", &SIDLL::setInterpointerDistance)
		.def("head",&SIDLL::head, py::arg("len") = 10, py::call_guard<py::gil_scoped_release>())
		.def("tail", &SIDLL::tail, py::arg("len") = 10, py::call_guard<py::gil_scoped_release>())
		.def("getMaxKey", &SIDLL::getMaxKey)
		.def("getMinKey", &SIDLL::getMinKey)
		.def("getMean", &SIDLL::getMean)
		.def("getMedian", &SIDLL::getMedian, py::call_guard<py::gil_scoped_release>())
		.def("setVerbosity", &SIDLL::setVerborsity);
}