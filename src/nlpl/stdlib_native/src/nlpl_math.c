/*
 * nlpl_math.c -- NLPL math library wrappers.
 *
 * Thin wrappers over libm functions, providing the "nlpl_" naming convention
 * and a consistent int64_t / double ABI for the NLPL runtime.
 *
 * Link with -lm.
 */

#include "../include/nlpl_runtime.h"

#include <math.h>
#include <stdlib.h>


/* ===========================================================================
 * Basic transcendental / exponential functions
 * =========================================================================*/

double nlpl_sqrt(double x)  { return sqrt(x); }
double nlpl_cbrt(double x)  { return cbrt(x); }
double nlpl_pow(double x, double y) { return pow(x, y); }
double nlpl_exp(double x)   { return exp(x); }
double nlpl_log(double x)   { return log(x); }
double nlpl_log2(double x)  { return log2(x); }
double nlpl_log10(double x) { return log10(x); }


/* ===========================================================================
 * Trigonometric functions
 * =========================================================================*/

double nlpl_sin(double x)   { return sin(x); }
double nlpl_cos(double x)   { return cos(x); }
double nlpl_tan(double x)   { return tan(x); }
double nlpl_asin(double x)  { return asin(x); }
double nlpl_acos(double x)  { return acos(x); }
double nlpl_atan(double x)  { return atan(x); }
double nlpl_atan2(double y, double x) { return atan2(y, x); }
double nlpl_sinh(double x)  { return sinh(x); }
double nlpl_cosh(double x)  { return cosh(x); }
double nlpl_tanh(double x)  { return tanh(x); }


/* ===========================================================================
 * Rounding and truncation
 * =========================================================================*/

double nlpl_floor(double x) { return floor(x); }
double nlpl_ceil(double x)  { return ceil(x);  }
double nlpl_round(double x) { return round(x); }
double nlpl_trunc(double x) { return trunc(x); }
double nlpl_fmod(double x, double y) { return fmod(x, y); }


/* ===========================================================================
 * Absolute value
 * =========================================================================*/

double nlpl_abs_float(double x)
{
    return fabs(x);
}

int64_t nlpl_abs_int(int64_t x)
{
    /* Avoid undefined behaviour for INT64_MIN by using unsigned arithmetic. */
    return (x < 0) ? (int64_t)(-(uint64_t)x) : x;
}


/* ===========================================================================
 * Min / max
 * =========================================================================*/

int64_t nlpl_min_int(int64_t a, int64_t b) { return (a < b) ? a : b; }
int64_t nlpl_max_int(int64_t a, int64_t b) { return (a > b) ? a : b; }
double  nlpl_min_float(double a, double b) { return (a < b) ? a : b; }
double  nlpl_max_float(double a, double b) { return (a > b) ? a : b; }


/* ===========================================================================
 * Classification
 * =========================================================================*/

int nlpl_is_nan(double x) { return isnan(x) ? 1 : 0; }
int nlpl_is_inf(double x) { return isinf(x) ? 1 : 0; }


/* ===========================================================================
 * Integer exponentiation
 * =========================================================================*/

int64_t nlpl_pow_int(int64_t base, int64_t exp)
{
    if (exp < 0) {
        nlpl_panic("nlpl_pow_int: negative exponent");
    }
    int64_t result = 1;
    while (exp > 0) {
        if (exp & 1) {
            result *= base;
        }
        base *= base;
        exp >>= 1;
    }
    return result;
}


/* ===========================================================================
 * Clamp
 * =========================================================================*/

int64_t nlpl_clamp_int(int64_t val, int64_t lo, int64_t hi)
{
    if (val < lo) return lo;
    if (val > hi) return hi;
    return val;
}

double nlpl_clamp_float(double val, double lo, double hi)
{
    if (val < lo) return lo;
    if (val > hi) return hi;
    return val;
}
