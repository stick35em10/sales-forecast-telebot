from flask import Flask, request, jsonify
import os
import pandas as pd
from model import SalesForecaster
import logging

app = Flask(__name__)
forecaster = SalesForecaster()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.route('/')
def home():
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>🤖 Bot Previsão de Vendas</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; }
            .container { max-width: 800px; margin: 0 auto; }
            .status { padding: 20px; background: #f0f8ff; border-radius: 10px; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🏪 Bot de Previsão de Vendas</h1>
            <div class="status">
                <h2>✅ Sistema Operacional</h2>
                <p><strong>Status:</strong> Online e funcionando</p>
                <p><strong>Serviço:</strong> Previsão de Vendas via Telegram</p>
                <p><strong>Modelo:</strong> Machine Learning (Random Forest)</p>
            </div>
            <div class="instructions">
                <h2>🔧 Endpoints:</h2>
                <ul>
                    <li><code>GET /</code> - Esta página</li>
                    <li><code>GET /health</code> - Health Check</li>
                    <li><code>GET /forecast</code> - Previsão JSON</li>
                    <li><code>GET /set_webhook</code> - Configurar webhook Telegram</li>
                </ul>
            </div>
        </div>
    </body>
    </html>
    '''

@app.route('/health')
def health_check():
    return jsonify({
        "status": "healthy", 
        "service": "sales-forecast-bot",
        "model_ready": forecaster.is_trained
    })

@app.route('/forecast')
def get_forecast():
    try:
        days = int(request.args.get('days', '7'))
        forecast = forecaster.forecast(days=days)
        return jsonify({
            'success': True,
            'days': days,
            'forecast': forecast.to_dict('records')
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/set_webhook')
def set_webhook():
    return jsonify({
        "status": "success",
        "message": "Webhook endpoint pronto - configure com URL completa",
        "webhook_url": f"{os.getenv('WEBHOOK_URL', 'https://your-app.onrender.com')}/webhook"
    })

def initialize_model():
    try:
        logger.info("Inicializando modelo...")
        forecaster.train_model()
        logger.info("✅ Modelo inicializado!")
    except Exception as e:
        logger.error(f"❌ Erro no modelo: {e}")

if __name__ == '__main__':
    initialize_model()
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
