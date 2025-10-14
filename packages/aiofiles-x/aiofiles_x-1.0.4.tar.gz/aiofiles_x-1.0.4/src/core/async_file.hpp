// Aiofiles-X - Optimized Version
// Copyright (C) 2025 ohmyarthur
//
// This file is part of <https://github.com/ohmyarthur/aiofiles-x/>
// Please read the GNU Affero General Public License in
// <https://github.com/ohmyarthur/aiofiles-x/blob/master/LICENSE/>.

#pragma once

#include <coroutine>
#include <cstdio>
#include <cstring>
#ifndef _WIN32
#include <unistd.h>
#endif
#include <memory>
#include <optional>
#include <stdexcept>
#include <string>
#include <vector>

namespace aiofiles {

constexpr size_t DEFAULT_READ_BUFFER_SIZE = 256 * 1024;
constexpr size_t DEFAULT_WRITE_BUFFER_SIZE = 256 * 1024;
constexpr size_t DEFAULT_LINE_BUFFER_SIZE = 256 * 1024;
constexpr size_t DEFAULT_LINE_RESERVE = 1024;

template <typename T>
class Task {
 public:
  struct promise_type {
    T value_;
    std::exception_ptr exception_;

    Task<T> get_return_object() {
      return Task<T>{std::coroutine_handle<promise_type>::from_promise(*this)};
    }

    std::suspend_never initial_suspend() { return {}; }
    std::suspend_always final_suspend() noexcept { return {}; }

    void return_value(T value) { value_ = std::move(value); }

    void unhandled_exception() { exception_ = std::current_exception(); }
  };

  explicit Task(std::coroutine_handle<promise_type> handle) : handle_(handle) {}

  ~Task() {
    if (handle_) handle_.destroy();
  }

  Task(Task&& other) noexcept : handle_(other.handle_) {
    other.handle_ = nullptr;
  }

  Task& operator=(Task&& other) noexcept {
    if (this != &other) {
      if (handle_) handle_.destroy();
      handle_ = other.handle_;
      other.handle_ = nullptr;
    }
    return *this;
  }

  Task(const Task&) = delete;
  Task& operator=(const Task&) = delete;

  T get() {
    if (!handle_.done()) {
      handle_.resume();
    }
    if (handle_.promise().exception_) {
      std::rethrow_exception(handle_.promise().exception_);
    }
    if constexpr (!std::is_void_v<T>) {
      return handle_.promise().value_;
    }
  }

  bool await_ready() { return handle_.done(); }
  void await_suspend(std::coroutine_handle<> awaiting) {}
  T await_resume() { return get(); }

 private:
  std::coroutine_handle<promise_type> handle_;
};

template <>
class Task<void> {
 public:
  struct promise_type {
    std::exception_ptr exception_;

    Task<void> get_return_object() {
      return Task<void>{
          std::coroutine_handle<promise_type>::from_promise(*this)};
    }

    std::suspend_never initial_suspend() { return {}; }
    std::suspend_always final_suspend() noexcept { return {}; }

    void return_void() {}

    void unhandled_exception() { exception_ = std::current_exception(); }
  };

  explicit Task(std::coroutine_handle<promise_type> handle) : handle_(handle) {}

  ~Task() {
    if (handle_) handle_.destroy();
  }

  Task(Task&& other) noexcept : handle_(other.handle_) {
    other.handle_ = nullptr;
  }

  Task& operator=(Task&& other) noexcept {
    if (this != &other) {
      if (handle_) handle_.destroy();
      handle_ = other.handle_;
      other.handle_ = nullptr;
    }
    return *this;
  }

  Task(const Task&) = delete;
  Task& operator=(const Task&) = delete;

  void get() {
    if (!handle_.done()) {
      handle_.resume();
    }
    if (handle_.promise().exception_) {
      std::rethrow_exception(handle_.promise().exception_);
    }
  }

  bool await_ready() { return handle_.done(); }
  void await_suspend(std::coroutine_handle<> awaiting) {}
  void await_resume() { return get(); }

 private:
  std::coroutine_handle<promise_type> handle_;
};

enum class FileMode {
  Read,
  Write,
  Append,
  ReadWrite,
  ReadWriteTruncate,
  ReadAppend
};

inline std::pair<FileMode, bool> parse_mode(const std::string& mode_str) {
  bool binary = mode_str.find('b') != std::string::npos;
  std::string mode = mode_str;
  mode.erase(std::remove(mode.begin(), mode.end(), 'b'), mode.end());
  mode.erase(std::remove(mode.begin(), mode.end(), '+'), mode.end());

  FileMode file_mode;
  if (mode == "r") {
    file_mode = mode_str.find('+') != std::string::npos ? FileMode::ReadWrite
                                                        : FileMode::Read;
  } else if (mode == "w") {
    file_mode = mode_str.find('+') != std::string::npos
                    ? FileMode::ReadWriteTruncate
                    : FileMode::Write;
  } else if (mode == "a") {
    file_mode = mode_str.find('+') != std::string::npos ? FileMode::ReadAppend
                                                        : FileMode::Append;
  } else {
    throw std::invalid_argument("Invalid file mode: " + mode_str);
  }

  return {file_mode, binary};
}

inline const char* mode_to_cstr(FileMode mode, bool binary) {
  switch (mode) {
    case FileMode::Read:
      return binary ? "rb" : "r";
    case FileMode::Write:
      return binary ? "wb" : "w";
    case FileMode::Append:
      return binary ? "ab" : "a";
    case FileMode::ReadWrite:
      return binary ? "r+b" : "r+";
    case FileMode::ReadWriteTruncate:
      return binary ? "w+b" : "w+";
    case FileMode::ReadAppend:
      return binary ? "a+b" : "a+";
    default:
      return binary ? "rb" : "r";
  }
}

class AsyncFile {
 public:
  AsyncFile() = default;

  AsyncFile(const std::string& filename, const std::string& mode)
      : filename_(filename), mode_str_(mode) {
    auto [file_mode, binary] = parse_mode(mode);
    mode_ = file_mode;
    binary_ = binary;
  }

  ~AsyncFile() {
    if (file_) {
      try {
        flush_write_buffer();
      } catch (...) {
      }
      fclose(file_);
    }
  }

  AsyncFile(const AsyncFile&) = delete;
  AsyncFile& operator=(const AsyncFile&) = delete;

  AsyncFile(AsyncFile&& other) noexcept
      : file_(other.file_),
        filename_(std::move(other.filename_)),
        mode_(other.mode_),
        binary_(other.binary_),
        mode_str_(std::move(other.mode_str_)),
        read_buffer_(std::move(other.read_buffer_)),
        write_buffer_(std::move(other.write_buffer_)),
        line_buffer_(std::move(other.line_buffer_)),
        write_buffer_pos_(other.write_buffer_pos_),
        line_buffer_pos_(other.line_buffer_pos_),
        line_buffer_size_(other.line_buffer_size_),
        line_buffer_eof_(other.line_buffer_eof_),
        file_size_cached_(other.file_size_cached_),
        file_size_(other.file_size_) {
    other.file_ = nullptr;
  }

  AsyncFile& operator=(AsyncFile&& other) noexcept {
    if (this != &other) {
      if (file_) {
        try {
          flush_write_buffer();
        } catch (...) {
        }
        fclose(file_);
      }
      file_ = other.file_;
      filename_ = std::move(other.filename_);
      mode_ = other.mode_;
      binary_ = other.binary_;
      mode_str_ = std::move(other.mode_str_);
      read_buffer_ = std::move(other.read_buffer_);
      write_buffer_ = std::move(other.write_buffer_);
      line_buffer_ = std::move(other.line_buffer_);
      write_buffer_pos_ = other.write_buffer_pos_;
      line_buffer_pos_ = other.line_buffer_pos_;
      line_buffer_size_ = other.line_buffer_size_;
      line_buffer_eof_ = other.line_buffer_eof_;
      file_size_cached_ = other.file_size_cached_;
      file_size_ = other.file_size_;
      other.file_ = nullptr;
    }
    return *this;
  }

  void open() {
    file_ = fopen(filename_.c_str(), mode_to_cstr(mode_, binary_));
    if (!file_) {
      throw std::runtime_error("Failed to open file: " + filename_ + " - " +
                               std::strerror(errno));
    }

    read_buffer_.reserve(DEFAULT_READ_BUFFER_SIZE);
    write_buffer_.reserve(DEFAULT_WRITE_BUFFER_SIZE);
    line_buffer_.reserve(DEFAULT_LINE_BUFFER_SIZE);

    write_buffer_pos_ = 0;
    line_buffer_pos_ = 0;
    line_buffer_size_ = 0;
    line_buffer_eof_ = false;
    file_size_cached_ = false;

    setvbuf(file_, nullptr, _IOFBF, 65536);
  }

  void close() {
    if (file_) {
      flush_write_buffer();

      if (fclose(file_) != 0) {
        throw std::runtime_error("Failed to close file: " + filename_);
      }
      file_ = nullptr;

      read_buffer_.clear();
      read_buffer_.shrink_to_fit();
      write_buffer_.clear();
      write_buffer_.shrink_to_fit();
      line_buffer_.clear();
      line_buffer_.shrink_to_fit();
    }
  }

  std::string read(std::optional<size_t> size = std::nullopt) {
    if (!file_) {
      throw std::runtime_error("File not open");
    }

    if (write_buffer_pos_ > 0) {
      flush_write_buffer();
    }

    if (size.has_value()) {
      size_t read_size = *size;
#ifdef _WIN32
      std::string result(read_size, '\0');
      size_t bytes_read = fread(result.data(), 1, read_size, file_);
      result.resize(bytes_read);
      return result;
#else
      if (read_size <= 8192) {
        if (read_buffer_.size() < read_size) {
          read_buffer_.resize(read_size);
        }
        int fd = fileno(file_);
        long current_pos = ftell(file_);
        ssize_t bytes_read =
            pread(fd, read_buffer_.data(), read_size, current_pos);
        if (bytes_read < 0) {
          throw std::runtime_error("pread failed");
        }
        fseek(file_, current_pos + bytes_read, SEEK_SET);
        return std::string(read_buffer_.data(), bytes_read);
      }
      std::string result(read_size, '\0');
      size_t bytes_read = fread(result.data(), 1, read_size, file_);
      result.resize(bytes_read);
      return result;
#endif
    } else {
      if (!file_size_cached_) {
        cache_file_size();
      }

      long current_pos = ftell(file_);
      size_t remaining = file_size_ - current_pos;

      if (remaining == 0) {
        return std::string();
      }

      std::string result(remaining, '\0');
      size_t bytes_read = fread(result.data(), 1, remaining, file_);
      result.resize(bytes_read);
      return result;
    }
  }

  std::string readall() { return read(std::nullopt); }

  std::string read1(std::optional<size_t> size = std::nullopt) {
    if (!file_) {
      throw std::runtime_error("File not open");
    }

    if (write_buffer_pos_ > 0) {
      flush_write_buffer();
    }

    size_t read_size = size.value_or(DEFAULT_READ_BUFFER_SIZE);
    std::string result(read_size, '\0');
    size_t bytes_read = fread(result.data(), 1, read_size, file_);
    result.resize(bytes_read);
    return result;
  }

  size_t readinto(std::vector<char>& buffer) {
    if (!file_) {
      throw std::runtime_error("File not open");
    }

    if (write_buffer_pos_ > 0) {
      flush_write_buffer();
    }

    if (buffer.empty()) {
      return 0;
    }

    size_t bytes_read = fread(buffer.data(), 1, buffer.size(), file_);
    return bytes_read;
  }

  std::string readline(std::optional<size_t> size = std::nullopt) {
    if (!file_) {
      throw std::runtime_error("File not open");
    }

    if (write_buffer_pos_ > 0) {
      flush_write_buffer();
    }

    std::string line;
    line.reserve(DEFAULT_LINE_RESERVE);
    size_t limit = size.value_or(SIZE_MAX);

    while (line.size() < limit) {
      if (line_buffer_pos_ >= line_buffer_size_) {
        if (!fill_line_buffer()) break;
      }

      char* start = line_buffer_.data() + line_buffer_pos_;
      size_t remaining = line_buffer_size_ - line_buffer_pos_;
      char* newline = static_cast<char*>(std::memchr(start, '\n', remaining));

      size_t chunk_size;
      if (newline) {
        chunk_size = newline - start + 1;
      } else {
        chunk_size = remaining;
      }

      if (line.size() + chunk_size > limit) {
        chunk_size = limit - line.size();
      }

      line.append(start, chunk_size);
      line_buffer_pos_ += chunk_size;

      if (newline || line.size() >= limit) break;
    }

    return line;
  }

  std::vector<std::string> readlines(
      std::optional<size_t> hint = std::nullopt) {
    if (!file_) {
      throw std::runtime_error("File not open");
    }

    if (write_buffer_pos_ > 0) {
      flush_write_buffer();
    }

    std::vector<std::string> lines;

    if (!file_size_cached_) {
      cache_file_size();
    }

    long current_pos = ftell(file_);
    size_t remaining = file_size_ - current_pos;

    if (remaining == 0) return lines;

    lines.reserve(remaining / 80);

    read_buffer_.resize(remaining);
    size_t bytes_read = fread(read_buffer_.data(), 1, remaining, file_);

    size_t start = 0;
    for (size_t i = 0; i < bytes_read; ++i) {
      if (read_buffer_[i] == '\n') {
        lines.emplace_back(read_buffer_.data() + start, i - start + 1);
        start = i + 1;
      }
    }

    if (start < bytes_read) {
      lines.emplace_back(read_buffer_.data() + start, bytes_read - start);
    }

    return lines;
  }
  size_t write(const std::string& data) {
    if (!file_) {
      throw std::runtime_error("File not open");
    }

    size_t data_size = data.size();

    if (data_size > DEFAULT_WRITE_BUFFER_SIZE / 2) {
      flush_write_buffer();
      size_t written = fwrite(data.c_str(), 1, data_size, file_);
      if (written != data_size) {
        throw std::runtime_error("Failed to write complete data");
      }
      return written;
    }

    if (write_buffer_pos_ + data_size > DEFAULT_WRITE_BUFFER_SIZE) {
      flush_write_buffer();
    }

    if (write_buffer_.size() < write_buffer_pos_ + data_size) {
      write_buffer_.resize(write_buffer_pos_ + data_size);
    }
    std::memcpy(write_buffer_.data() + write_buffer_pos_, data.c_str(),
                data_size);
    write_buffer_pos_ += data_size;

    return data_size;
  }

  void writelines(const std::vector<std::string>& lines) {
    if (!file_) {
      throw std::runtime_error("File not open");
    }

    size_t total_size = 0;
    for (const auto& line : lines) {
      total_size += line.size();
    }

    if (total_size > DEFAULT_WRITE_BUFFER_SIZE * 2) {
      for (const auto& line : lines) {
        write(line);
      }
      flush_write_buffer();
    } else {
      for (const auto& line : lines) {
        write(line);
      }
    }
  }

  long seek(long offset, int whence = SEEK_SET) {
    if (!file_) {
      throw std::runtime_error("File not open");
    }

    flush_write_buffer();

    if (fseek(file_, offset, whence) != 0) {
      throw std::runtime_error("Seek failed");
    }

    line_buffer_pos_ = 0;
    line_buffer_size_ = 0;
    file_size_cached_ = false;

    return ftell(file_);
  }

  long tell() {
    if (!file_) {
      throw std::runtime_error("File not open");
    }

    long pos = ftell(file_);
    if (pos == -1) {
      throw std::runtime_error("Tell failed");
    }

    return pos + write_buffer_pos_;
  }

  void flush() {
    if (!file_) {
      throw std::runtime_error("File not open");
    }

    flush_write_buffer();

    if (fflush(file_) != 0) {
      throw std::runtime_error("Flush failed");
    }
  }

  void truncate(std::optional<size_t> size = std::nullopt) {
    if (!file_) {
      throw std::runtime_error("File not open");
    }

    flush_write_buffer();

    long current_pos = ftell(file_);
    size_t truncate_size = size.value_or(current_pos);

#ifdef _WIN32
    if (_chsize(_fileno(file_), truncate_size) != 0) {
      throw std::runtime_error("Truncate failed");
    }
#else
    if (ftruncate(fileno(file_), truncate_size) != 0) {
      throw std::runtime_error("Truncate failed");
    }
#endif

    file_size_cached_ = false;
  }

  bool seekable() const { return file_ != nullptr; }
  bool writable() const {
    return mode_ == FileMode::Write || mode_ == FileMode::Append ||
           mode_ == FileMode::ReadWrite ||
           mode_ == FileMode::ReadWriteTruncate ||
           mode_ == FileMode::ReadAppend;
  }

  bool isatty() {
    if (!file_) {
      throw std::runtime_error("File not open");
    }
#ifdef _WIN32
    return _isatty(_fileno(file_)) != 0;
#else
    return ::isatty(fileno(file_)) != 0;
#endif
  }

  const std::string& filename() const { return filename_; }
  const std::string& mode() const { return mode_str_; }

 private:
  FILE* file_ = nullptr;
  std::string filename_;
  FileMode mode_;
  bool binary_ = false;
  std::string mode_str_;

  std::vector<char> read_buffer_;
  std::vector<char> write_buffer_;
  std::vector<char> line_buffer_;

  size_t write_buffer_pos_ = 0;
  size_t line_buffer_pos_ = 0;
  size_t line_buffer_size_ = 0;
  bool line_buffer_eof_ = false;

  bool file_size_cached_ = false;
  size_t file_size_ = 0;

  void cache_file_size() {
    long current_pos = ftell(file_);
    fseek(file_, 0, SEEK_END);
    file_size_ = ftell(file_);
    fseek(file_, current_pos, SEEK_SET);
    file_size_cached_ = true;
  }
  void flush_write_buffer() {
    if (write_buffer_pos_ == 0) return;

    size_t written = fwrite(write_buffer_.data(), 1, write_buffer_pos_, file_);
    if (written != write_buffer_pos_) {
      throw std::runtime_error("Failed to flush write buffer");
    }
    write_buffer_pos_ = 0;
  }
  bool fill_line_buffer() {
    if (line_buffer_eof_) return false;

    if (line_buffer_.size() < DEFAULT_LINE_BUFFER_SIZE) {
      line_buffer_.resize(DEFAULT_LINE_BUFFER_SIZE);
    }

    line_buffer_size_ =
        fread(line_buffer_.data(), 1, line_buffer_.size(), file_);
    line_buffer_pos_ = 0;
    line_buffer_eof_ = (line_buffer_size_ == 0);

    return !line_buffer_eof_;
  }
};

}  // namespace aiofiles
