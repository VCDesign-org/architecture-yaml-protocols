#include <stdlib.h>

void* test_memory() {
    // This should be flagged by b-memory-01
    void* ptr = malloc(1024);
    return ptr;
}
