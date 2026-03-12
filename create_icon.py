# Script para criar ícone básico .ico se não existir
# Requer Pillow

try:
    from PIL import Image, ImageDraw, ImageFont
    import os
    
    # Criar diretório assets se não existir
    os.makedirs("assets", exist_ok=True)
    
    # Criar imagem 256x256 com fundo azul
    img = Image.new('RGB', (256, 256), color=(41, 128, 185))
    draw = ImageDraw.Draw(img)
    
    # Desenhar círculo branco
    draw.ellipse([40, 40, 216, 216], fill=(236, 240, 241))
    
    # Desenhar "RF" no centro
    try:
        font = ImageFont.truetype("arial.ttf", 80)
    except:
        font = ImageFont.load_default()
    
    text = "RF"
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    x = (256 - text_width) // 2
    y = (256 - text_height) // 2 - 10
    
    draw.text((x, y), text, fill=(41, 128, 185), font=font)
    
    # Salvar como .ico
    img.save("assets/icon.ico", format='ICO', sizes=[(256,256), (128,128), (64,64), (48,48), (32,32), (16,16)])
    print("✓ Ícone criado em assets/icon.ico")
    
except ImportError:
    print("⚠ Pillow não instalado. Pulando criação de ícone.")
    print("  O build usará ícone padrão do PyInstaller")
except Exception as e:
    print(f"⚠ Erro ao criar ícone: {e}")
    print("  O build usará ícone padrão do PyInstaller")
