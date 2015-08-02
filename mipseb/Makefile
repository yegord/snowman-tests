TARGET		= mips-linux-gnu
CC		= $(TARGET)-gcc
CXX		= $(TARGET)-g++
CFLAGS		= -std=c99
CXXFLAGS	= -std=c++98
TARGETS		= 001_hello_world 002_gcd 003_call_many_args 004_for 005_if_compound_condition 006_while_compound_condition 007_calls 008_struct 009_vector 010_compound_condition 011_cyclic 012_loop_nests 013_switch_no_jump_table 014_switch_with_jump_table 015_tree 016_cstring 017_int2bool 018_misaligned_arg 019_a_plus_b 020_call_struct 021_fib

.PHONY: all
all: $(TARGETS)

%: src/%.c
	$(CC) -o $@ $(CFLAGS) $^
	chmod -x $@

%: src/%.cpp
	$(CXX) -o $@ $(CXXFLAGS) $^
	chmod -x $@

.PHONY: clean
clean:
	rm -f $(TARGETS)
