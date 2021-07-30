import taos

conn = taos.connect()
dbname = "pytest_taos_subscribe_callback"
conn.exec("drop database if exists %s" % dbname)
conn.exec("create database if not exists %s" % dbname)
conn.select_db(dbname)
conn.exec("create table if not exists log(ts timestamp, n int)")
for i in range(10):
    conn.exec("insert into log values(now, %d)" % i)

sub = conn.subscribe(True, "test", "select * from log", 1000)
print("# consume from begin")
for ts, n in sub.consume():
    print(ts, n)

print("# consume new data")
for i in range(5):
    conn.exec("insert into log values(now, %d)(now+1s, %d)" % (i, i))
    result = sub.consume()
    for ts, n in result:
        print(ts, n)

print("# consume with a stop condition")
for i in range(10):
    conn.exec("insert into log values(now, %d)" % int(random() * 10))
    result = sub.consume()
    try:
        ts, n = next(result)
        print(ts, n)
        if n > 5:
            result.stop_query()
            print("## stopped")
            break
    except StopIteration:
        continue

sub.close()

conn.exec("drop database if exists %s" % dbname)
conn.close()
