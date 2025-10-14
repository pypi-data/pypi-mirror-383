/*
 *  Copyright (C) GridGain Systems. All Rights Reserved.
 *  _________        _____ __________________        _____
 *  __  ____/___________(_)______  /__  ____/______ ____(_)_______
 *  _  / __  __  ___/__  / _  __  / _  / __  _  __ `/__  / __  __ \
 *  / /_/ /  _  /    _  /  / /_/ /  / /_/ /  / /_/ / _  /  _  / / /
 *  \____/   /_/     /_/   \_,__/   \____/   \__,_/  /_/   /_/ /_/
 */

#include "ignite/client/detail/table/table_impl.h"
#include "ignite/client/detail/continuous_query/continuous_query_impl.h"
#include "ignite/client/detail/transaction/transaction_impl.h"
#include "ignite/client/detail/utils.h"
#include "ignite/client/table/table.h"

#include "ignite/client/detail/client_error_flags.h"
#include "ignite/common/ignite_error.h"
#include "ignite/protocol/bitset_span.h"
#include "ignite/protocol/reader.h"
#include "ignite/protocol/writer.h"

#include <memory>

namespace ignite::detail {

/**
 * Write table operation header.
 *
 * @param writer Writer.
 * @param id Table ID.
 * @param tx Transaction.
 * @param sch Table schema.
 */
void write_table_operation_header(protocol::writer &writer, std::int32_t id, const transaction_impl *tx, const schema &sch) {
    writer.write(id);

    if (!tx)
        writer.write_nil();
    else
        writer.write(tx->get_id());

    writer.write(sch.version);
}

void table_impl::load_latest_schema_async(ignite_callback<std::shared_ptr<schema>> callback) {
    auto latest_schema_version = m_latest_schema_version;

    if (latest_schema_version >= 0) {
        std::shared_ptr<schema> schema;
        {
            std::lock_guard<std::recursive_mutex> guard(m_schemas_mutex);
            schema = m_schemas[latest_schema_version];
        }

        bool reload_schema = false;
        try {
            callback({std::move(schema)});
        } catch (ignite_error &err) {
            reload_schema = err.get_flags() & std::int32_t(error_flag::UNMAPPED_COLUMNS_PRESENT);
            if (!reload_schema)
                throw;
        }

        if (!reload_schema) {
            return;
        }
    }

    load_schema_async(std::nullopt, std::move(callback));
}

/**
 * Make a handler function for a case when it may require updating schema to complete operation.
 *
 * @tparam T Result type.
 * @param self Table shared reference.
 * @param uc User callback.
 * @param func Function that handles the schema.
 * @return Handler function.
 */
template<typename T>
std::function<void(ignite_result<bytes_view>)> make_schema_handler_function(std::shared_ptr<table_impl> self,
    ignite_callback<T> uc, std::function<void(protocol::reader &, const schema &, ignite_callback<T>)> &&func) {
    return [self = std::move(self), uc = std::move(uc), rf = std::move(func)](ignite_result<bytes_view> res) mutable {
        if (res.has_error()) {
            uc(std::move(res).error());
            return;
        }

        auto msg = res.value();
        protocol::reader reader(msg);
        auto schema_ver = reader.read_int32();
        std::shared_ptr<schema> sch = self->get_schema(schema_ver);
        if (sch) {
            rf(reader, *sch, std::move(uc));
            return;
        }

        msg.remove_prefix(reader.position());
        std::vector<std::byte> msg_copy(msg);

        self->with_schema_async<T>(schema_ver, std::move(uc),
            [msg = std::move(msg_copy), rf = std::move(rf)](const schema &sch, auto uc) mutable {
                protocol::reader reader(msg);
                rf(reader, sch, std::move(uc));
            });
    };
}

void table_impl::load_schema_async(
    std::optional<std::int32_t> version, ignite_callback<std::shared_ptr<schema>> callback) {
    auto cb = [callback = std::move(callback)](ignite_result<std::vector<std::shared_ptr<schema>>> &&res) {
        if (res.has_error())
            callback(std::move(res).error());
        else {
            auto schemas = std::move(res).value();
            assert(schemas.size() == 1);

            callback(std::move(schemas.back()));
        }
    };

    if (version) {
        std::set<std::int32_t> versions{*version};
        load_schemas_async(&versions, std::move(cb));
    } else {
        load_schemas_async(nullptr, std::move(cb));
    }
}

void table_impl::load_schemas_async(
    const std::set<std::int32_t> *versions, ignite_callback<std::vector<std::shared_ptr<schema>>> callback) {
    std::set<std::int32_t> filtered;

    if (versions) {
        std::lock_guard<std::recursive_mutex> guard(m_schemas_mutex);
        for (auto ver : *versions) {
            if (m_schemas.count(ver) == 0) {
                filtered.insert(ver);
            }
        }

        if (filtered.empty()) {
            callback(std::vector<std::shared_ptr<schema>>{});
            return;
        }
    }

    auto writer_func = [&](protocol::writer &writer, auto&) {
        writer.write(m_id);

        if (filtered.empty()) {
            writer.write_nil();
        } else {
            // Number of requested schemas.
            writer.write(std::int32_t(filtered.size()));
            for (auto ver : filtered) {
                writer.write(ver);
            }
        }
    };

    auto table = shared_from_this();
    auto reader_func = [table](protocol::reader &reader) mutable -> std::vector<std::shared_ptr<schema>> {
        auto schema_cnt = reader.read_int32();
        if (!schema_cnt)
            throw ignite_error("Schema not found");

        std::vector<std::shared_ptr<schema>> schemas;
        for (std::int32_t schema_idx = 0; schema_idx < schema_cnt; ++schema_idx) {
            auto sch = schema::read(reader);
            table->add_schema(sch);
            schemas.push_back(std::move(sch));
        }

        return schemas;
    };

    m_connection->perform_request<std::vector<std::shared_ptr<schema>>>(
        protocol::client_operation::SCHEMAS_GET, writer_func, std::move(reader_func), std::move(callback));
}

void table_impl::get_async(
    transaction *tx, const ignite_tuple &key, ignite_callback<std::optional<ignite_tuple>> callback) {

    with_proper_schema_async<std::optional<ignite_tuple>>(std::move(callback),
        [self = shared_from_this(), key = std::make_shared<ignite_tuple>(key), tx0 = to_impl(tx)](
            const schema &sch, auto callback) mutable {
            // The second parameter in the lambda is unused but required by the interface
            // for compatibility with the perform_request_raw method. It is reserved for
            // potential future use or extensions.
            auto writer_func = [self, key, &sch, &tx0](protocol::writer &writer, auto&) {
                write_table_operation_header(writer, self->m_id, tx0.get(), sch);
                write_tuple(writer, sch, *key, true);
            };

            auto handle_func = make_schema_handler_function<std::optional<ignite_tuple>>(
                self, std::move(callback), [](protocol::reader &reader, const schema &sch, auto callback) mutable {
                    callback(read_tuple_opt(reader, &sch));
                });

            self->m_connection->perform_request_raw(
                protocol::client_operation::TUPLE_GET, tx0.get(), writer_func, std::move(handle_func));
        });
}

void table_impl::contains_async(transaction *tx, const ignite_tuple &key, ignite_callback<bool> callback) {

    with_proper_schema_async<bool>(std::move(callback),
        [self = shared_from_this(), key = std::make_shared<ignite_tuple>(key), tx0 = to_impl(tx)](
            const schema &sch, auto callback) mutable {
            auto writer_func = [self, key, &sch, &tx0](protocol::writer &writer, auto&) {
                write_table_operation_header(writer, self->m_id, tx0.get(), sch);
                write_tuple(writer, sch, *key, true);
            };

            auto reader_func = [](protocol::reader &reader) -> bool {
                (void) reader.read_int32(); // Skip schema version.

                return reader.read_bool();
            };

            self->m_connection->perform_request<bool>(protocol::client_operation::TUPLE_CONTAINS_KEY, tx0.get(),
                writer_func, std::move(reader_func), std::move(callback));
        });
}

void table_impl::get_all_async(transaction *tx, std::vector<ignite_tuple> keys,
    ignite_callback<std::vector<std::optional<ignite_tuple>>> callback) {

    auto shared_keys = std::make_shared<std::vector<ignite_tuple>>(std::move(keys));
    with_proper_schema_async<std::vector<std::optional<ignite_tuple>>>(std::move(callback),
        [self = shared_from_this(), keys = shared_keys, tx0 = to_impl(tx)](const schema &sch, auto callback) mutable {
            auto writer_func = [self, keys, &sch, &tx0](protocol::writer &writer, auto&) {
                write_table_operation_header(writer, self->m_id, tx0.get(), sch);
                write_tuples(writer, sch, *keys, true);
            };

            auto handle_func = make_schema_handler_function<std::vector<std::optional<ignite_tuple>>>(
                self, std::move(callback), [](protocol::reader &reader, const schema &sch, auto callback) mutable {
                    callback(read_tuples_opt(reader, &sch, false));
                });

            self->m_connection->perform_request_raw(
                protocol::client_operation::TUPLE_GET_ALL, tx0.get(), writer_func, std::move(handle_func));
        });
}

void table_impl::upsert_async(transaction *tx, const ignite_tuple &record, ignite_callback<void> callback) {
    with_proper_schema_async<void>(std::move(callback),
        [self = shared_from_this(), record = ignite_tuple(record), tx0 = to_impl(tx)](
            const schema &sch, auto callback) mutable {
            auto writer_func = [self, &record, &sch, &tx0](protocol::writer &writer, auto&) {
                write_table_operation_header(writer, self->m_id, tx0.get(), sch);
                write_tuple(writer, sch, record, false);
            };

            self->m_connection->perform_request_wr(
                protocol::client_operation::TUPLE_UPSERT, tx0.get(), writer_func, std::move(callback));
        });
}

void table_impl::upsert_all_async(transaction *tx, std::vector<ignite_tuple> records, ignite_callback<void> callback) {
    auto shared_records = std::make_shared<std::vector<ignite_tuple>>(std::move(records));
    with_proper_schema_async<void>(std::move(callback),
        [self = shared_from_this(), records = shared_records, tx0 = to_impl(tx)](
            const schema &sch, auto callback) mutable {
            auto writer_func = [self, records, &sch, &tx0](protocol::writer &writer, auto&) {
                write_table_operation_header(writer, self->m_id, tx0.get(), sch);
                write_tuples(writer, sch, *records, false);
            };

            self->m_connection->perform_request_wr(
                protocol::client_operation::TUPLE_UPSERT_ALL, tx0.get(), writer_func, std::move(callback));
        });
}

void table_impl::get_and_upsert_async(
    transaction *tx, const ignite_tuple &record, ignite_callback<std::optional<ignite_tuple>> callback) {

    with_proper_schema_async<std::optional<ignite_tuple>>(std::move(callback),
        [self = shared_from_this(), record = std::make_shared<ignite_tuple>(record), tx0 = to_impl(tx)](
            const schema &sch, auto callback) {
            auto writer_func = [self, record, &sch, &tx0](protocol::writer &writer, auto&) {
                write_table_operation_header(writer, self->m_id, tx0.get(), sch);
                write_tuple(writer, sch, *record, false);
            };

            auto handle_func = make_schema_handler_function<std::optional<ignite_tuple>>(
                self, std::move(callback), [](protocol::reader &reader, const schema &sch, auto callback) mutable {
                    callback(read_tuple_opt(reader, &sch));
                });

            self->m_connection->perform_request_raw(
                protocol::client_operation::TUPLE_GET_AND_UPSERT, tx0.get(), writer_func, std::move(handle_func));
        });
}

void table_impl::insert_async(transaction *tx, const ignite_tuple &record, ignite_callback<bool> callback) {
    with_proper_schema_async<bool>(std::move(callback),
        [self = shared_from_this(), record = ignite_tuple(record), tx0 = to_impl(tx)](
            const schema &sch, auto callback) mutable {
            auto writer_func = [self, &record, &sch, &tx0](protocol::writer &writer, auto&) {
                write_table_operation_header(writer, self->m_id, tx0.get(), sch);
                write_tuple(writer, sch, record, false);
            };

            auto reader_func = [](protocol::reader &reader) -> bool {
                (void) reader.read_int32(); // Skip schema version.

                return reader.read_bool();
            };

            self->m_connection->perform_request<bool>(protocol::client_operation::TUPLE_INSERT, tx0.get(), writer_func,
                std::move(reader_func), std::move(callback));
        });
}

void table_impl::insert_all_async(
    transaction *tx, std::vector<ignite_tuple> records, ignite_callback<std::vector<ignite_tuple>> callback) {

    auto shared_records = std::make_shared<std::vector<ignite_tuple>>(std::move(records));
    with_proper_schema_async<std::vector<ignite_tuple>>(std::move(callback),
        [self = shared_from_this(), records = shared_records, tx0 = to_impl(tx)](
            const schema &sch, auto callback) mutable {
            auto writer_func = [self, records, &sch, &tx0](protocol::writer &writer, auto&) {
                write_table_operation_header(writer, self->m_id, tx0.get(), sch);
                write_tuples(writer, sch, *records, false);
            };

            auto handle_func = make_schema_handler_function<std::vector<ignite_tuple>>(
                self, std::move(callback), [](protocol::reader &reader, const schema &sch, auto callback) mutable {
                    callback(read_tuples(reader, &sch, false));
                });

            self->m_connection->perform_request_raw(
                protocol::client_operation::TUPLE_INSERT_ALL, tx0.get(), writer_func, std::move(handle_func));
        });
}

void table_impl::replace_async(transaction *tx, const ignite_tuple &record, ignite_callback<bool> callback) {
    with_proper_schema_async<bool>(std::move(callback),
        [self = shared_from_this(), record = ignite_tuple(record), tx0 = to_impl(tx)](
            const schema &sch, auto callback) mutable {
            auto writer_func = [self, &record, &sch, &tx0](protocol::writer &writer, auto&) {
                write_table_operation_header(writer, self->m_id, tx0.get(), sch);
                write_tuple(writer, sch, record, false);
            };

            auto reader_func = [](protocol::reader &reader) -> bool {
                (void) reader.read_int32(); // Skip schema version.

                return reader.read_bool();
            };

            self->m_connection->perform_request<bool>(protocol::client_operation::TUPLE_REPLACE, tx0.get(), writer_func,
                std::move(reader_func), std::move(callback));
        });
}

void table_impl::replace_async(
    transaction *tx, const ignite_tuple &record, const ignite_tuple &new_record, ignite_callback<bool> callback) {
    with_proper_schema_async<bool>(std::move(callback),
        [self = shared_from_this(), record = ignite_tuple(record), new_record = ignite_tuple(new_record),
            tx0 = to_impl(tx)](const schema &sch, auto callback) mutable {
            auto writer_func = [self, &record, &new_record, &sch, &tx0](protocol::writer &writer, auto&) {
                write_table_operation_header(writer, self->m_id, tx0.get(), sch);
                write_tuple(writer, sch, record, false);
                write_tuple(writer, sch, new_record, false);
            };

            auto reader_func = [](protocol::reader &reader) -> bool {
                (void) reader.read_int32(); // Skip schema version.

                return reader.read_bool();
            };

            self->m_connection->perform_request<bool>(protocol::client_operation::TUPLE_REPLACE_EXACT, tx0.get(),
                writer_func, std::move(reader_func), std::move(callback));
        });
}

void table_impl::get_and_replace_async(
    transaction *tx, const ignite_tuple &record, ignite_callback<std::optional<ignite_tuple>> callback) {

    with_proper_schema_async<std::optional<ignite_tuple>>(std::move(callback),
        [self = shared_from_this(), record = std::make_shared<ignite_tuple>(record), tx0 = to_impl(tx)](
            const schema &sch, auto callback) mutable {
            auto writer_func = [self, record, &sch, &tx0](protocol::writer &writer, auto&) {
                write_table_operation_header(writer, self->m_id, tx0.get(), sch);
                write_tuple(writer, sch, *record, false);
            };

            auto handle_func = make_schema_handler_function<std::optional<ignite_tuple>>(
                self, std::move(callback), [](protocol::reader &reader, const schema &sch, auto callback) mutable {
                    callback(read_tuple_opt(reader, &sch));
                });

            self->m_connection->perform_request_raw(
                protocol::client_operation::TUPLE_GET_AND_REPLACE, tx0.get(), writer_func, std::move(handle_func));
        });
}

void table_impl::remove_async(transaction *tx, const ignite_tuple &key, ignite_callback<bool> callback) {
    with_proper_schema_async<bool>(std::move(callback),
        [self = shared_from_this(), record = ignite_tuple(key), tx0 = to_impl(tx)](
            const schema &sch, auto callback) mutable {
            auto writer_func = [self, &record, &sch, &tx0](protocol::writer &writer, auto&) {
                write_table_operation_header(writer, self->m_id, tx0.get(), sch);
                write_tuple(writer, sch, record, true);
            };

            auto reader_func = [](protocol::reader &reader) -> bool {
                (void) reader.read_int32(); // Skip schema version.

                return reader.read_bool();
            };

            self->m_connection->perform_request<bool>(protocol::client_operation::TUPLE_DELETE, tx0.get(), writer_func,
                std::move(reader_func), std::move(callback));
        });
}

void table_impl::remove_exact_async(transaction *tx, const ignite_tuple &record, ignite_callback<bool> callback) {
    with_proper_schema_async<bool>(std::move(callback),
        [self = shared_from_this(), record = ignite_tuple(record), tx0 = to_impl(tx)](
            const schema &sch, auto callback) mutable {
            auto writer_func = [self, &record, &sch, &tx0](protocol::writer &writer, auto&) {
                write_table_operation_header(writer, self->m_id, tx0.get(), sch);
                write_tuple(writer, sch, record, false);
            };

            auto reader_func = [](protocol::reader &reader) -> bool {
                (void) reader.read_int32(); // Skip schema version.

                return reader.read_bool();
            };

            self->m_connection->perform_request<bool>(protocol::client_operation::TUPLE_DELETE_EXACT, tx0.get(),
                writer_func, std::move(reader_func), std::move(callback));
        });
}

void table_impl::get_and_remove_async(
    transaction *tx, const ignite_tuple &key, ignite_callback<std::optional<ignite_tuple>> callback) {

    with_proper_schema_async<std::optional<ignite_tuple>>(std::move(callback),
        [self = shared_from_this(), record = std::make_shared<ignite_tuple>(key), tx0 = to_impl(tx)](
            const schema &sch, auto callback) mutable {
            auto writer_func = [self, record, &sch, &tx0](protocol::writer &writer, auto&) {
                write_table_operation_header(writer, self->m_id, tx0.get(), sch);
                write_tuple(writer, sch, *record, true);
            };

            auto handle_func = make_schema_handler_function<std::optional<ignite_tuple>>(
                self, std::move(callback), [](protocol::reader &reader, const schema &sch, auto callback) mutable {
                    callback(read_tuple_opt(reader, &sch));
                });

            self->m_connection->perform_request_raw(
                protocol::client_operation::TUPLE_GET_AND_DELETE, tx0.get(), writer_func, std::move(handle_func));
        });
}

void table_impl::remove_all_async(
    transaction *tx, std::vector<ignite_tuple> keys, ignite_callback<std::vector<ignite_tuple>> callback) {

    with_proper_schema_async<std::vector<ignite_tuple>>(std::move(callback),
        [self = shared_from_this(), keys = std::move(keys), tx0 = to_impl(tx)](const schema &sch, auto callback) {
            auto writer_func = [self, &keys, &sch, &tx0](protocol::writer &writer, auto&) {
                write_table_operation_header(writer, self->m_id, tx0.get(), sch);
                write_tuples(writer, sch, keys, true);
            };

            auto handle_func = make_schema_handler_function<std::vector<ignite_tuple>>(
                self, std::move(callback), [](protocol::reader &reader, const schema &sch, auto callback) mutable {
                    callback(read_tuples(reader, &sch, true));
                });

            self->m_connection->perform_request_raw(
                protocol::client_operation::TUPLE_DELETE_ALL, tx0.get(), writer_func, std::move(handle_func));
        });
}

void table_impl::remove_all_exact_async(
    transaction *tx, std::vector<ignite_tuple> records, ignite_callback<std::vector<ignite_tuple>> callback) {

    with_proper_schema_async<std::vector<ignite_tuple>>(std::move(callback),
        [self = shared_from_this(), records = std::move(records), tx0 = to_impl(tx)](const schema &sch, auto callback) {
            auto writer_func = [self, &records, &sch, &tx0](protocol::writer &writer, auto&) {
                write_table_operation_header(writer, self->m_id, tx0.get(), sch);
                write_tuples(writer, sch, records, false);
            };

            auto handle_func = make_schema_handler_function<std::vector<ignite_tuple>>(
                self, std::move(callback), [](protocol::reader &reader, const schema &sch, auto callback) mutable {
                    callback(read_tuples(reader, &sch, false));
                });

            self->m_connection->perform_request_raw(
                protocol::client_operation::TUPLE_DELETE_ALL_EXACT, tx0.get(), writer_func, std::move(handle_func));
        });
}

std::shared_ptr<table_impl> table_impl::from_facade(table &tb) {
    return tb.m_impl;
}

void table_impl::load_partition_assignment_async(ignite_callback<std::shared_ptr<partition_assignment>> callback) {
    std::int64_t timestamp = m_connection->get_assignment_timestamp();

    {
        std::unique_lock<std::recursive_mutex> guard(m_partitions_mutex);
        auto pa = m_partition_assignment;
        if (pa && !pa->is_outdated(timestamp)) {
            callback(std::move(pa));
            return;
        }
    }

    auto new_assignment = std::make_shared<partition_assignment>();
    new_assignment->timestamp = timestamp;

    auto writer_func = [id = m_id, timestamp](protocol::writer &writer, auto&) {
        writer.write(id);
        writer.write(timestamp);
    };

    auto reader_func = [new_assignment, timestamp](protocol::reader &reader) -> std::shared_ptr<partition_assignment> {
        auto cnt = reader.read_int32();
        if (cnt < 0)
            throw ignite_error("Invalid partition count: " + std::to_string(cnt));

        new_assignment->partitions.reserve(cnt);

        bool assignment_available = reader.read_bool();
        if (!assignment_available) {
            // Invalidate the current assignment so that we can retry on the next call.
            // Return an empty array so that per-partition batches can be initialized.
            // We'll get the actual assignment on the next call.
            new_assignment->timestamp = 0;
        } else {
            // Returned timestamp can be newer than requested.
            std::int64_t ts = reader.read_int64();
            if (ts < timestamp)
                throw ignite_error("Returned timestamp is older than requested: " + std::to_string(ts) + " < "
                    + std::to_string(timestamp));

            new_assignment->timestamp = ts;

            for (std::int32_t i = 0; i < cnt; ++i) {
                new_assignment->partitions.emplace_back(reader.read_string_nullable());
            }
        }

        return new_assignment;
    };

    m_connection->perform_request<std::shared_ptr<partition_assignment>>(
        protocol::client_operation::PARTITION_ASSIGNMENT_GET, nullptr, writer_func, std::move(reader_func),
        std::move(callback));
}

void table_impl::query_continuously_async(
    continuous_query_options &&options, ignite_callback<std::shared_ptr<continuous_query_impl>> callback) {
    auto self = shared_from_this();
    load_partition_assignment_async([self, options = std::move(options), callback = std::move(callback)](
                                        auto &&res) mutable {
        if (res.has_error()) {
            callback(std::move(res).error());
            return;
        }

        std::shared_ptr<partition_assignment> assignment = std::move(res).value();
        auto partitions = std::int32_t(assignment->partitions.size());

        auto qry = std::make_shared<continuous_query_impl>(self->m_connection, self, partitions, std::move(options));

        callback({std::move(qry)});
    });
}

} // namespace ignite::detail
