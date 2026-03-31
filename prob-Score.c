#include <stdio.h>    // 輸入輸出
#include <stdlib.h>   // qsort

// # 定義學生結構（把一個人的所有資訊打包）
typedef struct {
    long long id;   // 學號
    int chinese;    // 國文
    int eng;        // 英文
    int math;       // 數學
    int total;      // 總分（預先算好）
} Student;


// # comparator：決定排序規則（整題靈魂）
// # qsort 會一直呼叫這個函式來決定誰排前面
int cmp(const void *a, const void *b){
    
    // # 把 void* 轉回 Student*
    Student *s1 = (Student *)a;
    Student *s2 = (Student *)b;

    // # 1. 總分（大 → 小）
    if (s1->total != s2->total)
        return s2->total - s1->total;

    // # 2. 國文（大 → 小）
    if (s1->chinese != s2->chinese)
        return s2->chinese - s1->chinese;

    // # 3. 英文（大 → 小）
    if (s1->eng != s2->eng)
        return s2->eng - s1->eng;

    // # 4. 數學（大 → 小）
    if (s1->math != s2->math)
        return s2->math - s1->math;

    // # 5. id（小 → 大）
    if (s1->id < s2->id) return -1;
    if (s1->id > s2->id) return 1;

    return 0;  // # 完全相同
}


int main(){

    int num;                 // # 學生數量
    Student stu[1000];       // # 存所有學生資料

    // # 先讀 N（非常重要！不然 num 是垃圾值）
    scanf("%d", &num);
    
    // # 讀入每位學生的資料
    for(int i = 0; i < num; i++){

        scanf("%lld%d%d%d",
            &stu[i].id,
            &stu[i].chinese,
            &stu[i].eng,
            &stu[i].math);

        // # 預先計算總分（避免排序時一直加）
        stu[i].total = stu[i].chinese + stu[i].eng + stu[i].math;
    }
    
    // # 呼叫 qsort 排序
    // # stu：陣列
    // # num：元素數量
    // # sizeof(Student)：每個元素大小
    // # cmp：比較規則
    qsort(stu, num, sizeof(Student), cmp);

    // # 輸出排序後的結果（只印 id）
    for(int i = 0; i < num; i++){
        printf("%lld\n", stu[i].id);
    }

    return 0;
}