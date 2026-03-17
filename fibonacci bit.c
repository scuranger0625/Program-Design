#include <stdio.h>
#define MAXK 100  // 給一個常數名稱

// 定義一個陣列來存儲 Fibonacci 字串的長度 ex:len[0], len[1], len[2] ... len[99]
unsigned long long len[MAXK];

// 建立函式 input k = 第幾層 p = 第幾個位置
char findBit(int k, unsigned long long p){
    // 只要還沒縮小至 s1 s2 就繼續縮小
    while (k>2){
        // 判斷落在：S(k-2) 還是 S(k-1)   
        if(p <= len[k-2]) { 
            k = k-2; 
        }
        // 在 s2
        else { p = p-len[k-2];
            k = k-1;
        } 

    }
    
    // 當 k=1 或 k=2 就可以直接回傳答案了
    if ( k==1){
        return '0';
    }
    
    else{
        return '1';
    }
    
}

int main(){
    int q; // q = 問題數量
    int k; // k = 第幾層
    unsigned long long p; // p = 第幾個位置

    len[1] = 1; // s1 的長度
    len[2] = 1; // s2 的長度
    
    // Fibonacci 字串的長度是前兩個長度的和
    for (int i=3; i<MAXK; i++){
        len[i] = len[i-1] + len[i-2]; 
    }
    
    scanf("%d", &q); // 輸入問題數量

    while (q--){
        scanf("%d %llu", &k, &p);
        printf("%c\n", findBit(k, p)); // 輸出答案
    }
    
    return 0;
}