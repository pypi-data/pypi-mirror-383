#pragma once

#include <algorithm>
#include <chrono>
#include <cstdint>
#include <deque>
#include <fstream>
#include <functional>
#include <future>
#include <map>
#include <mutex>
#include <string>
#include <tuple>
#include <vector>
#include <cmath>
#include <limits>
#include <set>

#include "structs.hpp"
#include "byte_util.cpp"
#include "file_util.cpp"
#include "util.cpp"
#include "reader_header.cpp"
#include "reader_values.cpp"






class Reader {
    std::string path;
    uint64_t parallel;
    float zoom_correction;
    std::shared_ptr<BufferedFilePool> file;

public:
    MainHeader main_header;
    std::vector<ZoomHeader> zoom_headers;
    OrderedMap<std::string, std::string> auto_sql;
    TotalSummary total_summary;
    ChrTreeHeader chr_tree_header;
    std::vector<ChrTreeLeaf> chr_tree;
    OrderedMap<std::string, ChrTreeLeaf> chr_map;
    std::string type;
    uint32_t data_count;

    Reader(
        const std::string& path,
        uint64_t parallel = 24,
        float zoom_correction = 0.33
    ) : path(path), parallel(parallel), zoom_correction(zoom_correction) {
        file = std::make_shared<BufferedFilePool>(path, "r", parallel);
    }

    std::future<void> read_headers() {
        return std::async(std::launch::async, [this]() {
            main_header = read_main_header(*file);
            zoom_headers = read_zoom_headers(*file, main_header.zoom_levels);
            auto_sql = read_auto_sql(*file, main_header.auto_sql_offset, main_header.field_count);
            total_summary = read_total_summary(*file, main_header.total_summary_offset);
            chr_tree_header = read_chr_tree_header(*file, main_header.chr_tree_offset);
            chr_tree = read_chr_tree(*file, main_header.chr_tree_offset + 32, chr_tree_header.key_size);
            chr_map = convert_chr_tree_to_map(chr_tree);
            type = main_header.magic == 0x888FFC26 ? "bigwig" : "bigbed";
            
            ByteArray buffer = file->read(4, main_header.full_data_offset).get();
            data_count = buffer.read_uint32(0);
        });
    }

    int32_t select_zoom(double bin_size) {
        int32_t best_level = -1;
        uint32_t best_reduction = 0;
        uint32_t rounded_bin_size = static_cast<uint32_t>(std::round(bin_size * zoom_correction));
        for (uint16_t i = 0; i < zoom_headers.size(); ++i) {
            uint32_t reduction = zoom_headers[i].reduction_level;
            if (reduction <= rounded_bin_size && reduction > best_reduction) {
                best_reduction = reduction;
                best_level = i;
            }
        }
        return best_level;
    }

    ChrTreeLeaf parse_chr(const std::string& chr_id) {
        std::string chr_key = chr_id.substr(0, chr_tree_header.key_size);
        auto it = chr_map.find(chr_key);
        if (it != chr_map.end()) return it->second;
        it = chr_map.find(lowercase(chr_key));
        if (it != chr_map.end()) return it->second;
        it = chr_map.find(uppercase(chr_key));
        if (it != chr_map.end()) return it->second;
        if (lowercase(chr_id.substr(0, 3)) == "chr") {
            chr_key = chr_id.substr(3).substr(0, chr_tree_header.key_size);
        } else {
            chr_key = ("chr" + chr_id).substr(0, chr_tree_header.key_size);
        }
        it = chr_map.find(chr_key);
        if (it != chr_map.end()) return it->second;
        it = chr_map.find(lowercase(chr_key));
        if (it != chr_map.end()) return it->second;
        it = chr_map.find(uppercase(chr_key));
        if (it != chr_map.end()) return it->second;
        std::string available;
        for (const auto& entry : chr_map) {
            if (!available.empty()) available += ", ";
            available += entry.first;
        }
        throw std::runtime_error(fstring("chr {} not in bigwig ({})", chr_id, available));
    }

    std::tuple<std::vector<int64_t>, std::vector<int64_t>> preparse_locs(
        const std::vector<std::string>& chr_ids,
        const std::vector<int64_t>& starts={},
        const std::vector<int64_t>& ends={},
        const std::vector<int64_t>& centers={},
        int64_t span = -1
    ) {
        std::vector<int64_t> preparsed_starts;
        std::vector<int64_t> preparsed_ends;
        if (span >= 0) {
            uint8_t starts_specified = starts.empty() ? 0 : 1;
            uint8_t ends_specified = ends.empty() ? 0 : 1;
            uint8_t centers_specified = centers.empty() ? 0 : 1;
            if (starts_specified + ends_specified + centers_specified != 1) {
                throw std::runtime_error("either starts/ends/centers must be specified when using span");
            } else if (starts_specified != 0) {
                preparsed_starts = starts;
                preparsed_ends.resize(starts.size());
                for (uint64_t i = 0; i < starts.size(); ++i) {
                    preparsed_ends[i] = starts[i] + span;
                }
            } else if (ends_specified != 0) {
                preparsed_ends = ends;
                preparsed_starts.resize(ends.size());
                for (uint64_t i = 0; i < ends.size(); ++i) {
                    preparsed_starts[i] = ends[i] - span;
                }
            } else {
                preparsed_starts.resize(centers.size());
                preparsed_ends.resize(centers.size());
                for (uint64_t i = 0; i < centers.size(); ++i) {
                    preparsed_starts[i] = centers[i] - span / 2;
                    preparsed_ends[i] = centers[i] + (span + 1) / 2;
                }
            }
        } else if (starts.empty() || ends.empty()) {
            throw std::runtime_error("either starts+ends or starts/ends/centers+span must be specified");
        } else {
            preparsed_starts = starts;
            preparsed_ends = ends;
        }
        if (chr_ids.size() != preparsed_starts.size() || chr_ids.size() != preparsed_ends.size()) {
            throw std::runtime_error("length mismatch between chr_ids and starts/ends/centers");
        }
        return {preparsed_starts, preparsed_ends};
    }

    std::vector<Loc> parse_locs(
        const std::vector<std::string>& chr_ids,
        const std::vector<int64_t>& starts,
        const std::vector<int64_t>& ends,
        double bin_size = 1.0,
        int64_t bin_count = -1,
        bool full_bin = false
    ) {
        if (chr_ids.size() != starts.size() || (!ends.empty() && chr_ids.size() != ends.size())) {
            throw std::runtime_error("length mismatch between chr_ids, starts or ends");
        }
        std::vector<Loc> locs(chr_ids.size());
        std::set<int64_t> binned_spans;
        for (uint64_t i = 0; i < chr_ids.size(); ++i) {
            Loc loc;
            loc.chr_index = parse_chr(chr_ids[i]).chr_index;
            loc.start = starts[i];
            loc.end = ends[i];
            if (loc.start > loc.end) {
                throw std::runtime_error(fstring("loc {}:{}-{} at index {} invalid", chr_ids[i], loc.start, loc.end, i));
            }
            loc.binned_start = static_cast<int64_t>(std::floor(loc.start / bin_size) * bin_size);
            loc.binned_end = full_bin
                ? static_cast<int64_t>(std::ceil(loc.end / bin_size) * bin_size)
                : static_cast<int64_t>(std::floor(loc.end / bin_size) * bin_size);
            locs[i] = loc;
            binned_spans.insert(loc.binned_end - loc.binned_start);
        }
        if (bin_count < 0) bin_count = static_cast<int64_t>(std::floor(*binned_spans.rbegin() / bin_size));
        std::sort(locs.begin(), locs.end(), [](const Loc& a, const Loc& b) {
            return std::tie(a.chr_index, a.binned_start, a.binned_end) < std::tie(b.chr_index, b.binned_start, b.binned_end);
        });
        for (uint64_t i = 0; i < chr_ids.size(); ++i) {
            auto& loc = locs[i];
            loc.bin_size = static_cast<double>(loc.binned_end - loc.binned_start) / bin_count;
            loc.values_start_index = i * bin_count;
            loc.values_end_index = (i + 1) * bin_count;
        }
        return locs;
    }

    uint64_t get_coverage(const std::vector<Loc>& locs) {
        uint64_t coverage = 0;
        for (const auto& loc : locs) {
            coverage += (loc.binned_end - loc.binned_start);
        }
        return coverage;
    }

    std::vector<float> read_signal(
        const std::vector<std::string>& chr_ids,
        const std::vector<int64_t>& starts = {},
        const std::vector<int64_t>& ends = {},
        const std::vector<int64_t>& centers = {},
        int64_t span = -1,
        double bin_size = 1.0,
        int64_t bin_count = -1,
        std::string bin_mode = "mean",
        bool full_bin = false,
        float def_value = 0.0f,
        int32_t zoom = -1,
        std::function<void(uint64_t, uint64_t)> progress = nullptr) {

        auto [preparsed_starts, preparsed_ends] = preparse_locs(chr_ids, starts, ends, centers, span);
        auto locs = parse_locs(chr_ids, preparsed_starts, preparsed_ends, bin_size, bin_count, full_bin);
        ProgressTracker tracker(get_coverage(locs), progress);

        if (type == "bigbed") zoom = -1;
        int32_t zoom_index = zoom < 0 ? -1 : zoom > 0 ? zoom - 1 : select_zoom(bin_size);
        uint64_t tree_offset = (zoom_index < 0) ?
            main_header.full_index_offset + 48 : 
            zoom_headers[zoom_index].index_offset + 48;
        TreeNodesGenerator tree_nodes(*file, locs, tree_offset);
        
        if (type == "bigbed") {
            return pileup_entries_at_locs(
                *file,
                main_header.uncompress_buffer_size,
                locs,
                tree_nodes,
                def_value,
                auto_sql,
                parallel,
                tracker
            );
        } else if (bin_mode == "single" || bin_size == 1) {
            return read_signal_at_locs(
                *file,
                main_header.uncompress_buffer_size,
                locs,
                tree_nodes,
                def_value,
                zoom_index,
                parallel,
                tracker
            );
        } else {
            return read_signal_stats_at_locs(
                *file,
                main_header.uncompress_buffer_size,
                locs,
                tree_nodes,
                bin_mode,
                def_value,
                zoom_index,
                parallel,
                tracker
            );
        }

    }

    std::vector<float> quantify(
        const std::vector<std::string>& chr_ids,
        const std::vector<int64_t>& starts = {},
        const std::vector<int64_t>& ends = {},
        const std::vector<int64_t>& centers = {},
        int64_t span = -1,
        double bin_size = 1.0,
        bool full_bin = false,
        float def_value = 0.0f,
        std::string reduce = "mean",
        int32_t zoom = -1,
        std::function<void(uint64_t, uint64_t)> progress = nullptr) {

        auto [preparsed_starts, preparsed_ends] = preparse_locs(chr_ids, starts, ends, centers, span);
        auto locs = parse_locs(chr_ids, preparsed_starts, preparsed_ends, bin_size, 1, full_bin);
        ProgressTracker tracker(get_coverage(locs), progress);

        if (type == "bigbed") zoom = -1;
        int32_t zoom_index = zoom < 0 ? -1 : zoom > 0 ? zoom - 1 : select_zoom(bin_size);
        uint64_t tree_offset = (zoom_index < 0) ?
            main_header.full_index_offset + 48 : 
            zoom_headers[zoom_index].index_offset + 48;
        TreeNodesGenerator tree_nodes(*file, locs, tree_offset);

        if (type == "bigbed") {
            return pileup_stats_entries_at_locs(
                *file,
                main_header.uncompress_buffer_size,
                locs,
                tree_nodes,
                def_value,
                reduce,
                auto_sql,
                parallel,
                tracker
            );
        } else {
            return read_stats_at_locs(
                *file,
                main_header.uncompress_buffer_size,
                locs,
                tree_nodes,
                def_value,
                reduce,
                zoom_index,
                parallel,
                tracker
            );
        }

    }

    std::vector<float> profile(
        const std::vector<std::string>& chr_ids,
        const std::vector<int64_t>& starts = {},
        const std::vector<int64_t>& ends = {},
        const std::vector<int64_t>& centers = {},
        int64_t span = -1,
        double bin_size = 1.0,
        int64_t bin_count = -1,
        std::string bin_mode = "mean",
        bool full_bin = false,
        float def_value = 0.0f,
        std::string reduce = "mean",
        int32_t zoom = -1,
        std::function<void(uint64_t, uint64_t)> progress = nullptr) {

        auto values = read_signal(chr_ids, starts, ends, centers, span, bin_size, bin_count, bin_mode, full_bin, def_value, zoom, progress);

        uint64_t row_count = chr_ids.size();
        uint64_t col_count = values.size() / row_count;
        std::vector<FullValueStats> stats(col_count);
        for (uint64_t col = 0; col < col_count; ++col) {
            for (uint64_t row = 0; row < row_count; ++row) {
                auto value = values[row * col_count + col];
                if (std::isnan(value)) continue;
                stats[col].count += 1;
                stats[col].sum += value;
                stats[col].sum_squared += value * value;
                if (value < stats[col].min || std::isnan(stats[col].min)) stats[col].min = value;
                if (value > stats[col].max || std::isnan(stats[col].max)) stats[col].max = value;
            }
        }
        std::vector<float> profile(col_count, def_value);
        for (uint64_t col = 0; col < col_count; ++col) {
            if (stats[col].count == 0) continue;
            if (reduce == "mean") {
                profile[col] = stats[col].sum / stats[col].count;
            } else if (reduce == "sd") {
                float mean = stats[col].sum / stats[col].count;
                profile[col] = std::sqrt((stats[col].sum_squared / stats[col].count) - (mean * mean));
            } else if (reduce == "sem") {
                float mean = stats[col].sum / stats[col].count;
                float sd = std::sqrt((stats[col].sum_squared / stats[col].count) - (mean * mean));
                profile[col] = sd / std::sqrt(stats[col].count);
            } else if (reduce == "sum") {
                profile[col] = stats[col].sum;
            } else if (reduce == "min") {
                profile[col] = stats[col].min;
            } else if (reduce == "max") {
                profile[col] = stats[col].max;
            } else {
                throw std::runtime_error("reduce " + reduce + " invalid");
            }
        }
        return profile;

    }

    std::vector<std::vector<BedEntry>> read_entries(
        const std::vector<std::string>& chr_ids = {},
        const std::vector<int64_t>& starts = {},
        const std::vector<int64_t>& ends = {},
        const std::vector<int64_t>& centers = {},
        int64_t span = -1,
        std::function<void(uint64_t, uint64_t)> progress = nullptr
    ) {

        if (type != "bigbed") throw std::runtime_error("read_entries only for bigbed");

        double bin_size = 1.0;
        auto locs = parse_locs(chr_ids, starts, ends, span, bin_size);
        ProgressTracker tracker(get_coverage(locs), progress);

        uint64_t tree_offset = main_header.full_index_offset + 48;
        TreeNodesGenerator tree_nodes(*file, locs, tree_offset);

        return read_entries_at_locs(
            *file,
            main_header.uncompress_buffer_size,
            locs,
            tree_nodes,
            auto_sql,
            parallel,
            tracker
        );

    }

    void to_bedgraph(
        const std::string& output_path,
        const std::vector<std::string>& chr_ids = {},
        int32_t zoom = -1,
        std::function<void(uint64_t, uint64_t)> progress = nullptr
    ) {

        if (type != "bigwig") throw std::runtime_error("to_bedgraph only for bigwig");

        std::vector<Loc> locs;
        locs.reserve(chr_ids.empty() ? chr_map.size() : chr_ids.size());
        for (auto chr_id : chr_ids.empty() ? chr_map.keys() : chr_ids) {
            auto chr_entry = parse_chr(chr_id);
            Loc loc;
            loc.chr_index = chr_entry.chr_index;
            loc.start = 0;
            loc.binned_start = 0;
            loc.end = chr_entry.chr_size;
            loc.binned_end = chr_entry.chr_size;
            locs.push_back(loc);
        }
        ProgressTracker tracker(get_coverage(locs), progress);

        auto output_file = open_file(output_path, "w");
        auto write_line = [&](std::string chr_id, uint32_t start, uint32_t end, float value) {
            std::string line =
                chr_id + "\t" +
                std::to_string(start) + "\t" +
                std::to_string(end) + "\t" +
                std::to_string(value) + "\n";
            output_file->write_string(line);
        };

        int32_t zoom_index = zoom <= 0 ? -1 : zoom - 1;
        uint64_t tree_offset = (zoom_index < 0) ?
            main_header.full_index_offset + 48 : 
            zoom_headers[zoom_index].index_offset + 48;
        TreeNodesGenerator tree_nodes(*file, locs, tree_offset);
        for (auto& node_with_locs : tree_nodes) {
            tracker.update(tree_nodes.coverage);
            DataTreeLeaf node = node_with_locs.node;
            ByteArray buffer = file->read(node.data_size, node.data_offset).get();
            if (main_header.uncompress_buffer_size > 0) buffer = buffer.decompress(main_header.uncompress_buffer_size);

            DataIntervalsGenerator data_intervals(node, buffer, zoom_index >= 0);
            for (auto& interval : data_intervals) {
                std::string chr_id = chr_tree[interval.chr_index].key;
                write_line(chr_id, interval.start, interval.end, interval.value);
            }
        }
        tracker.done();

    }

    void to_wig(
        const std::string& output_path,
        const std::vector<std::string>& chr_ids = {},
        int32_t zoom = -1,
        std::function<void(uint64_t, uint64_t)> progress = nullptr
    ) {

        if (type != "bigwig") throw std::runtime_error("to_wig only for bigwig");

        std::vector<Loc> locs;
        locs.reserve(chr_ids.empty() ? chr_map.size() : chr_ids.size());
        for (auto chr_id : chr_ids.empty() ? chr_map.keys() : chr_ids) {
            auto chr_entry = parse_chr(chr_id);
            Loc loc;
            loc.chr_index = chr_entry.chr_index;
            loc.start = 0;
            loc.binned_start = 0;
            loc.end = chr_entry.chr_size;
            loc.binned_end = chr_entry.chr_size;
            locs.push_back(loc);
        }
        ProgressTracker tracker(get_coverage(locs), progress);

        auto output_file = open_file(output_path, "w");
        auto write_header_line = [&](std::string chr_id, uint32_t start, int64_t span) {
            std::string line =
                "fixedStep chrom=" + chr_id +
                " start=" + std::to_string(start + 1) +
                " step=" + std::to_string(span) +
                " span=" + std::to_string(span) + "\n";
            output_file->write_string(line);
        };
        
        int32_t zoom_index = zoom <= 0 ? -1 : zoom - 1;
        uint64_t tree_offset = (zoom_index < 0) ?
            main_header.full_index_offset + 48 : 
            zoom_headers[zoom_index].index_offset + 48;
        TreeNodesGenerator tree_nodes(*file, locs, tree_offset);
        for (auto& node_with_locs : tree_nodes) {
            tracker.update(tree_nodes.coverage);
            DataTreeLeaf node = node_with_locs.node;
            ByteArray buffer = file->read(node.data_size, node.data_offset).get();
            if (main_header.uncompress_buffer_size > 0) buffer = buffer.decompress(main_header.uncompress_buffer_size);
            
            int64_t span = -1;
            DataIntervalsGenerator data_intervals(node, buffer, zoom_index >= 0);
            for (auto& interval : data_intervals) {
                std::string chr_id = chr_tree[interval.chr_index].key;
                if (interval.end - interval.start != span) {
                    span = interval.end - interval.start;
                    write_header_line(chr_id, interval.start, span);
                }
                output_file->write_string(std::to_string(interval.value) + "\n");
            }
        }
        tracker.done();

    }

    void to_bed(
        const std::string& output_path,
        const std::vector<std::string>& chr_ids = {},
        uint64_t col_count = 0,
        std::function<void(uint64_t, uint64_t)> progress = nullptr
    ) {

        if (type != "bigbed") throw std::runtime_error("to_bed only for bigbed");
        if (col_count == 0) col_count = main_header.field_count;
        if (col_count > main_header.field_count) {
            throw std::runtime_error(fstring("col_count {} exceeds number of fields {}", col_count, main_header.field_count));
        }

        std::vector<Loc> locs;
        locs.reserve(chr_ids.empty() ? chr_map.size() : chr_ids.size());
        for (auto chr_id : chr_ids.empty() ? chr_map.keys() : chr_ids) {
            auto chr_entry = parse_chr(chr_id);
            Loc loc;
            loc.chr_index = chr_entry.chr_index;
            loc.start = 0;
            loc.binned_start = 0;
            loc.end = chr_entry.chr_size;
            loc.binned_end = chr_entry.chr_size;
            locs.push_back(loc);
        }
        ProgressTracker tracker(get_coverage(locs), progress);

        auto output_file = open_file(output_path, "w");

        uint64_t tree_offset = main_header.full_index_offset + 48;
        TreeNodesGenerator tree_nodes(*file, locs, tree_offset);
        for (auto& node_with_locs : tree_nodes) {
            tracker.update(tree_nodes.coverage);
            DataTreeLeaf node = node_with_locs.node;
            auto buffer = file->read(node.data_size, node.data_offset).get();
            if (main_header.uncompress_buffer_size > 0) buffer = buffer.decompress(main_header.uncompress_buffer_size);
            BedEntriesGenerator bed_entries(buffer, auto_sql);
            for (auto& entry : bed_entries) {
                std::string chr_id = chr_tree[entry.chr_index].key;
                std::string line =
                    col_count == 1 ? chr_id :
                    col_count == 2 ? chr_id + "\t" + std::to_string(entry.start) :
                    chr_id + "\t" + std::to_string(entry.start) + "\t" + std::to_string(entry.end);
                uint64_t col_index = 3;
                for (const auto& field : entry.fields) {
                    if (col_index >= col_count) break;
                    line += "\t" + field.second;
                    col_index += 1;
                }
                line += "\n";
                output_file->write_string(line);
            }
        }
        tracker.done();

    }

};
