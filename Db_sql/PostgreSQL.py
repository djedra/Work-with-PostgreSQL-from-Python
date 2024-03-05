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


        def add(name, last_name, email, phone_number=None):
            cur.execute("""
                 SELECT id FROM client WHERE name=%s and last_name=%s and email=%s;
                 """, (name, last_name, email))
            if cur.rowcount > 0:
                return ('Клиент уже существует')
            else:
                cur.execute("""
                    INSERT INTO client(name, last_name, email) VALUES (%s, %s, %s) RETURNING id;
                     """, (name, last_name, email))
                if phone_number:
                    cur.execute("""
                        INSERT INTO phone_number(client_id, phone_number) VALUES (%s, %s);
                         """, (cur.fetchone(), phone_number))
                conn.commit()
                return 'Документ добавлен'


        def add_phone(client_id, phone_number):
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


        def change_inf(client_id, email=None, phone_number=None, new_name=None, new_last_name=None):
            if email:
                cur.execute("""
                     UPDATE client SET email=%s WHERE id=%s;
                     """, (email, client_id))
                conn.commit()
                return 'Почта изменена'
            elif phone_number:
                cur.execute("""
                     UPDATE phone_number SET phone_number=%s WHERE client_id=%s;
                     """, (phone_number, client_id))
                conn.commit()
                return 'Номер изменен'
            elif new_name:
                cur.execute("""
                     UPDATE client SET name=%s WHERE id=%s;
                     """, (new_name, client_id))
                conn.commit()
                return 'Имя изменено'
            elif new_last_name:
                cur.execute("""
                     UPDATE client SET last_name=%s WHERE id=%s;
                     """, (new_last_name, client_id))
                conn.commit()
                return 'Фамилия изменена'
            else:
                return 'Ничего не изменено'


        def dell_number(client_id, phone_number):
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


        def dell_client(client_id):
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


        def find_client(find_by, value):
            if find_by == 'ID':
                cur.execute("""
                            SELECT id FROM client WHERE id=%s;
                            """, (value,))
                cur.execute("""
                            SELECT * FROM client;
                            """)
                for row in cur.fetchall():
                    print("Имя клиента: ", row[1], )
                    print("Фамилия клиента: ", row[2])
                    print("Email: ", row[3])

                    cur.execute("""
                                 SELECT id FROM phone_number WHERE client_id=%s;
                             """, (value,))
                    cur.execute("""
                             SELECT * FROM phone_number ;
                             """)
                    for row1 in cur.fetchall():
                        print("Номер клиента", row1[2], )
                    return ''
            elif find_by == 'имя':
                cur.execute("""
                            SELECT id FROM client WHERE name=%s;
                            """, (value,))
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
            elif find_by == 'фамилия':
                cur.execute("""
                            SELECT id FROM client WHERE last_name=%s;
                            """, (value,))
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
            elif find_by == 'email':
                cur.execute("""
                            SELECT id FROM client WHERE email=%s;
                            """, (value,))
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

            elif find_by == 'номер':
                cur.execute("""
                            SELECT id FROM phone_number WHERE phone_number=%s;
                            """, (value,))
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

            elif find_by == 'IMEI' or find_by == 'фамилия' or find_by == 'email' or find_by == 'номер':
                cur.execute("""
                                        SELECT client.id, client.name, client.last_name, client.email, phone_number.phone_number 
                                        FROM client 
                                        LEFT JOIN phone_number ON client.id = phone_number.client_id 
                                        WHERE client.name=%s OR client.last_name=%s 
                                        OR client.email=%s OR phone_number.phone_number=%s;
                                        """, (value, value, value, value))
                for row in cur.fetchall():
                    print("ID:", row[0])
                    print("Имя клиента:", row[1])
                    print("Фамилия клиента:", row[2])
                    print("Email клиента:", row[3])
                    print("Номер клиента:", row[4])
                    print("------------------")
                return ''
            else:
                return 'Неправильный параметр поиска'

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
                    name = input('Введите имя клиента: ')
                    last_name = input('Введите фамилию клиента: ')
                    email = input('Введите email клиента: ')
                    phone_number = input('Введите номер телефона клиента: ')
                    print(add(name, last_name, email, phone_number))
                elif command == '3':
                    client_id = input('Введите ID существующего клиента: ')
                    phone_number = input('Введите номер телефона клиента: ')
                    print(add_phone(client_id, phone_number))
                elif command == '4':
                    client_id = input('Введите ID существующего клиента: ')
                    attribute = input('Выберите, что хотите изменить (email, номер, имя или фамилия): ')
                    new_value = input('Введите новое значение: ')
                    if attribute == 'email':
                        print(change_inf(client_id, email=new_value))
                    elif attribute == 'номер':
                        print(change_inf(client_id, phone_number=new_value))
                    elif attribute == 'имя':
                        print(change_inf(client_id, new_name=new_value))
                    elif attribute == 'фамилия':
                        print(change_inf(client_id, new_last_name=new_value))
                    else:
                        print('Неправильный атрибут для изменения')
                elif command == '5':
                    client_id = input('Введите ID существующего клиента: ')
                    phone_number = input('Введите номер, который хотите удалить: ')
                    print(dell_number(client_id, phone_number))
                elif command == '6':
                    client_id = input('Введите ID существующего клиента: ')
                    print(dell_client(client_id))
                elif command == '7':
                    find_by = input('Введите параметры поиска (ID, имя, фамилия, email или номер): ')
                    value = input('Введите значение: ')
                    print(find_client(find_by, value))
                elif command == '8':
                    view_all_clients()
                elif command == 'q':
                    print('Работа с базой данных завершена')
                    break
                else:
                    print('Неправильная команда')


        main()

conn.close()
