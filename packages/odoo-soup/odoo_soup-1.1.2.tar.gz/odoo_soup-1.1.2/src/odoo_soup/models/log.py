from sqlalchemy import Column, Integer, Text, Double, DateTime, String


# Factory for logline model so that name can be dynamic
def create_log_model(table_name: str, base):
    class Log(base):
        __tablename__ = table_name

        id = Column(Integer, primary_key=True)
        date = Column(DateTime, nullable=False)
        level = Column(String(15))
        origin = Column(Text)
        type = Column(String(64))
        ip = Column(String(128))
        http = Column(String(10))
        route = Column(Text)
        code = Column(Integer)
        time = Column(Double)
        user = Column(Text)
        object = Column(Text)
        records = Column(Text)
        text = Column(Text)

    return Log
