#include <stdio.h>
#include <string.h>

// # 原始輸入字串
char s[25];

// # 當前正在嘗試的字串（把 # 填完後的版本）
char cur[25];

// # 最後答案（合法數量）
long long ans = 0;


// # 將英文字母轉成對應的兩位數（題目給的 mapping）
int letter_to_num(char c) {
    if (c == 'A') return 10;
    if (c == 'B') return 11;
    if (c == 'C') return 12;
    if (c == 'D') return 13;
    if (c == 'E') return 14;
    if (c == 'F') return 15;
    if (c == 'G') return 16;
    if (c == 'H') return 17;
    if (c == 'I') return 34;
    if (c == 'J') return 18;
    if (c == 'K') return 19;
    if (c == 'L') return 20;
    if (c == 'M') return 21;
    if (c == 'N') return 22;
    if (c == 'O') return 35;
    if (c == 'P') return 23;
    if (c == 'Q') return 24;
    if (c == 'R') return 25;
    if (c == 'S') return 26;
    if (c == 'T') return 27;
    if (c == 'U') return 28;
    if (c == 'V') return 29;
    if (c == 'W') return 32;
    if (c == 'X') return 30;
    if (c == 'Y') return 31;
    if (c == 'Z') return 33;
    return -1;  // # 不合法字母（理論上不會發生）
}


// # 檢查目前 cur 是否為合法身份證
int is_valid(){

   // # 第 1 碼：一定要是 A~Z
   if(cur[0]<'A'||cur[0]>'Z') return 0;

   // # 第 2 碼：一定要是 1 或 2（性別）
   if(cur[1]!='1'&&cur[1]!='2') return 0;

   // # 第 3~10 碼：全部都要是數字
   for(int i=1;i<10;i++){
      if (cur[i]<'0'||cur[i]>'9') return 0;
   }

   // # 把字母轉成兩位數
   int x = letter_to_num(cur[0]);
   if (x == -1) return 0;

   int a = x/10;   // 十位
   int b = x%10;   // 個位

   // # 開始算 checksum
   int sum = 0;

   // # 字母轉出來的兩位數
   sum += a * 1;
   sum += b * 9;

   // # 後面數字乘權重
   sum += (cur[1]-'0') * 8;
   sum += (cur[2]-'0') * 7;
   sum += (cur[3]-'0') * 6;
   sum += (cur[4]-'0') * 5;
   sum += (cur[5]-'0') * 4;
   sum += (cur[6]-'0') * 3;
   sum += (cur[7]-'0') * 2;
   sum += (cur[8]-'0') * 1;

   // # 最後一碼直接加（checksum digit）
   sum += (cur[9]-'0');

   // # 必須能被 10 整除才合法
   return (sum%10==0);
}


// # DFS：逐個位置填 #（暴力枚舉）
void dfs(int pos){

   // # 如果 10 個位置都填完 → 檢查是否合法
   if (pos==10){
      if(is_valid()) ans++;
      return;
   }

   // # 如果這個位置不是 # → 直接用原本的字
   if(s[pos]!='#'){
      cur[pos]=s[pos];
      dfs(pos+1);
      return;
   }

   // # 如果是 #，依位置決定可填的範圍

   if(pos==0){
      // # 第 1 碼：只能是 A~Z
      for (char c ='A'; c<='Z';c++){
         cur[pos]=c;
         dfs(pos+1);
      }

   } else if(pos==1){
      // # 第 2 碼：只能是 1 或 2
      cur[pos]='1';
      dfs(pos+1);

      cur[pos]='2';
      dfs(pos+1);

   } else{
      // # 第 3~10 碼：只能是 0~9
      for(char c='0';c<='9';c++){
         cur[pos]=c;
         dfs(pos+1);
      }
   }
}


int main(){

   // # 讀入字串
   scanf("%s",s);

   // # 長度不是 10 → 不可能合法
   if (strlen(s)!=10){
      printf("0\n");
      return 0;
   }

   // # 開始 DFS 枚舉所有可能
   dfs(0);

   // # 輸出合法數量
   printf("%lld\n",ans);

   return 0;
}