#include <stdio.h>
#include <string.h>

int main() {
    char str[10000];
    for (int i = 0; i < 9999; i++)
        str[i] = 'a' + (i % 26);
    str[9999] = '\0';

    int count = 0;
    for (int i = 0; i < 9999; i++)
        if (str[i] == 'a' || str[i] == 'e' || str[i] == 'i' || str[i] == 'o' || str[i] == 'u')
            count++;

    printf("%d\n", count);
    return 0;
}
