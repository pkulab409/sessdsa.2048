#include <bitset>
#include <iomanip>
#include <memory>
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <sstream>
#include <stdexcept>
#include <string>
#include <utility>
#include <vector>

// clang-format off
constexpr char TABLE_LEFT[16][4] = {
/*0000*/ {-1, -1, -1, -1},
/*0001*/ { 0, -1, -1, -1},
/*0010*/ { 1, -1, -1, -1},
/*0011*/ { 0,  1, -1, -1},
/*0100*/ { 2, -1, -1, -1},
/*0101*/ { 0,  2, -1, -1},
/*0110*/ { 1,  2, -1, -1},
/*0111*/ { 0,  1,  2, -1},
/*1000*/ { 3, -1, -1, -1},
/*1001*/ { 0,  3, -1, -1},
/*1010*/ { 1,  3, -1, -1},
/*1011*/ { 0,  1,  3, -1},
/*1100*/ { 2,  3, -1, -1},
/*1101*/ { 0,  2,  3, -1},
/*1110*/ { 1,  2,  3, -1},
/*1111*/ { 0,  1,  2,  3}
};
constexpr char TABLE_RIGHT[16][4] = {
/*0000*/ {-1, -1, -1, -1},
/*0001*/ { 3, -1, -1, -1},
/*0010*/ { 2, -1, -1, -1},
/*0011*/ { 2,  3, -1, -1},
/*0100*/ { 1, -1, -1, -1},
/*0101*/ { 1,  3, -1, -1},
/*0110*/ { 1,  2, -1, -1},
/*0111*/ { 1,  2,  3, -1},
/*1000*/ { 0, -1, -1, -1},
/*1001*/ { 0,  3, -1, -1},
/*1010*/ { 0,  2, -1, -1},
/*1011*/ { 0,  2,  3, -1},
/*1100*/ { 0,  1, -1, -1},
/*1101*/ { 0,  1,  3, -1},
/*1110*/ { 0,  1,  2, -1},
/*1111*/ { 0,  1,  2,  3}
};
// clang-format on

using namespace pybind11;
constexpr bool left_player  = 1;
constexpr bool right_player = 0;

constexpr int up_direction    = 0;
constexpr int down_direction  = 1;
constexpr int left_direction  = 2;
constexpr int right_direction = 3;

struct Chessman {
    bool belong;
    unsigned char value;
};

struct Chessboard {
  private:
    Chessman board[4][8];

    // random position sequence
    std::shared_ptr<std::vector<int>> array;

    std::bitset<8> occupied[4];

    tuple decisions[2];
    float times[2];

  public:
    // copies given seq to this->array
    Chessboard(std::vector<int> &&array) : array(new std::vector<int>(std::move(array))) {
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
        if (value != 0) {
            occupied[y][x] = true;
        } else {
            occupied[y][x] = false;
        }
    }
    void add1(bool belong, tuple position) { this->add(belong, position, 1); }
    void add(bool _, tuple position, int value) {

        // _ means who did this decision
        // belong means who has the new chessman

        int y       = cast<int>(position[0]);
        int x       = cast<int>(position[1]);
        bool belong = x < 4 ? left_player : right_player;

        this->board[y][x].belong = belong;
        this->board[y][x].value  = value;

        // decisions[_] = position;

        if (value != 0) {
            occupied[y][x] = true;
        } else {
            occupied[y][x] = false;
        }
    }
    bool move(bool belong, object maybe_none) {

        bool change = false;

        if (maybe_none.is_none()) {
            // decisions[belong] = make_tuple();
            return false;
        }
        int direction = cast<int>(maybe_none);
        // decisions[belong] = make_tuple(direction);

        auto value   = [&](int y, int x) -> unsigned char { return board[y][x].value; };
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
            occupied[y_src][x_src]     = false;
            occupied[y_dst][x_dst]     = true;
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

            occupied[y_src][x_src] = false;
            occupied[y_dst][x_dst] = true;
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
    bool getBelong(tuple position) const {
        int y = cast<int>(position[0]);
        int x = cast<int>(position[1]);

        return board[y][x].belong;
    }
    int getValue(tuple position) const {
        int y = cast<int>(position[0]);
        int x = cast<int>(position[1]);

        return board[y][x].value;
    }
    list getScore(bool belong) const {
        list result;
        for (auto y = 0; y < 4; y++) {
            for (auto x = 0; x < 8; x++) {
                if (board[y][x].belong == belong and board[y][x].value != 0) {
                    result.append(board[y][x].value);
                }
            }
        }
        result.attr("sort")();
        return result;
    }
    list getNone(bool belong) const {
        list result;
        auto x_range_start = (belong == left_player) ? 0 : 4;
        auto x_range_end   = x_range_start + 4;
        for (auto y = 0; y < 4; y++) {
            for (auto x = x_range_start; x < x_range_end; x++) {
                if (board[y][x].value == 0) { // board[y][x].belong == belong and
                    result.append(make_tuple(y, x));
                }
            }
        }
        return result;
    }
    tuple getNext(bool belong, int currentRound) const {
        std::vector<std::tuple<int, int>> available;
        char spare[4]    = {0, 0, 0, 0};
        char total_spare = 0;
        currentRound     = this->array->at(currentRound % this->array->size());
        if (belong) {
            // 因为左玩家是低4位, 二进制的显示顺序和棋盘的左右顺序是反的
            std::bitset<8> mask(0b11110000);
            for (auto y = 0; y < 4; y++) {
                spare[y] = (~(occupied[y] | mask)).count();
                total_spare += spare[y];
            }
            // 没有空位
            if (total_spare == 0) {
                return make_tuple();
            }
            int y{0};
            currentRound = currentRound % total_spare;
            // Duff's Device, to make if-else easier
            switch (0) {
            case 0:
                if (currentRound < spare[0]) {
                    break;
                }
                currentRound -= spare[0];
                if (currentRound < spare[1]) {
                    y = 1;
                    break;
                }
                currentRound -= spare[1];
                if (currentRound < spare[2]) {
                    y = 2;
                    break;
                }
                currentRound -= spare[2];
                y = 3;
                break; // to aviod fall-through warning
            }
            int x = TABLE_LEFT[(~(occupied[y] | mask)).to_ulong()][currentRound];
            assert(x != -1);
            return make_tuple(y, x);
        } else {
            std::bitset<8> mask(0b00001111);
            for (auto y = 3; y >= 0; y--) {
                spare[y] = (~(occupied[y] | mask)).count();
                total_spare += spare[y];
            }
            // 没有空位
            if (total_spare == 0) {
                return make_tuple();
            }
            int y{3};
            currentRound = currentRound % total_spare;
            // Duff's Device, to make if-else easier
            switch (0) {
            case 0:
                if (currentRound < spare[3]) {
                    break;
                }
                currentRound -= spare[3];
                if (currentRound < spare[2]) {
                    y = 2;
                    break;
                }
                currentRound -= spare[2];
                if (currentRound < spare[1]) {
                    y = 1;
                    break;
                }
                currentRound -= spare[1];
                y = 0;
                break; // to aviod fall-through warning
            }
            int x = 7 - TABLE_RIGHT[((~(occupied[y] | mask)) >> 4).to_ulong()][currentRound];
            assert(x != 8);
            return make_tuple(y, x);
        }
        throw std::runtime_error("unknown error");
    }
    int _getArray(int index) const {
        return this->array->at(index);
    }
    tuple getDecision(bool belong) {
        return decisions[belong];
    }
    void updateDecision(bool belong, tuple decision) {
        decisions[belong] = decision;
    }
    void updateTime(bool belong, float time) {
        this->times[belong] = time;
    }
    float getTime(bool belong) {
        return this->times[belong];
    }
    std::string __repr__() {
        std::ostringstream result;
        auto s = [&](int y, int x) {
            result << (board[y][x].belong == left_player ? '+' : '-');
            if (board[y][x].value < 10) {
                result << '0';
            }
            result << static_cast<int>(board[y][x].value);
            if (x == 7) {
                if (y != 3) {
                    result << '\n';
                }
            } else {
                result << ' ';
            }
        };
        s(0, 0), s(0, 1), s(0, 2), s(0, 3), s(0, 4), s(0, 5), s(0, 6), s(0, 7);
        s(1, 0), s(1, 1), s(1, 2), s(1, 3), s(1, 4), s(1, 5), s(1, 6), s(1, 7);
        s(2, 0), s(2, 1), s(2, 2), s(2, 3), s(2, 4), s(2, 5), s(2, 6), s(2, 7);
        s(3, 0), s(3, 1), s(3, 2), s(3, 3), s(3, 4), s(3, 5), s(3, 6), s(3, 7);
        return result.str();
    }
    constexpr void getAnime() {}
    Chessboard copy() {
        return Chessboard(*this);
    }
    object __copy__() {
        throw std::runtime_error("Surprise, Motherfucker!!!");
    }
    object __deepcopy__(object memo) {
        throw std::runtime_error("Surprise, Motherfucker!!!");
    }
};

PYBIND11_MODULE(libchessboard, m) {
    class_<Chessboard>(m, "Chessboard")
        .def(init<std::vector<int>>())
        .def("add", &Chessboard::add)
        .def("add", &Chessboard::add1)
        .def("move", &Chessboard::move)
        .def("copy", &Chessboard::copy)
        .def("getBelong", &Chessboard::getBelong)
        .def("getValue", &Chessboard::getValue)
        .def("getScore", &Chessboard::getScore)
        .def("getNone", &Chessboard::getNone)
        .def("getNext", &Chessboard::getNext)
        .def("getTime", &Chessboard::getTime)
        .def("getDecision", &Chessboard::getDecision)
        .def("updateDecision", &Chessboard::updateDecision)
        .def("updateTime", &Chessboard::updateTime)
        .def("getAnime", &Chessboard::getAnime)
        .def("__copy__", &Chessboard::__copy__)
        .def("__deepcopy__", &Chessboard::__deepcopy__)
        .def("__repr__", &Chessboard::__repr__);
}
