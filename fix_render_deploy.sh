#!/bin/bash

echo "🔧 Corrigindo deploy para Render..."
echo "📝 Forçando Python 3.11 e versões compatíveis"

# 1. runtime.txt com Python 3.11
echo "python-3.11.8" > runtime.txt
echo "✅ runtime.txt atualizado"

# 2. requirements.txt compatível
cat > requirements.txt << 'REQ'
pandas==2.0.3
numpy==1.24.3
scikit-learn==1.3.0
matplotlib==3.7.2
seaborn==0.12.2
flask==2.3.3
flask-cors==4.0.0
gunicorn==21.2.0
joblib==1.3.2
python-dotenv==1.0.0
python-telegram-bot==20.7
twilio==8.10.0
openpyxl==3.1.2
plotly==5.15.0
kaleido==0.2.1
setuptools==68.2.2
wheel==0.41.3
REQ
echo "✅ requirements.txt atualizado"

# 3. Atualizar app.py para ser mais compatível
cat > app_simple.py << 'PY'
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
PY

# Renomear para app.py principal
mv app_simple.py app.py
echo "✅ app.py simplificado"

# 4. Criar arquivo de build específico
cat > build.sh << 'BUILD'
#!/bin/bash
echo "🔨 Build otimizado para Render..."
pip install --upgrade pip
pip install -r requirements.txt
echo "✅ Build completo!"
BUILD

chmod +x build.sh

echo ""
echo "🎉 CORREÇÕES APLICADAS!"
echo "========================"
echo "📦 Para deploy:"
echo "   git add ."
echo "   git commit -m 'Fix: Python 3.11 compatibility'"
echo "   git push"
echo ""
echo "🔧 Mudanças:"
echo "   • Python 3.11.8 (compatível)"
echo "   • Versões estáveis das bibliotecas"
echo "   • App simplificado"
echo "   • Build otimizado"
echo ""
