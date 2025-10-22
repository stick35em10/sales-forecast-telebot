import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, mean_squared_error
import joblib
import os

class SalesForecaster:
    def __init__(self):
        self.model = None
        self.is_trained = False
        
    def generate_sample_data(self, periods=365):
        """Gera dados de exemplo para demonstração"""
        dates = pd.date_range(start='2022-01-01', periods=periods, freq='D')
        
        # Tendência
        trend = np.linspace(100, 500, periods)
        
        # Sazonalidade semanal
        day_of_week = dates.dayofweek
        seasonal_weekly = 50 * np.sin(2 * np.pi * day_of_week / 7)
        
        # Sazonalidade mensal
        day_of_month = dates.day
        seasonal_monthly = 30 * np.sin(2 * np.pi * day_of_month / 30)
        
        # Ruído aleatório
        noise = np.random.normal(0, 20, periods)
        
        # Vendas totais
        sales = trend + seasonal_weekly + seasonal_monthly + noise
        sales = np.maximum(sales, 0)  # Garantir valores não negativos
        
        # Criar DataFrame
        df = pd.DataFrame({
            'date': dates,
            'sales': sales,
            'day_of_week': day_of_week,
            'day_of_month': day_of_month,
            'month': dates.month,
            'week_of_year': dates.isocalendar().week
        })
        
        return df
    
    def create_features(self, df):
        """Cria features para o modelo"""
        df = df.copy()
        df['day_sin'] = np.sin(2 * np.pi * df['day_of_week']/7)
        df['day_cos'] = np.cos(2 * np.pi * df['day_of_week']/7)
        df['month_sin'] = np.sin(2 * np.pi * df['month']/12)
        df['month_cos'] = np.cos(2 * np.pi * df['month']/12)
        return df
    
    def train_model(self, df=None):
        """Treina o modelo de previsão"""
        if df is None:
            df = self.generate_sample_data()
        
        df = self.create_features(df)
        
        # Features
        feature_columns = ['day_sin', 'day_cos', 'month_sin', 'month_cos', 
                          'day_of_month', 'week_of_year']
        
        X = df[feature_columns]
        y = df['sales']
        
        # Split dos dados
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )
        
        # Treinar modelo
        self.model = RandomForestRegressor(
            n_estimators=100,
            random_state=42,
            max_depth=10
        )
        
        self.model.fit(X_train, y_train)
        
        # Avaliar modelo
        y_pred = self.model.predict(X_test)
        mae = mean_absolute_error(y_test, y_pred)
        rmse = np.sqrt(mean_squared_error(y_test, y_pred))
        
        self.is_trained = True
        
        # Salvar modelo
        joblib.dump(self.model, 'sales_model.joblib')
        
        print(f"✅ Modelo treinado com sucesso!")
        print(f"📊 MAE: {mae:.2f}, RMSE: {rmse:.2f}")
        
        return mae, rmse
    
    def forecast(self, days=30):
        """Faz previsão para os próximos dias"""
        if not self.is_trained:
            if os.path.exists('sales_model.joblib'):
                self.model = joblib.load('sales_model.joblib')
                self.is_trained = True
                print("✅ Modelo carregado do arquivo")
            else:
                print("🔄 Treinando modelo...")
                self.train_model()
        
        # Criar datas futuras
        last_date = pd.Timestamp.now().normalize()
        future_dates = pd.date_range(
            start=last_date + pd.Timedelta(days=1),
            periods=days,
            freq='D'
        )
        
        # Criar DataFrame com features futuras
        future_df = pd.DataFrame({
            'date': future_dates,
            'day_of_week': future_dates.dayofweek,
            'day_of_month': future_dates.day,
            'month': future_dates.month,
            'week_of_year': future_dates.isocalendar().week
        })
        
        future_df = self.create_features(future_df)
        
        feature_columns = ['day_sin', 'day_cos', 'month_sin', 'month_cos', 
                          'day_of_month', 'week_of_year']
        
        # Fazer previsões
        predictions = self.model.predict(future_df[feature_columns])
        
        result_df = pd.DataFrame({
            'date': future_dates,
            'predicted_sales': predictions
        })
        
        print(f"✅ Previsão gerada para {days} dias")
        return result_df

# Teste do modelo
if __name__ == "__main__":
    print("🧪 Testando o modelo...")
    forecaster = SalesForecaster()
    forecaster.train_model()
    forecast = forecaster.forecast(7)
    print(forecast.head())
