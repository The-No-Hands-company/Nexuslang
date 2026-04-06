/*
 * nxl_runtime.c -- Core NexusLang runtime: error handling, print helpers,
 *                   and type conversion utilities.
 */

#include "../include/nxl_runtime.h"

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <errno.h>


/* ===========================================================================
 * Error handling
 * =========================================================================*/

void nxl_panic(const char *msg)
{
    fprintf(stderr, "Error: %s\n", msg ? msg : "unknown error");
    exit(1);
}

void nxl_assert(int condition, const char *msg)
{
    if (!condition) {
        nxl_panic(msg ? msg : "assertion failed");
    }
}


/* ===========================================================================
 * Print helpers
 * =========================================================================*/

void nxl_print(const char *s)
{
    if (s) {
        fputs(s, stdout);
    }
}

void nxl_println(const char *s)
{
    if (s) {
        puts(s);          /* puts appends '\n' */
    } else {
        putchar('\n');
    }
}

void nxl_print_int(int64_t n)
{
    printf("%lld\n", (long long)n);
}

void nxl_print_float(double d)
{
    /* Use %g so that 1.0 prints as "1" and 1.5 prints as "1.5",
     * matching Python's default float-to-string behaviour. */
    printf("%g\n", d);
}

void nxl_print_bool(int b)
{
    printf("%s\n", b ? "true" : "false");
}


/* ===========================================================================
 * Type conversion
 * =========================================================================*/

char *nxl_int_to_string(int64_t n)
{
    /* Maximum length of a 64-bit decimal integer (including sign) is 20 digits. */
    char buf[24];
    snprintf(buf, sizeof(buf), "%lld", (long long)n);
    char *result = strdup(buf);
    if (!result) {
        nxl_panic("nxl_int_to_string: memory allocation failed");
    }
    return result;
}

char *nxl_float_to_string(double d)
{
    char buf[64];
    snprintf(buf, sizeof(buf), "%g", d);
    char *result = strdup(buf);
    if (!result) {
        nxl_panic("nxl_float_to_string: memory allocation failed");
    }
    return result;
}

char *nxl_bool_to_string(int b)
{
    char *result = strdup(b ? "true" : "false");
    if (!result) {
        nxl_panic("nxl_bool_to_string: memory allocation failed");
    }
    return result;
}

int64_t nxl_string_to_int(const char *s)
{
    if (!s || *s == '\0') {
        return 0;
    }
    char *end = NULL;
    errno = 0;
    long long val = strtoll(s, &end, 10);
    if (errno != 0 || end == s) {
        return 0;
    }
    return (int64_t)val;
}

double nxl_string_to_float(const char *s)
{
    if (!s || *s == '\0') {
        return 0.0;
    }
    char *end = NULL;
    errno = 0;
    double val = strtod(s, &end);
    if (errno != 0 || end == s) {
        return 0.0;
    }
    return val;
}


/* ===========================================================================
 * Version
 * =========================================================================*/

const char *nxl_runtime_version(void)
{
    return "1.0.0";
}
