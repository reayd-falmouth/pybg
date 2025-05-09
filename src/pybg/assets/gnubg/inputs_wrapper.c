// inputs_wrapper.c
#include <stdio.h>
#include "eval.h"
#include "inputs.h"

// Wraps the original GNUBG getInputs function for FFI
void call_get_inputs(int board[2][25], int *which, float *out, int n) {
    getInputs(board, which, out);
}
