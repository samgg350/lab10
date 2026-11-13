/*
 * ESE 124 - Exercise 10 - Q5: Remove the Comments - switch AND 2D arrays
 * main.c is GIVEN. You write next_switch(), the two tables and next_by_table() in strip.c.
 *
 * main reads all of code.txt, removes the comments with way 1 AND with way 2, prints the
 * clean code (from way 2) between two marker lines, then COMMENTS= UNCLOSED= AGREE=
 * (AGREE=YES only when both ways give exactly the same result).
 */
#include <stdio.h>
#include <string.h>
#include "strip.h"

int main(void) {
    FILE *fp = fopen("code.txt", "r");
    if (fp == NULL) {
        printf("Cannot open code.txt\n");
        return 1;
    }
    char src[MAX_TEXT], way1[MAX_TEXT], way2[MAX_TEXT];
    size_t len = fread(src, 1, MAX_TEXT - 1, fp);
    fclose(fp);
    src[len] = '\0';

    int c1, c2;
    int open1 = strip_text(src, way1, 0, &c1);           /* WAY 1: switch */
    int open2 = strip_text(src, way2, 1, &c2);           /* WAY 2: tables */

    printf("---- clean code ----\n");
    printf("%s", way2);
    if (len > 0 && way2[strlen(way2) - 1] != '\n')
        printf("\n");
    printf("---- end ----\n");
    printf("COMMENTS=%d\n", c2);
    printf("UNCLOSED=%s\n", open2 ? "YES" : "NO");
    printf("AGREE=%s\n", (strcmp(way1, way2) == 0 && c1 == c2 && open1 == open2) ? "YES" : "NO");
    return 0;
}
