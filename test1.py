import sqlite3


def main():
    conn = sqlite3.connect('test.db')
    cur = conn.cursor()
    query1 = 'SELECT * FROM ingredients'
    print(cur.execute(query1).lastrowid)
    query = 'INSERT INTO ingredients(ingredient_name) VALUES ("bob")'
    result = cur.execute(query).lastrowid
    print(result)
    print(cur.execute(query1).fetchall())

if __name__ == '__main__':
    main()
