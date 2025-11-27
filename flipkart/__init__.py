# Allow using PyMySQL as a drop-in replacement for MySQLdb on Windows
try:
    import pymysql  # type: ignore
    pymysql.install_as_MySQLdb()
except Exception:
    # If PyMySQL is not installed yet, the project will still start;
    # installation steps are provided in the README/instructions.
    pass
