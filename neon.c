#include <stdio.h>

int main(void) {
    long long a, b;
    printf("Enter two numbers: ");
    if (scanf("%lld %lld", &a, &b) != 2) {
        fprintf(stderr, "Error: invalid input.\n");
        return 1;
    }
    long long product = a * b;
    printf("Product: %lld\n", product);
    return 0;
}
