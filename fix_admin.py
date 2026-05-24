import sqlite3, bcrypt
c = sqlite3.connect("auth.db")
p = bcrypt.hashpw(b"trannhuy", bcrypt.gensalt()).decode()
c.execute("UPDATE users SET hashed_password=?, email=? WHERE role=?", (p, "admin", "admin"))
c.commit()
print("ADMIN_OK: admin / trannhuy")
c.close()
