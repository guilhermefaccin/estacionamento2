
from getpass import getpass
from sqlmodel import Session, select

from banco.sessao import obter_sessao
from entidades.models import Usuario
from servicos.seguranca import gerar_hash_senha


def criar_admin():
    nome = input("Nome do administrador: ").strip()
    cpf = input("CPF (somente números): ").strip()
    email = input("E-mail: ").strip().lower()

    senha = getpass("Senha: ")
    confirmar_senha = getpass("Confirme a senha: ")

    if not nome or len(cpf) != 11 or not cpf.isdigit():
        print("Nome ou CPF inválido.")
        return

    if senha != confirmar_senha:
        print("As senhas não conferem.")
        return

    if len(senha) < 8:
        print("A senha deve ter pelo menos 8 caracteres.")
        return

    gerador = obter_sessao()
    db = next(gerador)

    try:
        existente = db.exec(
            select(Usuario).where(
                (Usuario.cpf == cpf) |
                (Usuario.email == email)
            )
        ).first()

        if existente:
            print("Já existe um usuário com esse CPF ou e-mail.")
            return

        admin = Usuario(
            nome=nome,
            cpf=cpf,
            email=email,
            senha=gerar_hash_senha(senha),
            perfil="ADMIN",
            ativo=True
        )

        db.add(admin)
        db.commit()

        print("Administrador criado com sucesso!")

    finally:
        db.close()
        gerador.close()


if __name__ == "__main__":
    criar_admin()
