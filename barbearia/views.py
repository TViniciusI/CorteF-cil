from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils import timezone
from django.db.models import Sum
from .models import Agendamento, Cliente, Barbearia, Preco
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User

def login_view(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        if user is not None:
            # Só deixa logar se já existir pelo menos uma barbearia
            if not Barbearia.objects.exists():
                messages.warning(request, "Nenhuma barbearia cadastrada ainda. Cadastre antes de usar o sistema.")
                return redirect("cadastrar_barbearia")

            auth_login(request, user)
            return redirect("home")
        else:
            messages.error(request, "Usuário ou senha inválidos.")
            return redirect("login")

    # GET → exibe a tela de login sempre
    return render(request, "barbearia/login.html")



def logout_view(request):
    auth_logout(request)
    return redirect("login")


def cadastrar_barbearia(request):
    if request.method == "POST":
        nome = request.POST.get("nome")
        cnpj = request.POST.get("cnpj")
        responsavel = request.POST.get("responsavel")
        telefone = request.POST.get("telefone")

        # Dados para criar usuário
        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")

        barbearia = Barbearia.objects.create(
            nome=nome,
            cnpj=cnpj,
            responsavel=responsavel,
            telefone=telefone or "",
        )

        # Cria usuário para login
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=responsavel
        )

        messages.success(request, "Barbearia cadastrada e usuário criado! Faça login para continuar.")
        return redirect("login")

    return render(request, "barbearia/cadastrar_barbearia.html")


# Cadastrar cliente
def cadastrar_cliente(request):
    if request.method == "POST":
        nome = request.POST.get("nome", "").strip()
        telefone = request.POST.get("telefone", "").strip()

        if not nome:
            messages.error(request, "Informe o nome do cliente.")
            return redirect("home")

        barbearia = Barbearia.objects.first() or Barbearia.objects.create(nome="Minha Barbearia", telefone="")

        cliente, created = Cliente.objects.get_or_create(
            barbearia=barbearia,
            nome=nome,
            defaults={"telefone": telefone},
        )

        if not created and telefone and not cliente.telefone:
            cliente.telefone = telefone
            cliente.save(update_fields=["telefone"])

        messages.success(request, "Cliente cadastrado com sucesso!")
    return redirect("home")


# Cadastrar serviço/preço
def cadastrar_preco(request):
    if request.method == "POST":
        servico = request.POST.get("servico")
        valor = request.POST.get("valor")

        barbearia = Barbearia.objects.first() or Barbearia.objects.create(nome="Minha Barbearia", telefone="")

        Preco.objects.create(
            barbearia=barbearia,
            servico=servico,
            valor=valor
        )

        messages.success(request, "Serviço cadastrado com sucesso!")
    return redirect("home")


# views.py (novo_agendamento)
from datetime import datetime

from datetime import datetime

def novo_agendamento(request):
    if request.method == "POST":
        cliente_nome = request.POST.get("cliente", "").strip()
        servico = request.POST.get("servico", "").strip()
        data_hora_str = request.POST.get("data_hora")
        valor = request.POST.get("valor", "").strip()
        barbeiro = request.POST.get("barbeiro", "").strip()  # <<< pega do formulário

        if not cliente_nome or not servico or not data_hora_str or not valor or not barbeiro:
            messages.error(request, "Preencha todos os campos obrigatórios.")
            return redirect("home")

        try:
            data_hora = datetime.fromisoformat(data_hora_str)
        except ValueError:
            messages.error(request, "Data e hora inválidas. Use o formato AAAA-MM-DDTHH:MM.")
            return redirect("home")

        barbearia = Barbearia.objects.first() or Barbearia.objects.create(
            nome="Minha Barbearia", telefone=""
        )

        # Tenta buscar cliente existente
        cliente = Cliente.objects.filter(
            barbearia=barbearia, nome__iexact=cliente_nome
        ).first()

        if not cliente:
            agendamento = Agendamento.objects.create(
                barbearia=barbearia,
                cliente=None,
                nome_avulso=cliente_nome,
                servico=servico,
                data_hora=data_hora,
                valor=valor,
                barbeiro=barbeiro,   # <<< salva barbeiro
            )
        else:
            agendamento = Agendamento.objects.create(
                barbearia=barbearia,
                cliente=cliente,
                servico=servico,
                data_hora=data_hora,
                valor=valor,
                barbeiro=barbeiro,   # <<< salva barbeiro
            )

        messages.success(request, f"Agendamento para {cliente_nome} com {barbeiro} criado com sucesso!")
        return redirect("home")

    return redirect("home")


# views.py (editar_agendamento)
def editar_agendamento(request, agendamento_id):
    ...
    data_hora_str = request.POST.get("data_hora")
    if data_hora_str:
        try:
            agendamento.data_hora = datetime.fromisoformat(data_hora_str)
        except ValueError:
            messages.error(
                request,
                "Data e hora inválidas. Utilize o formato AAAA-MM-DDTHH:MM."
            )
            return redirect("home")
    ...


# Finalizar corte
def finalizar_corte(request, agendamento_id):
    agendamento = get_object_or_404(Agendamento, id=agendamento_id)
    agendamento.realizado = True
    agendamento.save()
    messages.success(request, f"Corte de {agendamento.cliente.nome} finalizado com sucesso!")
    return redirect("home")


from datetime import timedelta

from django.contrib.auth.models import User

@login_required(login_url="login")
def home(request):
    hoje = timezone.now().date()
    mes_inicio = hoje.replace(day=1)
    semana_inicio = hoje - timedelta(days=7)

    agendamentos_mes = Agendamento.objects.filter(data_hora__date__gte=mes_inicio)
    total_agendamentos_mes = agendamentos_mes.count()
    total_cortes = agendamentos_mes.filter(realizado=True).count()
    clientes_mes = Cliente.objects.filter(data_criacao__gte=mes_inicio).count()
    faturamento_mes = agendamentos_mes.filter(realizado=True).aggregate(total=Sum("valor"))["total"] or 0

    faturamento_semana = Agendamento.objects.filter(
        data_hora__date__gte=semana_inicio, realizado=True
    ).aggregate(total=Sum("valor"))["total"] or 0

    faturamento_dia = Agendamento.objects.filter(
        data_hora__date=hoje, realizado=True
    ).aggregate(total=Sum("valor"))["total"] or 0

    proximos_agendamentos = Agendamento.objects.filter(
        data_hora__gte=timezone.now()
    ).order_by("data_hora")[:5]

    clientes = Cliente.objects.all().order_by("-data_criacao")
    precos = Preco.objects.all().order_by("servico")
    barbearia = Barbearia.objects.first()

    # Lista de barbeiros -> pega todos os usuários cadastrados
    barbeiros_list = User.objects.values_list("first_name", flat=True)

    context = {
        "total_agendamentos_mes": total_agendamentos_mes,
        "total_cortes": total_cortes,
        "clientes_mes": clientes_mes,
        "faturamento_mes": faturamento_mes,
        "proximos_agendamentos": proximos_agendamentos,
        "agendamentos": agendamentos_mes,
        "clientes": clientes,
        "precos": precos,
        "faturamento_semana": faturamento_semana,
        "faturamento_dia": faturamento_dia,
        "barbearia": barbearia,
        "barbeiros_list": barbeiros_list,  # <<<<< NOVO
    }
    return render(request, "barbearia/home.html", context)



# Editar cliente (apenas POST; GET redireciona)
def editar_cliente(request, cliente_id):
    cliente = get_object_or_404(Cliente, id=cliente_id)
    if request.method == "POST":
        cliente.nome = request.POST.get("nome", cliente.nome).strip()
        cliente.telefone = request.POST.get("telefone", cliente.telefone).strip()
        cliente.save(update_fields=["nome", "telefone"])
        messages.success(request, "Cliente atualizado com sucesso!")
    return redirect("home")


# Remover cliente
def remover_cliente(request, cliente_id):
    cliente = get_object_or_404(Cliente, id=cliente_id)
    cliente.delete()
    messages.success(request, "Cliente removido com sucesso!")
    return redirect("home")

def editar_agendamento(request, agendamento_id):
    agendamento = get_object_or_404(Agendamento, id=agendamento_id)
    if request.method == "POST":
        agendamento.servico = request.POST.get("servico", agendamento.servico)
        agendamento.data_hora = request.POST.get("data_hora", agendamento.data_hora)
        agendamento.valor = request.POST.get("valor", agendamento.valor)
        agendamento.save()
        messages.success(request, "Agendamento atualizado com sucesso!")
    return redirect("home")


# Remover agendamento
def remover_agendamento(request, agendamento_id):
    agendamento = get_object_or_404(Agendamento, id=agendamento_id)
    agendamento.delete()
    messages.success(request, "Agendamento removido com sucesso!")
    return redirect("home")

# Editar serviço/preço
def editar_preco(request, preco_id):
    preco = get_object_or_404(Preco, id=preco_id)
    if request.method == "POST":
        preco.servico = request.POST.get("servico", preco.servico)
        preco.valor = request.POST.get("valor", preco.valor)
        preco.save()
        messages.success(request, "Serviço atualizado com sucesso!")
        return redirect("home")
    return redirect("home")


# Remover serviço/preço
def remover_preco(request, preco_id):
    preco = get_object_or_404(Preco, id=preco_id)
    preco.delete()
    messages.success(request, "Serviço removido com sucesso!")
    return redirect("home")

# Finalizar corte
def finalizar_corte(request, agendamento_id):
    agendamento = get_object_or_404(Agendamento, id=agendamento_id)

    if not agendamento.realizado:  # evita marcar duas vezes
        agendamento.realizado = True
        agendamento.save()
        messages.success(
            request,
            f"Corte de {agendamento.cliente.nome} finalizado! Valor de R$ {agendamento.valor} adicionado ao faturamento."
        )
    else:
        messages.info(request, f"O corte de {agendamento.cliente.nome} já havia sido finalizado.")

    return redirect("home")

@login_required(login_url="login")
def editar_barbearia(request, barbearia_id):
    barbearia = get_object_or_404(Barbearia, id=barbearia_id)
    if request.method == "POST":
        barbearia.nome = request.POST.get("nome")
        barbearia.cnpj = request.POST.get("cnpj")
        barbearia.responsavel = request.POST.get("responsavel")
        barbearia.telefone = request.POST.get("telefone")
        barbearia.save()
        messages.success(request, "Barbearia atualizada com sucesso!")
        return redirect("home")
    return redirect("home")
