from django.db import models
from django.utils import timezone


class Barbearia(models.Model):
    nome = models.CharField(max_length=255)
    telefone = models.CharField(max_length=20, blank=True, null=True)
    cnpj = models.CharField(max_length=18, blank=True, null=True)
    responsavel = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return self.nome


class Cliente(models.Model):
    barbearia = models.ForeignKey(Barbearia, on_delete=models.CASCADE)
    nome = models.CharField(max_length=100)
    telefone = models.CharField(max_length=20)
    data_criacao = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nome


class Agendamento(models.Model):
    barbearia = models.ForeignKey(Barbearia, on_delete=models.CASCADE)
    cliente = models.ForeignKey(Cliente, null=True, blank=True, on_delete=models.SET_NULL)
    nome_avulso = models.CharField(max_length=100, blank=True, null=True)
    servico = models.CharField(max_length=100)
    data_hora = models.DateTimeField()
    valor = models.DecimalField(max_digits=8, decimal_places=2)
    barbeiro = models.CharField(max_length=100, null=True, blank=True)  # <<<<< AQUI
    realizado = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.cliente or self.nome_avulso} - {self.servico}"


class Preco(models.Model):
    barbearia = models.ForeignKey(Barbearia, on_delete=models.CASCADE)
    servico = models.CharField(max_length=100)
    valor = models.DecimalField(max_digits=8, decimal_places=2)

    def __str__(self):
        return f"{self.servico} - R$ {self.valor}"
