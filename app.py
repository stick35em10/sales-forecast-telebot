from flask import Flask, request, jsonify
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
import os
import pandas as pd
import matplotlib.pyplot as plt
import io
import base64
from model import SalesForecaster
import logging
import traceback
import asyncio

# Configuração
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
WEBHOOK_URL = os.getenv('WEBHOOK_URL')

app = Flask(__name__)
forecaster = SalesForecaster()

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Global para armazenar a aplicação do bot
bot_application = None

def init_bot():
    """Inicializa o bot do Telegram"""
    global bot_application
    if TELEGRAM_TOKEN:
        try:
            bot_application = Application.builder().token(TELEGRAM_TOKEN).build()
            
            # Registrar handlers
            bot_application.add_handler(CommandHandler("start", start_command))
            bot_application.add_handler(CommandHandler("previsao", forecast_command))
            bot_application.add_handler(CommandHandler("ajuda", help_command))
            bot_application.add_handler(CommandHandler("status", status_command))
            
            logger.info("✅ Bot do Telegram inicializado")
        except Exception as e:
            logger.error(f"❌ Erro ao inicializar bot: {e}")
    else:
        logger.warning("⚠️ TELEGRAM_TOKEN não configurado")

@app.route('/')
def home():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>🤖 Bot Previsão de Vendas</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; }
            .container { max-width: 800px; margin: 0 auto; }
            .status { padding: 20px; background: #f0f8ff; border-radius: 10px; }
            .instructions { margin-top: 30px; }
            code { background: #f4f4f4; padding: 2px 5px; border-radius: 3px; }
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
                <p><strong>Bot:</strong> {'Configurado' if TELEGRAM_TOKEN else 'Não configurado'}</p>
            </div>
            <div class="instructions">
                <h2>📋 Como usar:</h2>
                <ol>
                    <li>Adicione o bot no Telegram</li>
                    <li>Use o comando <code>/start</code> para iniciar</li>
                    <li>Use <code>/previsao</code> para gerar previsões</li>
                    <li>Use <code>/ajuda</code> para ver todos os comandos</li>
                </ol>
                
                <h2>🔧 Endpoints API:</h2>
                <ul>
                    <li><code>GET /</code> - Esta página</li>
                    <li><code>POST /webhook</code> - Webhook Telegram</li>
                    <li><code>GET /health</code> - Health Check</li>
                    <li><code>GET /set_webhook</code> - Configurar webhook</li>
                    <li><code>GET /forecast</code> - Previsão em JSON</li>
                </ul>
            </div>
        </div>
    </body>
    </html>
    """

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler para comando /start"""
    welcome_text = """
    🏪 *Bem-vindo ao Bot de Previsão de Vendas!*
    
    *Comandos disponíveis:*
    /start - Iniciar o bot
    /previsao - 📊 Gerar previsão de vendas (30 dias)
    /status - ℹ️ Status do sistema
    /ajuda - ❓ Mostrar ajuda
    
    *Desenvolvido com:*
    🤖 Python + Flask + Telegram Bot
    📈 Machine Learning (Random Forest)
    ☁️ Deploy no Render
    
    Clique em /previsao para começar!
    """
    await update.message.reply_text(welcome_text, parse_mode='Markdown')

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler para comando /ajuda"""
    help_text = """
    📊 *Como usar o bot de previsão de vendas:*
    
    */previsao* - Gera previsão de vendas para 30 dias
        - Gráficos interativos
        - Estatísticas detalhadas
        - Tabela completa
    
    */status* - Mostra status do sistema
    */start* - Reiniciar conversa
    */ajuda* - Mostrar esta mensagem
    
    💡 *Dica:* Use /previsao para obter insights sobre vendas futuras!
    """
    await update.message.reply_text(help_text, parse_mode='Markdown')

async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler para comando /status"""
    status_text = """
    📊 *Status do Sistema - Previsão de Vendas*
    
    ✅ *Serviço:* Online
    🤖 *Modelo:* Carregado e Pronto
    📈 *Algoritmo:* Random Forest
    💾 *Dados:* Simulação Realista
    ☁️ *Host:* Render
    
    🚀 *Pronto para prever vendas!*
    
    Use /previsao para gerar sua primeira previsão!
    """
    await update.message.reply_text(status_text, parse_mode='Markdown')

async def forecast_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler para comando /previsao"""
    try:
        # Enviar mensagem de processamento
        processing_msg = await update.message.reply_text("🔄 Gerando previsão de vendas...")
        
        # Gerar previsão
        forecast_df = forecaster.forecast(days=30)
        
        # Configurar estilo do matplotlib
        plt.style.use('default')
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))
        
        # Gráfico de linha principal
        ax1.plot(forecast_df['date'], forecast_df['predicted_sales'], 
                marker='o', linewidth=2.5, markersize=5, color='#2E86AB', 
                markerfacecolor='#A23B72', markeredgecolor='white', markeredgewidth=1)
        ax1.fill_between(forecast_df['date'], forecast_df['predicted_sales'], 
                        alpha=0.3, color='#2E86AB')
        ax1.set_title('📈 Previsão de Vendas - Próximos 30 Dias', 
                     fontsize=16, fontweight='bold', pad=20)
        ax1.set_ylabel('Vendas (R$)', fontsize=12, fontweight='bold')
        ax1.grid(True, alpha=0.3)
        ax1.tick_params(axis='x', rotation=45)
        
        # Formatar eixo Y para valores monetários
        ax1.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'R$ {x:,.0f}'))
        
        # Gráfico de barras
        colors = ['#A23B72' if x < forecast_df['predicted_sales'].mean() 
                 else '#2E86AB' for x in forecast_df['predicted_sales']]
        ax2.bar(forecast_df['date'].dt.strftime('%d/%m'), forecast_df['predicted_sales'],
               color=colors, alpha=0.8, edgecolor='white', linewidth=0.5)
        ax2.set_title('📅 Vendas por Dia', fontsize=14, fontweight='bold', pad=20)
        ax2.set_ylabel('Vendas (R$)', fontsize=12, fontweight='bold')
        ax2.tick_params(axis='x', rotation=45)
        ax2.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'R$ {x:,.0f}'))
        
        # Adicionar linha de média
        avg_sales = forecast_df['predicted_sales'].mean()
        ax2.axhline(y=avg_sales, color='red', linestyle='--', alpha=0.7, 
                   label=f'Média: R$ {avg_sales:,.0f}')
        ax2.legend()
        
        plt.tight_layout()
        
        # Salvar gráfico em buffer
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png', dpi=120, bbox_inches='tight')
        buffer.seek(0)
        plt.close()
        
        # Calcular estatísticas
        total_sales = forecast_df['predicted_sales'].sum()
        avg_daily = forecast_df['predicted_sales'].mean()
        max_day = forecast_df.loc[forecast_df['predicted_sales'].idxmax()]
        min_day = forecast_df.loc[forecast_df['predicted_sales'].idxmin()]
        
        # Texto com estatísticas
        stats_text = f"""
📈 *PREVISÃO DE VENDAS - 30 DIAS*

💰 *Total Previsto:* R$ {total_sales:,.2f}
📊 *Média Diária:* R$ {avg_daily:,.2f}

🏆 *Melhor Dia:* {max_day['date'].strftime('%d/%m')}
🎯 *Vendas Máximas:* R$ {max_day['predicted_sales']:,.2f}

📉 *Dia Mais Fraco:* {min_day['date'].strftime('%d/%m')}
🔻 *Vendas Mínimas:* R$ {min_day['predicted_sales']:,.2f}

*📅 Próximos 5 dias:*
"""
        
        # Adicionar previsões dos primeiros 5 dias
        for _, row in forecast_df.head().iterrows():
            emoji = "🔥" if row['predicted_sales'] > avg_daily else "⚡"
            stats_text += f"{emoji} {row['date'].strftime('%d/%m')}: R$ {row['predicted_sales']:,.2f}\n"
        
        stats_text += f"\n*💡 Dica:* {max_day['date'].strftime('%A')}s tendem a ser mais lucrativos!"
        
        # Enviar gráfico
        await update.message.reply_photo(
            photo=buffer,
            caption=stats_text,
            parse_mode='Markdown'
        )
        
        # Preparar tabela completa
        table_text = "*📋 Previsão Completa (30 dias):*\n\n"
        for _, row in forecast_df.iterrows():
            day_emoji = "🌟" if row['predicted_sales'] == max_day['predicted_sales'] else "📅"
            table_text += f"{day_emoji} {row['date'].strftime('%d/%m')}: R$ {row['predicted_sales']:,.0f}\n"
        
        # Dividir mensagem se for muito longa
        if len(table_text) > 4000:
            middle = len(table_text) // 2
            await update.message.reply_text(table_text[:middle], parse_mode='Markdown')
            await update.message.reply_text(table_text[middle:], parse_mode='Markdown')
        else:
            await update.message.reply_text(table_text, parse_mode='Markdown')
        
        # Mensagem final
        await update.message.reply_text(
            "🚀 *Previsão concluída!*\n\n"
            "Use /previsao a qualquer momento para gerar nova previsão!\n"
            "Use /ajuda para ver todos os comandos.",
            parse_mode='Markdown'
        )
        
        # Remover mensagem de processamento
        try:
            await processing_msg.delete()
        except:
            pass  # Ignora erro se não conseguir deletar
        
    except Exception as e:
        logger.error(f"Erro na previsão: {str(e)}")
        logger.error(traceback.format_exc())
        await update.message.reply_text(
            "❌ *Erro ao gerar previsão*\n\n"
            "Estamos enfrentando problemas técnicos. Tente novamente em alguns minutos.\n"
            "Se o problema persistir, use /status para verificar o sistema.",
            parse_mode='Markdown'
        )

@app.route('/webhook', methods=['POST'])
def webhook():
    """Endpoint para receber mensagens do Telegram"""
    if request.method == "POST" and bot_application:
        try:
            # Processar update de forma assíncrona
            update = Update.de_json(request.get_json(force=True), bot_application.bot)
            
            # Executar o processamento de forma assíncrona
            asyncio.run_coroutine_threadsafe(
                bot_application.process_update(update),
                bot_application._loop
            )
            
            logger.info("Mensagem processada com sucesso")
            return "ok"
            
        except Exception as e:
            logger.error(f"Erro no webhook: {str(e)}")
            logger.error(traceback.format_exc())
            return "error", 500
    
    return "ok"

@app.route('/set_webhook', methods=['GET'])
def set_webhook():
    """Configurar webhook no Telegram"""
    try:
        if not TELEGRAM_TOKEN or not bot_application:
            return jsonify({"status": "error", "message": "TELEGRAM_TOKEN não configurado"})
        
        webhook_url = f"{WEBHOOK_URL}/webhook"
        
        # Configurar webhook de forma assíncrona
        async def setup_webhook():
            await bot_application.bot.set_webhook(webhook_url)
        
        asyncio.run_coroutine_threadsafe(setup_webhook(), bot_application._loop)
        
        logger.info(f"Webhook configurado com sucesso: {webhook_url}")
        return jsonify({
            "status": "success",
            "message": "Webhook configurado",
            "webhook_url": webhook_url
        })
            
    except Exception as e:
        logger.error(f"Erro ao configurar webhook: {str(e)}")
        return jsonify({"status": "error", "error": str(e)})

@app.route('/forecast', methods=['GET'])
def get_forecast():
    """Endpoint para obter previsão em JSON"""
    try:
        days = int(request.args.get('days', '30'))
        forecast_df = forecaster.forecast(days=days)
        
        response_data = {
            'success': True,
            'days': days,
            'total_predicted': forecast_df['predicted_sales'].sum(),
            'daily_average': forecast_df['predicted_sales'].mean(),
            'forecast': forecast_df.to_dict('records'),
            'generated_at': pd.Timestamp.now().isoformat()
        }
        
        return jsonify(response_data)
        
    except Exception as e:
        logger.error(f"Erro na previsão: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Endpoint de health check"""
    health_status = {
        "status": "healthy",
        "service": "sales-forecast-bot",
        "model_ready": forecaster.is_trained,
        "telegram_configured": TELEGRAM_TOKEN is not None and bot_application is not None,
        "webhook_url": WEBHOOK_URL
    }
    return jsonify(health_status)

def initialize_model():
    """Treina o modelo na inicialização"""
    try:
        logger.info("Inicializando modelo de previsão...")
        forecaster.train_model()
        logger.info("✅ Modelo inicializado com sucesso!")
    except Exception as e:
        logger.error(f"❌ Erro na inicialização do modelo: {str(e)}")

if __name__ == '__main__':
    # Inicializar modelo e bot
    print("🚀 Iniciando servidor de previsão de vendas...")
    initialize_model()
    init_bot()
    
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
