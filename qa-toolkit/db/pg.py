"""Read-only запити до БД Foxtrot: стейдж (за замовчуванням) або спільна dev-БД динамічних стендів.

Використання:
    python qa-toolkit/db/pg.py "select 1"
    python qa-toolkit/db/pg.py -f qa-toolkit/tasks/CMS-27767/queries.sql
    echo "select 1" | python qa-toolkit/db/pg.py
    python qa-toolkit/db/pg.py --target dev "select 1"   # foxtrot01-dev-shared / foxtrot_dev

Пароль береться з %APPDATA%\\postgresql\\pgpass.conf — у коді й аргументах його немає.
Сесія відкривається з default_transaction_read_only=on: будь-який INSERT/UPDATE/DELETE/DDL
Postgres відхилить сам. statement_timeout = 60 с, щоб не вішати спільний стейдж.
Друк: TSV з заголовком; для кількох запитів у файлі — по блоку на кожен.
"""
import argparse
import sys

import psycopg

COMMON = dict(
    port=5432,
    connect_timeout=10,
    options="-c default_transaction_read_only=on -c statement_timeout=60000",
)
TARGETS = {
    "stage": dict(host="foxtrot01-stage-postgres14.crlrw0q1dnnx.eu-central-1.rds.amazonaws.com",
                  dbname="fox_stage_current", user="foxtrot_stage"),
    "dev": dict(host="foxtrot01-dev-shared.crlrw0q1dnnx.eu-central-1.rds.amazonaws.com",
                dbname="foxtrot_dev", user="shared"),
}
CONN = dict(COMMON, **TARGETS["stage"])


def run(sql: str) -> None:
    with psycopg.connect(**CONN) as conn:
        cur = conn.cursor()
        cur.execute(sql)
        while True:
            if cur.description:
                print("\t".join(c.name for c in cur.description))
                for row in cur.fetchall():
                    print("\t".join("NULL" if v is None else str(v) for v in row))
                print()
            if not cur.nextset():
                break


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("sql", nargs="?")
    p.add_argument("-f", "--file")
    p.add_argument("-t", "--target", choices=TARGETS, default="stage")
    a = p.parse_args()
    CONN = dict(COMMON, **TARGETS[a.target])
    if a.file:
        sql = open(a.file, encoding="utf-8").read()
    elif a.sql:
        sql = a.sql
    else:
        sql = sys.stdin.read()
    sys.stdout.reconfigure(encoding="utf-8")
    run(sql)
