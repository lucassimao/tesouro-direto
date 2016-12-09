from  datetime import datetime
from  datetime import timedelta
import math
import time
import re
from dateutil import rrule
import dateutil.relativedelta

lista_feriados = []
with open('feriados_nacionais.csv', 'r') as f:
    pattern = re.compile('^\d{1,2}\/\d{1,2}\/\d{4}')
    for line in f:
        match = pattern.search(line)
        if match:
            txt = match.group(0)
            dt = datetime.strptime(txt,'%d/%m/%Y')
            lista_feriados.append(dt)

def calcular_rendimento(data_de_compra,data_de_venda,data_do_vencimento,valor_titulo,valor_investido_liquido):
    taxa_de_compra = 6.01/100.0
    taxa_de_venda = 7.01/100.0 ## So da p/ saber se for vendido antes do tempo
    taxa_administracao = 0.1/100.0
    expectativa_ipca = 5/100.0
    aliquota_ir = 15/100.0

    dia_corridos_entre_compra_e_vencimento = (data_do_vencimento-data_de_compra).days - 1
    dia_corridos_entre_compra_e_venda = (data_de_venda-data_de_compra).days - 1
    business_days_compra_vencimento = len(list(rrule.rrule(rrule.DAILY, dtstart=data_de_compra, until=data_do_vencimento - timedelta(days=1),
                                              byweekday=(rrule.MO, rrule.TU, rrule.WE, rrule.TH, rrule.FR))))
    business_days_compra_venda = len(list(rrule.rrule(rrule.DAILY, dtstart=data_de_compra, until=data_de_venda - timedelta(days=1),
                                              byweekday=(rrule.MO, rrule.TU, rrule.WE, rrule.TH, rrule.FR))))
    dias_uteis_compra_vencimento = business_days_compra_vencimento
    dias_uteis_compra_venda = business_days_compra_venda
    for feriado in lista_feriados:
        if feriado.weekday() not in [5,6]:
            if feriado >  data_de_compra and feriado < data_do_vencimento:
                dias_uteis_compra_vencimento -=1
            if feriado >  data_de_compra and feriado < data_de_venda:
                dias_uteis_compra_venda -=1

    #print (dia_corridos_entre_compra_e_vencimento,dia_corridos_entre_compra_e_venda,dias_uteis_compra_vencimento,dias_uteis_compra_venda)

    if dia_corridos_entre_compra_e_venda <= 180:
        aliquota_ir = 22.5/100.0
    elif dia_corridos_entre_compra_e_venda <= 360:
        aliquota_ir = 20/100.0
    elif dia_corridos_entre_compra_e_venda <= 720:
        aliquota_ir = 17.5/100.0
    else:
        aliquota_ir = 15/100.0

    taxa_administracao_entrada = valor_investido_liquido*taxa_administracao
    valor_investido_bruto = taxa_administracao_entrada + valor_investido_liquido
    valor_bruto_resgate = 0
    valor_taxa_administracao = 0

    if dia_corridos_entre_compra_e_venda == dia_corridos_entre_compra_e_vencimento:
        valor_bruto_resgate = ((((1+taxa_de_compra)**(dias_uteis_compra_venda/252.0))*((1+expectativa_ipca)**(dias_uteis_compra_venda/252.0)))*(valor_investido_liquido))
    else:
        valor_bruto_resgate = ((((1+taxa_de_compra)**(dias_uteis_compra_venda/252.0))*((1+expectativa_ipca)**(dias_uteis_compra_venda/252.0)))*(valor_investido_liquido))
        valor_bruto_resgate = valor_bruto_resgate/((1+taxa_de_venda)**((dias_uteis_compra_vencimento-dias_uteis_compra_venda)/252.0))


    valor_custodia = (0.003*( (dia_corridos_entre_compra_e_venda-3)/365.0))*((valor_investido_liquido+valor_bruto_resgate)/2.0)
    if dia_corridos_entre_compra_e_vencimento > 365:
        valor_taxa_administracao = ((taxa_administracao
                                    *((dia_corridos_entre_compra_e_venda-3-365)/365.0))
                                    *((valor_investido_liquido+valor_bruto_resgate)/2.0))
    else:
        valor_taxa_administracao = 0

    imposto_de_renda = aliquota_ir*(valor_bruto_resgate-valor_investido_liquido-valor_custodia-valor_taxa_administracao)
    valor_liquido_resgate = ((valor_bruto_resgate-valor_custodia)-valor_taxa_administracao)-imposto_de_renda
    return valor_liquido_resgate

if __name__ == '__main__':
    data_de_compra = datetime(2016,12,20)
    data_de_venda = datetime(2035,05,15)
    data_do_vencimento = datetime(2035,05,15)
    valor_titulo = 1010.16
    valor_investido_liquido = 1000
    acumulado = 0
    while data_de_compra < data_do_vencimento:
        #print data_de_compra
        acumulado += calcular_rendimento(data_de_compra,data_de_venda,data_do_vencimento,valor_titulo,valor_investido_liquido)
        data_de_compra += dateutil.relativedelta.relativedelta(months=1)
    print '%.2f' % acumulado
