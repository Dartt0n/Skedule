В качестве языка программирования мы решили использовать Python. Мы так же рассматривали языки Rust и C++. 

|                        | Python  | Rust    | C++     |
| ---------------------- | ------- | ------- | ------- |
| Скорость разработки    | Высокая | Низкая  | Низкая  |
| Легкость разработки    | 5/5     | 4/5     | 3/5     |
| Уровень знаний команды | 9.8/10  | 6.7/10  | 3.4/10  |
| Доступность материалов | Высокая | Высокая | Средняя |
| Безопасность           | 4/5     | 5/5     | 3/5     |
| Производительность     | Низкая  | Высокая | Высокая |

Таким образом, Python имеет определенные преимущества, благодаря которым стал основным языком разработки. При появлении серьезных проблем с безопасностью и/или производительностью имеется альтернативный вариант - язык Rust.

Решение использовать докер, как инструмент виртуализации, было принято по ряду причин.

1. Docker позволяет изолировать процессы программ и обезопасить потоковую работу с файлами. 
2. Docker решает проблему зависимостей программ и рабочего окружения, позволяя собрать в едином образе приложение, все его зависимости и файлы настройки.
3. Docker использует особую виртуализацию, которая позволяет абстрагироваться от архитектуры и без изменений переносить на другой хост.
4. Docker обладает интерфейсом для автоматизации развертывания контейнера, что сильно уменьшает количество рутинной работы.
5. Образы Docker оптимизированы в отличии от прочих средств виртуализации, что позволяет экономить дисковое пространство

Мы выбрали Mariadb как систему управления базами данных благодаря следующим преимуществам:

1. MariaDB предоставляет широкие возможности по управлению базами данных и администрированию ролей.
2. MariaВD имеет более эффективный механизм хранения данных, чем у аналогов, что позволяет экономить дисковое пространство, тем самым увеличивая объемы данных хранимых на сервере. 
3. Ядро базы данных Mariadb было разработано с учетом преимуществ и недостатков прошлых поколений баз данных. Используются улучшенные алгоритмы кэширования, повышающие производительность
4. Mariadb значительно оптимизирует пользовательские запросы.

