#define TABLE_ROW0(j) table[j]
#define TABLE_COL0(i) table[(i)*nCol]

typedef size_t Interval[2];

typedef struct CombiTimeTable {
    char* key; /* Key consisting of concatenated names of file and table */
    double* table; /* Table values */
    size_t nRow; /* Number of rows of table */
} CombiTimeTable;

double maximumValue(void* _tableID) {
    double yMax = 0.;
    CombiTimeTable* tableID = (CombiTimeTable*)_tableID;
    if (NULL != tableID && NULL != tableID->table) {
        const double* table = tableID->table;
        const size_t nRow = tableID->nRow;
        yMax = TABLE_ROW0(0);
        int i;
        for (i = 1; i < nRow; i++) {
        	if (TABLE_ROW0(i) > yMax) {
        		yMax = TABLE_ROW0(i);
        	}
        }
    }
    return yMax;
}
