import sqlite3

DATABASE = 'mydatabase.db'

skills = [(_,) for _ in (['Python', 'SQL', 'API'])]
statuses = [(_,) for _ in (['На этапе проектирования', 'В процессе разработки', 'Разработан. Готов к использованию.', 'Обновлен', 'Завершен. Не поддерживается'])]

class DB_Manager:
    def __init__(self, database):
        self.database = database
        self.conn = sqlite3.connect(self.database)
        self.create_tables()

    def create_tables(self):
        cur = self.conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS skills (
                skill_id INTEGER PRIMARY KEY AUTOINCREMENT,
                skill_name TEXT UNIQUE
            )
        """)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS status (
                status_id INTEGER PRIMARY KEY AUTOINCREMENT,
                status_name TEXT UNIQUE
            )
        """)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS projects (
                project_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                project_name TEXT,
                description TEXT,
                url TEXT,
                status_id INTEGER,
                FOREIGN KEY (status_id) REFERENCES status(status_id)
            )
        """)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS project_skills (
                project_skill_id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id INTEGER,
                skill_id INTEGER,
                FOREIGN KEY (project_id) REFERENCES projects(project_id),
                FOREIGN KEY (skill_id) REFERENCES skills(skill_id)
            )
        """)
        self.conn.commit()


    def executemany(self, sql, data):
        with self.conn:
            self.conn.executemany(sql, data)
            self.conn.commit()

    def execute(self, sql, data=tuple()):
        with self.conn:
            cur = self.conn.cursor()
            cur.execute(sql, data)
            self.conn.commit()
            return cur.fetchall()

    def select_data(self, sql, data=tuple()):
        with self.conn:
            cur = self.conn.cursor()
            cur.execute(sql, data)
            return cur.fetchall()

    def default_insert(self):
        sql = 'INSERT INTO skills (skill_name) values(?)'
        self.executemany(sql, skills)
        sql = 'INSERT INTO status (status_name) values(?)'
        self.executemany(sql, statuses)

    def get_statuses(self):
        sql = 'SELECT * FROM status'
        return self.select_data(sql)


    def get_status_id(self, status_name):
        sql = 'SELECT status_id FROM status WHERE status_name = ?'
        res = self.select_data(sql, (status_name,))
        if res: return res[0][0]
        else: return None

    def get_projects(self, user_id):
        sql = 'SELECT * FROM projects WHERE user_id = ?'
        return self.select_data(sql, (user_id,))

    def get_project_id(self, project_name, user_id):
        return self.select_data(sql='SELECT project_id FROM projects WHERE project_name = ? AND user_id = ?', data=(project_name, user_id))[0][0]

    def get_skills(self):
        return self.select_data(sql='SELECT * FROM skills')

    def get_project_skills(self, project_name):
        res = self.select_data(sql='''SELECT skill_name FROM projects 
JOIN project_skills ON projects.project_id = project_skills.project_id 
JOIN skills ON skills.skill_id = project_skills.skill_id 
WHERE project_name = ?''', data=(project_name,))
        return ', '.join([x[0] for x in res])

    def get_project_info(self, user_id, project_name):
        sql = """
SELECT project_name, description, url, status_name FROM projects 
JOIN status ON
status.status_id = projects.status_id
WHERE project_name=? AND user_id=?
"""
        return self.select_data(sql=sql, data=(project_name, user_id))


    def update_projects(self, project_id, column, new_value): 
        sql = f'UPDATE projects SET {column} = ? WHERE project_id = ?'
        self.execute(sql, (new_value, project_id))


    def delete_project(self, user_id, project_id):
        sql = 'DELETE FROM projects WHERE user_id = ? AND project_id = ?'
        self.execute(sql, (user_id, project_id))

    def delete_skill(self, project_id, skill_id):
        sql = 'DELETE FROM project_skills WHERE project_id = ? AND skill_id = ?'
        self.execute(sql, (project_id, skill_id))


if __name__ == '__main__':
    manager = DB_Manager(DATABASE)
    manager.default_insert()

    # Тесты
    print("Статусы:", manager.get_statuses())
    print("ID статуса 'В процессе разработки':", manager.get_status_id('В процессе разработки'))
    

    
    project_id_to_update = manager.get_project_id("TestProject",1) 
    manager.update_projects(project_id_to_update, "description", "Updated description")

    

    manager.conn.close()

