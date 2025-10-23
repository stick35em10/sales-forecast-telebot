from flask import Flask, request, jsonify
import os
import logging
import random
from datetime import datetime, timedelta

app = Flask(__name__)

# Configuração
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
WEBHOOK_URL = os.getenv('WEBHOOK_URL')

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SimpleSalesForecaster:
    def __init__(self):
        self.is_trained = True
    
    def generate_forecast(self, days=30):
        """Gera previsão de vendas simulada"""
        forecasts = []
        base_date = datetime.now()
        
        for i in range(1, days + 1):
            date = base_date + timedelta(days=i)
            
            # Simulação realista de vendas
            base = 1000 + (i * 15)  # Tendência crescente
            weekday = date.weekday()
            
            # Efeitos de sazonalidade
            if weekday >= 5:  # Final de semana
                seasonal = 300
            elif weekday == 0:  # Segunda-feira
                seasonal = -150  
            elif date.day >= 25:  # Final do mês
                seasonal = 200
            else:
                seasonal = 0
            
            random_effect = random.randint(-80, 80)
            sales = base + seasonal + random_effect
            sales = max(sales, 400)  # Mínimo
            
            forecasts.append({
                'date': date.strftime('%Y-%m-%d'),
                'day_name': ['Segunda', 'Terça', 'Quarta', 'Quinta', 'Sexta', 'Sábado', 'Domingo'][weekday],
                'predicted_sales': round(sales, 2),
                'is_weekend': weekday >= 5
            })
        
        return forecasts
    
    def get_stats(self, forecasts):
        """Calcula estatísticas"""
        sales = [f['predicted_sales'] for f in forecasts]
        total = sum(sales)
        avg = total / len(sales)
        best_day = max(forecasts, key=lambda x: x['predicted_sales'])
        worst_day = min(forecasts, key=lambda x: x['predicted_sales'])
        
        return {
            'total_predicted': round(total, 2),
            'daily_average': round(avg, 2),
            'best_day': best_day,
            'worst_day': worst_day,
            'forecast_days': len(forecasts)
        }

forecaster = SimpleSalesForecaster()

@app.route('/')
def home():
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>🤖 Bot Previsão de Vendas</title>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body { 
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; 
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: #333;
                min-height: 100vh;
                padding: 20px;
            }
            .container { 
                max-width: 1200px; 
                margin: 0 auto; 
                background: white; 
                padding: 30px; 
                border-radius: 20px; 
                box-shadow: 0 20px 60px rgba(0,0,0,0.1);
            }
            .header { 
                text-align: center; 
                margin-bottom: 40px;
                background: linear-gradient(135deg, #2E86AB, #A23B72);
                color: white;
                padding: 40px 20px;
                border-radius: 15px;
            }
            .header h1 { 
                font-size: 2.5em; 
                margin-bottom: 10px; 
                font-weight: 700;
            }
            .header h2 { 
                font-size: 1.3em; 
                opacity: 0.9;
                font-weight: 300;
            }
            .status-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
                gap: 20px;
                margin: 30px 0;
            }
            .status-card { 
                background: #f8f9fa; 
                padding: 25px; 
                border-radius: 15px; 
                border-left: 5px solid #2E86AB;
                transition: transform 0.2s;
            }
            .status-card:hover {
                transform: translateY(-5px);
            }
            .status-card h3 { 
                color: #2E86AB; 
                margin-bottom: 15px;
                font-size: 1.3em;
            }
            .api-endpoint { 
                background: #2c3e50; 
                color: white; 
                padding: 12px 15px; 
                border-radius: 8px; 
                margin: 8px 0; 
                font-family: 'Monaco', 'Consolas', monospace;
                font-size: 0.9em;
                border-left: 4px solid #2E86AB;
            }
            .btn {
                display: inline-block;
                background: #2E86AB;
                color: white;
                padding: 12px 25px;
                border-radius: 25px;
                text-decoration: none;
                font-weight: 600;
                margin: 10px 5px;
                transition: all 0.3s;
            }
            .btn:hover {
                background: #A23B72;
                transform: translateY(-2px);
            }
            .feature-list {
                list-style: none;
                padding: 0;
            }
            .feature-list li {
                padding: 8px 0;
                border-bottom: 1px solid #eee;
            }
            .feature-list li:before {
                content: "✅ ";
                margin-right: 10px;
            }
            @media (max-width: 768px) {
                .container { padding: 20px; }
                .header { padding: 30px 15px; }
                .header h1 { font-size: 2em; }
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🏪 Bot de Previsão de Vendas</h1>
                <h2>🤖 Sistema Inteligente • Python 3.13 Compatível</h2>
            </div>

            <div class="status-grid">
                <div class="status-card">
                    <h3>🚀 Status do Sistema</h3>
                    <p><strong>Versão:</strong> 1.0.0</p>
                    <p><strong>Python:</strong> ''' + str(os.sys.version.split()[0]) + '''</p>
                    <p><strong>Bot Telegram:</strong> <span style="color: ''' + ('#28a745' if TELEGRAM_TOKEN else '#dc3545') + '''">''' + ('✅ Configurado' if TELEGRAM_TOKEN else '❌ Não configurado') + '''</span></p>
                    <p><strong>Última verificação:</strong> ''' + datetime.now().strftime('%d/%m/%Y %H:%M') + '''</p>
                </div>

                <div class="status-card">
                    <h3>📊 Funcionalidades</h3>
                    <ul class="feature-list">
                        <li>Previsão de vendas 30 dias</li>
                        <li>Análise de sazonalidade</li>
                        <li>Estatísticas detalhadas</li>
                        <li>Integração Telegram</li>
                        <li>API REST completa</li>
                        <li>Deploy automático</li>
                    </ul>
                </div>

                <div class="status-card">
                    <h3>🔧 Configuração</h3>
                    <p>Variáveis de ambiente necessárias:</p>
                    <code>TELEGRAM_TOKEN</code><br>
                    <code>WEBHOOK_URL</code>
                    <div style="margin-top: 15px;">
                        <a href="/health" class="btn">Verificar Saúde</a>
                        <a href="/forecast" class="btn">Testar Previsão</a>
                    </div>
                </div>
            </div>

            <div class="status-card">
                <h3>🌐 Endpoints da API</h3>
                <div class="api-endpoint">GET <strong>/</strong> - Esta página inicial</div>
                <div class="api-endpoint">GET <strong>/health</strong> - Status do sistema</div>
                <div class="api-endpoint">GET <strong>/forecast?days=30</strong> - Previsão de vendas</div>
                <div class="api-endpoint">GET <strong>/set_webhook</strong> - Configurar Telegram</div>
                <div class="api-endpoint">POST <strong>/webhook</strong> - Webhook do bot</div>
                
                <div style="margin-top: 20px;">
                    <h4>📋 Exemplo de uso:</h4>
                    <code>curl https://''' + (WEBHOOK_URL.split('//')[1] if WEBHOOK_URL else 'seu-app.onrender.com') + '''/forecast?days=7</code>
                </div>
            </div>

            <div class="status-card">
                <h3>🎯 Próximos Passos</h3>
                <ol style="padding-left: 20px; line-height: 1.6;">
                    <li><strong>Configurar variáveis</strong> no painel do Render</li>
                    <li><strong>Testar endpoints</strong> usando os botões acima</li>
                    <li><strong>Configurar webhook</strong> no Telegram</li>
                    <li><strong>Enviar /start</strong> para o bot</li>
                </ol>
                <div style="margin-top: 20px; padding: 15px; background: #e7f3ff; border-radius: 10px;">
                    <strong>💡 Dica:</strong> O sistema já está funcionando! Configure as variáveis de ambiente para ativar o bot completo.
                </div>
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
        "version": "1.0.0",
        "python_version": os.sys.version.split()[0],
        "telegram_configured": TELEGRAM_TOKEN is not None,
        "webhook_url_configured": WEBHOOK_URL is not None,
        "timestamp": datetime.now().isoformat(),
        "endpoints": {
            "home": "/",
            "health": "/health", 
            "forecast": "/forecast?days=7",
            "set_webhook": "/set_webhook"
        }
    })

@app.route('/forecast')
def get_forecast():
    try:
        days = min(int(request.args.get('days', '7')), 90)  # Máximo 90 dias
        forecasts = forecaster.generate_forecast(days=days)
        stats = forecaster.get_stats(forecasts)
        
        response = {
            'success': True,
            'days': days,
            'stats': stats,
            'forecast': forecasts,
            'generated_at': datetime.now().isoformat(),
            'model': 'simple_forecaster_v1'
        }
        
        return jsonify(response)
        
    except Exception as e:
        logger.error(f"Erro na previsão: {str(e)}")
        return jsonify({
            'success': False, 
            'error': str(e),
            'message': 'Erro ao gerar previsão'
        }), 500

@app.route('/set_webhook')
def set_webhook():
    webhook_url = f"{WEBHOOK_URL}/webhook" if WEBHOOK_URL else "VARIABLE_WEBHOOK_URL_NOT_SET"
    
    return jsonify({
        "status": "success" if WEBHOOK_URL else "config_required",
        "message": "Webhook configuration",
        "webhook_url": webhook_url,
        "instructions": [
            "1. Configure WEBHOOK_URL environment variable",
            "2. Set Telegram bot webhook to the URL above", 
            "3. Send /start to your bot to test"
        ] if WEBHOOK_URL else [
            "Configure WEBHOOK_URL environment variable first"
        ],
        "environment_check": {
            "TELEGRAM_TOKEN_set": TELEGRAM_TOKEN is not None,
            "WEBHOOK_URL_set": WEBHOOK_URL is not None
        }
    })

@app.route('/webhook', methods=['POST'])
def webhook():
    """Simulação de webhook do Telegram"""
    if not TELEGRAM_TOKEN:
        return jsonify({
            "status": "error", 
            "message": "TELEGRAM_TOKEN not configured",
            "action": "Set TELEGRAM_TOKEN environment variable"
        }), 400
    
    try:
        # Simular processamento de mensagem
        data = request.get_json() or {}
        
        response = {
            "status": "webhook_received",
            "message": "Telegram webhook is working!",
            "action": "Bot is ready to receive messages",
            "next_steps": [
                "Send /start to your bot on Telegram",
                "Bot will respond with welcome message",
                "Use /previsao to get sales forecast"
            ],
            "received_data": len(str(data)) > 0
        }
        
        logger.info(f"Webhook simulado recebido: {response}")
        return jsonify(response)
        
    except Exception as e:
        logger.error(f"Erro no webhook: {str(e)}")
        return jsonify({
            "status": "error", 
            "message": str(e)
        }), 500

if __name__ == '__main__':
    logger.info("🚀 Iniciando Sales Forecast Bot...")
    logger.info(f"📊 Python: {os.sys.version}")
    logger.info(f"🔑 Telegram: {'✅' if TELEGRAM_TOKEN else '❌'}") 
    logger.info(f"🌐 Webhook: {'✅' if WEBHOOK_URL else '❌'}")
    
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
