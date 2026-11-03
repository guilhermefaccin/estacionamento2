from argon2 import PasswordHasher
from argon2.exceptions import InvalidHashError, VerificationError, VerifyMismatchError

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

    except (InvalidHashError, VerifyMismatchError, VerificationError):
        return False
