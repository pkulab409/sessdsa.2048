#include <array>
#include <boost/python.hpp>
#include <fmt/format.h>
#include <functional>
#include <iostream>
#include <stdexcept>
#include <utility>
#include <vector>

using namespace boost::python;

struct Chessboard {
  private:
    static constexpr bool left_player  = 1;
    static constexpr bool right_player = 0;

    static constexpr int up_direction    = 0;
    static constexpr int down_direction  = 1;
    static constexpr int left_direction  = 2;
    static constexpr int right_direction = 3;

    struct Position {
        int y;
        int x;
        Position operator+(Position delta) {
            return Position{this->y + delta.y,
                            this->x + delta.x};
        }
        Position operator-(Position delta) {
            return Position{this->y - delta.y,
                            this->x - delta.x};
        }
    };

    struct Chessman {
        Position position;
        bool belong;
        unsigned value;
    };

    Chessman board[4][8];

    // random position sequence
    std::vector<int> array;

  public:
    // copies given seq to this->array
    Chessboard(list array) {

        this->array.resize(len(array));
        stl_input_iterator<int> begin(array), end;
        this->array.assign(begin, end);

        // belongs[0].reserve(32);
        // belongs[1].reserve(32);

        for (auto y = 0; y < 4; y++) {
            for (auto x = 0; x < 8; x++) {
                board[y][x] = Chessman{y, x, x < 4 ? left_player : right_player, 0};
            }
        }
    }

    // overload of add
    void add1(bool belong, tuple position) { this->add(belong, position, 1); }

    // add a chessman
    void add(bool _, tuple position, int value) {
        // in fact, first arg is useless,
        // but to keep the same interface with python version we keep it.
        bool belong = extract<int>(position[1]) < 4 ? left_player : right_player;
        Position pos{extract<int>(position[0]), extract<int>(position[1])};

        auto [y, x] = pos;

        // this->belongs[int(belong)].push_back(&this->board[y][x]);
        this->board[y][x].belong = belong;
        this->board[y][x].value  = value;
    }

    // bool move_none(bool belong, object none) {
    //     assert(none.ptr() == Py_None);
    //     return false;
    // }
    bool move(bool belong, object maybe_none) {

        bool change = false;

        if (maybe_none.ptr() == Py_None) { return false; }
        int direction = extract<int>(maybe_none);

        auto is_mine = [&](int y, int x) {
            return board[y][x].belong == belong;
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
                    auto position = Position{y, x};
                    if (!is_mine(y, x)) {
                        assert(board[y][x].value != 0);
                        should_check_for_eat = y;
                        continue;
                    }
                    if (board[y][x].value == 0) { continue; }
                    if (board[should_check_for_eat][x].value == 0 and is_mine(should_check_for_eat, x)) {
                        change                         = true;
                        board[should_check_for_eat][x] = board[y][x];
                        board[y][x].value              = 0;
                        board[y][x].belong             = x < 4 ? left_player : right_player;
                        continue;
                    }
                    if (board[y][x].value == board[should_check_for_eat][x].value) {
                        change                         = true;
                        board[should_check_for_eat][x] = board[y][x];
                        board[should_check_for_eat][x].value += 1;
                        board[y][x].value  = 0;
                        board[y][x].belong = x < 4 ? left_player : right_player;
                        should_check_for_eat += scan_step;
                        continue;
                    }
                    should_check_for_eat += scan_step;
                    if (should_check_for_eat == y) { continue; }
                    change                         = true;
                    board[should_check_for_eat][x] = board[y][x];
                    board[y][x].value              = 0;
                    board[y][x].belong             = x < 4 ? left_player : right_player;
                }
            }
            for (auto x = en_field_begin; x < en_field_end; x++) {
                for (auto y = scan_start; test_scan(y); y += scan_step) {
                    if (!is_mine(y, x)) {
                        continue;
                    }
                    if (board[y - scan_step][x].value == board[y][x].value) {
                        board[y - scan_step][x].belong = belong;
                        board[y - scan_step][x].value += 1;
                        board[y][x].belong = x < 4 ? left_player : right_player;
                        board[y][x].value  = 0;
                        change             = true;
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
                    if (board[y][should_check_for_eat].value == 0 and is_mine(y, should_check_for_eat)) {
                        change                         = true;
                        board[y][should_check_for_eat] = board[y][x];
                        board[y][x].value              = 0;
                        board[y][x].belong             = x < 4 ? left_player : right_player;
                        continue;
                    }
                    if (board[y][x].value == board[y][should_check_for_eat].value) {
                        change                                = true;
                        board[y][should_check_for_eat].belong = belong;
                        board[y][should_check_for_eat].value += 1;
                        board[y][x].value  = 0;
                        board[y][x].belong = x < 4 ? left_player : right_player;
                        should_check_for_eat += scan_step;
                        continue;
                    }
                    should_check_for_eat += scan_step;
                    if (should_check_for_eat == x) { continue; }
                    change                         = true;
                    board[y][should_check_for_eat] = board[y][x];
                    board[y][x].value              = 0;
                    board[y][x].belong             = x < 4 ? left_player : right_player;
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
        int y = extract<int>(position[0]);
        int x = extract<int>(position[1]);

        return board[y][x].belong;
    }
    bool getValue(tuple position) {
        int y = extract<int>(position[0]);
        int x = extract<int>(position[1]);

        return board[y][x].value;
    }
    list getScore(bool belong) {
        list result;
        for (auto y = 0; y < 4; y++) {
            for (auto x = 0; x < 8; x++) {
                result.append(board[y][x].value);
            }
        }
        return result;
    }
    list getNone(bool belong) {
        list result;
        for (auto y = 0; y < 4; y++) {
            for (auto x = 0; x < 8; x++) {
                if (board[y][x].belong == belong and board[y][x].value == 0) {
                    result.append(make_tuple(y, x));
                }
            }
        }
        return result;
    }
    list getNext(bool belong, int currentRound) {
        // auto available = getNone(belong);
        throw std::runtime_error("Not Implemented.");
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

BOOST_PYTHON_MODULE(libchessboard) {
    class_<Chessboard>("Chessboard", init<boost::python::list>())
        .def("add", &Chessboard::add)
        .def("add", &Chessboard::add1)
        .def("move", &Chessboard::move)
        .def("copy", &Chessboard::copy)
        .def("getBelong", &Chessboard::getBelong)
        .def("getValue", &Chessboard::getValue)
        .def("getScore", &Chessboard::getScore)
        .def("getNone", &Chessboard::getNone)
        .def("getNext", &Chessboard::getNext)
        .def("_getArray", &Chessboard::_getArray)
        .def("__repr__", &Chessboard::__repr__);
}
