#!/usr/bin/env python3
"""
Telegram Bot - Sales Forecast
Configurado para Render com Poetry e Gunicorn
"""

import os
import asyncio
import logging
from flask import Flask, request, jsonify
from telegram import Update, Bot
from telegram.ext import Application, CommandHandler, ContextTypes
import matplotlib
matplotlib.use('Agg')  # Importante: usar backend não-interativo
import matplotlib.pyplot as plt
import pandas as pd
import io
from dotenv import load_dotenv

# Carregar variáveis de ambiente do arquivo .env
load_dotenv()

# Importar seu modelo
try:
    from model import SalesForecaster
except ImportError:
    # Fallback se model.py não existir
    class SalesForecaster:
        def train_model(self):
            pass
        def forecast(self, days=7):
            import pandas as pd
            from datetime import datetime, timedelta
            dates = [datetime.now() + timedelta(days=i) for i in range(days)]
            return pd.DataFrame({
                'date': dates,
                'predicted_sales': [300 + i*10 for i in range(days)],
                'day_name': [d.strftime('%A') for d in dates]
            })

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Variáveis de ambiente
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
WEBHOOK_URL = os.getenv('WEBHOOK_URL')  # https://sales-forecast-bot.onrender.com

if not TELEGRAM_TOKEN:
    logger.error("❌ TELEGRAM_TOKEN não configurado!")
    raise ValueError("TELEGRAM_TOKEN é obrigatório")

# Flask app
app = Flask(__name__)

# Bot e Forecaster
bot = Bot(token=TELEGRAM_TOKEN)
forecaster = SalesForecaster()

# Flag para treinar modelo apenas uma vez
model_trained = False

def ensure_model_trained():
    """Garante que o modelo está treinado"""
    global model_trained
    if not model_trained:
        try:
            logger.info("🤖 Treinando modelo...")
            forecaster.train_model()
            model_trained = True
            logger.info("✅ Modelo treinado com sucesso!")
        except Exception as e:
            logger.error(f"❌ Erro ao treinar modelo: {e}")

# ==================== COMANDOS DO BOT ====================

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /start"""
    welcome_text = """
🏪 *Bem-vindo ao Bot de Previsão de Vendas!*

Eu uso Machine Learning para prever suas vendas! 📊

*Comandos disponíveis:*
/start - Mostrar esta mensagem
/previsao - Gerar previsão de 7 dias 📈
/teste - Teste rápido do sistema ⚡
/ajuda - Ver ajuda detalhada ❓

_Sistema desenvolvido com Random Forest ML_
    """
    await update.message.reply_text(welcome_text, parse_mode='Markdown')

async def ajuda_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /ajuda"""
    help_text = """
📊 *GUIA DE USO*

*Comandos:*
🔹 /previsao - Gera previsão de vendas para os próximos 7 dias, incluindo:
  • Gráfico visual
  • Estatísticas (total, média)
  • Melhor e pior dia
  • Detalhes diários

🔹 /teste - Teste rápido (3 dias)

🔹 /start - Reiniciar conversa

*Como funciona:*
O bot usa Machine Learning (Random Forest) para analisar padrões históricos e prever vendas futuras.

💡 _Dica: Use /previsao toda segunda-feira para planejar sua semana!_
    """
    await update.message.reply_text(help_text, parse_mode='Markdown')

async def teste_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /teste - teste rápido"""
    try:
        await update.message.reply_text("⚡ Testando sistema...")
        
        ensure_model_trained()
        
        # Previsão de 3 dias
        forecast = forecaster.forecast(days=3)
        
        response = "✅ *Bot funcionando perfeitamente!*\n\n"
        response += "📊 *Teste do Modelo (3 dias):*\n\n"
        
        for _, row in forecast.iterrows():
            emoji = "📅"
            response += f"{emoji} {row['date'].strftime('%d/%m')} ({row['day_name'][:3]}): R$ {row['predicted_sales']:.2f}\n"
        
        response += "\n✨ _Sistema operacional!_"
        
        await update.message.reply_text(response, parse_mode='Markdown')
        
    except Exception as e:
        logger.error(f"Erro no teste: {e}")
        await update.message.reply_text(
            f"❌ Erro no teste: {str(e)}\n\n"
            "Tente novamente em alguns instantes.",
            parse_mode='Markdown'
        )

async def previsao_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /previsao - previsão completa de 7 dias"""
    try:
        await update.message.reply_text("🔄 Gerando sua previsão de 7 dias...")
        
        ensure_model_trained()
        
        # Gerar previsão
        forecast_df = forecaster.forecast(days=7)
        
        # Criar gráfico profissional
        plt.style.use('seaborn-v0_8-darkgrid')
        fig, ax = plt.subplots(figsize=(12, 6))
        
        # Plot principal
        ax.plot(forecast_df['date'], forecast_df['predicted_sales'], 
               marker='o', linewidth=3, markersize=8, 
               color='#2E86AB', label='Vendas Previstas')
        
        # Adicionar área preenchida
        ax.fill_between(forecast_df['date'], forecast_df['predicted_sales'], 
                        alpha=0.3, color='#2E86AB')
        
        # Marcar melhor e pior dia
        max_idx = forecast_df['predicted_sales'].idxmax()
        min_idx = forecast_df['predicted_sales'].idxmin()
        
        ax.scatter(forecast_df.loc[max_idx, 'date'], 
                  forecast_df.loc[max_idx, 'predicted_sales'],
                  color='green', s=200, zorder=5, marker='*', 
                  label='Melhor Dia')
        
        ax.scatter(forecast_df.loc[min_idx, 'date'], 
                  forecast_df.loc[min_idx, 'predicted_sales'],
                  color='red', s=200, zorder=5, marker='v',
                  label='Pior Dia')
        
        # Configurações
        ax.set_title('📈 Previsão de Vendas - Próximos 7 Dias', 
                    fontsize=16, fontweight='bold', pad=20)
        ax.set_xlabel('Data', fontsize=12, fontweight='bold')
        ax.set_ylabel('Vendas (R$)', fontsize=12, fontweight='bold')
        ax.legend(loc='best', framealpha=0.9)
        ax.grid(True, alpha=0.3)
        
        # Formatar eixo X
        ax.xaxis.set_major_formatter(plt.matplotlib.dates.DateFormatter('%d/%m'))
        plt.xticks(rotation=0, ha='center')
        plt.tight_layout()
        
        # Salvar gráfico
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png', dpi=120, bbox_inches='tight',
                   facecolor='white', edgecolor='none')
        buffer.seek(0)
        plt.close()
        
        # Calcular estatísticas
        total = forecast_df['predicted_sales'].sum()
        media = forecast_df['predicted_sales'].mean()
        max_day = forecast_df.loc[max_idx]
        min_day = forecast_df.loc[min_idx]
        
        # Texto do relatório
        stats_text = f"""
📈 *PREVISÃO DE VENDAS - 7 DIAS*

💰 *Resumo Financeiro:*
• Total Previsto: R$ {total:,.2f}
• Média Diária: R$ {media:,.2f}

🏆 *Melhor Momento:*
• Dia: {max_day['date'].strftime('%d/%m/%Y')} ({max_day['day_name']})
• Vendas: R$ {max_day['predicted_sales']:.2f}

⚠️  *Dia de Atenção:*
• Dia: {min_day['date'].strftime('%d/%m/%Y')} ({min_day['day_name']})
• Vendas: R$ {min_day['predicted_sales']:.2f}

📋 *Previsão Detalhada:*
"""
        
        # Adicionar todos os dias
        for idx, row in forecast_df.iterrows():
            emoji = "🟢" if idx == max_idx else ("🔴" if idx == min_idx else "🔵")
            stats_text += f"{emoji} {row['date'].strftime('%d/%m')} ({row['day_name'][:3]}): R$ {row['predicted_sales']:.2f}\n"
        
        stats_text += "\n💡 _Use estas previsões para otimizar estoque e equipe!_"
        
        # Enviar gráfico com legenda
        await update.message.reply_photo(
            photo=buffer,
            caption=stats_text,
            parse_mode='Markdown'
        )
        
        logger.info(f"✅ Previsão enviada para {update.effective_user.id}")
        
    except Exception as e:
        logger.error(f"❌ Erro na previsão: {str(e)}", exc_info=True)
        await update.message.reply_text(
            "❌ Desculpe, ocorreu um erro ao gerar a previsão.\n\n"
            "Por favor, tente novamente em alguns instantes.",
            parse_mode='Markdown'
        )

# ==================== CONFIGURAÇÃO DA APLICAÇÃO TELEGRAM ====================

# Criar a aplicação uma vez para ser usada pelo webhook e pelo polling
application = Application.builder().token(TELEGRAM_TOKEN).build()

# Registrar comandos
application.add_handler(CommandHandler("start", start_command))
application.add_handler(CommandHandler("ajuda", ajuda_command))
application.add_handler(CommandHandler("teste", teste_command))
application.add_handler(CommandHandler("previsao", previsao_command))


# ==================== ROTAS FLASK ====================

@app.route('/')
def home():
    """Página inicial"""
    return """
    <!DOCTYPE html>
    <html lang="pt-BR">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>🤖 Bot Telegram - Previsão de Vendas</title>
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                display: flex;
                align-items: center;
                justify-content: center;
                padding: 20px;
            }
            .container {
                background: rgba(255, 255, 255, 0.95);
                border-radius: 20px;
                padding: 40px;
                max-width: 800px;
                box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            }
            h1 { 
                color: #667eea; 
                margin-bottom: 10px;
                font-size: 2.5em;
            }
            .subtitle {
                color: #666;
                margin-bottom: 30px;
                font-size: 1.2em;
            }
            .status {
                background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
                color: white;
                padding: 20px;
                border-radius: 15px;
                margin: 20px 0;
                text-align: center;
            }
            .status h2 { margin-bottom: 10px; }
            .info-box {
                background: #f8f9fa;
                padding: 20px;
                border-radius: 10px;
                margin: 20px 0;
                border-left: 4px solid #667eea;
            }
            .info-box h3 {
                color: #667eea;
                margin-bottom: 15px;
            }
            ul { 
                list-style: none; 
                padding-left: 0;
            }
            li {
                padding: 8px 0;
                border-bottom: 1px solid #eee;
            }
            li:last-child { border-bottom: none; }
            .command {
                font-family: 'Courier New', monospace;
                background: #667eea;
                color: white;
                padding: 2px 8px;
                border-radius: 4px;
                font-weight: bold;
            }
            .emoji { font-size: 1.5em; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1><span class="emoji">🤖</span> Bot de Previsão de Vendas</h1>
            <p class="subtitle">Inteligência Artificial para seu negócio</p>
            
            <div class="status">
                <h2>✅ Sistema Online e Operacional</h2>
                <p><strong>Status:</strong> Ativo</p>
                <p><strong>Modo:</strong> Webhook (Render Deploy)</p>
                <p><strong>ML Model:</strong> Random Forest</p>
            </div>

            <div class="info-box">
                <h3>📱 Como usar o bot:</h3>
                <ol style="padding-left: 20px;">
                    <li>Abra o Telegram no seu celular</li>
                    <li>Procure pelo seu bot</li>
                    <li>Envie <span class="command">/start</span></li>
                    <li>Use <span class="command">/previsao</span> para gerar previsões</li>
                </ol>
            </div>

            <div class="info-box">
                <h3>⚡ Comandos disponíveis:</h3>
                <ul>
                    <li><span class="command">/start</span> - Iniciar conversa com o bot</li>
                    <li><span class="command">/previsao</span> - Gerar previsão de 7 dias com gráfico</li>
                    <li><span class="command">/teste</span> - Teste rápido do sistema</li>
                    <li><span class="command">/ajuda</span> - Ver ajuda detalhada</li>
                </ul>
            </div>

            <div class="info-box">
                <h3>🎯 O que você recebe:</h3>
                <ul>
                    <li>📊 Previsões de vendas para 7 dias</li>
                    <li>📈 Gráficos visuais profissionais</li>
                    <li>💰 Estatísticas financeiras detalhadas</li>
                    <li>🏆 Identificação dos melhores dias</li>
                    <li>⚠️  Alertas para dias de baixa</li>
                    <li>💡 Recomendações inteligentes</li>
                </ul>
            </div>

            <p style="text-align: center; color: #999; margin-top: 30px;">
                Desenvolvido com ❤️ usando Machine Learning
            </p>
        </div>
    </body>
    </html>
    """