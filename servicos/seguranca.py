
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError, VerificationError

# Configuração do Argon2
password_hasher = PasswordHasher()


def gerar_hash_senha(senha: str) -> str:
    """
    Gera um hash seguro para a senha.
    """
    return password_hasher.hash(senha)


def verificar_senha(senha: str, senha_hash: str) -> bool:
    """
    Verifica se a senha corresponde ao hash armazenado.
    """
    try:
        return password_hasher.verify(senha_hash, senha)

    except (VerifyMismatchError, VerificationError):
        return False
