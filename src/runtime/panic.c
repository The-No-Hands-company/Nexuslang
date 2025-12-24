#include <stdio.h>
#include <stdlib.h>

void nlpl_panic(char* message) {
    fprintf(stderr, "Panic: %s\n", message);
    exit(1);
}
