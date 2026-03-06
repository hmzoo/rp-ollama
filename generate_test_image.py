#!/usr/bin/env python3
"""
Génère une image de test simple pour tester les modèles de vision
"""

try:
    from PIL import Image, ImageDraw, ImageFont
    import sys
    
    # Créer une image de test 800x600
    img = Image.new('RGB', (800, 600), color=(70, 130, 180))  # Bleu acier
    draw = ImageDraw.Draw(img)
    
    # Dessiner un rectangle rouge
    draw.rectangle([50, 50, 250, 250], fill=(255, 0, 0), outline=(0, 0, 0), width=3)
    
    # Dessiner un cercle vert
    draw.ellipse([300, 100, 500, 300], fill=(0, 255, 0), outline=(0, 0, 0), width=3)
    
    # Dessiner un triangle jaune
    draw.polygon([(600, 250), (700, 100), (750, 250)], fill=(255, 255, 0), outline=(0, 0, 0))
    
    # Ajouter du texte
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 40)
    except:
        font = ImageFont.load_default()
    
    draw.text((150, 350), "Image de Test", fill=(255, 255, 255), font=font)
    draw.text((120, 420), "3 formes géométriques", fill=(255, 255, 255), font=font)
    
    # Sauvegarder
    output_file = "test_image.jpg"
    img.save(output_file, quality=95)
    
    print(f"✅ Image de test créée : {output_file}")
    print("\nPour tester :")
    print(f"  ./vision_client.py {output_file} \"Décris cette image\"")
    print(f"  ./vision_client.py {output_file} \"Combien de formes géométriques?\"")
    print(f"  ./vision_client.py {output_file} \"Quelles couleurs vois-tu?\"")
    
except ImportError:
    print("❌ Pillow n'est pas installé")
    print("Installez-le avec: pip install Pillow")
    sys.exit(1)
