#include <fmt/format.h>
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <stdexcept>
#include <utility>
#include <vector>

using namespace pybind11;

struct Chessboard {
  private:
    static constexpr bool left_player  = 1;
    static constexpr bool right_player = 0;

    static constexpr int up_direction    = 0;
    static constexpr int down_direction  = 1;
    static constexpr int left_direction  = 2;
    static constexpr int right_direction = 3;

    struct Chessman {
        bool belong;
        unsigned value;
    };

    Chessman board[4][8];

    // random position sequence
    std::vector<int> array;

  public:
    // copies given seq to this->array
    Chessboard(std::vector<int> array) {

        // this->array.resize(len(array));
        this->array = array;

        for (auto y = 0; y < 4; y++) {
            for (auto x = 0; x < 8; x++) {
                board[y][x] = Chessman{x < 4 ? left_player : right_player, 0};
            }
        }
    }
    void add_dbg(bool _, tuple position, int value) {
        int y                    = cast<int>(position[0]);
        int x                    = cast<int>(position[1]);
        this->board[y][x].belong = _;
        this->board[y][x].value  = value;
    }
    void add1(bool belong, tuple position) { this->add(belong, position, 1); }
    void add(bool _, tuple position, int value) {
        // in fact, first arg is useless,
        // but to keep the same interface with python version we keep it.
        int y       = cast<int>(position[0]);
        int x       = cast<int>(position[1]);
        bool belong = x < 4 ? left_player : right_player;

        this->board[y][x].belong = belong;
        this->board[y][x].value  = value;
    }
    bool move(bool belong, object maybe_none) {

        bool change = false;

        if (maybe_none.is_none()) { return false; }
        int direction = cast<int>(maybe_none);

        auto value   = [&](int y, int x) -> unsigned & { return board[y][x].value; };
        auto is_mine = [&](int y, int x) {
            return board[y][x].belong == belong;
        };
        auto move_one = [&](int y_src, int x_src, int y_dst, int x_dst) {
            assert((y_src == y_dst) or (x_src == x_dst));
            assert(board[y_dst][x_dst].value == 0);
            assert(is_mine(y_dst, x_dst));

            if (y_src == y_dst and x_src == x_dst) {
                return true;
            }

            board[y_dst][x_dst].value  = board[y_src][x_src].value;
            board[y_src][x_src].value  = 0;
            board[y_src][x_src].belong = x_src < 4 ? left_player : right_player;

            return is_mine(y_src, x_src);
        };
        auto eat_one = [&](int y_src, int x_src, int y_dst, int x_dst) {
            assert((y_src == y_dst) or (x_src == x_dst));
            assert(value(y_dst, x_dst) != 0);
            assert(value(y_dst, x_dst) == value(y_src, x_src));
            assert(std::abs(y_dst - y_src) + std::abs(x_dst - x_src) != 0);

            board[y_dst][x_dst].value += 1;
            board[y_dst][x_dst].belong = belong;
            board[y_src][x_src].value  = 0;
            board[y_src][x_src].belong = x_src < 4 ? left_player : right_player;

            return is_mine(y_src, x_src);
        };
        auto move_updown = [&](int scan_step, int scan_start, int scan_end) {
            auto test_scan = [&](int y) {
                if (scan_step > 0) {
                    return y < scan_end;
                } else {
                    return y > scan_end;
                }
            };
            const int my_field_begin = 4 * (belong != left_player);
            const int my_field_end   = 4 + my_field_begin;
            const int en_field_begin = 4 * (belong != right_player);
            const int en_field_end   = 4 + en_field_begin;
            for (auto x = my_field_begin; x < my_field_end; x++) {
                int should_check_for_eat = scan_start - scan_step;
                for (auto y = scan_start; test_scan(y); y += scan_step) {

                    if (not is_mine(y, x)) {
                        assert(value(y, x) != 0);
                        should_check_for_eat = y;
                        continue;
                    }
                    if (value(y, x) == 0) { continue; }

                    // is_mine and != 0

                    if (value(y, x) == value(should_check_for_eat, x)) {
                        eat_one(y, x, should_check_for_eat, x);
                        change = true;
                        // can't be eaten again
                        should_check_for_eat += scan_step;
                        continue;
                    }

                    // not equ

                    if (is_mine(should_check_for_eat, x) and value(should_check_for_eat, x) == 0) {
                        // my space, move to
                        // can be eaten
                        change = true;
                        move_one(y, x, should_check_for_eat, x);
                        continue;
                    }
                    should_check_for_eat += scan_step;
                    if (should_check_for_eat == y) { continue; }
                    move_one(y, x, should_check_for_eat, x);
                    change = true;
                }
            }
            for (auto x = en_field_begin; x < en_field_end; x++) {
                for (auto y = scan_start; test_scan(y); y += scan_step) {
                    if (!is_mine(y, x)) {
                        continue;
                    }
                    if (board[y - scan_step][x].value == board[y][x].value) {
                        eat_one(y, x, y - scan_step, x);
                        change = true;
                        // my previous place must be 0 and can not be eat, so we can skip.
                        y += scan_step;
                    }
                }
            }
        };
        auto move_leftright = [&](int scan_step, int scan_start, int scan_end) {
            auto test_scan = [&](int x) {
                if (scan_step > 0) {
                    return x < scan_end;
                } else {
                    return x > scan_end;
                }
            };
            for (auto y = 0; y < 4; y++) {
                int should_check_for_eat = scan_start - scan_step;
                for (auto x = scan_start; test_scan(x); x += scan_step) {
                    if (!is_mine(y, x)) {
                        should_check_for_eat = x;
                        continue;
                    }
                    if (board[y][x].value == 0) { continue; }
                    if (value(y, should_check_for_eat) == 0 and is_mine(y, should_check_for_eat)) {
                        // move to should_check_for_eat
                        change = true;
                        if (not move_one(y, x, y, should_check_for_eat)) {
                            should_check_for_eat = x;
                        }
                        continue;
                    }
                    if (board[y][x].value == board[y][should_check_for_eat].value) {
                        // eat
                        change = true;
                        if (not eat_one(y, x, y, should_check_for_eat)) {
                            should_check_for_eat = x;
                        } else {
                            should_check_for_eat += scan_step;
                        }
                        continue;
                    }
                    should_check_for_eat += scan_step;
                    if (should_check_for_eat == x) { continue; }
                    if (not move_one(y, x, y, should_check_for_eat)) {
                        should_check_for_eat = x;
                    }
                    change = true;
                }
            }
        };
        auto move_to_up    = [&]() { move_updown(1, 1, 4); };
        auto move_to_down  = [&]() { move_updown(-1, 2, -1); };
        auto move_to_left  = [&]() { move_leftright(1, 1, 8); };
        auto move_to_right = [&]() { move_leftright(-1, 6, -1); };
        switch (direction) {
        case up_direction:
            move_to_up();
            break;
        case down_direction:
            move_to_down();
            break;
        case left_direction:
            move_to_left();
            break;
        case right_direction:
            move_to_right();
            break;
        default:
            break;
        }
        return change;
    }
    bool getBelong(tuple position) {
        int y = cast<int>(position[0]);
        int x = cast<int>(position[1]);

        return board[y][x].belong;
    }
    int getValue(tuple position) {
        int y = cast<int>(position[0]);
        int x = cast<int>(position[1]);

        return board[y][x].value;
    }
    list getScore(bool belong) {
        list result;
        for (auto y = 0; y < 4; y++) {
            for (auto x = 0; x < 8; x++) {
                if (board[y][x].belong == belong and board[y][x].value != 0) {
                    result.append(board[y][x].value);
                }
            }
        }
        return result;
    }
    list getNone(bool belong) {
        list result;
        auto x_range_start = (belong == left_player) ? 0 : 4;
        auto x_range_end   = x_range_start + 4;
        for (auto y = 0; y < 4; y++) {
            for (auto x = x_range_start; x < x_range_end; x++) {
                if (board[y][x].belong == belong and board[y][x].value == 0) {
                    result.append(make_tuple(y, x));
                }
            }
        }
        return result;
    }
    tuple getNext(bool belong, int currentRound) {
        std::vector<std::tuple<int, int>> available;

        auto x_range_start = (belong == left_player) ? 0 : 4;
        auto x_range_end   = x_range_start + 4;
        for (auto y = 0; y < 4; y++) {
            for (auto x = x_range_start; x < x_range_end; x++) {
                if (board[y][x].belong == belong and board[y][x].value == 0) {
                    available.push_back(std::make_tuple(y, x));
                    if (currentRound == 0) {
                        return make_tuple(y, x);
                    }
                    currentRound -= 1;
                }
            }
        }
        if (available.size() == 0) {
            return make_tuple();
        }
        currentRound = currentRound % available.size();
        auto result  = available.at(currentRound);
        return make_tuple(std::get<0>(result), std::get<1>(result));
    }
    int _getArray(int index) {
        return this->array.at(index);
    }
    std::string __repr__() {
        auto s = [&](int y, int x) {
            return fmt::format(
                "{}{:02d}",
                board[y][x].belong == left_player ? '+' : '-',
                board[y][x].value);
        };
        return fmt::format(
            "{} {} {} {} {} {} {} {}\n"
            "{} {} {} {} {} {} {} {}\n"
            "{} {} {} {} {} {} {} {}\n"
            "{} {} {} {} {} {} {} {}",
            s(0, 0), s(0, 1), s(0, 2), s(0, 3), s(0, 4), s(0, 5), s(0, 6), s(0, 7),
            s(1, 0), s(1, 1), s(1, 2), s(1, 3), s(1, 4), s(1, 5), s(1, 6), s(1, 7),
            s(2, 0), s(2, 1), s(2, 2), s(2, 3), s(2, 4), s(2, 5), s(2, 6), s(2, 7),
            s(3, 0), s(3, 1), s(3, 2), s(3, 3), s(3, 4), s(3, 5), s(3, 6), s(3, 7));
    }

    Chessboard copy() {
        return Chessboard(*this);
    }
};

PYBIND11_MODULE(libchessboard, m) {
    class_<Chessboard>(m, "Chessboard")
        .def(init<std::vector<int>>())
        .def("add", &Chessboard::add)
        .def("add", &Chessboard::add1)
        .def("add_dbg", &Chessboard::add_dbg)
        .def("move", &Chessboard::move)
        .def("copy", &Chessboard::copy)
        .def("getBelong", &Chessboard::getBelong)
        .def("getValue", &Chessboard::getValue)
        .def("getScore", &Chessboard::getScore)
        .def("getNone", &Chessboard::getNone)
        .def("getNext", &Chessboard::getNext)
        .def("_getArray", &Chessboard::_getArray)
        .def("_add_dbg", &Chessboard::add_dbg)
        .def("__repr__", &Chessboard::__repr__);
}
