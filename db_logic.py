import sqlite3
from config import DATABASE

skills = [(_,_) for _ in [('Python','SQL','API','Telegram')]]
statuses = [(_,_) for _ in [('На этапе проектирования','В процессе разработки','Разработан. Готов к использованию')]]

class DB_Manager:
    def __init__(self, database):
        self.database = database

    def create_tables(self):
        conn = sqlite3.connect(self.database)
        with conn:
            conn.execute("""CREATE TABLE IF NOT EXISTS projects (
                project_id INTEGER PRIMARY KEY,
                user_id INTEGER,
                project_name TEXT NOT NULL,
                description TEXT,
                url TEXT,
                status_id INTEGER,
                FOREIGN KEY (status_id) REFERENCES status(status_id)
            )""")

            conn.execute("""CREATE TABLE IF NOT EXISTS skills (
                skill_id INTEGER PRIMARY KEY,
                skill_name TEXT
            )""")

            conn.execute("""CREATE TABLE IF NOT EXISTS project_skills (
                project_id INTEGER,
                skill_id INTEGER,
                FOREIGN KEY (project_id) REFERENCES projects(project_id),
                FOREIGN KEY (skill_id) REFERENCES skills(skill_id)
            )""")

            conn.execute("""CREATE TABLE IF NOT EXISTS status (
                status_id INTEGER PRIMARY KEY,
                status_name TEXT
            )""")
        conn.commit()

    def _executemany(self, sql, data):
        conn = sqlite3.connect(self.database)
        with conn:
            conn.executemany(sql, data)
        conn.commit()

    def _select_data(self, sql, data = tuple()):
        conn = sqlite3.connect(self.database)
        cur = conn.cursor()
        cur.execute(sql, data)
        return cur.fetchall()

    def default_insert(self):
        sql = 'INSERT OR IGNORE INTO skills(skill_name) values(?)'
        data = skills
        self._executemany(sql, data)
        sql = 'INSERT OR IGNORE INTO status(status_name) values(?)'
        data = statuses
        self._executemany(sql, data)

    def insert_project(self, data):
        sql = """INSERT INTO projects (user_id, project_name, description, url, status_id) VALUES (?, ?, ?, ?, ?)"""
        self._executemany(sql, data)

    def insert_skill(self, user_id, project_name, skill):
        # Сначала находим project_id и skill_id
        sql = 'SELECT project_id FROM projects WHERE project_name = ? AND user_id = ?'
        project_id = self._select_data(sql, (project_name, user_id))[0][0]
        sql = 'SELECT skill_id FROM skills WHERE skill_name = ?'
        skill_id = self._select_data(sql, (skill,))[0][0]
        data = [(project_id, skill_id)]
        sql = 'INSERT OR IGNORE INTO project_skills VALUES(?,?)'
        self._executemany(sql, data)

    def get_statuses(self):
        sql = "SELECT status_name FROM status"
        return self._select_data(sql)

    def get_status_id(self, status_name):
        sql = 'SELECT status_id FROM status WHERE status_name = ?'
        res = self._select_data(sql, (status_name,))
        if res: return res[0][0]
        else: return None

    def get_projects(self, user_id):
        sql = """SELECT * FROM projects WHERE user_id = ?"""
        return self._select_data(sql, (user_id,)) # Важно передать user_id как tuple

    def get_project_id(self, project_name, user_id):
        sql = 'SELECT project_id FROM projects WHERE project_name = ? AND user_id = ?'
        return self._select_data(sql, (project_name, user_id))

    def get_project_skills(self, project_name):
        res = self._select_data(sql="""
            SELECT skill_name FROM projects 
            JOIN project_skills ON projects.project_id = project_skills.project_id
            JOIN skills ON skills.skill_id = project_skills.skill_id
            WHERE project_name = ?""", data = (project_name,) )
        return ','.join([x[0] for x in res])

    def get_project_info(self, user_id, project_name):
        sql = """
            SELECT project_name, description, url, status_name FROM projects 
            JOIN status ON 
            status.status_id = projects.status_id
            WHERE project_name=? AND user_id=?
        """
        return self._select_data(sql=sql, data = (project_name, user_id))

    def update_projects(self, param, data): #param имя поля для обновления
        sql = f"""UPDATE projects SET {param} = ? WHERE project_id = ?"""
        self._executemany(sql, data)

    def delete_project(self, user_id, project_id):
        sql = """DELETE FROM projects WHERE user_id = ? AND project_id = ?"""
        self._executemany(sql, [(user_id, project_id)]) #Важно передавать данные как список кортежей

    def delete_skill(self, project_id, skill_id):
        sql = """DELETE FROM project_skills WHERE skill_id = ? AND project_id = ?"""
        self._executemany(sql, [(skill_id, project_id)])  # Важно передавать данные как список кортежей

if __name__ == '__main__':
    DATABASE = "test.db"  # Используйте другую БД для тестов
    manager = DB_Manager(DATABASE)

    # Создаем таблицы (если их еще нет)
    manager.create_tables()

    # Заполняем начальными данными (если нужно)
    manager.default_insert()

    #Тест insert_project
    project_data = (1, 'Test Project', 'Описание', 'http://test.com', 1)
    manager.insert_project([project_data])

    # Тест get_projects
    projects = manager.get_projects(1) #User_id = 1
    print(projects) # Выводим полученные проекты.
