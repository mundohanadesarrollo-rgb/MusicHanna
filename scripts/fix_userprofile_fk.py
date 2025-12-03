import sqlite3
import json

DB='db.sqlite3'
BACKUP='scripts/offending_userprofiles.json'

def main():
    conn=sqlite3.connect(DB)
    cur=conn.cursor()
    auth_ids=set(r[0] for r in cur.execute('SELECT id FROM auth_user'))
    offending=[{'id': r[0], 'user_id': r[1], 'sede_id': r[2]} for r in cur.execute('SELECT id, user_id, sede_id FROM users_userprofile') if r[1] not in auth_ids]
    if not offending:
        print('No offending rows found.')
        return
    with open(BACKUP, 'w', encoding='utf-8') as f:
        json.dump(offending, f, ensure_ascii=False, indent=2)
    print(f'Backed up {len(offending)} rows to {BACKUP}')
    ids = [r['id'] for r in offending]
    print('Deleting offending rows with ids:', ids)
    cur.execute('BEGIN')
    try:
        cur.executemany('DELETE FROM users_userprofile WHERE id=?', [(i,) for i in ids])
        conn.commit()
        print('Deleted offending rows.')
    except Exception as e:
        conn.rollback()
        print('Error deleting rows:', e)
    finally:
        conn.close()

if __name__=='__main__':
    main()
