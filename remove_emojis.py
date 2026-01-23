import re

# Lê o arquivo
with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Remove emojis
emojis_to_remove = ['🏙️', '💡', '📍', '⚠️', '❌', '📊', '🌎']
for emoji in emojis_to_remove:
    content = content.replace(emoji, '')

# Remove espaços duplicados resultantes
content = re.sub(r'  +', ' ', content)

# Salva o arquivo
with open('app.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Emojis removidos com sucesso!")
