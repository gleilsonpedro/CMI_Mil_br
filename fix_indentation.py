import re

# Lê o arquivo
with open('app.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Corrige a indentação
fixed_lines = []
indent_level = 0
in_multiline_string = False
string_delimiter = None

for i, line in enumerate(lines):
    stripped = line.lstrip()
    
    # Detecta strings multilinhas
    if '"""' in stripped or "'''" in stripped:
        if not in_multiline_string:
            in_multiline_string = True
            string_delimiter = '"""' if '"""' in stripped else "'''"
        elif string_delimiter in stripped:
            in_multiline_string = False
    
    # Pula linhas vazias e comentários
    if not stripped or (stripped.startswith('#') and not in_multiline_string):
        fixed_lines.append(line)
        continue
    
    # Dentro de string multilinhas, mantém como está
    if in_multiline_string and i > 0:
        fixed_lines.append(line)
        continue
    
    # Conta quantos espaços deveria ter baseado no nível de indentação
    # Ajusta o nível baseado nas palavras-chave
    if i > 0:
        prev_stripped = lines[i-1].lstrip()
        
        # Diminui indentação para palavras-chave que fecham blocos
        if stripped.startswith(('elif ', 'else:', 'except:', 'except ', 'finally:', 'elif(')):
            indent_level = max(0, indent_level - 1)
        
        # Verifica se linha anterior abre bloco
        if prev_stripped.rstrip().endswith(':') and not prev_stripped.startswith('#'):
            if not (prev_stripped.startswith(('"""', "'''"))):
                indent_level += 1
    
    # Diminui indentação após return, break, continue, pass, raise
    if i > 0:
        prev_stripped = lines[i-1].lstrip()
        if prev_stripped.startswith(('return ', 'return\n', 'break', 'continue', 'pass', 'raise ')):
            # Se próxima linha não é def, class, if, for, while, try, with
            if not stripped.startswith(('def ', 'class ', '@', 'if ', 'elif ', 'else:', 'for ', 'while ', 'try:', 'with ', 'except')):
                # Verifica se devemos voltar ao nível anterior
                if indent_level > 0:
                    indent_level -= 1
    
    # Aplica indentação (4 espaços por nível)
    fixed_line = (' ' * (indent_level * 4)) + stripped
    fixed_lines.append(fixed_line)
    
    # Volta indentação após elif, else, except, finally
    if stripped.startswith(('elif ', 'else:', 'except:', 'except ', 'finally:', 'elif(')):
        indent_level += 1

# Salva arquivo corrigido
with open('app_fixed.py', 'w', encoding='utf-8') as f:
    f.writelines(fixed_lines)

print("Arquivo corrigido salvo como app_fixed.py")
print("Verifique se está correto antes de substituir o original")
