import sqlite3

def main():
    conn = sqlite3.connect('db.sqlite3')
    cur = conn.cursor()

    print('auth_user rows:')
    for row in cur.execute('SELECT id, username FROM auth_user'):
        print(row)

    print('\nusers_userprofile rows:')
    for row in cur.execute('SELECT id, user_id, sede_id FROM users_userprofile'):
        print(row)

    auth_ids = set(r[0] for r in cur.execute('SELECT id FROM auth_user'))
    off = [r for r in cur.execute('SELECT id, user_id FROM users_userprofile') if r[1] not in auth_ids]
    print('\nOffending rows (users_userprofile.id, user_id):', off)

    conn.close()

if __name__ == '__main__':
    main()
