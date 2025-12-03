#include <stdio.h>

void bubbleSort(int arr[], int n) {
    for (int i = 0; i < n - 1; i++)
        for (int j = 0; j < n - i - 1; j++)
            if (arr[j] > arr[j + 1]) {
                int temp = arr[j];
                arr[j] = arr[j + 1];
                arr[j + 1] = temp;
            }
}

int main() {
    int arr[1000];
    for (int i = 0; i < 1000; i++)
        arr[i] = 1000 - i;
    bubbleSort(arr, 1000);
    printf("%d\n", arr[0]);
    return 0;
}
