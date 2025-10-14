// Python bindings for shmx - Shared Memory IPC library
// Zero dependencies on numpy - returns native Python types (memoryview, bytes, dict)

#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <pybind11/functional.h>

#include "src/shmx_client.h"
#include "src/shmx_server.h"
#include "src/shmx_inspector.h"
#include "src/shmx_common.h"

namespace py = pybind11;

// ============================================================================
// Helper functions for data conversion
// ============================================================================

// Convert data type enum to Python string
std::string dtype_to_string(std::uint32_t dt) {
    switch (dt) {
        case shmx::DT_BOOL: return "bool";
        case shmx::DT_I8: return "int8";
        case shmx::DT_U8: return "uint8";
        case shmx::DT_I16: return "int16";
        case shmx::DT_U16: return "uint16";
        case shmx::DT_I32: return "int32";
        case shmx::DT_U32: return "uint32";
        case shmx::DT_I64: return "int64";
        case shmx::DT_U64: return "uint64";
        case shmx::DT_F16: return "float16";
        case shmx::DT_BF16: return "bfloat16";
        case shmx::DT_F32: return "float32";
        case shmx::DT_F64: return "float64";
        default: return "unknown";
    }
}

// Convert layout enum to string
std::string layout_to_string(std::uint32_t layout) {
    switch (layout) {
        case shmx::LAYOUT_SOA_SCALAR: return "scalar";
        case shmx::LAYOUT_AOS_VECTOR: return "vector";
        default: return "unknown";
    }
}

// ============================================================================
// Client bindings
// ============================================================================

class PyClient {
private:
    shmx::Client client_;
    shmx::StaticState static_state_;
    bool has_static_state_ = false;

public:
    PyClient() = default;

    bool open(const std::string& name) {
        bool result = client_.open(name);
        if (result) {
            has_static_state_ = client_.refresh_static(static_state_);
        }
        return result;
    }

    void close() {
        client_.close();
        has_static_state_ = false;
    }

    bool is_open() {
        return client_.header() != nullptr;
    }

    py::dict get_header_info() {
        auto* hdr = client_.header();
        if (!hdr) return py::dict();

        py::dict info;
        info["magic"] = hdr->magic;
        info["version_major"] = hdr->ver_major;
        info["version_minor"] = hdr->ver_minor;
        info["session_id"] = hdr->session_id;
        info["slots"] = hdr->slots;
        info["frame_bytes_cap"] = hdr->frame_bytes_cap;
        info["reader_slots"] = hdr->reader_slots;
        info["control_per_reader"] = hdr->control_per_reader;
        info["frame_seq"] = hdr->frame_seq.load(std::memory_order_relaxed);
        info["readers_connected"] = hdr->readers_connected.load(std::memory_order_relaxed);
        return info;
    }

    py::list get_streams_info() {
        if (!has_static_state_) {
            has_static_state_ = client_.refresh_static(static_state_);
        }

        py::list streams;
        for (const auto& stream : static_state_.dir) {
            py::dict info;
            info["id"] = stream.id;
            info["name"] = stream.name;
            info["dtype"] = dtype_to_string(stream.elem_type);
            info["dtype_code"] = stream.elem_type;
            info["components"] = stream.components;
            info["layout"] = layout_to_string(stream.layout);
            info["bytes_per_elem"] = stream.bytes_per_elem;

            // Extra data as bytes if present
            if (!stream.extra.empty()) {
                info["extra"] = py::bytes(reinterpret_cast<const char*>(stream.extra.data()),
                                         stream.extra.size());
            }

            streams.append(info);
        }
        return streams;
    }

    py::object get_latest_frame() {
        shmx::FrameView fv;
        if (!client_.latest(fv)) {
            return py::none();
        }

        if (fv.checksum_mismatch || fv.session_mismatch) {
            return py::none();
        }

        // Decode frame
        shmx::DecodedFrame df;
        if (!shmx::Client::decode(fv, df)) {
            return py::none();
        }

        // Build result dictionary
        py::dict result;

        // Add metadata
        py::dict metadata;
        metadata["frame_id"] = fv.fh->frame_id.load(std::memory_order_relaxed);
        metadata["sim_time"] = fv.fh->sim_time;
        metadata["payload_bytes"] = fv.fh->payload_bytes;
        metadata["tlv_count"] = fv.fh->tlv_count;
        result["__metadata__"] = metadata;

        // Add streams as memoryview objects (zero-copy when possible)
        for (const auto& [stream_id, item] : df.streams) {
            // Find stream name
            std::string stream_name = "stream_" + std::to_string(stream_id);
            for (const auto& s : static_state_.dir) {
                if (s.id == stream_id) {
                    stream_name = s.name;
                    break;
                }
            }

            // Create stream info dict
            py::dict stream_data;

            // Return data as memoryview (Python buffer protocol, zero-copy)
            // Note: The data is only valid until next frame, user should copy if needed
            stream_data["data"] = py::memoryview::from_memory(
                const_cast<void*>(item.ptr),
                item.bytes
            );

            stream_data["elem_count"] = item.elem_count;
            stream_data["bytes"] = item.bytes;

            result[stream_name.c_str()] = stream_data;
        }

        return result;
    }

    bool refresh_static() {
        has_static_state_ = client_.refresh_static(static_state_);
        return has_static_state_;
    }

    bool send_control(std::uint32_t type, const py::bytes& data) {
        std::string str = data;
        return client_.control_send(type, str.data(), static_cast<std::uint32_t>(str.size()));
    }

    bool send_control_empty(std::uint32_t type) {
        return client_.control_send(type, nullptr, 0);
    }
};

// ============================================================================
// Server bindings
// ============================================================================

class PyServer {
private:
    shmx::Server server_;
    std::vector<shmx::StaticStream> streams_;

public:
    PyServer() = default;

    bool create(const std::string& name,
                std::uint32_t slots,
                std::uint32_t reader_slots,
                std::uint32_t static_bytes_cap,
                std::uint32_t frame_bytes_cap,
                std::uint32_t control_per_reader,
                const py::list& streams) {

        streams_.clear();
        for (auto item : streams) {
            py::dict stream = item.cast<py::dict>();

            shmx::StaticStream ss;
            ss.stream_id = stream["id"].cast<std::uint32_t>();
            ss.element_type = stream["dtype_code"].cast<std::uint32_t>();
            ss.components = stream["components"].cast<std::uint32_t>();
            ss.layout = stream.contains("layout_code") ?
                       stream["layout_code"].cast<std::uint32_t>() :
                       shmx::LAYOUT_SOA_SCALAR;
            ss.bytes_per_elem = stream["bytes_per_elem"].cast<std::uint32_t>();
            ss.name_utf8 = stream["name"].cast<std::string>();

            if (stream.contains("extra")) {
                py::bytes extra = stream["extra"];
                std::string extra_str = extra;
                ss.extra.assign(extra_str.begin(), extra_str.end());
            }

            streams_.push_back(ss);
        }

        shmx::Server::Config cfg;
        cfg.name = name;
        cfg.slots = slots;
        cfg.reader_slots = reader_slots;
        cfg.static_bytes_cap = static_bytes_cap;
        cfg.frame_bytes_cap = frame_bytes_cap;
        cfg.control_per_reader = control_per_reader;

        return server_.create(cfg, streams_);
    }

    void destroy() {
        server_.destroy();
    }

    py::dict get_header_info() {
        auto* hdr = server_.header();
        if (!hdr) return py::dict();

        py::dict info;
        info["magic"] = hdr->magic;
        info["version_major"] = hdr->ver_major;
        info["version_minor"] = hdr->ver_minor;
        info["session_id"] = hdr->session_id;
        info["slots"] = hdr->slots;
        info["frame_bytes_cap"] = hdr->frame_bytes_cap;
        info["reader_slots"] = hdr->reader_slots;
        info["control_per_reader"] = hdr->control_per_reader;
        info["frame_seq"] = hdr->frame_seq.load(std::memory_order_relaxed);
        info["readers_connected"] = hdr->readers_connected.load(std::memory_order_relaxed);
        return info;
    }

    py::object begin_frame() {
        auto fm = server_.begin_frame();

        // Return frame handle as opaque capsule
        auto* fm_ptr = new shmx::Server::FrameMap(fm);
        return py::capsule(fm_ptr, [](void* ptr) {
            delete static_cast<shmx::Server::FrameMap*>(ptr);
        });
    }

    bool append_stream(py::object frame_handle,
                      std::uint32_t stream_id,
                      const py::bytes& data,
                      std::uint32_t elem_count) {
        auto* fm = static_cast<shmx::Server::FrameMap*>(
            PyCapsule_GetPointer(frame_handle.ptr(), nullptr)
        );
        if (!fm) return false;

        std::string data_str = data;
        return shmx::Server::append_stream(*fm, stream_id, data_str.data(),
                                          elem_count, static_cast<std::uint32_t>(data_str.size()));
    }

    bool publish_frame(py::object frame_handle, double sim_time) {
        auto* fm = static_cast<shmx::Server::FrameMap*>(
            PyCapsule_GetPointer(frame_handle.ptr(), nullptr)
        );
        if (!fm) return false;

        return server_.publish_frame(*fm, sim_time);
    }

    py::list poll_control(std::uint32_t max_messages) {
        std::vector<shmx::Server::ControlMsg> msgs;
        server_.poll_control(msgs, max_messages);

        py::list result;
        for (const auto& msg : msgs) {
            py::dict item;
            item["reader_id"] = msg.reader_id;
            item["type"] = msg.type;
            item["data"] = py::bytes(reinterpret_cast<const char*>(msg.data.data()),
                                    msg.data.size());
            result.append(item);
        }
        return result;
    }

    py::list snapshot_readers() {
        auto readers = server_.snapshot_readers();

        py::list result;
        for (const auto& reader : readers) {
            py::dict item;
            item["reader_id"] = reader.reader_id;
            item["heartbeat"] = reader.heartbeat;
            item["last_frame_seen"] = reader.last_frame_seen;
            item["in_use"] = reader.in_use;
            result.append(item);
        }
        return result;
    }

    std::uint32_t reap_stale_readers(std::uint64_t now_ticks, std::uint64_t timeout_ticks) {
        return server_.reap_stale_readers(now_ticks, timeout_ticks);
    }
};

// ============================================================================
// Inspector bindings
// ============================================================================

class PyInspector {
private:
    shmx::Inspector inspector_;

public:
    PyInspector() = default;

    bool open(const std::string& name) {
        return inspector_.open(name);
    }

    void close() {
        inspector_.close();
    }

    py::dict get_header_info() {
        auto* hdr = inspector_.header();
        if (!hdr) return py::dict();

        py::dict info;
        info["magic"] = hdr->magic;
        info["version_major"] = hdr->ver_major;
        info["version_minor"] = hdr->ver_minor;
        info["session_id"] = hdr->session_id;
        info["slots"] = hdr->slots;
        info["frame_bytes_cap"] = hdr->frame_bytes_cap;
        info["reader_slots"] = hdr->reader_slots;
        info["control_per_reader"] = hdr->control_per_reader;
        info["frame_seq"] = hdr->frame_seq.load(std::memory_order_relaxed);
        info["readers_connected"] = hdr->readers_connected.load(std::memory_order_relaxed);
        return info;
    }

    py::list get_streams_info() {
        auto dir_entries = inspector_.decode_static_dir();

        py::list streams;
        for (const auto& entry : dir_entries) {
            py::dict info;
            info["id"] = entry.stream_id;
            info["name"] = entry.name;
            info["dtype"] = dtype_to_string(entry.element_type);
            info["dtype_code"] = entry.element_type;
            info["components"] = entry.components;
            info["layout"] = layout_to_string(entry.layout);
            info["bytes_per_elem"] = entry.bytes_per_elem;

            if (!entry.extra.empty()) {
                info["extra"] = py::bytes(reinterpret_cast<const char*>(entry.extra.data()),
                                         entry.extra.size());
            }

            streams.append(info);
        }
        return streams;
    }

    py::list get_readers_info() {
        auto readers = inspector_.snapshot_readers();

        py::list result;
        for (const auto& reader : readers) {
            py::dict info;
            info["reader_id"] = reader.reader_id;
            info["heartbeat"] = reader.heartbeat;
            info["last_frame_seen"] = reader.last_frame_seen;
            info["in_use"] = reader.in_use;
            result.append(info);
        }
        return result;
    }

    py::dict inspect() {
        auto* hdr = inspector_.header();
        if (!hdr) return py::dict();

        py::dict output;
        output["session_id"] = hdr->session_id;
        output["static_gen"] = hdr->static_gen.load(std::memory_order_relaxed);
        output["frame_seq"] = hdr->frame_seq.load(std::memory_order_relaxed);
        output["readers_connected"] = hdr->readers_connected.load(std::memory_order_relaxed);
        output["streams"] = get_streams_info();
        output["readers"] = get_readers_info();

        return output;
    }
};

// ============================================================================
// Module definition
// ============================================================================

PYBIND11_MODULE(shmx_core, m) {
    m.doc() = "SHMX: High-performance shared-memory IPC for frame streaming\n\n"
              "Zero dependencies - returns native Python types (memoryview, bytes, dict.";

    // Version info
    m.attr("__version__") = "1.0.1";
    m.attr("VERSION_MAJOR") = shmx::VER_MAJOR;
    m.attr("VERSION_MINOR") = shmx::VER_MINOR;

    // Constants - Data types
    m.attr("DT_BOOL") = shmx::DT_BOOL;
    m.attr("DT_I8") = shmx::DT_I8;
    m.attr("DT_U8") = shmx::DT_U8;
    m.attr("DT_I16") = shmx::DT_I16;
    m.attr("DT_U16") = shmx::DT_U16;
    m.attr("DT_I32") = shmx::DT_I32;
    m.attr("DT_U32") = shmx::DT_U32;
    m.attr("DT_I64") = shmx::DT_I64;
    m.attr("DT_U64") = shmx::DT_U64;
    m.attr("DT_F16") = shmx::DT_F16;
    m.attr("DT_BF16") = shmx::DT_BF16;
    m.attr("DT_F32") = shmx::DT_F32;
    m.attr("DT_F64") = shmx::DT_F64;

    // Constants - Layouts
    m.attr("LAYOUT_SOA_SCALAR") = shmx::LAYOUT_SOA_SCALAR;
    m.attr("LAYOUT_AOS_VECTOR") = shmx::LAYOUT_AOS_VECTOR;

    // Constants - TLV types
    m.attr("TLV_STATIC_DIR") = shmx::TLV_STATIC_DIR;
    m.attr("TLV_FRAME_STREAM") = shmx::TLV_FRAME_STREAM;
    m.attr("TLV_CONTROL_USER") = shmx::TLV_CONTROL_USER;

    // Client class
    py::class_<PyClient>(m, "Client", "Shared memory client for consuming frames")
        .def(py::init<>())
        .def("open", &PyClient::open, py::arg("name"),
             "Open shared memory region by name")
        .def("close", &PyClient::close,
             "Close the connection and release resources")
        .def("is_open", &PyClient::is_open,
             "Check if connection is open")
        .def("get_header_info", &PyClient::get_header_info,
             "Get header information as dict")
        .def("get_streams_info", &PyClient::get_streams_info,
             "Get list of available streams with metadata")
        .def("get_latest_frame", &PyClient::get_latest_frame,
             "Get latest frame as dict with stream data as memoryview objects.\n"
             "Returns None if no frame available or validation failed.\n"
             "Frame dict contains '__metadata__' key and stream names as keys.\n"
             "Each stream value is a dict with 'data' (memoryview), 'elem_count', 'bytes'.")
        .def("refresh_static", &PyClient::refresh_static,
             "Refresh static stream metadata")
        .def("send_control", &PyClient::send_control,
             py::arg("type"), py::arg("data"),
             "Send control message to server")
        .def("send_control_empty", &PyClient::send_control_empty,
             py::arg("type"),
             "Send control message without data");

    // Server class
    py::class_<PyServer>(m, "Server", "Shared memory server for publishing frames")
        .def(py::init<>())
        .def("create", &PyServer::create,
             py::arg("name"),
             py::arg("slots") = 3,
             py::arg("reader_slots") = 16,
             py::arg("static_bytes_cap") = 4096,
             py::arg("frame_bytes_cap") = 65536,
             py::arg("control_per_reader") = 4096,
             py::arg("streams") = py::list(),
             "Create shared memory region with given configuration.\n"
             "streams: list of dicts with keys 'id', 'name', 'dtype_code', 'components', "
             "'bytes_per_elem', optional 'layout_code', 'extra'")
        .def("destroy", &PyServer::destroy,
             "Destroy and release shared memory")
        .def("get_header_info", &PyServer::get_header_info,
             "Get header information as dict")
        .def("begin_frame", &PyServer::begin_frame,
             "Begin a new frame, returns frame handle")
        .def("append_stream", &PyServer::append_stream,
             py::arg("frame_handle"), py::arg("stream_id"),
             py::arg("data"), py::arg("elem_count"),
             "Append stream data to frame")
        .def("publish_frame", &PyServer::publish_frame,
             py::arg("frame_handle"), py::arg("sim_time"),
             "Publish frame to shared memory")
        .def("poll_control", &PyServer::poll_control,
             py::arg("max_messages") = 256,
             "Poll control messages from clients, returns list of dicts")
        .def("snapshot_readers", &PyServer::snapshot_readers,
             "Get snapshot of connected readers")
        .def("reap_stale_readers", &PyServer::reap_stale_readers,
             py::arg("now_ticks"), py::arg("timeout_ticks"),
             "Remove stale readers, returns count of reaped readers");

    // Inspector class
    py::class_<PyInspector>(m, "Inspector", "Read-only inspector for shared memory state")
        .def(py::init<>())
        .def("open", &PyInspector::open, py::arg("name"),
             "Open shared memory region by name (read-only)")
        .def("close", &PyInspector::close,
             "Close the connection")
        .def("get_header_info", &PyInspector::get_header_info,
             "Get header information as dict")
        .def("get_streams_info", &PyInspector::get_streams_info,
             "Get list of available streams")
        .def("get_readers_info", &PyInspector::get_readers_info,
             "Get list of connected readers")
        .def("inspect", &PyInspector::inspect,
             "Get full inspection report as dict");

    // Utility functions
    m.def("dtype_to_string", &dtype_to_string, py::arg("dtype_code"),
          "Convert dtype code to string");
    m.def("layout_to_string", &layout_to_string, py::arg("layout_code"),
          "Convert layout code to string");
}
