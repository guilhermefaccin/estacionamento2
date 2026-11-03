
from servicos.seguranca import gerar_hash_senha, verificar_senha

senha = "Teste@123"

# Gerar hash
senha_hash = gerar_hash_senha(senha)

print("Hash gerado:")
print(senha_hash)

# Verificar senha correta
print("Senha correta:", verificar_senha(senha, senha_hash))

# Verificar senha incorreta
print("Senha incorreta:", verificar_senha("SenhaErrada", senha_hash))
