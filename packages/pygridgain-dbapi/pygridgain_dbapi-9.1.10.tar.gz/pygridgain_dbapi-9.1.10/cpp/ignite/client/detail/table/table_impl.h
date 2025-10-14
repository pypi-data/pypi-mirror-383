/*
 *  Copyright (C) GridGain Systems. All Rights Reserved.
 *  _________        _____ __________________        _____
 *  __  ____/___________(_)______  /__  ____/______ ____(_)_______
 *  _  / __  __  ___/__  / _  __  / _  / __  _  __ `/__  / __  __ \
 *  / /_/ /  _  /    _  /  / /_/ /  / /_/ /  / /_/ / _  /  _  / / /
 *  \____/   /_/     /_/   \_,__/   \____/   \__,_/  /_/   /_/ /_/
 */

#pragma once

#include "ignite/client/continuous_query/continuous_query_options.h"
#include "ignite/client/detail/cluster_connection.h"
#include "ignite/client/detail/continuous_query/continuous_query_event_consumer.h"
#include "ignite/client/detail/table/schema.h"
#include "ignite/client/table/ignite_tuple.h"
#include "ignite/client/table/table_row_event_batch.h"
#include "ignite/client/table/qualified_name.h"
#include "ignite/client/transaction/transaction.h"

#include <memory>
#include <mutex>
#include <unordered_map>

namespace ignite {
class table;
}

namespace ignite::detail {

/**
 * Partition assignment.
 */
struct partition_assignment {
    /** Assignment timestamp. */
    volatile std::int64_t timestamp{0};

    /** Partitions. */
    std::vector<std::optional<std::string>> partitions;

    /**
     * Check whether assignment is outdated.
     *
     * @param actual_timestamp Timestamp.
     * @return @c true if assignment is outdated.
     */
    [[nodiscard]] bool is_outdated(std::int64_t actual_timestamp) const { return timestamp >= actual_timestamp; }
};

/**
 * Table view implementation.
 */
class table_impl : public std::enable_shared_from_this<table_impl> {
public:
    // Deleted
    table_impl(table_impl &&) = delete;
    table_impl(const table_impl &) = delete;
    table_impl &operator=(table_impl &&) = delete;
    table_impl &operator=(const table_impl &) = delete;

    /**
     * Constructor.
     *
     * @param name Qualified name.
     * @param id ID.
     * @param connection Connection.
     */
    table_impl(qualified_name name, const std::int32_t id,
        std::shared_ptr<cluster_connection> connection)
        : m_qualified_name(std::move(name))
        , m_id(id)
        , m_connection(std::move(connection)) {}

    /**
     * Gets table name.
     *
     * @return Table name.
     */
    [[nodiscard]] const std::string &get_name() const { return m_qualified_name.get_canonical_name(); }

    /**
     * Gets the table qualified name.
     *
     * @return Table qualified name.
     */
    [[nodiscard]] const qualified_name &get_qualified_name() const noexcept { return m_qualified_name; }

    /**
     * Gets the latest schema.
     *
     * @param callback Callback which is going to be called with the latest schema.
     */
    void load_latest_schema_async(ignite_callback<std::shared_ptr<schema>> callback);

    /**
     * Gets the latest schema.
     *
     * @param handler Callback to call on error during retrieval of the latest schema.
     */
    template<typename T>
    void with_latest_schema_async(
        ignite_callback<T> handler, std::function<void(const schema &, ignite_callback<T>)> callback) {
        auto func = [this, handler = std::move(handler), callback = std::move(callback)](auto &&res) mutable {
            if (res.has_error()) {
                handler(ignite_error{res.error()});
                return;
            }

            auto schema = res.value();
            if (!schema) {
                handler(ignite_error{"Can not get the latest schema for the table " + get_name()});
                return;
            }

            callback(*schema, handler);
        };

        load_latest_schema_async(std::move(func));
    }

    /**
     * Load schema from server asynchronously.
     *
     * @param version Version to get. std::nullopt for latest.
     * @param callback Callback to call with received schema.
     */
    void load_schema_async(std::optional<std::int32_t> version, ignite_callback<std::shared_ptr<schema>> callback);

    /**
     * Load schemas from server asynchronously.
     *
     * @param versions Versions to get.
     * @param callback Callback to call with received schemas.
     */
    void load_schemas_async(
        const std::set<std::int32_t> *versions, ignite_callback<std::vector<std::shared_ptr<schema>>> callback);

    /**
     * Get schema by version and use it with callback.
     *
     * @param version Schema version.
     * @param callback Callback.
     * @param handler Callback to call on error during retrieval of the latest schema.
     */
    template<typename T>
    void with_schema_async(std::int32_t version, ignite_callback<T> handler,
        std::function<void(const schema &, ignite_callback<T>)> callback) {
        auto schema = get_schema(version);

        if (schema) {
            callback(*schema, std::move(handler));

            return;
        }

        auto func = [this, version, handler = std::move(handler), callback = std::move(callback)](auto &&res) mutable {
            if (res.has_error()) {
                handler(ignite_error{res.error()});
                return;
            }

            auto schema = res.value();
            if (!schema) {
                handler(ignite_error{
                    "Can not get a schema of version " + std::to_string(version) + " for the table " + get_name()});
                return;
            }

            callback(*schema, handler);
        };

        load_schema_async(version, std::move(func));
    }

    /**
     * Performs operation with proper schema.
     *
     * @param user_callback User callback.
     * @param callback Callback to call on error during retrieval of the latest schema.
     */
    template<typename T>
    void with_proper_schema_async(
        ignite_callback<T> user_callback, std::function<void(const schema &, ignite_callback<T>)> callback) {
        auto fail_over = [uc = std::move(user_callback), this, callback](ignite_result<T> &&res) mutable {
            if (res.has_error()) {
                auto ver_opt = res.error().template get_extra<std::int32_t>(
                    protocol::error_extensions::EXPECTED_SCHEMA_VERSION);
                if (ver_opt) {
                    with_schema_async<T>(*ver_opt, std::move(uc), callback);
                    return;
                }
            }
            uc(std::move(res));
        };

        with_latest_schema_async<T>(std::move(fail_over), callback);
    }

    /**
     * Gets a record by key asynchronously.
     *
     * @param tx Optional transaction. If nullptr implicit transaction for this
     *  single operation is used.
     * @param key Key.
     * @param callback Callback.
     */
    void get_async(transaction *tx, const ignite_tuple &key, ignite_callback<std::optional<ignite_tuple>> callback);

    /**
     * Asynchronously determines if the table contains an entry for the specified key.
     *
     * @param tx Optional transaction. If nullptr implicit transaction for this
     *  single operation is used.
     * @param key Key.
     * @param callback Callback.
     */
    void contains_async(transaction *tx, const ignite_tuple &key, ignite_callback<bool> callback);

    /**
     * Gets multiple records by keys asynchronously.
     *
     * @param tx Optional transaction. If nullptr implicit transaction for this
     *   single operation is used.
     * @param keys Keys.
     * @param callback Callback that is called on operation completion. Called with
     *   resulting records with all columns filled from the table. The order of
     *   elements is guaranteed to be the same as the order of keys. If a record
     *   does not exist, the resulting element of the corresponding order is
     *   @c std::nullopt.
     */
    void get_all_async(transaction *tx, std::vector<ignite_tuple> keys,
        ignite_callback<std::vector<std::optional<ignite_tuple>>> callback);

    /**
     * Inserts a record into the table if does not exist or replaces the existing one.
     *
     * @param tx Optional transaction. If nullptr implicit transaction for this
     *  single operation is used.
     * @param record A record to insert into the table. The record cannot be @c nullptr.
     * @param callback Callback.
     */
    void upsert_async(transaction *tx, const ignite_tuple &record, ignite_callback<void> callback);

    /**
     * Inserts multiple records into the table asynchronously, replacing existing ones.
     *
     * @param tx Optional transaction. If nullptr implicit transaction for this
     *   single operation is used.
     * @param records Records to upsert.
     * @param callback Callback that is called on operation completion.
     */
    void upsert_all_async(transaction *tx, std::vector<ignite_tuple> records, ignite_callback<void> callback);

    /**
     * Inserts a record into the table and returns previous record asynchronously.
     *
     * @param tx Optional transaction. If nullptr implicit transaction for this
     *   single operation is used.
     * @param record A record to upsert.
     * @param callback Callback. Called with a value which contains replaced
     *   record or @c std::nullopt if it did not exist.
     */
    void get_and_upsert_async(
        transaction *tx, const ignite_tuple &record, ignite_callback<std::optional<ignite_tuple>> callback);

    /**
     * Inserts a record into the table if it does not exist.
     *
     * @param tx Optional transaction. If nullptr implicit transaction for this
     *   single operation is used.
     * @param record A record to insert into the table. The record cannot be
     *   @c nullptr.
     * @param callback Callback. Called with a value indicating whether the
     *   record was inserted. Equals @c false if a record with the same key
     *   already exists.
     */
    void insert_async(transaction *tx, const ignite_tuple &record, ignite_callback<bool> callback);

    /**
     * Inserts multiple records into the table asynchronously, skipping existing ones.
     *
     * @param tx Optional transaction. If nullptr implicit transaction for this
     *   single operation is used.
     * @param records Records to upsert.
     * @param callback Callback that is called on operation completion. Called with
     *   skipped records.
     */
    void insert_all_async(
        transaction *tx, std::vector<ignite_tuple> records, ignite_callback<std::vector<ignite_tuple>> callback);

    /**
     * Asynchronously replaces a record with the same key columns if it exists,
     * otherwise does nothing.
     *
     * @param tx Optional transaction. If nullptr implicit transaction for this
     *   single operation is used.
     * @param record A record to insert into the table.
     * @param callback Callback. Called with a value indicating whether a record
     *   with the specified key was replaced.
     */
    void replace_async(transaction *tx, const ignite_tuple &record, ignite_callback<bool> callback);

    /**
     * Asynchronously replaces a record with a new one only if all existing
     * columns have the same values as the specified @c record.
     *
     * @param tx Optional transaction. If nullptr implicit transaction for this
     *   single operation is used.
     * @param record Current value of the record to be replaced.
     * @param new_record A record to replace it with.
     * @param callback Callback. Called with a value indicating whether a
     *   specified record was replaced.
     */
    void replace_async(
        transaction *tx, const ignite_tuple &record, const ignite_tuple &new_record, ignite_callback<bool> callback);

    /**
     * Asynchronously replaces a record with the same key columns if it exists
     * returning previous record value.
     *
     * @param tx Optional transaction. If nullptr implicit transaction for this
     *   single operation is used.
     * @param record A record to insert.
     * @param callback Callback. Called with a previous value for the given key,
     *   or @c std::nullopt if it did not exist.
     */
    void get_and_replace_async(
        transaction *tx, const ignite_tuple &record, ignite_callback<std::optional<ignite_tuple>> callback);

    /**
     * Deletes a record with the specified key asynchronously.
     *
     * @param tx Optional transaction. If nullptr implicit transaction for this
     *   single operation is used.
     * @param key A record with key columns set.
     * @param callback Callback that is called on operation completion. Called with
     *   a value indicating whether a record with the specified key was deleted.
     */
    void remove_async(transaction *tx, const ignite_tuple &key, ignite_callback<bool> callback);

    /**
     * Deletes a record only if all existing columns have the same values as
     * the specified record asynchronously.
     *
     * @param tx Optional transaction. If nullptr implicit transaction for this
     *   single operation is used.
     * @param record A record with all columns set.
     * @param callback Callback that is called on operation completion. Called with
     *   a value indicating whether a record with the specified key was deleted.
     */
    void remove_exact_async(transaction *tx, const ignite_tuple &record, ignite_callback<bool> callback);

    /**
     * Gets and deletes a record with the specified key asynchronously.
     *
     * @param tx Optional transaction. If nullptr implicit transaction for this
     *   single operation is used.
     * @param key A record with key columns set.
     * @param callback Callback that is called on operation completion. Called with
     *   a deleted record or @c std::nullopt if it did not exist.
     */
    void get_and_remove_async(
        transaction *tx, const ignite_tuple &key, ignite_callback<std::optional<ignite_tuple>> callback);

    /**
     * Deletes multiple records from the table asynchronously. If one or more
     * keys do not exist, other records are still deleted
     *
     * @param tx Optional transaction. If nullptr implicit transaction for this
     *   single operation is used.
     * @param keys Record keys to delete.
     * @param callback Callback that is called on operation completion. Called with
     *   records from @c keys that did not exist.
     */
    void remove_all_async(
        transaction *tx, std::vector<ignite_tuple> keys, ignite_callback<std::vector<ignite_tuple>> callback);

    /**
     * Deletes multiple exactly matching records asynchronously. If one or more
     * records do not exist, other records are still deleted.
     *
     * @param tx Optional transaction. If nullptr implicit transaction for this
     *   single operation is used.
     * @param records Records to delete.
     * @param callback Callback that is called on operation completion. Called with
     *   records from @c records that did not exist.
     */
    void remove_all_exact_async(
        transaction *tx, std::vector<ignite_tuple> records, ignite_callback<std::vector<ignite_tuple>> callback);

    /**
     * Starts a continuous query which listens to data events within the underlying table.
     *
     * @param options Options (use empty initializer list for default).
     * @param callback Callback to call on result.
     */
    void query_continuously_async(
        continuous_query_options &&options, ignite_callback<std::shared_ptr<continuous_query_impl>> callback);

    /**
     * Extract implementation from facade.
     *
     * @param tb Table.
     * @return Implementation.
     */
    [[nodiscard]] static std::shared_ptr<table_impl> from_facade(table &tb);

    /**
     * Get table ID.
     *
     * @return ID.
     */
    [[nodiscard]] std::int32_t get_id() const { return m_id; }

    /**
     * Get schema by version.
     *
     * @param version Schema version.
     */
    std::shared_ptr<schema> get_schema(std::int32_t version) {
        std::lock_guard<std::recursive_mutex> lock(m_schemas_mutex);

        auto it = m_schemas.find(version);
        if (it == m_schemas.end())
            return {};

        return it->second;
    }

private:
    /**
     * Add schema.
     *
     * @param val Schema.
     */
    void add_schema(const std::shared_ptr<schema> &val) {
        std::lock_guard<std::recursive_mutex> lock(m_schemas_mutex);
        if (m_latest_schema_version < val->version)
            m_latest_schema_version = val->version;

        m_schemas[val->version] = val;
    }

    /**
     * Get partition assignment.
     *
     * @return Partition assignment.
     */
    std::shared_ptr<partition_assignment> get_partition_assignment() {
        std::lock_guard<std::recursive_mutex> lock(m_partitions_mutex);
        return m_partition_assignment;
    }

    /**
     * Load partition assignment.
     *
     * @param callback Callback to call with the actual assignment.
     */
    void load_partition_assignment_async(ignite_callback<std::shared_ptr<partition_assignment>> callback);

    /**
     * Get impl of transaction.
     * @param tx Transaction.
     * @return Implementation pointer.
     */
    static std::shared_ptr<transaction_impl> to_impl(transaction *tx) { return tx ? tx->m_impl : nullptr; }

    /** Table qualified name. */
    const qualified_name m_qualified_name;

    /** Table ID. */
    const std::int32_t m_id;

    /** Cluster connection. */
    std::shared_ptr<cluster_connection> m_connection;

    /** Latest schema version. */
    volatile std::int32_t m_latest_schema_version{-1};

    /** Schemas mutex. */
    std::recursive_mutex m_schemas_mutex;

    /** Schemas. */
    std::unordered_map<int32_t, std::shared_ptr<schema>> m_schemas;

    /** Partitions mutex. */
    std::recursive_mutex m_partitions_mutex;

    /** Partition assignment. */
    std::shared_ptr<partition_assignment> m_partition_assignment;
};

} // namespace ignite::detail
