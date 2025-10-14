// Aiofiles-X
// Copyright (C) 2025 ohmyarthur
//
// This file is part of <https://github.com/ohmyarthur/aiofiles-x/>
// Please read the GNU Affero General Public License in
// <https://github.com/ohmyarthur/aiofiles-x/blob/master/LICENSE/>.

#include <pybind11/functional.h>
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

#include "../core/async_file.hpp"

namespace py = pybind11;

// Python-friendly async file wrapper
class PyAsyncFile {
 public:
  PyAsyncFile(const std::string& filename, const std::string& mode)
      : file_(filename, mode),
        opened_(false),
        binary_(mode.find('b') != std::string::npos) {}

  py::object enter() {
    // This will be called by __aenter__
    return py::cast(this);
  }

  void exit(py::object exc_type, py::object exc_val, py::object exc_tb) {
    // This will be called by __aexit__
    if (opened_) {
      file_.close();  // Direct synchronous call
    }
  }

  py::object open_async() {
    try {
      file_.open();  // Direct synchronous call
      opened_ = true;
      return py::cast(this);
    } catch (const std::runtime_error& e) {
      std::string msg = e.what();
      // Convert C++ exceptions to appropriate Python exceptions
      if (msg.find("Failed to open file") != std::string::npos) {
        if (msg.find("No such file") != std::string::npos ||
            msg.find("cannot open") != std::string::npos) {
          throw py::value_error(msg);  // Will be caught as FileNotFoundError
        } else if (msg.find("Permission denied") != std::string::npos) {
          throw py::value_error(msg);  // Will be caught as PermissionError
        }
      }
      throw;
    }
  }

  py::object close_async() {
    file_.close();  // Direct synchronous call
    opened_ = false;
    return py::none();
  }

  py::object read_async(py::object size = py::none()) {
    std::optional<size_t> read_size;
    if (!size.is_none()) {
      read_size = size.cast<size_t>();
    }
    std::string data = file_.read(read_size);

    if (binary_) {
      return py::bytes(data);
    } else {
      return py::cast(data);
    }
  }

  py::object readall_async() {
    std::string data = file_.readall();
    if (binary_) {
      return py::bytes(data);
    } else {
      return py::cast(data);
    }
  }

  py::object read1_async(py::object size = py::none()) {
    std::optional<size_t> read_size;
    if (!size.is_none()) {
      read_size = size.cast<size_t>();
    }
    std::string data = file_.read1(read_size);
    if (binary_) {
      return py::bytes(data);
    } else {
      return py::cast(data);
    }
  }

  py::object readinto_async(py::object buffer) {
    if (!py::isinstance<py::buffer>(buffer)) {
      throw py::type_error("readinto requires a buffer object");
    }

    py::buffer_info info = buffer.cast<py::buffer>().request();
    std::vector<char> temp_buffer(info.size);
    size_t bytes_read = file_.readinto(temp_buffer);

    std::memcpy(info.ptr, temp_buffer.data(), bytes_read);
    return py::cast(bytes_read);
  }

  py::object readline_async(py::object size = py::none()) {
    std::optional<size_t> read_size;
    if (!size.is_none()) {
      read_size = size.cast<size_t>();
    }
    return py::cast(file_.readline(read_size));  // Direct sync call
  }

  py::object readlines_async(py::object hint = py::none()) {
    std::optional<size_t> hint_size;
    if (!hint.is_none()) {
      hint_size = hint.cast<size_t>();
    }
    return py::cast(file_.readlines(hint_size));  // Direct sync call
  }

  py::object write_async(py::object data) {
    std::string str_data;

    // Handle both bytes and string input
    if (py::isinstance<py::bytes>(data)) {
      str_data = data.cast<std::string>();
    } else if (py::isinstance<py::str>(data)) {
      str_data = data.cast<std::string>();
    } else {
      str_data = py::str(data).cast<std::string>();
    }

    return py::cast(file_.write(str_data));  // Direct sync call
  }

  py::object writelines_async(const std::vector<std::string>& lines) {
    file_.writelines(lines);  // Direct sync call
    return py::none();
  }

  py::object seek_async(long offset, int whence = 0) {
    return py::cast(file_.seek(offset, whence));  // Direct sync call
  }

  py::object tell_async() {
    return py::cast(file_.tell());  // Direct sync call
  }

  py::object flush_async() {
    file_.flush();  // Direct sync call
    return py::none();
  }

  py::object truncate_async(py::object size = py::none()) {
    std::optional<size_t> truncate_size;
    if (!size.is_none()) {
      truncate_size = size.cast<size_t>();
    }
    file_.truncate(truncate_size);  // Direct sync call
    return py::none();
  }

  py::object isatty_async() {
    return py::cast(file_.isatty());  // Direct sync call
  }

  bool seekable() const { return file_.seekable(); }

  bool writable() const { return file_.writable(); }

  const std::string& name() const { return file_.filename(); }

  const std::string& mode() const { return file_.mode(); }

  // Iterator support
  py::object iter() { return py::cast(this); }

  py::object next() {
    std::string line = file_.readline();  // Direct sync call
    if (line.empty()) {
      throw py::stop_iteration();
    }
    return py::cast(line);
  }

 private:
  aiofiles::AsyncFile file_;
  bool opened_;
  bool binary_;
};

PYBIND11_MODULE(_aiofiles_core, m) {
  m.doc() = "High-performance async file I/O for Python (C++ backend)";

  py::class_<PyAsyncFile>(m, "AsyncFile")
      .def(py::init<const std::string&, const std::string&>(),
           py::arg("filename"), py::arg("mode") = "r")
      .def("__aenter__", &PyAsyncFile::enter)
      .def("__aexit__", &PyAsyncFile::exit)
      .def("__enter__", &PyAsyncFile::enter)
      .def("__exit__", &PyAsyncFile::exit)
      .def("open", &PyAsyncFile::open_async)
      .def("close", &PyAsyncFile::close_async)
      .def("read", &PyAsyncFile::read_async, py::arg("size") = py::none())
      .def("readall", &PyAsyncFile::readall_async)
      .def("read1", &PyAsyncFile::read1_async, py::arg("size") = py::none())
      .def("readinto", &PyAsyncFile::readinto_async, py::arg("buffer"))
      .def("readline", &PyAsyncFile::readline_async,
           py::arg("size") = py::none())
      .def("readlines", &PyAsyncFile::readlines_async,
           py::arg("hint") = py::none())
      .def("write", &PyAsyncFile::write_async, py::arg("data"))
      .def("writelines", &PyAsyncFile::writelines_async, py::arg("lines"))
      .def("seek", &PyAsyncFile::seek_async, py::arg("offset"),
           py::arg("whence") = 0)
      .def("tell", &PyAsyncFile::tell_async)
      .def("flush", &PyAsyncFile::flush_async)
      .def("truncate", &PyAsyncFile::truncate_async,
           py::arg("size") = py::none())
      .def("isatty", &PyAsyncFile::isatty_async)
      .def("seekable", &PyAsyncFile::seekable)
      .def("writable", &PyAsyncFile::writable)
      .def("__iter__", &PyAsyncFile::iter)
      .def("__next__", &PyAsyncFile::next)
      .def("__aiter__", &PyAsyncFile::iter)
      .def("__anext__", &PyAsyncFile::next)
      .def_property_readonly("name", &PyAsyncFile::name)
      .def_property_readonly("mode", &PyAsyncFile::mode);
}
