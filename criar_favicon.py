#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script para converter a logo.jpg em favicon.ico com múltiplos tamanhos
"""

import os
from PIL import Image

# Caminho para a logo
logo_path = os.path.join('static', 'logo.jpg')
favicon_path = os.path.join('static', 'favicon.ico')

# Verificar se a logo existe
if not os.path.exists(logo_path):
    print(f"❌ Arquivo {logo_path} não encontrado!")
    exit(1)

try:
    # Abrir a imagem
    print(f"📂 Abrindo {logo_path}...")
    img = Image.open(logo_path)
    
    # Converter para RGBA se necessário
    if img.mode != 'RGBA':
        img = img.convert('RGBA')
    
    # Tamanhos comuns para favicon (16x16, 32x32, 48x48, 64x64)
    sizes = [(16, 16), (32, 32), (48, 48), (64, 64)]
    
    # Redimensionar para o maior tamanho primeiro
    img_resized = img.resize((64, 64), Image.Resampling.LANCZOS)
    
    # Salvar como ICO com múltiplos tamanhos
    print(f"💾 Salvando favicon em {favicon_path}...")
    img_resized.save(
        favicon_path,
        format='ICO',
        sizes=sizes
    )
    
    print(f"✅ Favicon criado com sucesso!")
    print(f"📏 Tamanhos: {sizes}")
    
    # Criar também PNG para Apple Touch Icon e Android
    favicon_png_path = os.path.join('static', 'favicon.png')
    img_180 = img.resize((180, 180), Image.Resampling.LANCZOS)
    img_180.save(favicon_png_path, format='PNG', optimize=True)
    print(f"✅ favicon.png (180x180) criado para dispositivos móveis!")
    
    # Criar favicon 192x192 para PWA
    favicon_192_path = os.path.join('static', 'favicon-192.png')
    img_192 = img.resize((192, 192), Image.Resampling.LANCZOS)
    img_192.save(favicon_192_path, format='PNG', optimize=True)
    print(f"✅ favicon-192.png criado para PWA!")
    
    # Criar favicon 512x512 para PWA
    favicon_512_path = os.path.join('static', 'favicon-512.png')
    img_512 = img.resize((512, 512), Image.Resampling.LANCZOS)
    img_512.save(favicon_512_path, format='PNG', optimize=True)
    print(f"✅ favicon-512.png criado para PWA!")
    
    print("\n🎉 Todos os favicons foram criados com sucesso!")
    print("\n📋 Arquivos criados:")
    print(f"  • {favicon_path} - Favicon tradicional (ICO)")
    print(f"  • {favicon_png_path} - Apple Touch Icon (180x180)")
    print(f"  • {favicon_192_path} - PWA Icon (192x192)")
    print(f"  • {favicon_512_path} - PWA Icon (512x512)")
    
except Exception as e:
    print(f"❌ Erro ao criar favicon: {e}")
    import traceback
    traceback.print_exc()
