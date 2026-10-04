/*
 * Замер пропускной способности памяти — STREAM-подобный, без зависимостей.
 *
 * ЗАЧЕМ. Гипотеза хозяина 30.08: Qwen3.8-Flash-Next даёт 12-15 t/s не из-за
 * карт, а из-за памяти. У Next почти все веса лежат в ОЗУ (эксперты на
 * процессоре), значит его потолок — это полоса памяти, а не видеокарты.
 * Узлы отличаются заметно:
 *     .104 — 12 планок по 32 ГБ на 2133 MT/s, 6 каналов из 8 на сокет
 *     .105 — 16 планок по 16 ГБ на 2666 MT/s, все 8 каналов
 * По теории это 102 против 170 ГБ/с на сокет. Проверяем замером, а не теорией:
 * мой же оплаченный урок — полоса не доказывает выход, но здесь мы меряем
 * именно полосу, и сравнивать надо ОДНИМ инструментом на обеих машинах.
 *
 * Почему свой файл, а не пакет: на боевых узлах нет ни sysbench, ни mbw, ни
 * numactl, а ставить пакеты на работающие ноды ради замера — лишний риск.
 * gcc есть на обеих, этого хватает.
 *
 * Сборка:  gcc -O3 -march=native -fopenmp -o membw membw.c
 * Запуск:  ./membw [гигабайт_на_массив] [потоков]
 *
 * Меряется triad (a[i] = b[i] + k*c[i]) — три обращения к памяти на элемент,
 * классическая метрика STREAM. Массивы берём заведомо больше кэша L3.
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <omp.h>

static double now_sec(void) {
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);
    return ts.tv_sec + ts.tv_nsec * 1e-9;
}

int main(int argc, char **argv) {
    double gib = (argc > 1) ? atof(argv[1]) : 4.0;
    int threads = (argc > 2) ? atoi(argv[2]) : omp_get_max_threads();
    size_t n = (size_t)(gib * 1073741824.0 / sizeof(double));

    omp_set_num_threads(threads);

    double *a = aligned_alloc(64, n * sizeof(double));
    double *b = aligned_alloc(64, n * sizeof(double));
    double *c = aligned_alloc(64, n * sizeof(double));
    if (!a || !b || !c) { fprintf(stderr, "нет памяти под массивы\n"); return 1; }

    /* Раскладка первого касания: каждый поток трогает свою часть, чтобы
       страницы легли на локальный для него узел NUMA. Без этого вся память
       окажется на одном сокете и замер покажет половину правды. */
    #pragma omp parallel for schedule(static)
    for (size_t i = 0; i < n; i++) { a[i] = 1.0; b[i] = 2.0; c[i] = 3.0; }

    const double k = 3.0;
    double best = 0.0;
    /* Три прогона, берём лучший — первый обычно ловит остаточный прогрев. */
    for (int rep = 0; rep < 3; rep++) {
        double t0 = now_sec();
        #pragma omp parallel for schedule(static)
        for (size_t i = 0; i < n; i++) a[i] = b[i] + k * c[i];
        double dt = now_sec() - t0;
        /* triad: чтение b, чтение c, запись a = 3 обращения по 8 байт */
        double gbs = (3.0 * n * sizeof(double)) / dt / 1e9;
        if (gbs > best) best = gbs;
    }

    printf("потоков %-4d массив %.1f ГиБ x3   TRIAD %.1f ГБ/с\n",
           threads, gib, best);

    free(a); free(b); free(c);
    return 0;
}
