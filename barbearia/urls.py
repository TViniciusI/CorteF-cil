from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("cadastrar_barbearia/", views.cadastrar_barbearia, name="cadastrar_barbearia"),

    # Clientes
    path("cadastrar_cliente/", views.cadastrar_cliente, name="cadastrar_cliente"),
    path("cliente/editar/<int:cliente_id>/", views.editar_cliente, name="editar_cliente"),
    path("cliente/remover/<int:cliente_id>/", views.remover_cliente, name="remover_cliente"),

    # Agendamentos
    path("novo_agendamento/", views.novo_agendamento, name="novo_agendamento"),
    path("agendamento/finalizar/<int:agendamento_id>/", views.finalizar_corte, name="finalizar_corte"),
    path("agendamento/editar/<int:agendamento_id>/", views.editar_agendamento, name="editar_agendamento"),
    path("agendamento/remover/<int:agendamento_id>/", views.remover_agendamento, name="remover_agendamento"),

    # Serviços & Preços
    path("cadastrar_preco/", views.cadastrar_preco, name="cadastrar_preco"),
    path("preco/editar/<int:preco_id>/", views.editar_preco, name="editar_preco"),
    path("preco/remover/<int:preco_id>/", views.remover_preco, name="remover_preco"),
    path("editar_barbearia/<int:barbearia_id>/", views.editar_barbearia, name="editar_barbearia"),

]
