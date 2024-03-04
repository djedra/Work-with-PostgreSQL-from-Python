import psycopg2

print('''Управление базой данных:
            1 - создать базу данных
            2 - добавить нового клиента
            3 - добавить телефон существующему клиенту
            4 - изменить данные о клиенте
            5 - удалить телефон существующего клиента
            6 - удалить существующего клиента
            7 - найти клиента по его данным: имени, фамилии, email или телефону
            8 - вывести список всех клиентов находящихся в базе
            q - выход''')

with psycopg2.connect(database="clients_db", user="postgres", password="1234") as conn:
    with conn.cursor() as cur:
        def get_BD():
            cur.execute("select exists(select * from information_schema.tables where table_name=%s)", ('client',))
            cur.execute("select exists(select * from information_schema.tables where table_name=%s)", ('phone_number',))
            exists = cur.fetchone()[0]
            if exists is True:
                # удаление таблиц
                cur.execute("""
                DROP TABLE phone_number;
                DROP TABLE client;
                """)
                cur.execute("""
                CREATE TABLE IF NOT EXISTS client(
                            id SERIAL PRIMARY KEY,
                            name VARCHAR(40),
                            last_name VARCHAR(40),
                            email VARCHAR(40) UNIQUE
                );
                """)
                cur.execute("""
                           CREATE TABLE IF NOT EXISTS phone_number(
                            id SERIAL PRIMARY KEY,
                            client_id INTEGER REFERENCES client(id),
                            phone_number NUMERIC(11) UNIQUE
                           );   
                """)
            else:
                cur.execute("""
                            CREATE TABLE IF NOT EXISTS client(
                            id SERIAL PRIMARY KEY,
                            name VARCHAR(40) UNIQUE,
                            last_name VARCHAR(40) UNIQUE,
                            email VARCHAR(40) UNIQUE
                            );       
                                           """)
                cur.execute("""
                           CREATE TABLE IF NOT EXISTS phone_number(
                            id SERIAL PRIMARY KEY,
                            client_id INTEGER REFERENCES client(id),
                            phone_number NUMERIC(11) UNIQUE
                           );   
                           """)
            return conn.commit()


        def add():
            name = input('Введите имя клиента: ')
            last_name = input('Введите фамилию клиента: ')
            email = input('Введите почту клиента: ')
            cur.execute("""
                        SELECT id FROM client WHERE name=%s and last_name=%s and email=%s;
                        """, (name, last_name, email))
            if cur.rowcount > 0:
                return ('Клиент уже существует')
            else:
                cur.execute("""
                           INSERT INTO client(name, last_name, email) VALUES (%s, %s, %s) RETURNING id;
                            """, (name, last_name, email))
                phone_number = input('Введите телефон клиента: ')
                if phone_number == '':
                    conn.commit()
                    return 'Добавлено'
                else:
                    cur.execute("""
                            INSERT INTO phone_number(client_id, phone_number) VALUES (%s, %s);
                            """, (cur.fetchone(), phone_number))
                    conn.commit()
                    return 'Документ добавлен'


        def add_phone():
            client_id = input('Введите ID существующего клиента: ')
            phone_number = input('Введите номер для добавления: ')
            cur.execute("""
                        SELECT id FROM phone_number WHERE phone_number=%s;
                                                    """, (phone_number,))
            if cur.rowcount > 0:
                return 'Номер уже существует'
            else:
                cur.execute("""
                       INSERT INTO phone_number(client_id, phone_number) VALUES (%s, %s);
                       """, (client_id, phone_number))
                conn.commit()
                return 'Документ добавлен'


        def change_inf():
            client_id = input('Введите ID существующего клиента: ')
            change = input('Введите информацию которую хотели бы поменять(почта или номер): ')

            if change == 'почта':
                email = input('Введите новую почту: ')
                cur.execute("""
                        UPDATE client SET email=%s WHERE id=%s;
                        """, (email, client_id,))
                cur.execute("""
                        SELECT * FROM client;
                        """)
                conn.commit()
                return 'Почта изменена'

            elif change == 'номер':
                phone_number1 = input('Введите номер который хотите изменить: ')
                cur.execute("""
                       SELECT id FROM phone_number WHERE phone_number=%s;
                       """, (phone_number1,))
                if cur.rowcount > 0:
                    phone_number = input('Введите новый номер: ')
                    cur.execute("""
                                SELECT id FROM phone_number WHERE phone_number=%s;
                                """, (phone_number,))
                    if cur.rowcount > 0:
                        return 'Такой номер уже существует'
                    else:
                        cur.execute("""
                                    UPDATE phone_number SET phone_number=%s WHERE id=%s;
                                    """, (phone_number, cur.fetchone(),))
                        cur.execute("""
                                    SELECT * FROM phone_number;
                                    """)
                        conn.commit()
                        return 'Номер изменен'
                else:
                    return 'Такого номер нет'


        def dell_number():
            client_id = input('Введите ID существующего клиента: ')
            phone_number = input('Введите номер который хотите удалить: ')
            cur.execute("""
                            SELECT id FROM phone_number WHERE client_id=%s and phone_number=%s;
                            """, (client_id, phone_number,))
            if cur.rowcount > 0:
                cur.execute("""
                        DELETE FROM phone_number WHERE id=%s;
                        """, (cur.fetchone(),))
                cur.execute("""
                        SELECT * FROM phone_number;
                        """)
                conn.commit()
                return 'Номер удалён'
            else:
                return 'Такого номера нет'


        def dell_client():
            client_id = input('Введите ID существующего клиента: ')
            cur.execute("""
                            SELECT id FROM phone_number WHERE client_id=%s;
                            """, (client_id,))
            for row in cur.fetchall():
                cur.execute("""
                            DELETE FROM phone_number WHERE id=%s;
                            """, (row,))
                cur.execute("""
                                        SELECT * FROM phone_number;
                                        """)
                conn.commit()
            cur.execute("""
                                    DELETE FROM client WHERE id=%s;
                                    """, (client_id,))
            cur.execute("""
                                    SELECT * FROM client;
                                    """)
            conn.commit()
            return 'Клиент удален'


        def find_client():
            find = input('Введите параметры поиска(ID, имя, фамилия, email или номер: ')
            if find == 'ID':
                client_id = input('Введите ID существующего клиента: ')
                cur.execute("""
                           SELECT id FROM client WHERE id=%s;
                           """, (client_id,))
                cur.execute("""
                           SELECT * FROM client;
                           """)
                for row in cur.fetchall():
                    print("Имя клиента: ", row[1], )
                    print("Фамилия клиента: ", row[2])
                    print("Email: ", row[3])

                    cur.execute("""
                                SELECT id FROM phone_number WHERE client_id=%s;
                            """, (client_id,))
                    cur.execute("""
                            SELECT * FROM phone_number ;
                            """)
                    for row1 in cur.fetchall():
                        print("Номер клиента", row1[2], )
                    return ''
            elif find == 'имя':
                name = input('Введите имя клиента: ')
                cur.execute("""
                           SELECT id FROM client WHERE name=%s;
                           """, (name,))
                cur.execute("""
                           SELECT * FROM client;
                           """)
                for row in cur.fetchall():
                    print("Имя клиента: ", row[1], )
                    print("Фамилия клиента: ", row[2])
                    print("Email: ", row[3])

                    cur.execute("""
                                SELECT id FROM phone_number WHERE client_id=%s;
                            """, (cur.rowcount,))
                    cur.execute("""
                            SELECT * FROM phone_number ;
                            """)
                    for row1 in cur.fetchall():
                        print("Номер клиента", row1[2], )
                    return ''
            elif find == 'фамилия':
                last_name = input('Введите фамилию клиента: ')
                cur.execute("""
                           SELECT id FROM client WHERE last_name=%s;
                           """, (last_name,))
                cur.execute("""
                           SELECT * FROM client;
                           """)
                for row in cur.fetchall():
                    print("Имя клиента: ", row[1], )
                    print("Фамилия клиента: ", row[2])
                    print("Email: ", row[3])

                    cur.execute("""
                                SELECT id FROM phone_number WHERE client_id=%s;
                            """, (cur.rowcount,))
                    cur.execute("""
                            SELECT * FROM phone_number ;
                            """)
                    for row1 in cur.fetchall():
                        print("Номер клиента", row1[2], )
                    return ''
            elif find == 'email':
                email = input('Введите email клиента: ')
                cur.execute("""
                           SELECT id FROM client WHERE email=%s;
                           """, (email,))
                cur.execute("""
                           SELECT * FROM client;
                           """)
                for row in cur.fetchall():
                    print("Имя клиента: ", row[1], )
                    print("Фамилия клиента: ", row[2])
                    print("Email: ", row[3])

                    cur.execute("""
                                SELECT id FROM phone_number WHERE client_id=%s;
                            """, (cur.rowcount,))
                    cur.execute("""
                            SELECT * FROM phone_number ;
                            """)
                    for row1 in cur.fetchall():
                        print("Номер клиента", row1[2], )
                    return ''

            elif find == 'номер':
                num = input('Введите номер клиента: ')
                cur.execute("""
                           SELECT id FROM phone_number WHERE phone_number=%s;
                           """, (num,))
                cur.execute("""
                           SELECT * FROM client;
                           """)
                for row in cur.fetchall():
                    print("Имя клиента: ", row[1], )
                    print("Фамилия клиента: ", row[2])
                    print("Email: ", row[3])

                    cur.execute("""
                                SELECT id FROM phone_number WHERE client_id=%s;
                            """, (cur.rowcount,))
                    cur.execute("""
                            SELECT * FROM phone_number ;
                            """)
                    for row1 in cur.fetchall():
                        print("Номер клиента", row1[2], )
                    return ''


        def view_all_clients():
            cur.execute("SELECT * FROM client;")
            for row in cur.fetchall():
                print("ID:", row[0])
                print("Имя клиента:", row[1])
                print("Фамилия клиента:", row[2])
                print("Email клиента:", row[3])
                print("------------------")


        def main():
            while True:
                command = input('Введите команду: ')
                if command == '1':
                    get_BD()
                    print('База создана')
                elif command == '2':
                    print(add())
                elif command == '3':
                    print(add_phone())
                elif command == '4':
                    print(change_inf())
                elif command == '5':
                    print(dell_number())
                elif command == '6':
                    print(dell_client())
                elif command == '7':
                    print(find_client())
                elif command == '8':
                    view_all_clients()
                elif command == 'q':
                    print('Работа с базой данных завершена')
                    break
                else:
                    print('Неправильная команда')


        main()

conn.close()
