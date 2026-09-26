# Strata на 2×2080Ti: патч под две карты

Патч к [Strata](https://github.com/Niko1221/Strata) v0.1.2 (коммит `6da1f66`) — движку под одну модель,
Qwen3.8-Flash-Next. Из коробки Strata собирается только для sm_80 и новее и работает на одной карте. Патч
переносит её на 2080Ti (sm_75) и добавляет вторую карту как хранилище экспертов.

На нашем стенде (2×2080Ti 22 ГБ, 2×Xeon Ice Lake, квант ISTA GSQ-RCO IQ3_XXS) это **50–68 т/с** на задачах
«хомяки» и «аквариум». Strata без доработок на одной карте даёт 25–39 т/с. Таблицы, оценка сцен и сравнение с
llama.cpp — на странице [Flash-Next](https://tirex999.github.io/2x2080ti-nvlink-44gb/flash-next.html).

## Что в патче

| что | где | ключ или переменная |
|---|---|---|
| Перенос на sm_75: в выборке внимания скалярная ветка вместо tf32 `mma`; ядра гипер-связей делят окно, если не хватает общей памяти (на sm_75 её 64 КБ) | `CMakeLists.txt`, `setup.py`, `native_qsa_score.cu`, `fused_gr.cu` | — |
| Пул процессора на Linux: один рабочий на физическое ядро (раньше садились по два на соседей SMT) | `pool.cpp` | — |
| Вторая карта держит экспертов, которых нет на первой, и считает их одновременно с ней; строки пишет туда же, куда процессор, поэтому граф первой карты не меняется | `expert_source.*`, `generate.cpp`, `verify.*`, `iq_kernels.*` | `--second-card 1`, `--second-card-usage`, `--second-card-reserve-mib`, `--second-card-dup` |
| Таблица маршрутизации — какие эксперты зовутся чаще, копится между прогонами — и профиль для главной карты из неё | `expert_source.cpp`, `generate.cpp`, `tools/mk_profile_from_usage.py` | `STRATA_USAGE_DUMP=файл` |
| Ядра гипер-связей на всю карту (было 41 блок на 68 мультипроцессоров); совпадают со штатными до округления fp32 | `fused_gr.cu` | `STRATA_GR_V1=1` — штатные |
| Путь промахов по PCIe выкидывается из графа, если его доля 0 | `verify.*` | `--pcie-frac 0` |
| Для замеров: огромные страницы арены, запуск графа отдельным потоком, раскладка плотных проекций, поправка деления общих экспертов | `pinned.cu`, `verify.*`, `native_mmvq.cu`, `expert_source.cpp` | `STRATA_ARENA_THP=0`, `STRATA_ASYNC_LAUNCH=1`, `STRATA_MMVQ_UPSTREAM=1`, `STRATA_MMVQ_ROWS=4`, `STRATA_CARD2_BIAS` |

## Сборка

```bash
git clone https://github.com/Niko1221/Strata && cd Strata && git checkout 6da1f66
git apply --ignore-whitespace ../strata-2x2080ti.patch     # проверено: встаёт на чистую 0.1.2
# зависимости, пакет модели, MTP — по README Strata (setup.sh, tools/iq_pack.py, tools/mtp_fetch.py, tools/mtp_rt.py)
cmake -S . -B build -G Ninja -DCMAKE_BUILD_TYPE=Release -DSTRATA_ENABLE_CUDA=ON -DSTRATA_NATIVE_EXPERTS=ON \
      -DCMAKE_CUDA_ARCHITECTURES=75 -DSTRATA_GGML_DIR=/путь/к/llama.cpp
cmake --build build -j
```

У нас: CUDA 13.0, gcc 15, драйвер 610, ggml из llama.cpp `3cf03257`.

## Запуск на двух картах

Главная карта — та, у которой сокет с памятью процесса (у нас карта 1 на сокете 1); она становится устройством 0,
вторая — устройством 1:

```bash
cat шард-2.gguf > /dev/null     # прогреть таблицу n-грамм в кэш ОС (28.8 ГБ), иначе первые ответы медленнее
CUDA_VISIBLE_DEVICES=1,0 numactl --cpunodebind=1 --membind=1 ./build/strata \
  --pack <пакет> --native <шард 1> --ple-gguf <шард 2> --ple-io mmap \
  --expert-profile data/profile_other_2609.bin --expert-cache auto --adapt-every 0 \
  --second-card 1 --second-card-usage data/usage_other_2609.bin --pcie-frac 0 \
  --prefill 2048 --spec 4 --spec-min-p 0.5 --mtp <mtp/rt> --max-context 131072 --kv int8 --tokens ...
```

Сервер с OpenAI-совместимым API — `run-fast.sh` в этой папке: он пишет конфиг для `serve/server.py` Strata с
теми же ключами.

## Таблицы маршрутизации (`data/`)

Сняты на модели ISTA IQ3_XXS, по 1024 токена ответа на шести промптах: задачи «майнкрафт» и «хомяки-физика»,
два разговора, проба на 4.6 тыс. токенов и короткий бенч. Хомяков и аквариума среди них нет.

- `profile_other_2609.bin` — 9000 самых частых пар (слой, эксперт), профиль главной карты;
- `usage_other_2609.bin` — полная таблица частот; по ней выбираются эксперты второй карты.

Своя таблица: `STRATA_USAGE_DUMP=usage.bin ./build/strata ...` на своих запросах (таблица копится между
прогонами), затем `python3 tools/mk_profile_from_usage.py usage.bin profile.bin 9000`.

## Что важно знать

- **Перед замерами гасите простаивающие копии Strata.** Её рабочие ждут задачу в спин-цикле и занимают все ядра
  своего сокета; соседний процесс от этого замедлялся у нас в 3–4 раза.
- `--pcie-frac`: с одной картой лучше 0.15 (заводское 0.55 рассчитано на PCIe 4.0), с двумя — 0.
- Не помогли: огромные страницы, окно черновика 6, запуск графа отдельным потоком, `--second-card-dup`
  (+2.5 % при росте промахов) — всё это оставлено выключенным.
- Один запрос за раз; кэш между запросами не переиспользуется, каждый ход перечитывает весь контекст
  (чтение промпта ~120 т/с).
- Автор Strata предупреждает, что эксперт, посчитанный на карте, даёт другие токены, чем на процессоре: у них
  разное квантование активаций (оба способа — из llama.cpp). На наших задачах качество сцен на одной и двух
  картах одинаковое.
