import pandas as pd
from sqlalchemy import create_engine, text

# Usando SQLite (banco local em arquivo, sem precisar de Docker)
DATABASE_URL = "sqlite:///iot_database.db"
engine = create_engine(DATABASE_URL)

def executar_pipeline():
    print("A gerar dados simulados de IoT...")
    dados = {
        'device_id': ['sensor_01', 'sensor_01', 'sensor_02', 'sensor_02', 'sensor_03', 'sensor_03'],
        'temperature': [22.5, 24.1, 19.8, 28.3, 21.0, 25.4],
        'timestamp': [
            '2026-06-01 10:00:00', '2026-06-01 11:00:00', 
            '2026-06-01 10:00:00', '2026-06-01 11:00:00',
            '2026-06-01 10:00:00', '2026-06-01 11:00:00'
        ]
    }
    df = pd.DataFrame(dados)
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df['data'] = df['timestamp'].dt.date
    df['hora'] = df['timestamp'].dt.hour

    print("A inserir dados no banco de dados...")
    df.to_sql('temperature_readings', engine, if_exists='replace', index=False)

    print("A criar as Views SQL...")
    with engine.connect() as connection:
        connection.execute(text("""
            CREATE VIEW IF NOT EXISTS avg_temp_por_dispositivo AS
            SELECT device_id, AVG(temperature) as avg_temp
            FROM temperature_readings
            GROUP BY device_id;
        """))
        
        connection.execute(text("""
            CREATE VIEW IF NOT EXISTS leituras_por_hora AS
            SELECT hora, COUNT(*) as contagem
            FROM temperature_readings
            GROUP BY hora
            ORDER BY hora;
        """))

        connection.execute(text("""
            CREATE VIEW IF NOT EXISTS temp_max_min_por_dia AS
            SELECT data, MAX(temperature) as temp_max, MIN(temperature) as temp_min
            FROM temperature_readings
            GROUP BY data;
        """))
        connection.commit()
    print("Pipeline executado com sucesso e Views criadas!")

if __name__ == "__main__":
    executar_pipeline()