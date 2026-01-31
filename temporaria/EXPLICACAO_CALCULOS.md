# EXPLICAÇÃO DOS CÁLCULOS: CMI vs CMI-Mil

## PROBLEMA IDENTIFICADO

Encontramos **316 municípios** (5.5% do total) com valores praticamente IDÊNTICOS entre CMI e CMI-Mil em todos os anos. Isso é **IMPOSSÍVEL** porque são metodologias completamente diferentes.

### Municípios mais afetados:
- **RJ**: 27.2% dos municípios (25 de 92)
- **SP**: 12.2% dos municípios (79 de 645) 
- **ES**: 12.8% dos municípios (10 de 78)
- **PE**: 9.7% dos municípios (18 de 185)
- **PA**: 10.4% dos municípios (15 de 144)

---

## COMO SÃO FEITOS OS CÁLCULOS

### 1. **CMI (Coeficiente de Mortalidade Infantil)**

**Fórmula:**
```
CMI = (Óbitos de menores de 1 ano / Nascidos Vivos) × 1.000
```

**Explicação:**
- Mede quantos bebês morrem **antes de completar 1 ano** para cada 1.000 nascimentos
- É uma **taxa por mil nascimentos**
- Reflete a mortalidade infantil real em relação aos nascimentos ocorridos

**Exemplo:**
- Nascidos Vivos: 10.000
- Óbitos < 1 ano: 150
- CMI = (150 / 10.000) × 1.000 = **15.0 por mil**

**Interpretação:** A cada 1.000 bebês que nascem, 15 morrem antes de completar 1 ano.

---

### 2. **CMI-Mil (Coeficiente de Mortalidade Infantil por Mil Habitantes)**

**Fórmula:**
```
CMI-Mil = (Óbitos de menores de 1 ano / População total) × 1.000
```

**Explicação:**
- Mede quantos bebês morrem **antes de completar 1 ano** para cada 1.000 habitantes da população TOTAL
- É uma **taxa por mil habitantes**
- Reflete a mortalidade infantil em relação à população inteira (incluindo adultos e idosos)

**Exemplo:**
- População Total: 100.000 habitantes
- Óbitos < 1 ano: 150
- CMI-Mil = (150 / 100.000) × 1.000 = **1.5 por mil habitantes**

**Interpretação:** A cada 1.000 habitantes (de todas as idades), ocorrem 1.5 mortes de bebês < 1 ano.

---

## POR QUE SÃO DIFERENTES?

### Denominadores completamente diferentes:

1. **CMI**: Usa **Nascidos Vivos** (ex: 10.000)
2. **CMI-Mil**: Usa **População Total** (ex: 100.000)

**A população total é sempre MUITO MAIOR que nascidos vivos!**

### Resultado esperado:

```
CMI >>> CMI-Mil  (CMI é sempre MUITO MAIOR)
```

**Exemplo real (Abreulandia-TO):**
- CMI Médio: 14.72
- CMI-Mil Médio: 12.95
- **Diferença**: 1.77

Mas **Fortaleza-CE** (SUSPEITO):
- CMI Médio: 17.69
- CMI-Mil Médio: 17.70
- **Diferença**: 0.01 ⚠️ **IMPOSSÍVEL!**

---

## O QUE ESTÁ ACONTECENDO?

### Hipóteses:

1. **As planilhas CMI.ods e CMI-Mil.ods foram calculadas com a MESMA fórmula**
   - Alguém pode ter copiado os valores de CMI para CMI-Mil
   - Ou usou a mesma fórmula para ambos

2. **Os denominadores nas planilhas estão trocados**
   - CMI pode estar usando População em vez de Nascidos Vivos
   - CMI-Mil pode estar usando Nascidos Vivos em vez de População

3. **Dados foram duplicados/copiados incorretamente**
   - Nas planilhas originais do IBGE/Ministério da Saúde

---

## SOLUÇÃO PROPOSTA

### Recalcular CMI e CMI-Mil usando nossos dados de Óbitos e Nascidos Vivos

Temos todos os dados necessários:
- ✅ **Óbitos** (extraídos das abas "UF OB")
- ✅ **Nascidos Vivos** (extraídos das abas "UF NV")
- ❌ **População Total** (precisamos buscar no IBGE)

### Passos:

1. **Buscar dados de População Total** (IBGE - estimativas anuais)
2. **Recalcular CMI** usando nossa fórmula:
   ```python
   CMI = (Obitos < 1 ano / Nascidos Vivos) × 1000
   ```
3. **Recalcular CMI-Mil** usando nossa fórmula:
   ```python
   CMI_Mil = (Obitos < 1 ano / Populacao Total) × 1000
   ```
4. **Comparar** nossos cálculos com as planilhas originais
5. **Substituir** os valores incorretos pelos nossos cálculos

---

## EXEMPLO PRÁTICO

### Município: FORTALEZA-CE (2020)

**Dados que temos:**
- Óbitos < 1 ano: 500 (hipotético)
- Nascidos Vivos: 40.000 (hipotético)

**Dados que precisamos:**
- População Total: 2.700.000 habitantes (IBGE)

**Cálculos corretos:**
```
CMI = (500 / 40.000) × 1.000 = 12.5 por mil nascimentos

CMI-Mil = (500 / 2.700.000) × 1.000 = 0.185 por mil habitantes
```

**Diferença esperada:** CMI é **67 vezes MAIOR** que CMI-Mil!

---

## PRÓXIMOS PASSOS

1. ✅ Identificar municípios com valores suspeitos (FEITO - 316 municípios)
2. ⏳ Buscar dados de População Total (IBGE) para todos os municípios/anos
3. ⏳ Recalcular CMI usando nossos dados de Óbitos e Nascidos Vivos
4. ⏳ Recalcular CMI-Mil usando População Total + Óbitos
5. ⏳ Comparar e validar os novos cálculos
6. ⏳ Substituir dados incorretos no dashboard

---

## REFERÊNCIAS

- **CMI**: Usado por OMS, UNICEF, Ministério da Saúde
  - Mede mortalidade em relação aos nascimentos
  
- **CMI-Mil**: Menos comum, usado em análises demográficas
  - Mede mortalidade infantil como proporção da população total

**IMPORTANTE:** Ambos são indicadores válidos, mas medem coisas DIFERENTES e NÃO PODEM ter valores idênticos!
