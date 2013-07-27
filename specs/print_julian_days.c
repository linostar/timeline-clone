#include <stdio.h>

// Algorithms from:
// Henry F. Fliegel and Thomas C. Van Flandern
// "Letters to the editor: a machine algorithm for processing calendar dates"
// http://dx.doi.org/10.1145/364096.364097

void from_julian_day(int julian_day, int *year, int *month, int *day)
{
    int JD, L, N, I, J, K;
    JD = julian_day;
    L = JD + 68569;
    N = 4*L/146097;
    L = L - (146097*N + 3)/4;
    I = 4000*(L + 1)/1461001;
    L = L - 1461*I/4 + 31;
    J = 80*L/2447;
    K = L - 2447*J/80;
    L = J/11;
    J = J + 2 - 12*L;
    I = 100*(N - 49) + I + L;
    *year = I;
    *month = J;
    *day = K;
}

void to_julian_day(int year, int month, int day, int *julian_day)
{
    int I, J, K;
    I = year;
    J = month;
    K = day;
    *julian_day = K - 32075 + 1461*(I + 4800 + (J - 14)/12)/4 + 367*(J - 2 - (J - 14)/12*12)/12 - 3*((I + 4900 + (J - 14)/12)/100)/4;
}

int main()
{
    int julian_day, year, month, day, roundtrip_julian_day;

    for (julian_day = 0; julian_day < 10000000; julian_day++)
    {
        from_julian_day(julian_day, &year, &month, &day);
        to_julian_day(year, month, day, &roundtrip_julian_day);
        printf("%d - %d-%d-%d - %d\n", julian_day, year, month, day, roundtrip_julian_day);
    }

    return 0;
}
