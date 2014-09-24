CC		= clang
CXX		= clang++
CFLAGS		= -target arm -mfloat-abi=soft -integrated-as -std=c11
CXXFLAGS	= -target arm -mfloat-abi=soft -integrated-as -std=c++11
TARGETS		= 001_hello_world.o 002_gcd.o 003_call_many_args.o 004_for.o 005_if_compound_condition.o 006_while_compound_condition.o 007_calls.o 008_struct.o 009_vector.o 010_compound_condition.o 011_cyclic.o 012_loop_nests.o 013_switch_no_jump_table.o 014_switch_with_jump_table.o 015_tree.o 016_cstring.o 017_int2bool.o 018_misaligned_arg.o 019_a_plus_b.o 020_call_struct.o 021_fib.o

.PHONY: all
all: $(TARGETS)

%.o: src/%.c
	$(CC) -c -o $@ $(CFLAGS) $^

%.o: src/%.cpp
	$(CXX) -c -o $@ $(CXXFLAGS) $^

.PHONY: clean
clean:
	rm -f $(TARGETS)
