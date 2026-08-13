import os

dirs_to_check = [
    'c:/xampp/htdocs/ifood',
    'c:/xampp/htdocs/ifood/quiz-clone'
]

required_html = [
    'index.html',
    'quiz.html',
    'dados.html',
    'endereco.html',
    'processando.html',
    'checkout.html',
    'pix-loading.html',
    'pix.html',
    'orderbump.html',
    'upsell.html',
    'upsell-correios.html',
    'upsell-iof.html',
    'sucesso.html'
]

required_assets = [
    'assets/ifoodentregadores.webp',
    'assets/bagfoto-home.webp',
    'assets/envio-rastreado.webp',
    'assets/dados-protegidos.webp',
    'assets/processo-rapido.webp',
    'assets/bagfoto.webp',
    'assets/vsl-poster.webp',
    'assets/vsl.mp4',
    'assets/pix-photo.webp',
    'assets/correios-logo.svg',
    'assets/correios-volume-banner.webp',
    'assets/seguro-bag.png',
    'assets/upsellfoto.webp',
    'assets/__task____fix_ifood_logo_on_jacket_,_202603260102 (1).webp',
    'assets/__task____isolate_ifood_delivery_box_white_background_,_202603260112 (1).webp'
]

required_images = [
    'images/gov.br-logo-0.png',
    'images/image.png',
    'images/receitafederal.png'
]

for d in dirs_to_check:
    print(f"\n================ Verification for {d} ================")
    missing = []
    
    for h in required_html:
        path = os.path.join(d, h)
        if not os.path.exists(path) or os.path.getsize(path) == 0:
            missing.append(h)
    
    for a in required_assets:
        path = os.path.join(d, a)
        if not os.path.exists(path) or os.path.getsize(path) == 0:
            missing.append(a)

    for i in required_images:
        path = os.path.join(d, i)
        if not os.path.exists(path) or os.path.getsize(path) == 0:
            missing.append(i)

    if missing:
        print(f"FAILED: Missing items: {missing}")
    else:
        print(f"SUCCESS: All {len(required_html) + len(required_assets) + len(required_images)} items present and non-empty!")

