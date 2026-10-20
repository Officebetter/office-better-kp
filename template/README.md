# Шаблон новорічної КП Office Better
Генератор КП у фірмовому стилі (A4 альбомна, PDF + HTML).
- style.css — оформлення (кольори, гірлянда, сітка). Змінювати лише свідомо.
- build.py — збирає HTML з data.py, фото з products/ і бренду з brand/.
- render.py — друкує HTML у PDF.
- data_example.py — приклад даних однієї КП (позиції, варіанти, тираж, менеджер).
Запуск: скопіювати data_example.py у data.py, заповнити, потім `python3 build.py && python3 render.py`.
