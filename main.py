import requests
import time
import threading
from flask import Flask

# --- CONFIGURAÇÃO WEB PARA NUVEM ---
app = Flask('')

@app.route('/')
def home():
    return "Bot Polymarket Copa 2026 ativo e rodando!"

def run_flask():
    # O Render exige que o script escute em uma porta (geralmente 10000)
    app.run(host='0.0.0.0', port=10000)

# --- SEU CÓDIGO DO ROBÔ ---
TOKEN = "8543455492:AAGDehwxwgwkUlCxu-mn2wD6PsMsGeaMr_c"
CHAT_ID = "-1004332406435"

CARTEIRAS_ALVO = [
    "0x81da605d7dac06478367ed1bae0593b7791ca109",
    "0x58483a07148bf1c4ddc4a1f0c0ea8daeb9e8a698",
    "0x26437896ed9dfeb2f69765edcafe8fdceaab39ae",
    "0xed64a7bf029040aa331abc87902434d815ef217d",
    "0x3f87d51f27ba6e19ec52aaeebb68559a839c742c",
    "0x96cfcb0c30942cfcd1cdf76c7d408794d66b1acb",
    "0xbc11a64ab34a03a043fbe80598fa065ee87eeec6",
    "0x97cb27132b9dd66a2ef49390893cbeb26c3fe4d0",
    "0x664ce9fb97ae1bbd538d7381b2f4e92dab16f49c",
    "0x5bdd63899629bcfa0375496df6fdc271c18dc4cb",
    "0xb61b2079b95f6b7476fd3203e0274ffb93308a06",
    "0x5e4c3b5b81171e2ca4ab776ac0d6bba787f9dba2",
    "0x0f0edbb5fca07a7efffe283624f085a7b2e2a019",
    "0x3d1ecf16942939b3603c2539a406514a40b504d0",
    "0xd60419ae698bd0ae7c0ef69470bfc1e0f9a9bc8a",
    "0xa36fcb6947c4ac1f09ee894aa1fd0756b90e180b",
    "0xe9a6ed2e4d4ee8ce47cd47cac834746dc4cf627b"
]

ultimas_trades_enviadas = {}
VALOR_MINIMO_INVESTIDO = 1000.0

TERMOS_COPA = [
    "world cup", "copa do mundo", "fifa", "group a", "group b", "group c", "group d", 
    "group e", "group f", "group g", "group h",
    "mexico", "méxico", "uruguay", "uruguaia", "uruguaio", "germany", "alemanha",
    "argentina", "norway", "noruega", "colombia", "colômbia", "switzerland", "suíça", 
    "suiça", "canada", "canadá", "bosnia", "bósnia", "morocco", "marrocos",
    "south africa", "áfrica do sul", "africa do sul", "costa do marfim", "ivory coast", 
    "côte d'ivoire", "equador", "ecuador", "holanda", "netherlands", "japao", "japaõ", 
    "japão", "japan", "brasil", "brazil", "suecia", "suécia", "sweden", "australia", 
    "austrália", "paraguai", "paraguay", "espanha", "spain", "cabo verde", "cape verde",
    "egito", "egypt", "portugal", "inglaterra", "england", "gana", "ghana", "senegal",
    "croacia", "croácia", "croatia", "argelia", "argélia", "algeria", "austria", "áustria",
    "belgica", "bélgica", "belgium", "rd congo", "dr congo", "congo"
]

def enviar_telegram(mensagem):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    dados = {"chat_id": CHAT_ID, "text": mensagem, "parse_mode": "Markdown", "disable_web_page_preview": True}
    requests.post(url, json=dados)

def pertence_a_copa(titulo_mercado):
    texto = titulo_mercado.lower()
    return any(termo in texto for termo in TERMOS_COPA)

def checar_trades():
    print(f"\n⚽ Varrendo baleias (Filtro: Copa do Mundo | Mínimo: ${VALOR_MINIMO_INVESTIDO:,.0f})...")
    sessao = requests.Session()
    sessao.headers.update({"User-Agent": "Mozilla/5.0"})
    
    for carteira in CARTEIRAS_ALVO:
        url = f"https://greg.polymarket.com/activity?user={carteira}&limit=1"
        try:
            resposta = sessao.get(url, timeout=8)
            if resposta.status_code == 200:
                trades = resposta.json()
                if trades and len(trades) > 0:
                    trade = trades[0]
                    trade_id = trade.get("id") or trade.get("transactionHash")
                    
                    if ultimas_trades_enviadas.get(carteira) != trade_id:
                        tipo_atividade = str(trade.get("type", "")).upper()
                        activity_type = str(trade.get("activityType", "")).upper()
                        
                        if "SELL" in tipo_atividade or "SELL" in activity_type or "REDEEM" in tipo_atividade:
                            continue
                        
                        mercado = trade.get("marketTitle", "")
                        if not pertence_a_copa(mercado):
                            continue
                            
                        lado = trade.get("outcome", "N/A").upper()
                        tamanho = float(trade.get("size", 0))
                        preco_pago = float(trade.get("price", 0))
                        investido = tamanho * preco_pago
                        
                        if investido < VALOR_MINIMO_INVESTIDO:
                            continue
                        
                        porcentagem = preco_pago * 100
                        odd = 1 / preco_pago if preco_pago > 0 else 0
                        carteira_curta = f"{carteira[:6]}...{carteira[-4:]}"
                        
                        mensagem = (
                            f"🏆 *BALEIA ENTROU COMPRADA · COPA DO MUNDO*\n"
                            f"🕵️‍♂️ *Carteira:* `{carteira_curta}`\n"
                            f"📌 *Mercado:* {mercado}\n\n"
                            f"Lado Escolhido: *{lado}*\n"
                            f"Cotação: {porcentagem:.1f}% (Odd {odd:.2f})\n"
                            f"Investido: *${investido:,.2f}*\n"
                            f"--- \n"
                            f"🔗 [Ver no Polymarket](https://polymarket.com/profile/{carteira})"
                        )
                        
                        enviar_telegram(mensagem)
                        ultimas_trades_enviadas[carteira] = trade_id
                        
            elif resposta.status_code == 429:
                time.sleep(15)
        except:
            pass
        time.sleep(3)

def loop_principal():
    print("🚀 Loop de monitoramento iniciado em background!")
    while True:
        checar_trades()
        time.sleep(120)

# --- INICIALIZAÇÃO MULTI-THREADING ---
if __name__ == "__main__":
    # Inicia o robô em segundo plano
    t = threading.Thread(target=loop_principal)
    t.daemon = True
    t.start()
    
    # Inicia o servidor web na thread principal para o Render manter vivo
    run_flask()
