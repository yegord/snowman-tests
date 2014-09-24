#include <stdio.h>

int fib(n) {
	if (n < 2) {
		return n;
	} else {
		return fib(n-1) + fib(n-2);
	}
}

int main() {
	printf("%d", fib(5));
}
